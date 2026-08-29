"""学习路线、逐日进度、复习和学习成果的输入输出契约。"""

from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import (
    AIProviderCredential,
    Contribution,
    DayProgress,
    Enrollment,
    Evidence,
    Gap,
    LearningPlan,
    PlanDay,
    PlanFeedback,
    ReviewAttempt,
)
from ..system.media import normalize_image, protected_media_url
from .experience import record_review, review_due_at
from .lesson_content import build_lesson_content, split_knowledge_points


class PlanDaySummarySerializer(serializers.ModelSerializer):
    """输出学习路线中的逐日摘要。"""

    class Meta:
        model = PlanDay
        fields = ("id", "day_number", "phase", "week_number", "week_title", "title", "estimated_minutes")


class PlanDaySerializer(serializers.ModelSerializer):
    """输出单个学习日的完整课程内容。"""

    knowledge_points = serializers.SerializerMethodField()
    knowledge_details = serializers.SerializerMethodField()
    plan_slug = serializers.CharField(source="plan.slug", read_only=True)

    class Meta:
        model = PlanDay
        fields = (
            "id",
            "plan_slug",
            "day_number",
            "phase",
            "week_number",
            "week_title",
            "title",
            "core_knowledge",
            "knowledge_points",
            "knowledge_details",
            "hands_on_task",
            "acceptance_criteria",
            "estimated_minutes",
            "content",
            "reference_answer",
            "commands",
            "community_supplements",
        )

    def get_knowledge_points(self, obj):
        return split_knowledge_points(obj.core_knowledge)

    def get_knowledge_details(self, obj):
        return obj.knowledge_details()


class LearningPlanListSerializer(serializers.ModelSerializer):
    """输出学习路线列表及当前用户关联状态。"""

    enrolled = serializers.SerializerMethodField()
    my_enrollment = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()
    owned = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    feedback_summary = serializers.SerializerMethodField()
    my_feedback = serializers.SerializerMethodField()
    forked_from = serializers.SerializerMethodField()
    fork_count = serializers.IntegerField(source="forks.count", read_only=True)

    class Meta:
        model = LearningPlan
        fields = (
            "id",
            "slug",
            "title",
            "subtitle",
            "summary",
            "audience",
            "total_days",
            "estimated_weeks",
            "accent_start",
            "accent_end",
            "enrolled",
            "my_enrollment",
            "creator_name",
            "owned",
            "editable",
            "is_published",
            "review_status",
            "review_note",
            "feedback_summary",
            "my_feedback",
            "forked_from",
            "fork_note",
            "fork_count",
        )

    def joined_enrollment(self, obj):
        """当前用户仍然属于这条路线的报名记录；已退出的返回 None。"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        cache = self.context.setdefault("_joined_enrollments", {})
        if obj.id not in cache:
            cache[obj.id] = obj.enrollments.filter(
                user=request.user, status__in=Enrollment.JOINED_STATUSES
            ).first()
        return cache[obj.id]

    def get_enrolled(self, obj):
        return bool(self.joined_enrollment(obj))

    def get_my_enrollment(self, obj):
        enrollment = self.joined_enrollment(obj)
        if not enrollment:
            return None
        return {"id": enrollment.id, "status": enrollment.status, "current_day": enrollment.current_day}

    def get_creator_name(self, obj):
        return obj.creator.first_name or obj.creator.username if obj.creator else "知序"

    def get_owned(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.creator_id == request.user.id)

    def get_editable(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.creator_id == request.user.id and obj.is_editable)

    def get_feedback_summary(self, obj):
        feedback = obj.feedback.all()
        count = len(feedback)
        if not count:
            return {"count": 0, "clarity": None, "practicality": None, "difficulty": {}}
        difficulties = {key: 0 for key, _ in PlanFeedback.Difficulty.choices}
        for item in feedback:
            difficulties[item.difficulty] += 1
        return {
            "count": count,
            "clarity": round(sum(item.clarity for item in feedback) / count, 1),
            "practicality": round(sum(item.practicality for item in feedback) / count, 1),
            "difficulty": difficulties,
        }

    def get_my_feedback(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        item = next((feedback for feedback in obj.feedback.all() if feedback.user_id == request.user.id), None)
        return PlanFeedbackSerializer(item).data if item else None

    def get_forked_from(self, obj):
        if not obj.forked_from:
            return None
        return {"slug": obj.forked_from.slug, "title": obj.forked_from.title}


class LearningPlanDetailSerializer(LearningPlanListSerializer):
    """在路线列表信息上补充逐日摘要。"""

    days = PlanDaySummarySerializer(many=True, read_only=True)

    class Meta(LearningPlanListSerializer.Meta):
        fields = LearningPlanListSerializer.Meta.fields + ("days",)


class CustomPlanDaySerializer(serializers.ModelSerializer):
    """校验用户自建路线的单日内容。"""

    class Meta:
        model = PlanDay
        fields = (
            "day_number",
            "phase",
            "week_number",
            "week_title",
            "title",
            "core_knowledge",
            "hands_on_task",
            "acceptance_criteria",
            "estimated_minutes",
        )

    def validate_acceptance_criteria(self, value):
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            raise serializers.ValidationError("每一天至少需要一个明确的验收项。")
        return [item.strip() for item in value]


class CustomLearningPlanSerializer(serializers.ModelSerializer):
    """创建和更新用户自建学习路线及其学习日。"""

    days = CustomPlanDaySerializer(many=True)
    creator_name = serializers.SerializerMethodField(read_only=True)
    owned = serializers.SerializerMethodField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    editable = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LearningPlan
        fields = (
            "id",
            "slug",
            "title",
            "subtitle",
            "summary",
            "audience",
            "total_days",
            "estimated_weeks",
            "creator_name",
            "owned",
            "enrolled",
            "editable",
            "is_published",
            "review_status",
            "review_note",
            "days",
        )
        read_only_fields = (
            "id",
            "slug",
            "total_days",
            "estimated_weeks",
            "creator_name",
            "owned",
            "enrolled",
            "editable",
            "is_published",
            "review_status",
            "review_note",
        )

    def get_creator_name(self, obj):
        return obj.creator.first_name or obj.creator.username

    def get_owned(self, obj):
        return True

    def get_enrolled(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and obj.enrollments.filter(user=request.user, status__in=Enrollment.JOINED_STATUSES).exists()
        )

    def get_editable(self, obj):
        return obj.is_editable

    def validate_days(self, value):
        if not value:
            raise serializers.ValidationError("学习路线至少需要一天。")
        if len(value) > 365:
            raise serializers.ValidationError("一条学习路线最多包含365天。")
        numbers = [day["day_number"] for day in value]
        if numbers != list(range(1, len(value) + 1)):
            raise serializers.ValidationError("学习日必须从1开始连续排列。")
        return value

    @transaction.atomic
    def create(self, validated_data):
        days = validated_data.pop("days")
        user = self.context["request"].user
        plan = LearningPlan.objects.create(
            creator=user,
            slug=f"custom-{user.id}-{timezone.now():%Y%m%d%H%M%S%f}",
            total_days=len(days),
            estimated_weeks=(len(days) + 6) // 7,
            is_published=False,
            review_status=LearningPlan.ReviewStatus.DRAFT,
            **validated_data,
        )
        PlanDay.objects.bulk_create(self.plan_days(plan, days))
        return plan

    @transaction.atomic
    def update(self, instance, validated_data):
        days = validated_data.pop("days", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if days is not None:
            instance.total_days = len(days)
            instance.estimated_weeks = (len(days) + 6) // 7
        instance.review_status = LearningPlan.ReviewStatus.DRAFT
        instance.review_note = ""
        instance.save()
        if days is not None:
            instance.days.all().delete()
            PlanDay.objects.bulk_create(self.plan_days(instance, days))
        return instance

    @staticmethod
    def plan_days(plan, days):
        return [
            PlanDay(
                plan=plan,
                content=build_lesson_content(
                    day["day_number"], day["core_knowledge"], day["hands_on_task"],
                    day["acceptance_criteria"], plan.slug,
                ),
                **day,
            )
            for day in days
        ]


class MarkdownRoadmapPreviewSerializer(serializers.Serializer):
    """校验一次多 Markdown 路线生成请求及当前用户选择的长期模型配置。"""

    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        max_length=settings.AI_ATTACHMENT_MAX_FILES,
    )
    credential = serializers.PrimaryKeyRelatedField(queryset=AIProviderCredential.objects.none())
    target_days = serializers.IntegerField(min_value=1, max_value=30, default=14)
    daily_minutes = serializers.IntegerField(min_value=15, max_value=240, default=60)
    learner_background = serializers.CharField(required=False, allow_blank=True, max_length=500, trim_whitespace=True)
    goal = serializers.CharField(required=False, allow_blank=True, max_length=500, trim_whitespace=True)
    allow_supplement = serializers.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        """把可选配置限制为当前登录用户，避免跨账号对象枚举。"""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["credential"].queryset = AIProviderCredential.objects.filter(user=request.user)

    def validate_files(self, value):
        """只允许 Markdown 文件列表进入现有附件安全处理层。"""
        invalid = next(
            (item.name for item in value if Path(item.name or "").suffix.lower() != ".md"),
            None,
        )
        if invalid:
            raise serializers.ValidationError(f"文件 {invalid} 不是 .md Markdown 文件。")
        return value

    def validate_credential(self, value):
        """路线生成必须绑定一个明确模型，避免旧配置调用空模型名。"""
        if not value.model:
            raise serializers.ValidationError("所选模型配置缺少模型名称，请先编辑并重新验证。")
        return value


class EvidenceSerializer(serializers.ModelSerializer):
    """校验并输出学习证据及受保护附件。"""

    attachment_url = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()
    attachment_is_image = serializers.SerializerMethodField()

    class Meta:
        model = Evidence
        fields = (
            "id", "progress", "kind", "title", "content", "url", "attachment",
            "attachment_url", "attachment_name", "attachment_is_image", "created_at",
        )
        read_only_fields = ("id", "attachment_url", "attachment_name", "attachment_is_image", "created_at")
        extra_kwargs = {"progress": {"write_only": True}, "attachment": {"write_only": True}}

    def validate_attachment(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("附件不能超过10MB。")
        allowed = {"image/png", "image/jpeg", "image/webp", "text/plain", "application/pdf", "application/json"}
        if getattr(value, "content_type", "") not in allowed:
            raise serializers.ValidationError("仅支持图片、文本、JSON或PDF证据。")
        if value.content_type.startswith("image/"):
            return normalize_image(value)[0]
        return value

    def validate(self, attrs):
        if not any((attrs.get("content"), attrs.get("url"), attrs.get("attachment"))):
            raise serializers.ValidationError("请填写内容、链接或上传附件。")
        return attrs

    def get_attachment_url(self, obj):
        """返回仅指向当前证据附件的短时签名地址。"""
        if not obj.attachment:
            return ""
        return protected_media_url(self.context.get("request"), "evidence", obj.id)

    def get_attachment_name(self, obj):
        """返回证据附件的存储文件名用于链接提示。"""
        return Path(obj.attachment.name).name if obj.attachment else ""

    def get_attachment_is_image(self, obj):
        """标记附件是否可以在学习页内直接预览。"""
        return bool(obj.attachment and Path(obj.attachment.name).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})


class GapSerializer(serializers.ModelSerializer):
    """校验并输出学习过程中的知识缺口。"""

    verified_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Gap
        fields = (
            "id", "progress", "title", "detail", "status", "resolution",
            "verification_group", "verified_by_name", "verification_note", "verification_requested_at",
            "verified_at", "created_at", "resolved_at",
        )
        read_only_fields = (
            "id", "verification_group", "verified_by_name", "verification_note", "verification_requested_at",
            "verified_at", "created_at", "resolved_at",
        )
        extra_kwargs = {"progress": {"write_only": True}}

    def update(self, instance, validated_data):
        validated_data.pop("progress", None)
        return super().update(instance, validated_data)

    def get_verified_by_name(self, obj):
        if not obj.verified_by:
            return ""
        return obj.verified_by.first_name or obj.verified_by.username


class PlanFeedbackSerializer(serializers.ModelSerializer):
    """校验并输出学习者对路线的反馈。"""

    class Meta:
        model = PlanFeedback
        fields = ("id", "plan", "clarity", "practicality", "difficulty", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "plan", "created_at", "updated_at")

    def validate_comment(self, value):
        return value.strip()


class DayProgressSerializer(serializers.ModelSerializer):
    """校验并输出单日学习进度。"""

    day = PlanDaySerializer(source="plan_day", read_only=True)
    evidence = EvidenceSerializer(many=True, read_only=True)
    gaps = GapSerializer(many=True, read_only=True)

    class Meta:
        model = DayProgress
        fields = (
            "id",
            "enrollment",
            "day",
            "status",
            "acceptance_checks",
            "knowledge_checks",
            "reflection",
            "recall_score",
            "started_at",
            "completed_at",
            "evidence",
            "gaps",
        )
        read_only_fields = ("id", "enrollment", "day", "status", "started_at", "completed_at", "evidence", "gaps")

    def validate_acceptance_checks(self, value):
        if not isinstance(value, list) or not all(isinstance(item, bool) for item in value):
            raise serializers.ValidationError("验收状态必须是布尔值列表。")
        expected = len(self.instance.plan_day.acceptance_criteria) if self.instance else len(value)
        if len(value) != expected:
            raise serializers.ValidationError("验收项数量与当天任务不一致。")
        return value

    def validate_knowledge_checks(self, value):
        if not isinstance(value, list) or not all(isinstance(item, bool) for item in value):
            raise serializers.ValidationError("知识点状态必须是布尔值列表。")
        expected = self.instance.plan_day.knowledge_count() if self.instance else len(value)
        if len(value) != expected:
            raise serializers.ValidationError("知识点状态数量与当天内容不一致。")
        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    """输出报名记录及其路线概况。"""

    plan = LearningPlanListSerializer(read_only=True)
    completed_days = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "plan",
            "status",
            "current_day",
            "completed_days",
            "progress_percent",
            "started_at",
            "last_studied_at",
        )
        read_only_fields = ("id", "plan", "current_day", "completed_days", "progress_percent", "started_at", "last_studied_at")

    def get_completed_days(self, obj):
        return getattr(obj, "completed_count", None) or obj.progress.filter(status=DayProgress.Status.COMPLETED).count()

    def get_progress_percent(self, obj):
        return round(self.get_completed_days(obj) / obj.plan.total_days * 100) if obj.plan.total_days else 0

    def validate_status(self, value):
        if value not in (Enrollment.Status.ACTIVE, Enrollment.Status.PAUSED):
            raise serializers.ValidationError("只能暂停或恢复学习计划。")
        return value


class JourneyDaySerializer(serializers.ModelSerializer):
    """输出学习路径页面需要的逐日状态。"""

    status = serializers.CharField()
    progress_id = serializers.IntegerField(allow_null=True)
    previewable = serializers.BooleanField(default=False)
    is_boss = serializers.BooleanField(default=False)
    boss_challenge = serializers.SerializerMethodField()

    class Meta:
        model = PlanDay
        fields = (
            "day_number",
            "week_number",
            "week_title",
            "phase",
            "title",
            "estimated_minutes",
            "status",
            "progress_id",
            "previewable",
            "is_boss",
            "boss_challenge",
        )

    def get_boss_challenge(self, obj):
        """为阶段末学习日提供可直接执行的 Boss 挑战说明。"""
        if not obj.is_boss:
            return None
        return {
            "title": f"{obj.phase} · 阶段 Boss",
            "objective": obj.hands_on_task,
            "requirements": obj.acceptance_criteria,
        }


class ReviewAttemptSerializer(serializers.ModelSerializer):
    """校验并创建属于当前学习者的间隔复习记录。"""

    progress = serializers.PrimaryKeyRelatedField(queryset=DayProgress.objects.none())
    rating_label = serializers.CharField(source="get_rating_display", read_only=True)

    class Meta:
        model = ReviewAttempt
        fields = (
            "id", "progress", "rating", "rating_label", "note",
            "interval_days", "reviewed_at", "next_review_at",
        )
        read_only_fields = (
            "id", "rating_label", "interval_days", "reviewed_at", "next_review_at",
        )
        extra_kwargs = {"note": {"max_length": 4000}}

    def __init__(self, *args, **kwargs):
        """把可选学习日限制为当前登录用户自己的已完成记录。"""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["progress"].queryset = DayProgress.objects.select_for_update().filter(
                enrollment__user=request.user,
                enrollment__status__in=Enrollment.JOINED_STATUSES,
                status=DayProgress.Status.COMPLETED,
            )

    def create(self, validated_data):
        """按掌握结果计算新间隔并写入复习记录。"""
        return record_review(**validated_data)

    def validate_progress(self, value):
        """只接受已经进入到期队列的学习日，防止重复刷取复习经验。"""
        if review_due_at(value) > timezone.now():
            raise serializers.ValidationError("该学习日尚未到复习时间。")
        return value


class ContributionSerializer(serializers.ModelSerializer):
    """输出用户的学习社区贡献记录。"""

    class Meta:
        model = Contribution
        fields = ("id", "kind", "title", "detail", "created_at")
