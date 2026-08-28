from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .study.lesson_content import split_knowledge_points

User = get_user_model()


def generate_invite_code():
    """返回适合人工输入且不可预测的小队邀请码。"""
    return uuid4().hex[:12].upper()


def current_week_start():
    """返回当前本地日期所在周的星期一。"""
    today = timezone.localdate()
    return today - timedelta(days=today.weekday())


class LearningPlan(models.Model):
    """描述一条可发布、报名和审核的学习路线。"""

    class ReviewStatus(models.TextChoices):
        DRAFT = "draft", "草稿"
        PENDING = "pending", "待审核"
        APPROVED = "approved", "审核通过"
        REJECTED = "rejected", "审核退回"

    creator = models.ForeignKey(
        User, related_name="created_learning_plans", on_delete=models.SET_NULL, null=True, blank=True
    )
    forked_from = models.ForeignKey(
        "self", related_name="forks", on_delete=models.SET_NULL, null=True, blank=True
    )
    fork_note = models.CharField(max_length=240, blank=True)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=200, blank=True)
    summary = models.TextField()
    audience = models.CharField(max_length=240, blank=True)
    total_days = models.PositiveSmallIntegerField(default=0)
    estimated_weeks = models.PositiveSmallIntegerField(default=0)
    accent_start = models.CharField(max_length=16, default="#3b7d6b")
    accent_end = models.CharField(max_length=16, default="#ef8354")
    is_published = models.BooleanField(default=True)
    review_status = models.CharField(max_length=12, choices=ReviewStatus.choices, default=ReviewStatus.APPROVED)
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def is_editable(self):
        started = self.enrollments.filter(progress__status__in=("in_progress", "completed")).exists()
        return self.review_status in (self.ReviewStatus.DRAFT, self.ReviewStatus.REJECTED) and not started


class PlanDay(models.Model):
    plan = models.ForeignKey(LearningPlan, related_name="days", on_delete=models.CASCADE)
    day_number = models.PositiveSmallIntegerField()
    phase = models.CharField(max_length=160)
    week_number = models.PositiveSmallIntegerField()
    week_title = models.CharField(max_length=160)
    title = models.CharField(max_length=200)
    core_knowledge = models.TextField()
    hands_on_task = models.TextField()
    acceptance_criteria = models.JSONField(default=list)
    estimated_minutes = models.PositiveSmallIntegerField(default=120)
    content = models.JSONField(default=list, blank=True)
    reference_answer = models.TextField(blank=True)
    commands = models.JSONField(default=list, blank=True)
    community_supplements = models.JSONField(default=list, blank=True)
    # 管理员在站点后台改过正文的时间。导入命令默认跳过这些天，避免把人工修改静默覆盖掉。
    content_edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["day_number"]
        constraints = [models.UniqueConstraint(fields=["plan", "day_number"], name="unique_plan_day")]

    def __str__(self):
        return f"{self.plan.title} · Day {self.day_number}"

    def knowledge_details(self):
        return self.content.get("knowledge_details", []) if isinstance(self.content, dict) else []

    def knowledge_count(self):
        return len(self.knowledge_details()) or len(split_knowledge_points(self.core_knowledge))


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "进行中"
        PAUSED = "paused", "已暂停"
        COMPLETED = "completed", "已完成"
        WITHDRAWN = "withdrawn", "已退出"

    # 退出是软退出：报名记录和学习证据全部保留，只从学习面和小组成员身份中移除。
    # 凡是判断“这个用户属于这条路线”的地方都用这个集合，不要各自写 exclude。
    JOINED_STATUSES = (Status.ACTIVE, Status.PAUSED, Status.COMPLETED)

    user = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    plan = models.ForeignKey(LearningPlan, related_name="enrollments", on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    current_day = models.PositiveSmallIntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    last_studied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [models.UniqueConstraint(fields=["user", "plan"], name="unique_user_plan")]

    def __str__(self):
        return f"{self.user.username} · {self.plan.title}"


class PlanFeedback(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "偏简单"
        RIGHT = "right", "刚刚好"
        HARD = "hard", "偏困难"

    user = models.ForeignKey(User, related_name="plan_feedback", on_delete=models.CASCADE)
    plan = models.ForeignKey(LearningPlan, related_name="feedback", on_delete=models.CASCADE)
    clarity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    practicality = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    difficulty = models.CharField(max_length=8, choices=Difficulty.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [models.UniqueConstraint(fields=["user", "plan"], name="unique_user_plan_feedback")]

    def __str__(self):
        return f"{self.user.username} · {self.plan.title}"


class DayProgress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "未开始"
        IN_PROGRESS = "in_progress", "进行中"
        COMPLETED = "completed", "已完成"

    enrollment = models.ForeignKey(Enrollment, related_name="progress", on_delete=models.CASCADE)
    plan_day = models.ForeignKey(PlanDay, related_name="progress", on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NOT_STARTED)
    acceptance_checks = models.JSONField(default=list, blank=True)
    knowledge_checks = models.JSONField(default=list, blank=True)
    reflection = models.TextField(blank=True)
    recall_score = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["plan_day__day_number"]
        constraints = [models.UniqueConstraint(fields=["enrollment", "plan_day"], name="unique_day_progress")]

    def clean(self):
        if self.enrollment_id and self.plan_day_id and self.enrollment.plan_id != self.plan_day.plan_id:
            raise ValidationError("学习进度与学习计划不匹配。")

    def start(self):
        if self.status == self.Status.NOT_STARTED:
            self.status = self.Status.IN_PROGRESS
            self.started_at = timezone.now()

    def completion_errors(self):
        expected_knowledge = self.plan_day.knowledge_count()
        knowledge_ok = len(self.knowledge_checks) == expected_knowledge and all(self.knowledge_checks)
        expected = len(self.plan_day.acceptance_criteria)
        checks_ok = len(self.acceptance_checks) == expected and all(self.acceptance_checks)
        errors = []
        if not knowledge_ok:
            errors.append("请完成全部知识点的学习与复现。")
        if not checks_ok:
            errors.append("请完成全部验收项。")
        if not self.evidence.exists():
            errors.append("请至少提交一项学习证据。")
        return errors

    def __str__(self):
        return f"{self.enrollment.user.username} · Day {self.plan_day.day_number}"


class ReviewAttempt(models.Model):
    """记录学习者对已完成学习日的一次间隔复习结果。"""

    class Rating(models.TextChoices):
        FORGOT = "forgot", "需要重学"
        UNSURE = "unsure", "基本想起"
        MASTERED = "mastered", "熟练掌握"

    progress = models.ForeignKey(DayProgress, related_name="review_attempts", on_delete=models.CASCADE)
    rating = models.CharField(max_length=12, choices=Rating.choices)
    note = models.TextField(blank=True)
    interval_days = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)
    next_review_at = models.DateTimeField()

    class Meta:
        ordering = ["-reviewed_at"]

    def clean(self):
        """拒绝为尚未完成的学习日写入复习记录。"""
        if self.progress_id and self.progress.status != DayProgress.Status.COMPLETED:
            raise ValidationError("只能复习已经完成的学习日。")

    def __str__(self):
        return f"{self.progress} · {self.get_rating_display()}"


def evidence_upload_path(instance, filename):
    """为学习证据附件生成按用户和学习日隔离的随机存储路径。"""
    extension = Path(filename).suffix.lower()
    safe_extension = extension if extension in {".jpg", ".jpeg", ".png", ".webp", ".txt", ".json", ".pdf"} else ""
    return (
        f"evidence/{instance.progress.enrollment.user_id}/{instance.progress.plan_day.day_number}/"
        f"{uuid4().hex}{safe_extension}"
    )


class Evidence(models.Model):
    class Kind(models.TextChoices):
        COMMIT = "commit", "Git提交"
        CODE = "code", "代码"
        TEST = "test", "测试结果"
        LOG = "log", "日志"
        REPORT = "report", "报告"
        LINK = "link", "链接"
        NOTE = "note", "学习笔记"

    progress = models.ForeignKey(DayProgress, related_name="evidence", on_delete=models.CASCADE)
    kind = models.CharField(max_length=12, choices=Kind.choices)
    title = models.CharField(max_length=120)
    content = models.TextField(blank=True)
    url = models.URLField(blank=True)
    attachment = models.FileField(upload_to=evidence_upload_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Gap(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "待解决"
        VERIFYING = "verifying", "等待验证"
        RESOLVED = "resolved", "已解决"

    progress = models.ForeignKey(DayProgress, related_name="gaps", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    detail = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    resolution = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User, related_name="verified_gaps", on_delete=models.SET_NULL, null=True, blank=True
    )
    verification_group = models.ForeignKey(
        "StudyGroup", related_name="gap_verifications", on_delete=models.SET_NULL, null=True, blank=True
    )
    verification_note = models.CharField(max_length=300, blank=True)
    verification_requested_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "-created_at"]

    def save(self, *args, **kwargs):
        self.resolved_at = timezone.now() if self.status == self.Status.RESOLVED else None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CommunityPost(models.Model):
    class Type(models.TextChoices):
        SHARE = "share", "技术分享"
        QUESTION = "question", "问题求助"
        CHECK_IN = "check_in", "学习打卡"
        PROJECT = "project", "项目展示"

    author = models.ForeignKey(User, related_name="community_posts", on_delete=models.CASCADE)
    plan = models.ForeignKey(
        LearningPlan, related_name="community_posts", on_delete=models.CASCADE, null=True, blank=True
    )
    plan_day = models.ForeignKey(
        PlanDay, related_name="community_posts", on_delete=models.CASCADE, null=True, blank=True
    )
    post_type = models.CharField(max_length=12, choices=Type.choices, default=Type.SHARE)
    title = models.CharField(max_length=160)
    content = models.TextField()
    is_solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


def community_image_upload_path(instance, filename):
    """将帖子图片存入帖子专属目录，并使用不可预测的文件名。"""
    extension = Path(filename).suffix.lower()
    return f"community/{instance.post_id}/{uuid4().hex}{extension}"


class CommunityPostImage(models.Model):
    """保存社区帖子的经过清洗的展示图片。"""

    post = models.ForeignKey(CommunityPost, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=community_image_upload_path)
    alt_text = models.CharField(max_length=160, blank=True)
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    position = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.post.title} · 图片 {self.position + 1}"


class CommunityComment(models.Model):
    post = models.ForeignKey(CommunityPost, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="community_comments", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", related_name="replies", on_delete=models.CASCADE, null=True, blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} · {self.post.title}"


class CommunityPostLike(models.Model):
    post = models.ForeignKey(CommunityPost, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="community_post_likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "user"], name="unique_community_post_like")]


class CommunityReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "待处理"
        RESOLVED = "resolved", "已处理"

    reporter = models.ForeignKey(User, related_name="community_reports", on_delete=models.CASCADE)
    post = models.ForeignKey(
        CommunityPost, related_name="reports", on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        CommunityComment, related_name="reports", on_delete=models.CASCADE, null=True, blank=True
    )
    reason = models.CharField(max_length=300)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(post__isnull=False, comment__isnull=True) | Q(post__isnull=True, comment__isnull=False)),
                name="community_report_has_one_target",
            )
        ]


class Contribution(models.Model):
    """记录用户对课程和同伴学习产生的可验证贡献。"""

    class Kind(models.TextChoices):
        COURSE = "course", "课程共建"
        REVIEW = "review", "同伴互评"
        ANSWER = "answer", "志愿答疑"
        CHALLENGE = "challenge", "小队挑战"

    user = models.ForeignKey(User, related_name="contributions", on_delete=models.CASCADE)
    kind = models.CharField(max_length=12, choices=Kind.choices)
    title = models.CharField(max_length=160)
    detail = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CourseSuggestion(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已采纳"
        REJECTED = "rejected", "未采纳"

    author = models.ForeignKey(User, related_name="course_suggestions", on_delete=models.CASCADE)
    post = models.ForeignKey(CommunityPost, related_name="course_suggestions", on_delete=models.CASCADE)
    plan_day = models.ForeignKey(PlanDay, related_name="course_suggestions", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    content = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    review_note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["post", "plan_day"], name="unique_post_course_suggestion")]


class PeerReview(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "等待互评"
        CLAIMED = "claimed", "评审中"
        COMPLETED = "completed", "已完成"

    progress = models.ForeignKey(DayProgress, related_name="peer_reviews", on_delete=models.CASCADE)
    requester = models.ForeignKey(User, related_name="requested_peer_reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        User, related_name="completed_peer_reviews", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    accuracy = models.BooleanField(null=True, blank=True)
    runnable = models.BooleanField(null=True, blank=True)
    clarity = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "created_at"]


class HelpSession(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "征集中"
        ARCHIVED = "archived", "已归档"

    plan = models.ForeignKey(
        LearningPlan, related_name="help_sessions", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    created_by = models.ForeignKey(User, related_name="created_help_sessions", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "deadline"]


class HelpQuestion(models.Model):
    session = models.ForeignKey(HelpSession, related_name="questions", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="help_questions", on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(
        User, related_name="volunteer_answers", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["answered_at", "created_at"]


class BuddyProfile(models.Model):
    enrollment = models.OneToOneField(Enrollment, related_name="buddy_profile", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="buddy_profiles", on_delete=models.CASCADE)
    study_time = models.CharField(max_length=80)
    goal = models.CharField(max_length=240)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class StudyGroup(models.Model):
    """表示由朋友组成、共享周目标和缺口验证的小型学习队伍。"""

    name = models.CharField(max_length=80)
    owner = models.ForeignKey(User, related_name="owned_study_groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="study_groups", blank=True)
    invite_code = models.CharField(max_length=12, unique=True, default=generate_invite_code)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WeeklyContract(models.Model):
    """记录一名小队成员在指定自然周承诺完成的学习日目标。"""

    group = models.ForeignKey(StudyGroup, related_name="contracts", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="weekly_contracts", on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, related_name="weekly_contracts", on_delete=models.CASCADE)
    week_start = models.DateField(default=current_week_start)
    target_days = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-week_start", "user__username"]
        constraints = [
            models.UniqueConstraint(fields=["group", "user", "week_start"], name="unique_group_week_contract")
        ]

    def __str__(self):
        return f"{self.group.name} · {self.user.username} · {self.week_start}"


class TeamChallenge(models.Model):
    """表示小队成员需要分工并合并学习证据的限时协作挑战。"""

    class Status(models.TextChoices):
        OPEN = "open", "进行中"
        COMPLETED = "completed", "已完成"

    group = models.ForeignKey(StudyGroup, related_name="challenges", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name="created_team_challenges", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "deadline", "-created_at"]

    def __str__(self):
        return f"{self.group.name} · {self.title}"


class TeamChallengeEntry(models.Model):
    """保存一名成员在协作挑战中的角色、说明和已有学习证据。"""

    class Role(models.TextChoices):
        REPRODUCE = "reproduce", "复现"
        TEST = "test", "测试"
        EXPLAIN = "explain", "讲解"
        REVIEW = "review", "复核"

    challenge = models.ForeignKey(TeamChallenge, related_name="entries", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="team_challenge_entries", on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=Role.choices)
    evidence = models.ForeignKey(
        Evidence, related_name="team_challenge_entries", on_delete=models.SET_NULL, null=True
    )
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["challenge", "user"], name="unique_team_challenge_member"
            ),
            models.UniqueConstraint(
                fields=["challenge", "role"], name="unique_team_challenge_role"
            ),
        ]

    def __str__(self):
        return f"{self.challenge.title} · {self.user.username} · {self.get_role_display()}"


class Notification(models.Model):
    """保存需要学习者主动处理或知晓的站内通知。"""

    class Kind(models.TextChoices):
        COMMUNITY = "community", "社区互动"
        REVIEW = "review", "同伴互评"
        HELP = "help", "公开答疑"
        COURSE = "course", "课程共建"
        GAP = "gap", "缺口验证"
        CHALLENGE = "challenge", "小队挑战"
        SYSTEM = "system", "系统通知"

    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.SYSTEM)
    title = models.CharField(max_length=160)
    body = models.CharField(max_length=300, blank=True)
    url = models.CharField(max_length=240, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "read_at", "-created_at"], name="notice_user_unread_idx")]

    def __str__(self):
        return self.title


class AIProvider(models.TextChoices):
    """列出当前应用已经实现认证方式的大模型供应商。"""

    OPENAI = "openai", "OpenAI"
    ANTHROPIC = "anthropic", "Anthropic"


class AIAdapter(models.TextChoices):
    """列出用户可选择且服务端已经实现的模型接口协议。"""

    OPENAI_RESPONSES = "openai_responses", "OpenAI Responses"
    OPENAI_CHAT_COMPLETIONS = "openai_chat_completions", "OpenAI Chat Completions"
    ANTHROPIC_MESSAGES = "anthropic_messages", "Anthropic Messages"


class AIProviderCredential(models.Model):
    """保存用户主动选择持久化的模型接口配置、密钥密文和非敏感提示。"""

    user = models.ForeignKey(User, related_name="ai_credentials", on_delete=models.CASCADE)
    name = models.CharField(max_length=80, default="模型配置")
    provider = models.CharField(max_length=24, choices=AIProvider.choices)
    adapter = models.CharField(max_length=32, choices=AIAdapter.choices, blank=True)
    api_url = models.CharField(max_length=500, blank=True)
    model = models.CharField(max_length=100, blank=True)
    encrypted_api_key = models.TextField()
    key_last_four = models.CharField(max_length=4)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return f"{self.user.username} · {self.name} · ····{self.key_last_four}"


class AIChatSession(models.Model):
    """保存一段属于单个用户、可选关联当前学习日的 AI 学习对话配置。"""

    class TeachingMode(models.TextChoices):
        HINT = "hint", "提示优先"
        EXPLAIN = "explain", "详细讲解"
        EXAMPLE = "example", "举例对比"
        DEBUG = "debug", "报错分析"
        QUIZ = "quiz", "出题检验"

    user = models.ForeignKey(User, related_name="ai_chat_sessions", on_delete=models.CASCADE)
    credential = models.ForeignKey(
        AIProviderCredential,
        related_name="chat_sessions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    progress = models.ForeignKey(
        DayProgress,
        related_name="ai_chat_sessions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=120)
    provider = models.CharField(max_length=24, choices=AIProvider.choices)
    adapter = models.CharField(max_length=32, choices=AIAdapter.choices, blank=True)
    api_url = models.CharField(max_length=500, blank=True)
    model = models.CharField(max_length=100)
    context_rounds = models.PositiveSmallIntegerField(
        default=8, validators=[MinValueValidator(4), MaxValueValidator(12)]
    )
    max_output_tokens = models.PositiveSmallIntegerField(
        default=1024, validators=[MinValueValidator(128), MaxValueValidator(4096)]
    )
    teaching_mode = models.CharField(
        max_length=16, choices=TeachingMode.choices, default=TeachingMode.HINT
    )
    include_current_lesson = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["user", "-updated_at"], name="ai_chat_user_updated_idx")]

    def __str__(self):
        return f"{self.user.username} · {self.title}"


class AIChatMessage(models.Model):
    """保存 AI 学习对话中的文本、限时附件元数据和供应商用量。"""

    class Role(models.TextChoices):
        USER = "user", "用户"
        ASSISTANT = "assistant", "助手"

    session = models.ForeignKey(AIChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=Role.choices)
    content = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    context_snapshot = models.JSONField(default=dict, blank=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    provider_request_id = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["session", "created_at"], name="ai_msg_session_time_idx")]

    def __str__(self):
        return f"{self.session.title} · {self.get_role_display()} · {self.created_at:%Y-%m-%d %H:%M}"
