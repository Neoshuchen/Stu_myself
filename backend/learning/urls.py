from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .ai.views import (
    AICredentialTestView,
    AIChatSessionViewSet,
    AIProviderCatalogView,
    AIProviderCredentialViewSet,
)
from .accounts.views import CsrfView, EmailCodeView, LoginView, LogoutView, MeView, RefreshView, RegisterView
from .administration.views import AdminUserViewSet, PlanReviewViewSet
from .collaboration.views import (
    BuddyProfileViewSet,
    CourseSuggestionViewSet,
    HelpSessionViewSet,
    NotificationViewSet,
    PeerReviewViewSet,
    StudyGroupViewSet,
    TeamChallengeViewSet,
    WeeklyContractViewSet,
)
from .community.views import CommunityCommentViewSet, CommunityPostViewSet, CommunityReportViewSet
from .study.views import (
    ContributionView,
    CustomLearningPlanViewSet,
    DashboardView,
    DayProgressViewSet,
    EnrollmentViewSet,
    EvidenceViewSet,
    GapViewSet,
    LearningExportView,
    LearningInsightsView,
    LearningPlanViewSet,
    MarkdownRoadmapPreviewView,
    ReviewCenterView,
)
from .system.views import LiveHealthView, ProtectedMediaView, ReadyHealthView

router = DefaultRouter()
router.register("plans", LearningPlanViewSet, basename="plan")
router.register("my-plans", CustomLearningPlanViewSet, basename="my-plan")
router.register("admin/plan-reviews", PlanReviewViewSet, basename="plan-review")
router.register("admin/users", AdminUserViewSet, basename="admin-user")
router.register("community/posts", CommunityPostViewSet, basename="community-post")
router.register("community/comments", CommunityCommentViewSet, basename="community-comment")
router.register("community/reports", CommunityReportViewSet, basename="community-report")
router.register("course-suggestions", CourseSuggestionViewSet, basename="course-suggestion")
router.register("peer-reviews", PeerReviewViewSet, basename="peer-review")
router.register("help-sessions", HelpSessionViewSet, basename="help-session")
router.register("buddy-profiles", BuddyProfileViewSet, basename="buddy-profile")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("progress", DayProgressViewSet, basename="progress")
router.register("evidence", EvidenceViewSet, basename="evidence")
router.register("gaps", GapViewSet, basename="gap")
router.register("study-groups", StudyGroupViewSet, basename="study-group")
router.register("team-challenges", TeamChallengeViewSet, basename="team-challenge")
router.register("weekly-contracts", WeeklyContractViewSet, basename="weekly-contract")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("ai/credentials", AIProviderCredentialViewSet, basename="ai-credential")
router.register("ai/chats", AIChatSessionViewSet, basename="ai-chat")

urlpatterns = [
    path("health/live/", LiveHealthView.as_view(), name="health_live"),
    path("health/ready/", ReadyHealthView.as_view(), name="health_ready"),
    path("media/<str:token>/", ProtectedMediaView.as_view(), name="protected_media"),
    path("auth/csrf/", CsrfView.as_view(), name="csrf"),
    path("auth/email-code/", EmailCodeView.as_view(), name="email_code"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("ai/providers/", AIProviderCatalogView.as_view(), name="ai-providers"),
    path("ai/credentials/test/", AICredentialTestView.as_view(), name="ai-credential-test"),
    path("my-plans/markdown-preview/", MarkdownRoadmapPreviewView.as_view(), name="markdown-roadmap-preview"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("insights/export/", LearningExportView.as_view(), name="learning_export"),
    path("insights/", LearningInsightsView.as_view(), name="insights"),
    path("reviews/", ReviewCenterView.as_view(), name="reviews"),
    path("contributions/", ContributionView.as_view(), name="contributions"),
    path("", include(router.urls)),
]
