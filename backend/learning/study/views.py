"""学习路线、学习进度、复习、洞察和成果接口。"""

import json

from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (
    BuddyProfile,
    Contribution,
    DayProgress,
    Enrollment,
    Evidence,
    Gap,
    LearningPlan,
    Notification,
    PlanDay,
    PlanFeedback,
    StudyGroup,
)
from ..services import joined_enrollments, notify
from .experience import activity_summary, growth_summary, review_center
from .serializers import (
    ContributionSerializer,
    CustomLearningPlanSerializer,
    DayProgressSerializer,
    EnrollmentSerializer,
    EvidenceSerializer,
    GapSerializer,
    JourneyDaySerializer,
    LearningPlanDetailSerializer,
    LearningPlanListSerializer,
    PlanDaySerializer,
    PlanFeedbackSerializer,
    ReviewAttemptSerializer,
)

# 学习者可以提前查看的天数。预习是只读的：不建 DayProgress，也不能开始或完成。
PREVIEW_DAYS = 5


def progress_for(enrollment, day_number):
    day = get_object_or_404(PlanDay, plan=enrollment.plan, day_number=day_number)
    progress, _ = DayProgress.objects.get_or_create(
        enrollment=enrollment,
        plan_day=day,
        defaults={
            "acceptance_checks": [False] * len(day.acceptance_criteria),
            "knowledge_checks": [False] * day.knowledge_count(),
        },
    )
    normalized_acceptance = [bool(progress.acceptance_checks[index]) if index < len(progress.acceptance_checks) else False for index in range(len(day.acceptance_criteria))]
    normalized_knowledge = [bool(progress.knowledge_checks[index]) if index < len(progress.knowledge_checks) else False for index in range(day.knowledge_count())]
    changed = []
    if progress.acceptance_checks != normalized_acceptance:
        progress.acceptance_checks = normalized_acceptance
        changed.append("acceptance_checks")
    if progress.knowledge_checks != normalized_knowledge:
        progress.knowledge_checks = normalized_knowledge
        changed.append("knowledge_checks")
    if changed:
        progress.save(update_fields=changed)
    return progress


class DashboardView(APIView):
    """汇总当前用户的今日学习任务和活动状态。"""

    def get(self, request):
        enrollments = joined_enrollments(request.user).select_related("plan").annotate(
            completed_count=Count("progress", filter=Q(progress__status=DayProgress.Status.COMPLETED))
        ).order_by("-last_studied_at", "-started_at")
        enrollment_id = request.query_params.get("enrollment")
        if enrollment_id:
            if not enrollment_id.isdigit():
                return Response({"detail": "学习路线参数无效。"}, status=400)
            enrollment = get_object_or_404(enrollments, pk=enrollment_id)
        else:
            enrollment = enrollments.filter(status=Enrollment.Status.ACTIVE).first() or enrollments.first()
        plans = LearningPlan.objects.filter(is_published=True).prefetch_related("feedback")
        if not enrollment:
            activity = activity_summary(request.user)
            return Response(
                {
                    "enrollment": None,
                    "enrollments": [],
                    "recommended_plans": LearningPlanListSerializer(plans[:3], many=True, context={"request": request}).data,
                    "stats": {"completed_days": 0, "open_gaps": 0, "evidence_count": 0, "streak": activity["current_streak"]},
                    "activity": activity,
                }
            )

        current = progress_for(enrollment, enrollment.current_day)
        completed_numbers = set(
            enrollment.progress.filter(status=DayProgress.Status.COMPLETED).values_list("plan_day__day_number", flat=True)
        )
        activity = activity_summary(request.user)
        upcoming = enrollment.plan.days.filter(day_number__gt=enrollment.current_day)[:PREVIEW_DAYS]
        last_activity = enrollment.last_studied_at or enrollment.started_at
        days_away = max((timezone.localdate() - timezone.localtime(last_activity).date()).days, 0)
        return Response(
            {
                "enrollment": EnrollmentSerializer(enrollment, context={"request": request}).data,
                "enrollments": EnrollmentSerializer(enrollments, many=True, context={"request": request}).data,
                "current_progress": DayProgressSerializer(current, context={"request": request}).data,
                "upcoming": [
                    {
                        "day_number": day.day_number,
                        "title": day.title,
                        "week_title": day.week_title,
                        "core_knowledge": day.core_knowledge,
                        "estimated_minutes": day.estimated_minutes,
                    }
                    for day in upcoming
                ],
                "stats": {
                    "completed_days": len(completed_numbers),
                    "open_gaps": Gap.objects.filter(progress__enrollment=enrollment, status=Gap.Status.OPEN).count(),
                    "evidence_count": Evidence.objects.filter(progress__enrollment=enrollment).count(),
                    "streak": activity["current_streak"],
                },
                "activity": activity,
                "rescue": {
                    "days_away": days_away,
                    "title": f"用 25 分钟回到 Day {enrollment.current_day}",
                    "steps": ["回忆上次完成的一个结论", "重新运行上次保留的代码或测试", "只完成当前任务的最小输入与输出"],
                } if days_away >= 3 and enrollment.status != Enrollment.Status.COMPLETED else None,
            }
        )


class LearningPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """提供登录用户可见的学习路线及其只读学习内容。"""

    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticated]

    def is_site_admin(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_queryset(self):
        # 管理员在详情类操作上始终能看到全部路线（含草稿与未发布）；
        # 列表只有显式 scope=all 时才放开，否则 /plans 页面会混进别人的草稿。
        if self.is_site_admin() and (self.action != "list" or self.request.query_params.get("scope") == "all"):
            return LearningPlan.objects.all().select_related("creator", "forked_from").prefetch_related("days", "feedback")
        visible = Q(is_published=True, review_status=LearningPlan.ReviewStatus.APPROVED)
        if self.request.user.is_authenticated:
            visible |= Q(creator=self.request.user)
        return LearningPlan.objects.filter(visible).select_related("creator", "forked_from").prefetch_related("days", "feedback").distinct()

    def get_serializer_class(self):
        return LearningPlanDetailSerializer if self.action == "retrieve" else LearningPlanListSerializer

    @action(detail=True, methods=["get"])
    def day(self, request, slug=None):
        """单个学习日的完整内容。学习者可以预习未来 PREVIEW_DAYS 天，管理员不受限制。

        只读：不会创建 DayProgress，也不会推进任何进度。
        """
        plan = self.get_object()
        try:
            number = int(request.query_params.get("number", ""))
        except (TypeError, ValueError):
            return Response({"detail": "Day参数无效。"}, status=400)
        if number < 1 or number > plan.total_days:
            return Response({"detail": "Day超出学习计划范围。"}, status=400)

        preview_limit = None
        if not self.is_site_admin():
            enrollment = joined_enrollments(request.user).filter(plan=plan).first()
            if not enrollment:
                return Response({"detail": "加入这条学习路线后才能查看每日内容。"}, status=403)
            preview_limit = enrollment.current_day + PREVIEW_DAYS
            if number > preview_limit:
                return Response(
                    {"detail": f"最多只能预习到 Day {preview_limit}，请先完成当前学习日。"}, status=403
                )
        day = get_object_or_404(PlanDay, plan=plan, day_number=number)
        return Response({
            "day": PlanDaySerializer(day).data,
            "read_only": True,
            "preview_limit": preview_limit,
        })

    @action(detail=True, methods=["post"])
    def enroll(self, request, slug=None):
        plan = self.get_object()
        if not plan.is_published and plan.creator_id != request.user.id:
            return Response({"detail": "该学习计划尚未发布。"}, status=403)
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, plan=plan)
        update_fields = ["last_studied_at"]
        enrollment.last_studied_at = timezone.now()
        if not created and enrollment.status in (Enrollment.Status.PAUSED, Enrollment.Status.WITHDRAWN):
            enrollment.status = Enrollment.Status.ACTIVE
            update_fields.append("status")
        enrollment.save(update_fields=update_fields)
        progress_for(enrollment, enrollment.current_day)
        return Response(EnrollmentSerializer(enrollment, context={"request": request}).data, status=201 if created else 200)

    @action(detail=True, methods=["post"])
    def feedback(self, request, slug=None):
        plan = self.get_object()
        # 退出过的学习者也可以留下反馈：他们的离开原因同样值得记录。
        if not plan.enrollments.filter(user=request.user).exists():
            return Response({"detail": "加入并体验该路线后才能提交反馈。"}, status=403)
        instance = PlanFeedback.objects.filter(user=request.user, plan=plan).first()
        serializer = PlanFeedbackSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, plan=plan)
        return Response(serializer.data, status=200 if instance else 201)

    @action(detail=True, methods=["post"])
    def fork(self, request, slug=None):
        source = self.get_object()
        if not source.is_published:
            return Response({"detail": "只能复制已经公开的学习路线。"}, status=400)
        title = str(request.data.get("title", f"{source.title} · 我的版本")).strip()
        fork_note = str(request.data.get("fork_note", "")).strip()
        if not title:
            return Response({"title": ["路线名称不能为空。"]}, status=400)
        if len(title) > 160:
            return Response({"title": ["路线名称不能超过160个字符。"]}, status=400)
        if len(fork_note) > 240:
            return Response({"fork_note": ["调整说明不能超过240个字符。"]}, status=400)
        with transaction.atomic():
            plan = LearningPlan.objects.create(
                creator=request.user,
                forked_from=source,
                fork_note=fork_note,
                slug=f"custom-{request.user.id}-{timezone.now():%Y%m%d%H%M%S%f}",
                title=title,
                subtitle=source.subtitle,
                summary=source.summary,
                audience=source.audience,
                total_days=source.total_days,
                estimated_weeks=source.estimated_weeks,
                is_published=False,
                review_status=LearningPlan.ReviewStatus.DRAFT,
            )
            PlanDay.objects.bulk_create([
                PlanDay(
                    plan=plan, day_number=day.day_number, phase=day.phase, week_number=day.week_number,
                    week_title=day.week_title, title=day.title, core_knowledge=day.core_knowledge,
                    hands_on_task=day.hands_on_task, acceptance_criteria=day.acceptance_criteria,
                    estimated_minutes=day.estimated_minutes, content=day.content,
                    reference_answer=day.reference_answer, commands=day.commands,
                    community_supplements=day.community_supplements,
                ) for day in source.days.all()
            ])
        return Response(CustomLearningPlanSerializer(plan, context={"request": request}).data, status=201)


class LearningInsightsView(APIView):
    """汇总用户跨路线的知识掌握与缺口数据。"""

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related("plan").prefetch_related(
            "progress__plan_day", "progress__gaps", "progress__evidence"
        )
        plans = []
        repeated = {}
        for enrollment in enrollments:
            progress_items = list(enrollment.progress.all())
            gaps = [gap for progress in progress_items for gap in progress.gaps.all()]
            completed = sum(item.status == DayProgress.Status.COMPLETED for item in progress_items)
            learned = sum(sum(bool(value) for value in item.knowledge_checks) for item in progress_items)
            knowledge_total = sum(item.plan_day.knowledge_count() for item in progress_items)
            scores = [item.recall_score for item in progress_items if item.recall_score is not None]
            plan_gaps = []
            for gap in gaps:
                key = gap.title.strip().casefold()
                repeated.setdefault(key, {"title": gap.title.strip(), "count": 0, "open_count": 0})
                repeated[key]["count"] += 1
                repeated[key]["open_count"] += gap.status == Gap.Status.OPEN
                plan_gaps.append({
                    "id": gap.id, "title": gap.title, "detail": gap.detail, "status": gap.status,
                    "day_number": gap.progress.plan_day.day_number, "day_title": gap.progress.plan_day.title,
                })
            plans.append({
                "enrollment_id": enrollment.id, "slug": enrollment.plan.slug, "title": enrollment.plan.title,
                "status": enrollment.status,
                "current_day": enrollment.current_day, "total_days": enrollment.plan.total_days,
                "completed_days": completed, "knowledge_learned": learned, "knowledge_total": knowledge_total,
                "average_recall": round(sum(scores) / len(scores)) if scores else None,
                "open_gaps": sum(gap.status == Gap.Status.OPEN for gap in gaps), "gaps": plan_gaps,
            })
        return Response({
            "summary": {
                "plans": len(plans), "completed_days": sum(item["completed_days"] for item in plans),
                "knowledge_learned": sum(item["knowledge_learned"] for item in plans),
                "open_gaps": sum(item["open_gaps"] for item in plans),
            },
            "repeated_gaps": sorted(repeated.values(), key=lambda item: (-item["count"], item["title"])),
            "plans": plans,
        })


class ReviewCenterView(APIView):
    """提供间隔复习队列、复习提交以及实时成长信息。"""

    def get(self, request):
        """返回当前学习者的到期任务、近期任务和成长状态。"""
        return Response({
            "reviews": review_center(request.user),
            "growth": growth_summary(request.user),
        })

    def post(self, request):
        """记录一次复习结果并返回新安排。"""
        # 进度字段使用行锁防止并发重复复习，校验和写入必须处于同一事务。
        with transaction.atomic():
            serializer = ReviewAttemptSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            attempt = serializer.save()
        return Response(
            {
                "attempt": ReviewAttemptSerializer(attempt, context={"request": request}).data,
                "reviews": review_center(request.user),
                "growth": growth_summary(request.user),
            },
            status=status.HTTP_201_CREATED,
        )


class LearningExportView(APIView):
    """导出当前用户的 Markdown 或 JSON 学习记录。"""

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related("plan").prefetch_related(
            "progress__plan_day", "progress__evidence", "progress__gaps"
        )
        records = []
        for enrollment in enrollments:
            days = []
            for progress in enrollment.progress.all():
                days.append({
                    "day": progress.plan_day.day_number, "title": progress.plan_day.title, "status": progress.status,
                    "reflection": progress.reflection, "recall_score": progress.recall_score,
                    "evidence": [{"kind": item.kind, "title": item.title, "content": item.content, "url": item.url} for item in progress.evidence.all()],
                    "gaps": [{"title": item.title, "detail": item.detail, "status": item.status, "resolution": item.resolution} for item in progress.gaps.all()],
                })
            records.append({"plan": enrollment.plan.title, "slug": enrollment.plan.slug, "status": enrollment.status, "current_day": enrollment.current_day, "days": days})
        export_format = request.query_params.get("type", "markdown")
        if export_format == "json":
            content = json.dumps({"user": request.user.username, "exported_at": timezone.now().isoformat(), "learning_records": records}, ensure_ascii=False, indent=2)
            return Response({"filename": "zhixu-learning-records.json", "mime": "application/json", "content": content})
        lines = [f"# {request.user.first_name or request.user.username} 的学习记录", ""]
        for record in records:
            lines.extend([f"## {record['plan']}", f"当前进度：Day {record['current_day']} · {record['status']}", ""])
            for day in record["days"]:
                lines.extend([f"### Day {day['day']} · {day['title']}", f"- 状态：{day['status']}", f"- 闭卷掌握度：{day['recall_score'] if day['recall_score'] is not None else '未记录'}", f"- 复盘：{day['reflection'] or '未记录'}"])
                if day["gaps"]:
                    lines.append("- 知识缺口：" + "；".join(item["title"] for item in day["gaps"]))
                if day["evidence"]:
                    lines.append("- 学习证据：" + "；".join(item["title"] for item in day["evidence"]))
                lines.append("")
        return Response({"filename": "zhixu-learning-records.md", "mime": "text/markdown;charset=utf-8", "content": "\n".join(lines)})


class ContributionView(APIView):
    """汇总当前用户的学习社区贡献。"""

    def get(self, request):
        items = Contribution.objects.filter(user=request.user)
        counts = {key: items.filter(kind=key).count() for key, _ in Contribution.Kind.choices}
        return Response({"total": items.count(), "counts": counts, "items": ContributionSerializer(items, many=True).data})


class CustomLearningPlanViewSet(viewsets.ModelViewSet):
    """管理当前用户创建的学习路线。"""

    serializer_class = CustomLearningPlanSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return LearningPlan.objects.filter(creator=self.request.user).select_related("creator").prefetch_related("days")

    def perform_destroy(self, instance):
        if instance.is_published:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("已公开的学习路线不能删除。")
        instance.delete()

    def update(self, request, *args, **kwargs):
        if not self.get_object().is_editable:
            return Response({"detail": "待审核、已发布或已经开始学习的计划不能修改。"}, status=400)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def enroll(self, request, slug=None):
        plan = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, plan=plan)
        enrollment.last_studied_at = timezone.now()
        update_fields = ["last_studied_at"]
        if not created and enrollment.status in (Enrollment.Status.PAUSED, Enrollment.Status.WITHDRAWN):
            enrollment.status = Enrollment.Status.ACTIVE
            update_fields.append("status")
        enrollment.save(update_fields=update_fields)
        progress_for(enrollment, enrollment.current_day)
        return Response(EnrollmentSerializer(enrollment, context={"request": request}).data, status=201 if created else 200)

    @action(detail=True, methods=["post"])
    def submit(self, request, slug=None):
        plan = self.get_object()
        if plan.review_status not in (LearningPlan.ReviewStatus.DRAFT, LearningPlan.ReviewStatus.REJECTED):
            return Response({"detail": "当前状态不能重复提交审核。"}, status=400)
        if not plan.days.exists():
            return Response({"detail": "学习路线至少需要一天。"}, status=400)
        plan.review_status = LearningPlan.ReviewStatus.PENDING
        plan.review_note = ""
        plan.save(update_fields=["review_status", "review_note", "updated_at"])
        return Response(self.get_serializer(plan).data)


class EnrollmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """管理当前用户的路线报名与学习路径。"""

    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        # 管理员可以读任意用户的报名与逐日进度；写操作仍然只对本人开放。
        if self.request.user.is_staff:
            queryset = Enrollment.objects.all()
            user_id = self.request.query_params.get("user")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = joined_enrollments(self.request.user)
        return queryset.select_related("plan").annotate(
            completed_count=Count("progress", filter=Q(progress__status=DayProgress.Status.COMPLETED))
        ).order_by("-last_studied_at", "-started_at")

    def owned_or_denied(self):
        enrollment = self.get_object()
        if enrollment.user_id != self.request.user.id:
            return None, Response({"detail": "只能操作自己的学习路线。"}, status=403)
        return enrollment, None

    def perform_update(self, serializer):
        enrollment = serializer.save()
        if enrollment.status == Enrollment.Status.ACTIVE:
            enrollment.last_studied_at = timezone.now()
            enrollment.save(update_fields=["last_studied_at"])

    def update(self, request, *args, **kwargs):
        _, denied = self.owned_or_denied()
        return denied or super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """退出学习路线：软退出。

        学习进度、证据、附件和知识缺口全部保留，只把路线从学习面和小组成员身份中移除。
        重新加入同一条路线会回到退出时的 current_day。
        """
        enrollment, denied = self.owned_or_denied()
        if denied:
            return denied
        enrollment.status = Enrollment.Status.WITHDRAWN
        enrollment.save(update_fields=["status"])
        BuddyProfile.objects.filter(enrollment=enrollment).update(active=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def day(self, request, pk=None):
        enrollment, denied = self.owned_or_denied()
        if denied:
            return denied
        try:
            number = int(request.query_params.get("number", enrollment.current_day))
        except (TypeError, ValueError):
            return Response({"detail": "Day参数无效。"}, status=400)
        if number < 1 or number > enrollment.plan.total_days:
            return Response({"detail": "Day超出学习计划范围。"}, status=400)
        if number > enrollment.current_day:
            return Response(
                {"detail": "请先完成当前学习日，再进入后续内容。未来的学习日可以在学习路径中预习。"}, status=400
            )
        if enrollment.status == Enrollment.Status.PAUSED:
            return Response({"detail": "该学习路线已暂停，请先恢复路线。"}, status=400)
        return Response(DayProgressSerializer(progress_for(enrollment, number), context={"request": request}).data)

    @action(detail=True, methods=["get"])
    def days(self, request, pk=None):
        enrollment = self.get_object()
        states = {item.plan_day_id: item for item in enrollment.progress.all()}
        # 管理员不受预习窗口限制，任何路线的每一天都能直接打开。
        preview_limit = (
            enrollment.plan.total_days
            if request.user.is_staff
            else enrollment.current_day + PREVIEW_DAYS
        )
        payload = []
        plan_days = list(enrollment.plan.days.all())
        for index, day in enumerate(plan_days):
            progress = states.get(day.id)
            day.status = progress.status if progress else DayProgress.Status.NOT_STARTED
            day.progress_id = progress.id if progress else None
            day.previewable = enrollment.current_day < day.day_number <= preview_limit
            # 阶段的最后一天就是 Boss 节点；直接使用课程已有任务和验收标准，不复制挑战内容。
            day.is_boss = index == len(plan_days) - 1 or plan_days[index + 1].phase != day.phase
            payload.append(day)
        return Response(JourneyDaySerializer(payload, many=True).data)


class DayProgressViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """管理单日学习的开始、保存和完成状态。"""

    serializer_class = DayProgressSerializer

    def get_queryset(self):
        return DayProgress.objects.filter(enrollment__user=self.request.user).select_related(
            "enrollment", "plan_day", "plan_day__plan"
        ).prefetch_related("evidence", "gaps")

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        progress = self.get_object()
        if progress.enrollment.status == Enrollment.Status.PAUSED and progress.status != DayProgress.Status.COMPLETED:
            return Response({"detail": "该学习路线已暂停，请先恢复路线。"}, status=400)
        if progress.plan_day.day_number > progress.enrollment.current_day:
            return Response({"detail": "请先完成当前学习日，再进入后续内容。"}, status=400)
        progress.start()
        progress.enrollment.last_studied_at = timezone.now()
        progress.save(update_fields=["status", "started_at", "updated_at"])
        progress.enrollment.save(update_fields=["last_studied_at"])
        return Response(self.get_serializer(progress).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        with transaction.atomic():
            progress = self.get_queryset().select_for_update().get(pk=pk)
            if progress.status == DayProgress.Status.COMPLETED:
                return Response(self.get_serializer(progress).data)
            if progress.enrollment.status == Enrollment.Status.PAUSED:
                return Response({"detail": "该学习路线已暂停，请先恢复路线。"}, status=400)
            if progress.plan_day.day_number != progress.enrollment.current_day:
                return Response({"detail": "只能完成当前学习日。"}, status=400)
            errors = progress.completion_errors()
            if errors:
                return Response({"detail": errors}, status=400)
            progress.status = DayProgress.Status.COMPLETED
            progress.completed_at = timezone.now()
            progress.save(update_fields=["status", "completed_at", "updated_at"])

            enrollment = Enrollment.objects.select_for_update().get(pk=progress.enrollment_id)
            if progress.plan_day.day_number >= enrollment.current_day:
                if progress.plan_day.day_number >= enrollment.plan.total_days:
                    enrollment.status = Enrollment.Status.COMPLETED
                else:
                    enrollment.current_day = progress.plan_day.day_number + 1
                enrollment.last_studied_at = timezone.now()
                enrollment.save(update_fields=["status", "current_day", "last_studied_at"])
        return Response(self.get_serializer(progress).data)


class OwnedProgressChildMixin:
    """把证据和缺口写操作限制在当前用户的学习进度内。"""

    def get_progress(self):
        return get_object_or_404(DayProgress, pk=self.request.data.get("progress"), enrollment__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(progress=self.get_progress())


class EvidenceViewSet(OwnedProgressChildMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """管理当前用户学习进度下的学习证据。"""

    serializer_class = EvidenceSerializer
    throttle_scope = "upload"

    def get_queryset(self):
        return Evidence.objects.filter(progress__enrollment__user=self.request.user)


class GapViewSet(OwnedProgressChildMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """管理知识缺口及小队朋友验证流程。"""

    serializer_class = GapSerializer

    def get_queryset(self):
        if self.action == "verify":
            return Gap.objects.filter(
                status=Gap.Status.VERIFYING,
                verification_group__members=self.request.user,
            ).select_related("progress__enrollment__user", "progress__plan_day").distinct()
        return Gap.objects.filter(progress__enrollment__user=self.request.user)

    @action(detail=True, methods=["post"], url_path="request-verification")
    def request_verification(self, request, pk=None):
        """提交缺口解决说明，并通知同队朋友进行验证。"""
        gap = self.get_object()
        resolution = str(request.data.get("resolution", "")).strip()
        if not resolution:
            return Response({"resolution": ["请先填写具体解决过程。"]}, status=400)
        if not gap.progress.evidence.exists():
            return Response({"detail": "至少保留一份学习证据后才能申请朋友验证。"}, status=400)
        group_id = request.data.get("group")
        if group_id not in (None, ""):
            try:
                group_id = int(group_id)
            except (TypeError, ValueError):
                return Response({"group": ["学习小队参数无效。"]}, status=400)
        groups = StudyGroup.objects.annotate(member_count=Count("members", distinct=True)).filter(
            members=request.user
        )
        group = groups.filter(pk=group_id, member_count__gt=1).first() if group_id else groups.filter(
            member_count__gt=1
        ).first()
        if not group:
            return Response({"detail": "小队中还没有可以验证该缺口的朋友。"}, status=400)
        recipients = group.members.exclude(pk=request.user.id)
        gap.status = Gap.Status.VERIFYING
        gap.resolution = resolution
        gap.verification_note = ""
        gap.verification_requested_at = timezone.now()
        gap.verification_group = group
        gap.verified_by = None
        gap.verified_at = None
        gap.resolved_at = None
        gap.save(update_fields=[
            "status", "resolution", "verification_note", "verification_requested_at",
            "verification_group", "verified_by", "verified_at", "resolved_at",
        ])
        url = f"/team?group={group.id}&gap={gap.id}"
        for recipient in recipients:
            notify(
                recipient,
                Notification.Kind.GAP,
                "朋友提交了知识缺口验证",
                f"{request.user.first_name or request.user.username}：{gap.title}",
                url,
            )
        return Response(self.get_serializer(gap).data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """由同队且非缺口所有者的成员通过或退回验证。"""
        gap = self.get_object()
        owner = gap.progress.enrollment.user
        if owner.id == request.user.id:
            return Response({"detail": "不能验证自己的知识缺口。"}, status=400)
        approved = request.data.get("approved")
        note = str(request.data.get("note", "")).strip()
        if not isinstance(approved, bool):
            return Response({"approved": ["验证结果必须是布尔值。"]}, status=400)
        if not approved and not note:
            return Response({"note": ["退回时请说明还需要补充什么。"]}, status=400)
        now = timezone.now()
        gap.status = Gap.Status.RESOLVED if approved else Gap.Status.OPEN
        gap.verified_by = request.user
        gap.verification_note = note
        gap.verified_at = now
        gap.resolved_at = now if approved else None
        gap.save(update_fields=["status", "verified_by", "verification_note", "verified_at", "resolved_at"])
        notify(
            owner,
            Notification.Kind.GAP,
            "知识缺口验证已通过" if approved else "知识缺口验证需要补充",
            note or f"{request.user.first_name or request.user.username} 已确认你的解决过程。",
            f"/learn/{gap.progress.enrollment_id}/{gap.progress.plan_day.day_number}",
        )
        return Response(self.get_serializer(gap).data)
