from datetime import timedelta

from django.utils import timezone

from ..models import Contribution, DayProgress, Enrollment, Evidence, Gap, PlanDay, ReviewAttempt

LEVEL_XP = 500
INITIAL_REVIEW_DAYS = 3
LOW_RECALL_REVIEW_DAYS = 1
MAX_REVIEW_DAYS = 30


def activity_summary(user, days=28):
    """按学习日真实完成日期计算日历、当前连续天数和最长连续天数。"""
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    completed_at = DayProgress.objects.filter(
        enrollment__user=user,
        status=DayProgress.Status.COMPLETED,
        completed_at__isnull=False,
    ).values_list("completed_at", flat=True)
    dates = [timezone.localtime(value).date() for value in completed_at]
    active_dates = set(dates)
    recent_counts = {}
    for value in dates:
        if value >= start:
            recent_counts[value] = recent_counts.get(value, 0) + 1

    # 当天尚未完成时从昨天开始计算，避免白天查看页面就提前打断连续记录。
    cursor = today if today in active_dates else today - timedelta(days=1)
    current_streak = 0
    while cursor in active_dates:
        current_streak += 1
        cursor -= timedelta(days=1)

    # 最长连续天数只按去重后的自然日计算，同一天完成多条路线仍只算一天。
    longest_streak = 0
    running = 0
    previous = None
    for value in sorted(active_dates):
        running = running + 1 if previous and value == previous + timedelta(days=1) else 1
        longest_streak = max(longest_streak, running)
        previous = value

    week_start = today - timedelta(days=today.weekday())
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "this_week_active_days": sum(value >= week_start for value in active_dates),
        "last_active_date": max(active_dates).isoformat() if active_dates else None,
        "calendar": [
            {
                "date": (start + timedelta(days=offset)).isoformat(),
                "count": recent_counts.get(start + timedelta(days=offset), 0),
            }
            for offset in range(days)
        ],
    }


def boss_day_ids(plan_ids):
    """返回指定路线中每个连续阶段最后一个学习日的主键集合。"""
    result = set()
    previous = None
    for day_id, plan_id, phase in PlanDay.objects.filter(plan_id__in=plan_ids).order_by(
        "plan_id", "day_number"
    ).values_list("id", "plan_id", "phase"):
        if previous and previous[1:] != (plan_id, phase):
            result.add(previous[0])
        previous = (day_id, plan_id, phase)
    if previous:
        result.add(previous[0])
    return result


def review_interval_days(rating, previous_interval=0):
    """根据本次掌握结果和上次间隔计算下一次复习天数。"""
    if rating == ReviewAttempt.Rating.FORGOT:
        return 1
    if rating == ReviewAttempt.Rating.UNSURE:
        return max(3, min(previous_interval, 7))
    return min(MAX_REVIEW_DAYS, max(7, previous_interval * 2))


def record_review(progress, rating, note=""):
    """为已完成学习日记录复习，并安排下一次复习时间。"""
    previous = progress.review_attempts.order_by("-reviewed_at").first()
    interval = review_interval_days(rating, previous.interval_days if previous else 0)
    return ReviewAttempt.objects.create(
        progress=progress,
        rating=rating,
        note=note.strip(),
        interval_days=interval,
        next_review_at=timezone.now() + timedelta(days=interval),
    )


def review_due_at(progress):
    """返回某个已完成学习日当前一次复习应到期的时间。"""
    latest = progress.review_attempts.order_by("-reviewed_at").first()
    if latest:
        return latest.next_review_at
    open_gaps = progress.gaps.filter(status=Gap.Status.OPEN).exists()
    initial_days = (
        LOW_RECALL_REVIEW_DAYS
        if open_gaps or progress.recall_score is None or progress.recall_score < 80
        else INITIAL_REVIEW_DAYS
    )
    return (progress.completed_at or progress.updated_at) + timedelta(days=initial_days)


def growth_summary(user):
    """基于已有学习事实实时计算经验、等级和徽章，避免维护重复积分状态。"""
    progress = DayProgress.objects.filter(enrollment__user=user)
    completed = progress.filter(status=DayProgress.Status.COMPLETED).count()
    evidence = Evidence.objects.filter(progress__enrollment__user=user).count()
    resolved_gaps = Gap.objects.filter(
        progress__enrollment__user=user, status=Gap.Status.RESOLVED
    ).count()
    reviews = ReviewAttempt.objects.filter(progress__enrollment__user=user).count()
    mastered_reviews = ReviewAttempt.objects.filter(
        progress__enrollment__user=user, rating=ReviewAttempt.Rating.MASTERED
    ).count()
    contributions = Contribution.objects.filter(user=user).count()
    plan_ids = Enrollment.objects.filter(user=user).values_list("plan_id", flat=True)
    completed_bosses = progress.filter(
        status=DayProgress.Status.COMPLETED, plan_day_id__in=boss_day_ids(plan_ids)
    ).count()

    xp = completed * 100 + evidence * 20 + resolved_gaps * 40 + reviews * 30 + contributions * 50
    level = xp // LEVEL_XP + 1
    badge_specs = (
        ("first_step", "迈出第一步", "完成第 1 个学习日", completed, 1),
        ("steady_week", "稳定一周", "累计完成 7 个学习日", completed, 7),
        ("evidence_keeper", "证据收藏家", "累计提交 10 份学习证据", evidence, 10),
        ("gap_breaker", "破障者", "解决 5 个知识缺口", resolved_gaps, 5),
        ("recall_master", "记忆锻造师", "完成 5 次熟练掌握复习", mastered_reviews, 5),
        ("boss_slayer", "阶段征服者", "完成 1 次阶段 Boss 挑战", completed_bosses, 1),
    )
    badges = [
        {
            "key": key,
            "name": name,
            "description": description,
            "unlocked": current >= target,
            "progress": min(current, target),
            "target": target,
        }
        for key, name, description, current, target in badge_specs
    ]
    return {
        "xp": xp,
        "level": level,
        "level_xp": xp % LEVEL_XP,
        "next_level_xp": LEVEL_XP,
        "completed_bosses": completed_bosses,
        "review_count": reviews,
        "badges": badges,
        "xp_rules": {
            "completed_day": 100,
            "evidence": 20,
            "resolved_gap": 40,
            "review": 30,
            "contribution": 50,
        },
    }


def review_center(user):
    """生成当前用户的到期复习队列和最近即将到期项目。"""
    now = timezone.now()
    progress_items = DayProgress.objects.filter(
        enrollment__user=user,
        enrollment__status__in=Enrollment.JOINED_STATUSES,
        status=DayProgress.Status.COMPLETED,
    ).select_related("enrollment__plan", "plan_day").prefetch_related("gaps", "review_attempts")
    items = []
    for progress in progress_items:
        attempts = list(progress.review_attempts.all())
        latest = attempts[0] if attempts else None
        open_gaps = sum(gap.status == Gap.Status.OPEN for gap in progress.gaps.all())
        initial_days = (
            LOW_RECALL_REVIEW_DAYS
            if open_gaps or progress.recall_score is None or progress.recall_score < 80
            else INITIAL_REVIEW_DAYS
        )
        due_at = latest.next_review_at if latest else (
            progress.completed_at or progress.updated_at
        ) + timedelta(days=initial_days)
        if open_gaps:
            reason = "仍有未解决的知识缺口"
        elif progress.recall_score is None:
            reason = "尚未验证闭卷掌握度"
        elif progress.recall_score < 80:
            reason = "闭卷掌握度偏低"
        else:
            reason = "间隔复习时间已安排"
        items.append({
            "progress_id": progress.id,
            "enrollment_id": progress.enrollment_id,
            "plan_title": progress.enrollment.plan.title,
            "day_number": progress.plan_day.day_number,
            "day_title": progress.plan_day.title,
            "phase": progress.plan_day.phase,
            "core_knowledge": progress.plan_day.core_knowledge,
            "recall_score": progress.recall_score,
            "open_gaps": open_gaps,
            "review_count": len(attempts),
            "latest_rating": latest.rating if latest else None,
            "due_at": due_at,
            "due": due_at <= now,
            "reason": reason,
        })
    items.sort(key=lambda item: (not item["due"], item["due_at"]))
    due = [item for item in items if item["due"]]
    upcoming = [item for item in items if not item["due"]][:5]
    return {
        "due_count": len(due),
        "due": due,
        "upcoming": upcoming,
        "ratings": [
            {"value": value, "label": label}
            for value, label in ReviewAttempt.Rating.choices
        ],
    }
