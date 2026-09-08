"""学习小队、互助、互评、答疑、搭子和通知接口。"""

from datetime import datetime, time, timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ..models import (
    BuddyProfile,
    Contribution,
    CourseSuggestion,
    DayProgress,
    Enrollment,
    Evidence,
    Gap,
    HelpQuestion,
    HelpSession,
    Notification,
    PeerReview,
    PlanDay,
    StudyGroup,
    TeamChallenge,
    TeamChallengeEntry,
    WeeklyContract,
    current_week_start,
    generate_invite_code,
)
from ..services import joined_enrollments, notify
from ..study.experience import activity_summary, review_center
from .serializers import (
    BuddyProfileSerializer,
    CourseSuggestionSerializer,
    HelpQuestionSerializer,
    HelpSessionSerializer,
    NotificationSerializer,
    PeerReviewSerializer,
    StudyGroupSerializer,
    TeamChallengeEntrySerializer,
    TeamChallengeSerializer,
    WeeklyContractSerializer,
)


class StudyGroupViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """管理当前用户所在的小队、邀请码和本周共享进度。"""

    serializer_class = StudyGroupSerializer

    def get_queryset(self):
        return StudyGroup.objects.filter(members=self.request.user).select_related("owner").annotate(
            member_count=Count("members", distinct=True)
        )

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        group.members.add(self.request.user)

    @action(detail=False, methods=["post"])
    def join(self, request):
        """让已有账号使用邀请码加入对应小队。"""
        code = str(request.data.get("invite_code", "")).strip().upper()
        group = get_object_or_404(StudyGroup, invite_code=code)
        joined = not group.members.filter(pk=request.user.id).exists()
        group.members.add(request.user)
        if joined:
            notify(
                group.owner,
                Notification.Kind.SYSTEM,
                "有新成员加入学习小队",
                f"{request.user.first_name or request.user.username} 已加入 {group.name}。",
                "/team",
            )
        group.member_count = group.members.count()
        return Response(self.get_serializer(group).data, status=201 if joined else 200)

    @action(detail=True, methods=["post"], url_path="rotate-code")
    def rotate_code(self, request, pk=None):
        """由小队创建者立即废止旧邀请码并生成新邀请码。"""
        group = self.get_object()
        if group.owner_id != request.user.id:
            return Response({"detail": "只有小队创建者可以更新邀请码。"}, status=403)
        group.invite_code = generate_invite_code()
        group.save(update_fields=["invite_code"])
        return Response({"invite_code": group.invite_code})

    @action(detail=True, methods=["get"])
    def dashboard(self, request, pk=None):
        """返回本周成员契约、真实活动和等待队友验证的知识缺口。"""
        group = self.get_object()
        week_start = current_week_start()
        week_end = week_start + timedelta(days=6)
        start_at = timezone.make_aware(datetime.combine(week_start, time.min))
        end_at = start_at + timedelta(days=7)
        members = list(group.members.all().order_by("username"))
        contracts = {
            item.user_id: item
            for item in group.contracts.filter(week_start=week_start).select_related("enrollment__plan", "user")
        }
        member_payload = []
        # 小队规模固定很小，直接复用个人活动统计可保持日历口径完全一致。
        for member in members:
            contract = contracts.get(member.id)
            completed = 0
            if contract:
                completed = DayProgress.objects.filter(
                    enrollment=contract.enrollment,
                    status=DayProgress.Status.COMPLETED,
                    # 使用时间范围避免依赖 MySQL 时区表执行日期转换。
                    completed_at__gte=start_at,
                    completed_at__lt=end_at,
                ).count()
            activity = activity_summary(member)
            member_payload.append({
                "id": member.id,
                "name": member.first_name or member.username,
                "username": member.username,
                "is_current_user": member.id == request.user.id,
                "contract": WeeklyContractSerializer(contract, context={"request": request}).data if contract else None,
                "completed_days": completed,
                "current_streak": activity["current_streak"],
                "last_active_date": activity["last_active_date"],
            })
        pending_gaps = Gap.objects.filter(
            status=Gap.Status.VERIFYING,
            verification_group=group,
        ).select_related("progress__enrollment__user", "progress__enrollment__plan", "progress__plan_day").annotate(
            evidence_count=Count("progress__evidence", distinct=True)
        )
        evidence_options = Evidence.objects.filter(
            progress__enrollment__user=request.user
        ).select_related("progress__enrollment__plan", "progress__plan_day").order_by("-created_at")[:30]
        return Response({
            "group": self.get_serializer(group).data,
            "week_start": week_start,
            "week_end": week_end,
            "members": member_payload,
            "pending_gaps": [
                {
                    "id": gap.id,
                    "owner_id": gap.progress.enrollment.user_id,
                    "owner_name": gap.progress.enrollment.user.first_name or gap.progress.enrollment.user.username,
                    "plan_title": gap.progress.enrollment.plan.title,
                    "day_number": gap.progress.plan_day.day_number,
                    "title": gap.title,
                    "detail": gap.detail,
                    "resolution": gap.resolution,
                    "evidence_count": gap.evidence_count,
                    "can_verify": gap.progress.enrollment.user_id != request.user.id,
                }
                for gap in pending_gaps
            ],
            "evidence_options": [
                {
                    "id": evidence.id,
                    "title": evidence.title,
                    "kind": evidence.kind,
                    "plan_title": evidence.progress.enrollment.plan.title,
                    "day_number": evidence.progress.plan_day.day_number,
                }
                for evidence in evidence_options
            ],
        })

    @action(detail=True, methods=["get"], url_path="result-card")
    def result_card(self, request, pk=None):
        """实时聚合当前成员本周成果，供页面展示和用户主动分享。"""
        group = self.get_object()
        week_start = current_week_start()
        week_end = week_start + timedelta(days=6)
        start_at = timezone.make_aware(datetime.combine(week_start, time.min))
        end_at = start_at + timedelta(days=7)
        user = request.user
        completed_progress = DayProgress.objects.filter(
            enrollment__user=user,
            status=DayProgress.Status.COMPLETED,
            completed_at__gte=start_at,
            completed_at__lt=end_at,
        )
        evidence_count = Evidence.objects.filter(
            progress__enrollment__user=user, created_at__gte=start_at, created_at__lt=end_at
        ).count()
        resolved_gaps = Gap.objects.filter(
            progress__enrollment__user=user,
            status=Gap.Status.RESOLVED,
            resolved_at__gte=start_at,
            resolved_at__lt=end_at,
        ).count()
        peer_reviews = PeerReview.objects.filter(
            reviewer=user,
            status=PeerReview.Status.COMPLETED,
            updated_at__gte=start_at,
            updated_at__lt=end_at,
        ).count()
        challenges_completed = TeamChallengeEntry.objects.filter(
            user=user,
            challenge__group=group,
            challenge__status=TeamChallenge.Status.COMPLETED,
            challenge__completed_at__gte=start_at,
            challenge__completed_at__lt=end_at,
        ).count()
        contract = group.contracts.filter(user=user, week_start=week_start).first()
        contract_completed = completed_progress.filter(enrollment=contract.enrollment).count() if contract else 0
        return Response({
            "group_name": group.name,
            "user_name": user.first_name or user.username,
            "week_start": week_start,
            "week_end": week_end,
            "target_days": contract.target_days if contract else None,
            "completed_days": completed_progress.count(),
            "contract_completed_days": contract_completed,
            "goal_met": bool(contract and contract_completed >= contract.target_days),
            "evidence_count": evidence_count,
            "resolved_gaps": resolved_gaps,
            "peer_reviews": peer_reviews,
            "challenges_completed": challenges_completed,
            "current_streak": activity_summary(user)["current_streak"],
        })


class WeeklyContractViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """允许成员创建和调整自己的每周学习契约。"""

    serializer_class = WeeklyContractSerializer

    def get_queryset(self):
        return WeeklyContract.objects.filter(user=self.request.user).select_related("group", "enrollment__plan")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TeamChallengeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """管理小队协作挑战的发起、分工证据提交和合并完成。"""

    serializer_class = TeamChallengeSerializer

    def get_queryset(self):
        """只返回当前用户所在小队的挑战。"""
        queryset = TeamChallenge.objects.filter(group__members=self.request.user).select_related(
            "group", "created_by"
        ).prefetch_related("entries__user", "entries__evidence").distinct()
        group_id = self.request.query_params.get("group")
        if not group_id:
            return queryset
        try:
            group_id = int(group_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError({"group": "学习小队参数无效。"}) from exc
        return queryset.filter(group_id=group_id)

    def perform_create(self, serializer):
        """保存发起人并通知同队朋友。"""
        challenge = serializer.save(created_by=self.request.user)
        url = f"/team?group={challenge.group_id}&challenge={challenge.id}"
        for member in challenge.group.members.exclude(pk=self.request.user.id):
            notify(
                member,
                Notification.Kind.CHALLENGE,
                "朋友发起了小队协作挑战",
                f"{self.request.user.first_name or self.request.user.username}：{challenge.title}",
                url,
            )

    @action(detail=True, methods=["post"])
    def contribute(self, request, pk=None):
        """创建或更新当前成员的一项角色分工和学习证据。"""
        with transaction.atomic():
            challenge = TeamChallenge.objects.select_for_update().get(pk=self.get_object().pk)
            instance = challenge.entries.filter(user=request.user).first()
            serializer = TeamChallengeEntrySerializer(
                instance,
                data=request.data,
                context={"request": request, "challenge": challenge},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(challenge=challenge, user=request.user)
        if not instance:
            url = f"/team?group={challenge.group_id}&challenge={challenge.id}"
            for member in challenge.group.members.exclude(pk=request.user.id):
                notify(
                    member,
                    Notification.Kind.CHALLENGE,
                    "小队挑战有了新进展",
                    f"{request.user.first_name or request.user.username} 已完成“{serializer.instance.get_role_display()}”分工。",
                    url,
                )
        return Response(serializer.data, status=200 if instance else 201)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """在至少两名成员完成不同分工后合并挑战并记录成长贡献。"""
        with transaction.atomic():
            challenge = TeamChallenge.objects.select_for_update().get(pk=self.get_object().pk)
            # 锁住分工行，让删除证据时的 SET_NULL 与结算按顺序执行。
            entries = list(challenge.entries.select_for_update().select_related("user"))
            errors = challenge.completion_errors(entries)
            if errors:
                return Response({"detail": errors}, status=400)
            challenge.status = TeamChallenge.Status.COMPLETED
            challenge.completed_at = timezone.now()
            challenge.save(update_fields=["status", "completed_at"])
            Contribution.objects.bulk_create([
                Contribution(
                    user=entry.user,
                    kind=Contribution.Kind.CHALLENGE,
                    title=f"完成小队挑战：{challenge.title}",
                    detail=entry.get_role_display(),
                )
                for entry in entries
            ])
            for member in challenge.group.members.all():
                notify(
                    member,
                    Notification.Kind.CHALLENGE,
                    "小队协作挑战已完成",
                    f"{challenge.title} · {len(entries)} 名成员合并了学习证据。",
                    f"/team?group={challenge.group_id}&challenge={challenge.id}",
                )
        challenge = self.get_queryset().get(pk=challenge.pk)
        return Response(self.get_serializer(challenge).data)


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """提供当前用户的通知列表、未读数量和已读操作。"""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()[:100]
        return Response({
            "items": self.get_serializer(queryset, many=True).data,
            "unread_count": self.get_queryset().filter(read_at__isnull=True).count(),
            "due_review_count": review_center(request.user)["due_count"],
        })

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """返回侧栏徽标所需的通知与到期复习合计。"""
        notifications = self.get_queryset().filter(read_at__isnull=True).count()
        reviews = review_center(request.user)["due_count"]
        return Response({"count": notifications + reviews, "notifications": notifications, "reviews": reviews})

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        """将当前用户的一条通知标记为已读。"""
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        if not notification.read_at:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_read(self, request):
        """一次性清除当前用户的全部未读通知。"""
        updated = self.get_queryset().filter(read_at__isnull=True).update(read_at=timezone.now())
        return Response({"updated": updated})


class CourseSuggestionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """管理课程补充推荐及管理员审核。"""

    serializer_class = CourseSuggestionSerializer

    def get_permissions(self):
        if self.action in ("approve", "reject"):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = CourseSuggestion.objects.select_related("author", "post", "plan_day__plan")
        if self.request.user.is_staff:
            return queryset.filter(status=CourseSuggestion.Status.PENDING) if self.action == "list" else queryset
        return queryset.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        with transaction.atomic():
            suggestion = CourseSuggestion.objects.select_for_update().select_related("author").get(pk=self.get_object().pk)
            if suggestion.status != CourseSuggestion.Status.PENDING:
                return Response({"detail": "该课程建议已经处理。"}, status=400)
            plan_day = PlanDay.objects.select_for_update().get(pk=suggestion.plan_day_id)
            supplements = list(plan_day.community_supplements)
            supplements.append({"title": suggestion.title, "content": suggestion.content, "author": suggestion.author.first_name or suggestion.author.username})
            plan_day.community_supplements = supplements
            plan_day.save(update_fields=["community_supplements"])
            suggestion.status = CourseSuggestion.Status.APPROVED
            suggestion.review_note = ""
            suggestion.save(update_fields=["status", "review_note", "updated_at"])
        Contribution.objects.create(
            user=suggestion.author, kind=Contribution.Kind.COURSE,
            title=f"补充课程：{plan_day.title}", detail=suggestion.title,
        )
        notify(
            suggestion.author,
            Notification.Kind.COURSE,
            "课程补充已被采纳",
            f"{plan_day.plan.title} · Day {plan_day.day_number}：{suggestion.title}",
            f"/plans/{plan_day.plan.slug}",
        )
        return Response(self.get_serializer(suggestion).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        suggestion = self.get_object()
        if suggestion.status != CourseSuggestion.Status.PENDING:
            return Response({"detail": "该课程建议已经处理。"}, status=400)
        suggestion.status = CourseSuggestion.Status.REJECTED
        suggestion.review_note = str(request.data.get("review_note", "")).strip()
        suggestion.save(update_fields=["status", "review_note", "updated_at"])
        notify(
            suggestion.author,
            Notification.Kind.COURSE,
            "课程补充暂未采纳",
            suggestion.review_note or suggestion.title,
            "/mutual-help",
        )
        return Response(self.get_serializer(suggestion).data)


class PeerReviewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """管理同伴互评的申请、领取和提交。"""

    serializer_class = PeerReviewSerializer

    def get_queryset(self):
        enrolled_plans = joined_enrollments(self.request.user).values("plan_id")
        return PeerReview.objects.filter(
            Q(requester=self.request.user) | Q(reviewer=self.request.user) |
            Q(status=PeerReview.Status.OPEN, progress__enrollment__plan_id__in=enrolled_plans)
        ).select_related("requester", "reviewer", "progress__plan_day", "progress__enrollment__plan").prefetch_related("progress__evidence").distinct()

    def perform_create(self, serializer):
        progress = serializer.validated_data["progress"]
        if progress.enrollment.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只能为自己的学习成果申请互评。")
        if not progress.evidence.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("提交学习证据后才能申请互评。")
        if PeerReview.objects.filter(progress=progress, status__in=(PeerReview.Status.OPEN, PeerReview.Status.CLAIMED)).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("该学习日已经有一项进行中的互评。")
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        with transaction.atomic():
            review = PeerReview.objects.select_for_update().select_related("requester", "progress__enrollment__plan", "progress__plan_day").get(pk=self.get_object().pk)
            if review.requester_id == request.user.id:
                return Response({"detail": "不能评审自己的学习成果。"}, status=400)
            if review.status != PeerReview.Status.OPEN:
                return Response({"detail": "该互评任务已被领取。"}, status=400)
            review.reviewer = request.user
            review.status = PeerReview.Status.CLAIMED
            review.save(update_fields=["reviewer", "status", "updated_at"])
        notify(
            review.requester,
            Notification.Kind.REVIEW,
            "朋友领取了你的互评任务",
            f"{request.user.first_name or request.user.username} 正在查看 Day {review.progress.plan_day.day_number} 的证据。",
            "/mutual-help",
        )
        return Response(self.get_serializer(review).data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        values = {
            "accuracy": request.data.get("accuracy"), "runnable": request.data.get("runnable"),
            "clarity": request.data.get("clarity"), "feedback": str(request.data.get("feedback", "")).strip(),
        }
        required = tuple(values.values())
        if any(value is None or value == "" for value in required):
            return Response({"detail": "请完成三个检查项并填写具体反馈。"}, status=400)
        if not all(isinstance(values[key], bool) for key in ("accuracy", "runnable", "clarity")):
            return Response({"detail": "检查项必须是布尔值。"}, status=400)
        with transaction.atomic():
            review = PeerReview.objects.select_for_update().select_related(
                "progress__plan_day", "progress__enrollment__plan"
            ).get(pk=self.get_object().pk)
            if review.reviewer_id != request.user.id:
                return Response({"detail": "只有领取任务的评审者可以提交。"}, status=403)
            if review.status != PeerReview.Status.CLAIMED:
                return Response({"detail": "该互评任务已经完成或尚未领取。"}, status=400)
            for key, value in values.items():
                setattr(review, key, value)
            review.status = PeerReview.Status.COMPLETED
            review.save(update_fields=["accuracy", "runnable", "clarity", "feedback", "status", "updated_at"])
            Contribution.objects.create(
                user=request.user, kind=Contribution.Kind.REVIEW,
                title=f"完成同伴互评：Day {review.progress.plan_day.day_number}", detail=review.progress.enrollment.plan.title,
            )
        notify(
            review.requester,
            Notification.Kind.REVIEW,
            "同伴互评已经完成",
            review.feedback,
            "/mutual-help",
        )
        return Response(self.get_serializer(review).data)


class HelpSessionViewSet(viewsets.ModelViewSet):
    """管理公开答疑场次、问题和回答。"""

    serializer_class = HelpSessionSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "archive"):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = HelpSession.objects.select_related("plan", "created_by").prefetch_related("questions__author", "questions__answered_by")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(
            Q(plan__isnull=True)
            | Q(plan__enrollments__user=self.request.user, plan__enrollments__status__in=Enrollment.JOINED_STATUSES)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        session = self.get_object()
        if session.status != HelpSession.Status.OPEN:
            return Response({"detail": "该答疑场次已经归档。"}, status=400)
        session.status = HelpSession.Status.ARCHIVED
        session.save(update_fields=["status"])
        return Response(self.get_serializer(session).data)

    @action(detail=True, methods=["post"])
    def questions(self, request, pk=None):
        session = self.get_object()
        if session.status != HelpSession.Status.OPEN or session.deadline < timezone.now():
            return Response({"detail": "本场答疑已停止征集问题。"}, status=400)
        serializer = HelpQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(session=session, author=request.user)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"], url_path=r"questions/(?P<question_id>[^/.]+)/answer")
    def answer(self, request, pk=None, question_id=None):
        session = self.get_object()
        if session.status != HelpSession.Status.OPEN:
            return Response({"detail": "本场答疑已经归档。"}, status=400)
        answer = str(request.data.get("answer", "")).strip()
        if not answer:
            return Response({"detail": "回答内容不能为空。"}, status=400)
        with transaction.atomic():
            question = get_object_or_404(HelpQuestion.objects.select_for_update(), pk=question_id, session=session)
            if question.answered_at:
                return Response({"detail": "该问题已经得到回答。"}, status=400)
            question.answer = answer
            question.answered_by = request.user
            question.answered_at = timezone.now()
            question.save(update_fields=["answer", "answered_by", "answered_at"])
            Contribution.objects.create(
                user=request.user, kind=Contribution.Kind.ANSWER,
                title=f"志愿答疑：{session.title}", detail=question.question[:160],
            )
        if question.author_id != request.user.id:
            notify(
                question.author,
                Notification.Kind.HELP,
                "你的问题得到了回答",
                session.title,
                "/mutual-help",
            )
        return Response(HelpQuestionSerializer(question).data)


class BuddyProfileViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """管理当前用户的搭子资料和匹配结果。"""

    serializer_class = BuddyProfileSerializer

    def get_queryset(self):
        queryset = BuddyProfile.objects.filter(
            active=True, enrollment__status__in=Enrollment.JOINED_STATUSES
        ).select_related("user", "enrollment__plan")
        enrollment_id = self.request.query_params.get("enrollment")
        if not enrollment_id:
            return queryset.filter(user=self.request.user)
        enrollment = get_object_or_404(joined_enrollments(self.request.user), pk=enrollment_id)
        return queryset.filter(
            enrollment__plan=enrollment.plan,
            enrollment__current_day__gte=max(1, enrollment.current_day - 3),
            enrollment__current_day__lte=enrollment.current_day + 3,
        ).exclude(user=self.request.user)

    def perform_create(self, serializer):
        enrollment = serializer.validated_data["enrollment"]
        if enrollment.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只能为自己的学习路线开启搭子匹配。")
        profile, _ = BuddyProfile.objects.update_or_create(
            enrollment=enrollment,
            defaults={"user": self.request.user, "study_time": serializer.validated_data["study_time"], "goal": serializer.validated_data["goal"], "active": serializer.validated_data.get("active", True)},
        )
        serializer.instance = profile

    def create(self, request, *args, **kwargs):
        enrollment = get_object_or_404(
            joined_enrollments(request.user), pk=request.data.get("enrollment")
        )
        instance = BuddyProfile.objects.filter(enrollment=enrollment).first()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=200 if instance else 201)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user_id != request.user.id:
            return Response({"detail": "只能修改自己的搭子资料。"}, status=403)
        enrollment_id = request.data.get("enrollment", profile.enrollment_id)
        try:
            enrollment_id = int(enrollment_id)
        except (TypeError, ValueError):
            return Response({"enrollment": ["报名记录无效。"]}, status=400)
        if enrollment_id != profile.enrollment_id:
            return Response({"enrollment": ["搭子资料不能切换到其他报名记录。"]}, status=400)
        return super().update(request, *args, **kwargs)
