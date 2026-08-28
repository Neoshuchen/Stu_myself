from django.contrib import admin

from .models import BuddyProfile, CommunityComment, CommunityPost, CommunityReport, Contribution, CourseSuggestion, DayProgress, Enrollment, Evidence, Gap, HelpQuestion, HelpSession, LearningPlan, Notification, PeerReview, PlanDay, PlanFeedback, ReviewAttempt, StudyGroup, TeamChallenge, TeamChallengeEntry, WeeklyContract


class PlanDayInline(admin.TabularInline):
    model = PlanDay
    extra = 0
    fields = ("day_number", "week_number", "title", "estimated_minutes")
    show_change_link = True


@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    """管理路线元数据和审核状态。"""

    list_display = ("title", "creator", "total_days", "review_status", "is_published", "updated_at")
    list_filter = ("review_status", "is_published")
    search_fields = ("title", "summary")
    actions = ("approve_plans", "reject_plans")
    inlines = (PlanDayInline,)

    @admin.action(description="审核通过并发布")
    def approve_plans(self, request, queryset):
        queryset.update(review_status=LearningPlan.ReviewStatus.APPROVED, is_published=True, review_note="")

    @admin.action(description="退回修改")
    def reject_plans(self, request, queryset):
        queryset.update(review_status=LearningPlan.ReviewStatus.REJECTED, is_published=False)


@admin.register(PlanDay)
class PlanDayAdmin(admin.ModelAdmin):
    list_display = ("day_number", "title", "week_number", "plan")
    list_filter = ("plan", "phase", "week_number")
    search_fields = ("title", "core_knowledge", "hands_on_task")


admin.site.register(Enrollment)
admin.site.register(DayProgress)
admin.site.register(Evidence)
admin.site.register(Gap)
admin.site.register(PlanFeedback)
admin.site.register(Contribution)
admin.site.register(CourseSuggestion)
admin.site.register(PeerReview)
admin.site.register(HelpSession)
admin.site.register(HelpQuestion)
admin.site.register(BuddyProfile)
admin.site.register(ReviewAttempt)
admin.site.register(StudyGroup)
admin.site.register(TeamChallenge)
admin.site.register(TeamChallengeEntry)
admin.site.register(WeeklyContract)
admin.site.register(Notification)


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "post_type", "plan", "is_solved", "created_at")
    list_filter = ("post_type", "is_solved", "plan")
    search_fields = ("title", "content", "author__username")


@admin.register(CommunityComment)
class CommunityCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("content", "author__username", "post__title")


@admin.register(CommunityReport)
class CommunityReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "post", "comment", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reason",)
