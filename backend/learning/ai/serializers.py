"""校验并输出 AI 凭据、会话、消息和多模态请求。"""

from rest_framework import serializers

from ..models import AIAdapter, AIChatMessage, AIChatSession, AIProviderCredential, DayProgress
from .services import CONTEXT_ROUNDS, provider_config


class AIProviderCredentialSerializer(serializers.ModelSerializer):
    """输出可识别的配置和密钥提示，永不序列化密文或原始 Key。"""

    class Meta:
        model = AIProviderCredential
        fields = (
            "id", "name", "provider", "adapter", "api_url", "model", "key_last_four",
            "last_verified_at", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "provider", "adapter", "api_url", "model", "key_last_four",
            "last_verified_at", "created_at", "updated_at",
        )


class AICredentialInputSerializer(serializers.Serializer):
    """校验一次凭据连接测试或保存请求。"""

    name = serializers.CharField(max_length=80, required=False, allow_blank=False, trim_whitespace=True)
    provider = serializers.CharField(max_length=24)
    adapter = serializers.ChoiceField(choices=AIAdapter.choices, required=False, allow_blank=True)
    api_url = serializers.CharField(max_length=500, required=False, allow_blank=True, trim_whitespace=True)
    model = serializers.CharField(max_length=100, required=False, allow_blank=True, trim_whitespace=True)
    api_key = serializers.CharField(
        max_length=512,
        required=False,
        allow_blank=False,
        trim_whitespace=True,
        write_only=True,
    )

    def validate_provider(self, value):
        """拒绝服务端未注册的供应商。"""
        provider_config(value)
        return value

    def validate_api_key(self, value):
        """拒绝可能破坏认证请求头边界的空白和非 ASCII 控制内容。"""
        if not value or any(ord(char) < 33 or ord(char) > 126 for char in value):
            raise serializers.ValidationError("API Key 只能包含可打印的 ASCII 字符且不能含空格。")
        return value

    def validate(self, attrs):
        """验证完整的用户接口配置，并保存统一格式的 HTTPS 地址。"""
        if self.context.get("require_api_key") and not attrs.get("api_key"):
            raise serializers.ValidationError({"api_key": "请输入 API Key。"})
        config = provider_config(
            attrs.get("provider"),
            attrs.get("model") or None,
            attrs.get("adapter", ""),
            attrs.get("api_url", ""),
        )
        if attrs.get("api_url"):
            attrs["api_url"] = config["api_url"]
        return attrs


class AIChatMessageSerializer(serializers.ModelSerializer):
    """输出聊天文本、限时附件说明和供应商用量。"""

    class Meta:
        model = AIChatMessage
        fields = (
            "id", "role", "content", "attachments", "input_tokens", "output_tokens",
            "provider_request_id", "created_at",
        )
        read_only_fields = fields


class AIChatSessionSerializer(serializers.ModelSerializer):
    """创建和输出用户自己的 AI 学习会话配置。"""

    credential = serializers.PrimaryKeyRelatedField(
        queryset=AIProviderCredential.objects.all(), allow_null=True, required=False
    )
    progress = serializers.PrimaryKeyRelatedField(queryset=DayProgress.objects.all(), allow_null=True, required=False)
    message_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AIChatSession
        fields = (
            "id", "credential", "progress", "title", "provider", "adapter", "api_url", "model",
            "context_rounds", "max_output_tokens", "teaching_mode", "include_current_lesson",
            "message_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "message_count", "created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        """把可关联进度的查询集提前限制为当前用户，避免跨用户对象枚举。"""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        progress_queryset = DayProgress.objects.none()
        credential_queryset = AIProviderCredential.objects.none()
        if request and request.user.is_authenticated:
            progress_queryset = DayProgress.objects.filter(enrollment__user=request.user)
            credential_queryset = AIProviderCredential.objects.filter(user=request.user)
        self.fields["progress"].queryset = progress_queryset
        self.fields["credential"].queryset = credential_queryset

    def validate_context_rounds(self, value):
        """把上下文设置限制在 UI 明确展示的三个档位。"""
        if value not in CONTEXT_ROUNDS:
            raise serializers.ValidationError("上下文轮数只能选择 4、8 或 12。")
        return value

    def validate(self, attrs):
        """验证供应商与模型组合，并禁止修改已有会话的调用配置。"""
        if self.instance:
            changed = set(attrs) - {"title"}
            if changed:
                raise serializers.ValidationError("已有会话只能修改标题；切换模型请新建会话。")
            return attrs
        config = provider_config(
            attrs.get("provider"),
            attrs.get("model"),
            attrs.get("adapter", ""),
            attrs.get("api_url", ""),
        )
        if attrs.get("api_url"):
            attrs["api_url"] = config["api_url"]
        credential = attrs.get("credential")
        if credential:
            # 会话只绑定请求中明确选择且调用地址完全一致的配置，避免误用其他服务的密钥。
            endpoint_matches = (
                credential.provider == attrs.get("provider")
                and (credential.adapter or "") == (attrs.get("adapter") or "")
                and (credential.api_url or "") == (attrs.get("api_url") or "")
            )
            model_matches = not credential.model or credential.model == attrs.get("model")
            if not endpoint_matches or not model_matches:
                raise serializers.ValidationError({"credential": "所选配置与当前模型接口不匹配。"})
        return attrs


class AIChatSessionDetailSerializer(AIChatSessionSerializer):
    """在会话详情中附带按时间排序的完整本地文本历史。"""

    messages = AIChatMessageSerializer(many=True, read_only=True)

    class Meta(AIChatSessionSerializer.Meta):
        fields = AIChatSessionSerializer.Meta.fields + ("messages",)


class AIMessageInputSerializer(serializers.Serializer):
    """校验一次文本或多模态消息；附件文件本体由视图从 multipart 读取。"""

    content = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    api_key = serializers.CharField(required=False, allow_blank=True, max_length=512, trim_whitespace=True, write_only=True)
    focus_title = serializers.CharField(required=False, allow_blank=True, max_length=160, trim_whitespace=True)
    focus_content = serializers.CharField(required=False, allow_blank=True, max_length=4000, trim_whitespace=True)

    def validate_content(self, value):
        """执行运行时配置的单条问题字符上限。"""
        from django.conf import settings

        if len(value) > settings.AI_MESSAGE_MAX_CHARS:
            raise serializers.ValidationError(f"单条问题不能超过 {settings.AI_MESSAGE_MAX_CHARS} 个字符。")
        return value

    def focus(self):
        """返回可持久化的当前知识点或缺口快照；空输入返回空字典。"""
        title = self.validated_data.get("focus_title", "")
        content = self.validated_data.get("focus_content", "")
        return {"title": title, "content": content} if title or content else {}
