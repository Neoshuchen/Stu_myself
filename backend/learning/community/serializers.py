"""社区帖子、评论、图片和举报的输入输出契约。"""

from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models, transaction
from rest_framework import serializers

from ..models import CommunityComment, CommunityPost, CommunityPostImage, CommunityReport, Enrollment
from ..system.media import normalize_image, protected_media_url

User = get_user_model()


class CommunityAuthorSerializer(serializers.ModelSerializer):
    """输出社区作者的公开身份信息。"""

    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "name")

    def get_name(self, obj):
        return obj.first_name or obj.username


class CommunityCommentSerializer(serializers.ModelSerializer):
    """校验并输出社区评论和回复关系。"""

    author = CommunityAuthorSerializer(read_only=True)
    owned = serializers.SerializerMethodField()

    class Meta:
        model = CommunityComment
        fields = ("id", "post", "author", "parent", "content", "owned", "created_at", "updated_at")
        read_only_fields = ("id", "post", "author", "owned", "created_at", "updated_at")

    def get_owned(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("评论内容不能为空。")
        return value

    def validate_parent(self, value):
        post = self.context.get("post") or getattr(self.instance, "post", None)
        if value and post and value.post_id != post.id:
            raise serializers.ValidationError("回复必须属于同一个帖子。")
        return value


class CommunityPostImageSerializer(serializers.ModelSerializer):
    """输出社区图片的签名地址和固有尺寸。"""

    url = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPostImage
        fields = ("id", "url", "alt_text", "width", "height", "position")

    def get_url(self, obj):
        """返回帖子图片的短时签名地址。"""
        return protected_media_url(self.context.get("request"), "community-image", obj.id)


class CommunityPostSerializer(serializers.ModelSerializer):
    """校验并输出社区帖子、图片和互动数据。"""

    author = CommunityAuthorSerializer(read_only=True)
    plan_slug = serializers.CharField(source="plan.slug", read_only=True)
    plan_title = serializers.CharField(source="plan.title", read_only=True)
    day_number = serializers.IntegerField(source="plan_day.day_number", read_only=True)
    comments = CommunityCommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    like_count = serializers.IntegerField(read_only=True, default=0)
    liked = serializers.SerializerMethodField()
    owned = serializers.SerializerMethodField()
    images = CommunityPostImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, allow_empty=False
    )
    remove_image_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), write_only=True, required=False
    )

    class Meta:
        model = CommunityPost
        fields = (
            "id", "author", "plan", "plan_slug", "plan_title", "plan_day", "day_number", "post_type",
            "title", "content", "is_solved", "like_count", "liked", "comment_count", "owned", "comments",
            "images", "image_files", "remove_image_ids",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "author", "plan_slug", "plan_title", "day_number", "is_solved", "like_count", "liked",
            "comment_count", "owned", "comments", "images", "created_at", "updated_at",
        )
        extra_kwargs = {"plan": {"required": False, "allow_null": True}, "plan_day": {"required": False, "allow_null": True}}

    def get_liked(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.likes.filter(user=request.user).exists())

    def get_owned(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("标题不能为空。")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("正文不能为空。")
        return value

    def validate_image_files(self, value):
        """一次性校验并清洗本次新增的全部帖子图片。"""
        normalized = []
        for upload in value:
            original_name = Path(upload.name).stem[:160]
            image, width, height = normalize_image(upload)
            normalized.append((image, width, height, original_name))
        return normalized

    def validate(self, attrs):
        plan = attrs.get("plan", getattr(self.instance, "plan", None))
        day = attrs.get("plan_day", getattr(self.instance, "plan_day", None))
        if day and day.plan_id != getattr(plan, "id", None):
            raise serializers.ValidationError({"plan_day": "学习日必须属于所选学习路线。"})
        request = self.context["request"]
        if plan and not request.user.is_staff and not plan.enrollments.filter(
            user=request.user, status__in=Enrollment.JOINED_STATUSES
        ).exists():
            raise serializers.ValidationError({"plan": "加入该学习路线后才能在小组发言。"})
        remove_ids = set(attrs.get("remove_image_ids", []))
        if self.instance:
            owned_ids = set(self.instance.images.values_list("id", flat=True))
            if not remove_ids.issubset(owned_ids):
                raise serializers.ValidationError({"remove_image_ids": "只能删除当前帖子的图片。"})
            existing_count = len(owned_ids - remove_ids)
        else:
            if remove_ids:
                raise serializers.ValidationError({"remove_image_ids": "新帖子没有可删除的图片。"})
            existing_count = 0
        if existing_count + len(attrs.get("image_files", [])) > 4:
            raise serializers.ValidationError({"image_files": "每篇帖子最多上传4张图片。"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """在同一数据库事务中创建帖子及其图片记录。"""
        images = validated_data.pop("image_files", [])
        validated_data.pop("remove_image_ids", None)
        post = super().create(validated_data)
        self.save_images(post, images, 0)
        return post

    @transaction.atomic
    def update(self, instance, validated_data):
        """保持原文本更新语义，同时应用图片新增和删除。"""
        images = validated_data.pop("image_files", [])
        remove_ids = validated_data.pop("remove_image_ids", [])
        post = super().update(instance, validated_data)
        if remove_ids:
            post.images.filter(id__in=remove_ids).delete()
        self.save_images(post, images, post.images.count())
        return post

    @staticmethod
    def save_images(post, images, start_position):
        """按上传顺序保存已清洗的帖子图片。"""
        for offset, (image, width, height, alt_text) in enumerate(images):
            CommunityPostImage.objects.create(
                post=post,
                image=image,
                width=width,
                height=height,
                alt_text=alt_text,
                position=start_position + offset,
            )


class CommunityPostListSerializer(CommunityPostSerializer):
    """输出不包含完整评论列表的帖子摘要。"""

    class Meta(CommunityPostSerializer.Meta):
        fields = tuple(field for field in CommunityPostSerializer.Meta.fields if field != "comments")


class CommunityReportSerializer(serializers.ModelSerializer):
    """校验并输出帖子或评论举报。"""

    target_title = serializers.SerializerMethodField()
    target_excerpt = serializers.SerializerMethodField()
    target_author = serializers.SerializerMethodField()

    class Meta:
        model = CommunityReport
        fields = ("id", "post", "comment", "target_title", "target_excerpt", "target_author", "reason", "status", "created_at")
        read_only_fields = ("id", "target_title", "target_excerpt", "target_author", "created_at")

    def validate_reason(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请填写举报原因。")
        return value

    def validate(self, attrs):
        if self.instance:
            changed_targets = set(self.initial_data) - {"status"}
            if changed_targets:
                raise serializers.ValidationError("审核举报时只能更新处理状态。")
            if self.instance.status != CommunityReport.Status.PENDING:
                raise serializers.ValidationError("该举报已经处理。")
            if attrs.get("status") != CommunityReport.Status.RESOLVED:
                raise serializers.ValidationError({"status": "待处理举报只能标记为已处理。"})
            return attrs
        post = attrs.get("post", getattr(self.instance, "post", None))
        comment = attrs.get("comment", getattr(self.instance, "comment", None))
        if bool(post) == bool(comment):
            raise serializers.ValidationError("请选择一个要举报的帖子或评论。")
        target_post = post or comment.post
        if not visible_community_posts_for(self.context["request"].user).filter(pk=target_post.pk).exists():
            raise serializers.ValidationError("无法举报不可见的内容。")
        return attrs

    def get_target_title(self, obj):
        return obj.post.title if obj.post else obj.comment.post.title

    def get_target_excerpt(self, obj):
        content = obj.post.content if obj.post else obj.comment.content
        return content[:180]

    def get_target_author(self, obj):
        author = obj.post.author if obj.post else obj.comment.author
        return author.first_name or author.username


def visible_community_posts_for(user):
    queryset = CommunityPost.objects.all()
    if getattr(user, "is_staff", False):
        return queryset
    if getattr(user, "is_authenticated", False):
        return queryset.filter(
            models.Q(plan__isnull=True)
            | models.Q(plan__enrollments__user=user, plan__enrollments__status__in=Enrollment.JOINED_STATUSES)
        ).distinct()
    return queryset.filter(plan__isnull=True)

