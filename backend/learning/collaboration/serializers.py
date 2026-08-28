"""学习小队、互助、互评、答疑和通知的输入输出契约。"""

from django.utils import timezone
from rest_framework import serializers

from ..models import (
    BuddyProfile,
    CourseSuggestion,
    Enrollment,
    Evidence,
    HelpQuestion,
    HelpSession,
    Notification,
    PeerReview,
    StudyGroup,
    TeamChallenge,
    TeamChallengeEntry,
    WeeklyContract,
)
from ..study.serializers import EvidenceSerializer


class StudyGroupSerializer(serializers.ModelSerializer):
    """输出当前用户可见的小队摘要，并只向创建者展示邀请码。"""

    owner_name = serializers.CharField(source="owner.first_name", read_only=True)
    member_count = serializers.IntegerField(read_only=True, default=0)
    owned = serializers.SerializerMethodField()
    invite_code = serializers.SerializerMethodField()

    class Meta:
        model = StudyGroup
        fields = ("id", "name", "owner_name", "member_count", "owned", "invite_code", "created_at")
        read_only_fields = ("id", "owner_name", "member_count", "owned", "invite_code", "created_at")

    def get_owned(self, obj):
        request = self.context.get("request")
        return bool(request and obj.owner_id == request.user.id)

    def get_invite_code(self, obj):
        request = self.context.get("request")
        return obj.invite_code if request and obj.owner_id == request.user.id else ""

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("小队名称不能为空。")
        return value


class WeeklyContractSerializer(serializers.ModelSerializer):
    """校验当前成员为自己制定的自然周学习目标。"""

    user_name = serializers.CharField(source="user.first_name", read_only=True)
    plan_title = serializers.CharField(source="enrollment.plan.title", read_only=True)

    class Meta:
        model = WeeklyContract
        fields = (
            "id", "group", "enrollment", "week_start", "target_days", "note",
            "user_name", "plan_title", "created_at", "updated_at",
        )
        read_only_fields = ("id", "user_name", "plan_title", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        group = attrs.get("group", getattr(self.instance, "group", None))
        enrollment = attrs.get("enrollment", getattr(self.instance, "enrollment", None))
        week_start = attrs.get("week_start", getattr(self.instance, "week_start", None))
        if not group or not group.members.filter(pk=request.user.id).exists():
            raise serializers.ValidationError({"group": "只能为自己所在的小队制定目标。"})
        if not enrollment or enrollment.user_id != request.user.id or enrollment.status not in Enrollment.JOINED_STATUSES:
            raise serializers.ValidationError({"enrollment": "请选择自己仍在学习的路线。"})
        if week_start and week_start.weekday() != 0:
            raise serializers.ValidationError({"week_start": "每周目标必须从星期一开始。"})
        # 已存在目标只允许修改数量和说明，避免历史统计被切换路线或周次后失真。
        if self.instance and (
            group.id != self.instance.group_id
            or enrollment.id != self.instance.enrollment_id
            or week_start != self.instance.week_start
        ):
            raise serializers.ValidationError("已有周目标不能切换小队、路线或周次，请重新创建。")
        return attrs

    def validate_note(self, value):
        return value.strip()


class TeamChallengeEntrySerializer(serializers.ModelSerializer):
    """校验挑战分工只能使用成员自己的学习证据且每个角色唯一。"""

    user_id = serializers.IntegerField(read_only=True)
    user_name = serializers.SerializerMethodField()
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    evidence_id = serializers.IntegerField(read_only=True)
    evidence_title = serializers.CharField(source="evidence.title", read_only=True, default="证据已删除")
    evidence = serializers.PrimaryKeyRelatedField(queryset=Evidence.objects.all(), write_only=True)

    class Meta:
        model = TeamChallengeEntry
        fields = (
            "id", "user_id", "user_name", "role", "role_label", "evidence", "evidence_id",
            "evidence_title", "summary", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "user_id", "user_name", "role_label", "evidence_id", "evidence_title",
            "created_at", "updated_at",
        )

    def get_user_name(self, obj):
        """返回适合小队页面展示的成员名称。"""
        return obj.user.first_name or obj.user.username

    def validate_summary(self, value):
        """拒绝没有说明复现、测试或复核结论的空提交。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请说明本次分工的过程和结论。")
        return value

    def validate(self, attrs):
        """统一校验挑战状态、证据归属和角色占用情况。"""
        request = self.context["request"]
        challenge = self.context["challenge"]
        if challenge.status != TeamChallenge.Status.OPEN:
            raise serializers.ValidationError("该挑战已经完成。")
        if challenge.deadline < timezone.now():
            raise serializers.ValidationError("该挑战已经超过截止时间。")
        evidence = attrs.get("evidence", getattr(self.instance, "evidence", None))
        if not evidence or evidence.progress.enrollment.user_id != request.user.id:
            raise serializers.ValidationError({"evidence": "只能提交自己的学习证据。"})
        role = attrs.get("role", getattr(self.instance, "role", None))
        occupied = challenge.entries.filter(role=role)
        if self.instance:
            occupied = occupied.exclude(pk=self.instance.pk)
        if occupied.exists():
            raise serializers.ValidationError({"role": "这个分工已经由其他成员承担。"})
        return attrs


class TeamChallengeSerializer(serializers.ModelSerializer):
    """输出小队挑战、成员分工和当前完成条件。"""

    group_name = serializers.CharField(source="group.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    entries = TeamChallengeEntrySerializer(many=True, read_only=True)
    can_complete = serializers.SerializerMethodField()
    expired = serializers.SerializerMethodField()

    class Meta:
        model = TeamChallenge
        fields = (
            "id", "group", "group_name", "created_by_name", "title", "description", "deadline",
            "status", "status_label", "entries", "can_complete", "expired", "created_at", "completed_at",
        )
        read_only_fields = (
            "id", "group_name", "created_by_name", "status", "status_label", "entries",
            "can_complete", "expired", "created_at", "completed_at",
        )

    def get_created_by_name(self, obj):
        """返回挑战发起人的展示名称。"""
        return obj.created_by.first_name or obj.created_by.username

    def get_can_complete(self, obj):
        """至少两名成员承担不同角色后才允许合并并完成挑战。"""
        entries = list(obj.entries.all())
        return obj.status == TeamChallenge.Status.OPEN and len(entries) >= 2

    def get_expired(self, obj):
        """返回挑战是否已经错过截止时间。"""
        return obj.status == TeamChallenge.Status.OPEN and obj.deadline < timezone.now()

    def validate_title(self, value):
        """清理并校验挑战标题。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("挑战标题不能为空。")
        return value

    def validate_description(self, value):
        """要求挑战说明包含具体协作任务。"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请填写需要共同完成的任务。")
        return value

    def validate_deadline(self, value):
        """拒绝创建截止时间已经过去的挑战。"""
        if value <= timezone.now():
            raise serializers.ValidationError("截止时间必须晚于当前时间。")
        return value

    def validate_group(self, value):
        """只允许在当前用户所在的小队中发起挑战。"""
        request = self.context["request"]
        if not value.members.filter(pk=request.user.id).exists():
            raise serializers.ValidationError("只能在自己所在的小队发起挑战。")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """输出当前用户自己的站内通知。"""

    read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("id", "kind", "title", "body", "url", "read", "created_at")
        read_only_fields = fields

    def get_read(self, obj):
        return obj.read_at is not None


class CourseSuggestionSerializer(serializers.ModelSerializer):
    """校验社区内容向课程补充的推荐请求。"""

    author_name = serializers.CharField(source="author.first_name", read_only=True)
    plan_title = serializers.CharField(source="plan_day.plan.title", read_only=True)
    day_number = serializers.IntegerField(source="plan_day.day_number", read_only=True)

    class Meta:
        model = CourseSuggestion
        fields = ("id", "author_name", "post", "plan_day", "plan_title", "day_number", "title", "content", "status", "review_note", "created_at")
        read_only_fields = ("id", "author_name", "status", "review_note", "plan_title", "day_number", "created_at")
        extra_kwargs = {"content": {"required": False}}

    def validate(self, attrs):
        post, day = attrs["post"], attrs["plan_day"]
        if post.author_id != self.context["request"].user.id:
            raise serializers.ValidationError("只能提交自己的社区帖子。")
        if post.plan_day_id != day.id:
            raise serializers.ValidationError("帖子必须关联同一个学习日。")
        attrs["content"] = attrs.get("content", "").strip() or post.content
        return attrs


class PeerReviewSerializer(serializers.ModelSerializer):
    """校验并输出同伴互评任务。"""

    requester_name = serializers.CharField(source="requester.first_name", read_only=True)
    reviewer_name = serializers.CharField(source="reviewer.first_name", read_only=True)
    plan_title = serializers.CharField(source="progress.enrollment.plan.title", read_only=True)
    day_number = serializers.IntegerField(source="progress.plan_day.day_number", read_only=True)
    day_title = serializers.CharField(source="progress.plan_day.title", read_only=True)
    evidence = EvidenceSerializer(source="progress.evidence", many=True, read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = PeerReview
        fields = ("id", "progress", "requester_name", "reviewer_name", "plan_title", "day_number", "day_title", "evidence", "role", "status", "accuracy", "runnable", "clarity", "feedback", "created_at")
        read_only_fields = ("id", "requester_name", "reviewer_name", "plan_title", "day_number", "day_title", "evidence", "role", "status", "created_at")

    def get_role(self, obj):
        request = self.context.get("request")
        if request and obj.requester_id == request.user.id:
            return "requester"
        if request and obj.reviewer_id == request.user.id:
            return "reviewer"
        return "candidate"


class HelpQuestionSerializer(serializers.ModelSerializer):
    """校验并输出公开答疑中的问题。"""

    author_name = serializers.CharField(source="author.first_name", read_only=True)
    answered_by_name = serializers.CharField(source="answered_by.first_name", read_only=True)

    class Meta:
        model = HelpQuestion
        fields = ("id", "author_name", "question", "answer", "answered_by_name", "created_at", "answered_at")
        read_only_fields = ("id", "author_name", "answer", "answered_by_name", "created_at", "answered_at")

    def validate_question(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("问题不能为空。")
        return value


class HelpSessionSerializer(serializers.ModelSerializer):
    """校验并输出公开答疑场次。"""

    plan_title = serializers.CharField(source="plan.title", read_only=True)
    questions = HelpQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = HelpSession
        fields = ("id", "plan", "plan_title", "title", "description", "deadline", "status", "questions", "created_at")
        read_only_fields = ("id", "plan_title", "status", "questions", "created_at")

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("征集截止时间必须晚于当前时间。")
        return value


class BuddyProfileSerializer(serializers.ModelSerializer):
    """校验并输出学习搭子匹配资料。"""

    name = serializers.CharField(source="user.first_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    plan_title = serializers.CharField(source="enrollment.plan.title", read_only=True)
    plan_slug = serializers.CharField(source="enrollment.plan.slug", read_only=True)
    current_day = serializers.IntegerField(source="enrollment.current_day", read_only=True)

    class Meta:
        model = BuddyProfile
        fields = ("id", "enrollment", "name", "username", "plan_title", "plan_slug", "current_day", "study_time", "goal", "active", "updated_at")
        read_only_fields = ("id", "name", "username", "plan_title", "plan_slug", "current_day", "updated_at")

    def validate_study_time(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请填写通常学习时间。")
        return value

    def validate_goal(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请填写希望如何互助。")
        return value

    def validate_enrollment(self, value):
        request = self.context.get("request")
        if not request or value.user_id != request.user.id:
            raise serializers.ValidationError("只能使用自己的学习路线报名记录。")
        return value

    def validate(self, attrs):
        attrs.pop("user", None)
        return attrs
