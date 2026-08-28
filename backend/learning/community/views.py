"""学习社区帖子、评论、互动和举报接口。"""

from django.db.models import Count, Q
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import CommunityComment, CommunityPost, CommunityReport, Enrollment, Notification
from ..services import notify
from .serializers import (
    CommunityCommentSerializer,
    CommunityPostListSerializer,
    CommunityPostSerializer,
    CommunityReportSerializer,
)


def visible_community_posts(user):
    visible = Q(plan__isnull=True)
    if user.is_authenticated:
        visible |= Q(plan__enrollments__user=user, plan__enrollments__status__in=Enrollment.JOINED_STATUSES)
        if user.is_staff:
            return CommunityPost.objects.all()
    return CommunityPost.objects.filter(visible).distinct()


class CommunityPostViewSet(viewsets.ModelViewSet):
    """提供登录用户可见的社区帖子及其互动操作。"""

    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_throttles(self):
        """仅对社区写操作叠加严格限流，读取仍使用全局用户限额。"""
        self.throttle_scope = "community_write" if self.action in {"create", "update", "partial_update", "destroy"} else None
        return super().get_throttles()

    def get_serializer_class(self):
        return CommunityPostListSerializer if self.action == "list" else CommunityPostSerializer

    def get_queryset(self):
        queryset = visible_community_posts(self.request.user).select_related(
            "author", "plan", "plan_day"
        ).prefetch_related("comments__author", "images").annotate(
            like_count=Count("likes", distinct=True), comment_count=Count("comments", distinct=True)
        )
        plan_slug = self.request.query_params.get("plan")
        post_type = self.request.query_params.get("type")
        day_number = self.request.query_params.get("day")
        scope = self.request.query_params.get("scope")
        if plan_slug:
            queryset = queryset.filter(plan__slug=plan_slug)
        elif scope == "global":
            queryset = queryset.filter(plan__isnull=True)
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        if day_number:
            queryset = queryset.filter(plan_day__day_number=day_number)
        if self.request.query_params.get("solved") == "false":
            queryset = queryset.filter(post_type=CommunityPost.Type.QUESTION, is_solved=False)
        if self.request.query_params.get("sort") == "hot":
            return queryset.order_by("-like_count", "-comment_count", "-created_at")
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "只能修改自己的帖子。"}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "只能删除自己的帖子。"}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = post.likes.get_or_create(user=request.user)
        if not created:
            like.delete()
        return Response({"liked": created, "like_count": post.likes.count()})

    @action(detail=True, methods=["post"])
    def comments(self, request, pk=None):
        post = self.get_object()
        serializer = CommunityCommentSerializer(data=request.data, context={"request": request, "post": post})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(post=post, author=request.user)
        recipient = comment.parent.author if comment.parent_id else post.author
        if recipient.id != request.user.id:
            notify(
                recipient,
                Notification.Kind.COMMUNITY,
                "社区内容收到了新回复",
                post.title,
                f"/community/posts/{post.id}",
            )
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"])
    def solve(self, request, pk=None):
        post = self.get_object()
        if post.author_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "只有作者或管理员可以更新问题状态。"}, status=403)
        if post.post_type != CommunityPost.Type.QUESTION:
            return Response({"detail": "只有问题帖可以标记已解决。"}, status=400)
        post.is_solved = not post.is_solved
        post.save(update_fields=["is_solved", "updated_at"])
        return Response({"is_solved": post.is_solved})


class CommunityCommentViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """管理当前用户可见社区评论的修改和删除。"""

    serializer_class = CommunityCommentSerializer

    def get_queryset(self):
        visible_posts = visible_community_posts(self.request.user).values("pk")
        return CommunityComment.objects.filter(post_id__in=visible_posts).select_related("author", "post")

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "只能修改自己的评论。"}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "只能删除自己的评论。"}, status=403)
        return super().destroy(request, *args, **kwargs)


class CommunityReportViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """管理社区举报提交和管理员处理。"""

    serializer_class = CommunityReportSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = CommunityReport.objects.select_related(
            "reporter", "post", "post__author", "comment", "comment__author", "comment__post"
        )
        if self.action == "list":
            queryset = queryset.filter(status=CommunityReport.Status.PENDING)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user, status=CommunityReport.Status.PENDING)

