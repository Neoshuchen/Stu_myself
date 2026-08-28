"""学习路线审核和用户治理接口。"""

import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import DayProgress, Enrollment, LearningPlan, PlanDay
from ..study.serializers import PlanDaySerializer
from .serializers import (
    AdminLearningPlanListSerializer,
    AdminLearningPlanSerializer,
    AdminPlanDayEditSerializer,
    AdminUserSerializer,
)

User = get_user_model()


class PlanReviewViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """站点管理员的路线管理：默认是审核队列，`?scope=all` 时是全部路线（含系统路线）。"""

    serializer_class = AdminLearningPlanSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "slug"

    def all_scope(self):
        return self.action == "list" and self.request.query_params.get("scope") == "all"

    def get_serializer_class(self):
        return AdminLearningPlanListSerializer if self.all_scope() else AdminLearningPlanSerializer

    def get_queryset(self):
        queryset = LearningPlan.objects.select_related("creator")
        if self.all_scope():
            # 全部路线可能有几百个学习日，列表里不带正文。
            return queryset.order_by("created_at")
        if self.action == "list":
            queryset = queryset.filter(review_status=LearningPlan.ReviewStatus.PENDING)
        return queryset.prefetch_related("days").order_by("created_at")

    def destroy(self, request, *args, **kwargs):
        """删除路线会连带删除全部学习进度和证据，因此有学习者时必须显式确认。"""
        plan = self.get_object()
        learners = plan.enrollments.filter(status__in=Enrollment.JOINED_STATUSES).count()
        if learners and request.query_params.get("confirm") != "1":
            return Response(
                {
                    "detail": f"这条路线还有 {learners} 位学习者，删除会一并清除他们的学习进度和证据。"
                    "确认删除请重试并带上 confirm=1，或改为下架。",
                    "learner_count": learners,
                },
                status=status.HTTP_409_CONFLICT,
            )
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get", "patch"])
    def day(self, request, slug=None):
        """管理员查看或编辑任意路线任意学习日的完整正文，不受学习进度限制。"""
        plan = self.get_object()
        try:
            number = int(request.query_params.get("number", 1))
        except (TypeError, ValueError):
            return Response({"detail": "Day参数无效。"}, status=400)
        day = get_object_or_404(PlanDay, plan=plan, day_number=number)
        if request.method == "PATCH":
            form = AdminPlanDayEditSerializer(day, data=request.data, partial=True)
            form.is_valid(raise_exception=True)
            day = form.save()
        return Response({
            "day": PlanDaySerializer(day).data,
            "read_only": request.method == "GET",
            "preview_limit": None,
            "content_edited_at": day.content_edited_at,
        })

    @action(detail=True, methods=["post"])
    def approve(self, request, slug=None):
        plan = self.get_object()
        if plan.review_status != LearningPlan.ReviewStatus.PENDING:
            return Response({"detail": "只能审核待审核状态的路线。"}, status=400)
        plan.review_status = LearningPlan.ReviewStatus.APPROVED
        plan.is_published = True
        plan.review_note = ""
        plan.save(update_fields=["review_status", "is_published", "review_note", "updated_at"])
        return Response(self.get_serializer(plan).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, slug=None):
        plan = self.get_object()
        if plan.review_status != LearningPlan.ReviewStatus.PENDING:
            return Response({"detail": "只能退回待审核状态的路线。"}, status=400)
        note = str(request.data.get("review_note", "")).strip()
        if not note:
            return Response({"review_note": ["退回路线时请填写修改意见。"]}, status=400)
        plan.review_status = LearningPlan.ReviewStatus.REJECTED
        plan.is_published = False
        plan.review_note = note
        plan.save(update_fields=["review_status", "is_published", "review_note", "updated_at"])
        return Response(self.get_serializer(plan).data)


class AdminUserViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """提供管理员用户查询、停用和删除能力。"""

    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return User.objects.annotate(
            enrollment_count=Count("enrollments", distinct=True),
            completed_days=Count(
                "enrollments__progress",
                filter=Q(enrollments__progress__status=DayProgress.Status.COMPLETED),
                distinct=True,
            ),
            last_studied_at=Max("enrollments__last_studied_at"),
        ).order_by("-date_joined")

    @action(detail=True, methods=["post"], url_path="set-active")
    def set_active(self, request, pk=None):
        user = self.get_object()
        is_active = request.data.get("is_active")
        if not isinstance(is_active, bool):
            return Response({"is_active": ["必须是布尔值。"]}, status=400)
        if user == request.user and not is_active:
            return Response({"detail": "不能停用当前管理员账号。"}, status=400)
        user.is_active = is_active
        user.save(update_fields=["is_active"])
        return Response(self.get_serializer(self.get_queryset().get(pk=user.pk)).data)

    def destroy(self, request, *args, **kwargs):
        """删除用户：连带清除他的全部学习与社区数据。

        报名、逐日进度、证据、缺口、帖子、评论、点赞、举报、互评、答疑、搭子资料都由
        数据库外键级联删除；证据附件按 `evidence/<user_id>/` 目录一起删掉。
        他创建的学习路线如果还有别人在学就保留（作者显示为“系统”），否则一并删除。
        """
        user = self.get_object()
        # 管理员账号只能在 Django 后台删除：先撤掉 is_staff 再删，避免管理员之间互删。
        if user.is_staff or user.is_superuser:
            return Response({"detail": "管理员账号不能在这里删除，请先在 Django 后台取消管理员权限。"}, status=400)
        created = LearningPlan.objects.filter(creator=user)
        kept = [
            plan.id
            for plan in created
            if plan.enrollments.filter(status__in=Enrollment.JOINED_STATUSES).exclude(user=user).exists()
        ]
        username = user.username
        user_id = user.pk
        with transaction.atomic():
            dropped = created.exclude(id__in=kept)
            dropped_count = dropped.count()
            dropped.delete()
            user.delete()
        # 附件不在事务里，删完数据库记录再清目录，避免回滚后文件已经没了。
        shutil.rmtree(Path(settings.MEDIA_ROOT) / "evidence" / str(user_id), ignore_errors=True)
        return Response(
            {
                "detail": f"已删除账号 {username}，其学习记录和社区内容一并清除。",
                "deleted_plans": dropped_count,
                "kept_plans": len(kept),
            }
        )

