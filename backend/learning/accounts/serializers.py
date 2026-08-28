"""账号注册、认证和个人资料的输入输出契约。"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from ..models import StudyGroup
from .email_verification import EmailVerificationError, consume_verification_code, normalize_email

User = get_user_model()


class SafeTokenRefreshSerializer(TokenRefreshSerializer):
    """在用户已删除时返回稳定认证错误的刷新令牌序列化器。"""

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("登录账号已不存在，请重新登录。") from exc


class UserSerializer(serializers.ModelSerializer):
    """输出前端会话所需的当前用户公开资料。"""

    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "name", "is_staff")

    def get_name(self, obj):
        return obj.first_name or obj.username


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """校验并更新当前用户的资料、邮箱和密码。"""

    name = serializers.CharField(source="first_name", max_length=80, required=False, allow_blank=True)
    email_code = serializers.RegexField(r"^\d{6}$", write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("email", "email_code", "name", "current_password", "new_password")
        extra_kwargs = {"email": {"required": False, "allow_blank": True}}

    def validate_email(self, value):
        value = normalize_email(value)
        if value and User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("该邮箱已被使用。")
        return value

    def validate(self, attrs):
        current = attrs.pop("current_password", "")
        new = attrs.pop("new_password", "")
        code = attrs.pop("email_code", "")
        email = attrs.get("email")
        if email is not None and email != normalize_email(self.instance.email):
            if not email or not code:
                raise serializers.ValidationError({"email_code": "修改邮箱时请先获取并填写验证码。"})
            attrs["email_code"] = code
        if bool(current) != bool(new):
            raise serializers.ValidationError("修改密码时请同时填写当前密码和新密码。")
        if new:
            user = self.instance
            if not user.check_password(current):
                raise serializers.ValidationError({"current_password": "当前密码不正确。"})
            if user.check_password(new):
                raise serializers.ValidationError({"new_password": "新密码不能与当前密码相同。"})
            validate_password(new, user=user)
            attrs["new_password"] = new
        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop("new_password", "")
        code = validated_data.pop("email_code", "")
        if code:
            try:
                consume_verification_code(validated_data["email"], code)
            except EmailVerificationError as exc:
                raise serializers.ValidationError({"email_code": str(exc)}) from exc
        for key, value in validated_data.items():
            setattr(instance, key, value.strip() if isinstance(value, str) else value)
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """校验邮箱验证和小队邀请后创建账号。"""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    email_code = serializers.RegexField(r"^\d{6}$", write_only=True)
    name = serializers.CharField(write_only=True, max_length=80, required=False, allow_blank=True)
    invite_code = serializers.CharField(write_only=True, max_length=12, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "email", "email_code", "password", "password_confirm", "name", "invite_code")
        extra_kwargs = {"email": {"required": True, "allow_blank": False}}

    def validate_email(self, value):
        value = normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("该邮箱已被注册。")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "两次输入的密码不一致。"})
        invite_code = attrs.pop("invite_code", "").strip().upper()
        self.invite_group = StudyGroup.objects.filter(invite_code=invite_code).first() if invite_code else None
        if invite_code and not self.invite_group:
            raise serializers.ValidationError({"invite_code": "邀请码无效或已经更新。"})
        if settings.INVITE_ONLY_REGISTRATION and not self.invite_group:
            raise serializers.ValidationError({"invite_code": "当前仅允许通过学习小队邀请注册。"})
        return attrs

    def create(self, validated_data):
        name = validated_data.pop("name", "").strip()
        code = validated_data.pop("email_code")
        try:
            consume_verification_code(validated_data["email"], code)
        except EmailVerificationError as exc:
            raise serializers.ValidationError({"email_code": str(exc)}) from exc
        with transaction.atomic():
            user = User.objects.create_user(first_name=name, **validated_data)
            if self.invite_group:
                self.invite_group.members.add(user)
        return user


class EmailCodeRequestSerializer(serializers.Serializer):
    """校验注册或换绑邮箱验证码的发送请求。"""

    email = serializers.EmailField(max_length=254)
    invite_code = serializers.CharField(write_only=True, max_length=12, required=False, allow_blank=True)

    def validate_email(self, value):
        value = normalize_email(value)
        queryset = User.objects.filter(email__iexact=value)
        user = self.context["request"].user
        if user.is_authenticated:
            queryset = queryset.exclude(pk=user.pk)
        if queryset.exists():
            raise serializers.ValidationError("该邮箱已被使用。")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        if not request.user.is_authenticated and settings.INVITE_ONLY_REGISTRATION:
            code = attrs.get("invite_code", "").strip().upper()
            if not code or not StudyGroup.objects.filter(invite_code=code).exists():
                raise serializers.ValidationError({"invite_code": "请先填写有效的学习小队邀请码。"})
        return attrs

