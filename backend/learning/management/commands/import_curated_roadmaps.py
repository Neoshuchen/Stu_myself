from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from learning.models import LearningPlan, PlanDay
from learning.study.roadmap_catalog import SYSTEM_ROADMAPS


class Command(BaseCommand):
    help = "从版本化JSON导入全部系统学习路线；重复执行会更新而不会重复创建"

    def add_arguments(self, parser):
        parser.add_argument("--slug", choices=[plan["slug"] for plan in SYSTEM_ROADMAPS])
        parser.add_argument(
            "--force", action="store_true",
            help="连管理员在站点后台改过的学习日一起覆盖（默认跳过这些天）",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        catalogs = [plan for plan in SYSTEM_ROADMAPS if not options["slug"] or plan["slug"] == options["slug"]]
        if not catalogs:
            raise CommandError("没有匹配的学习路线。")

        for catalog in catalogs:
            days = catalog["days"]
            plan, _ = LearningPlan.objects.update_or_create(
                slug=catalog["slug"],
                defaults={
                    key: catalog[key]
                    for key in (
                        "title", "subtitle", "summary", "audience", "total_days", "estimated_weeks",
                        "accent_start", "accent_end",
                    )
                }
                | {
                    "creator": None,
                    "is_published": True,
                    "review_status": LearningPlan.ReviewStatus.APPROVED,
                    "review_note": "",
                },
            )
            # 管理员改过正文的学习日默认不动，避免把人工修改覆盖掉。
            edited = set()
            if not options["force"]:
                edited = set(
                    plan.days.exclude(content_edited_at=None).values_list("day_number", flat=True)
                )
            for item in days:
                if item["day_number"] in edited:
                    continue
                values = {
                    key: item[key]
                    for key in (
                        "phase", "week_number", "week_title", "title", "core_knowledge", "hands_on_task",
                        "acceptance_criteria", "estimated_minutes", "content",
                    )
                }
                if options["force"]:
                    values["content_edited_at"] = None
                PlanDay.objects.update_or_create(
                    plan=plan,
                    day_number=item["day_number"],
                    defaults=values,
                )
            obsolete_days = plan.days.exclude(day_number__in=[item["day_number"] for item in days])
            # 缩短系统路线时不得级联删除学习进度、社区讨论或课程改进记录。
            protected_days = obsolete_days.filter(
                Q(content_edited_at__isnull=False)
                | Q(progress__isnull=False)
                | Q(community_posts__isnull=False)
                | Q(course_suggestions__isnull=False)
            ).distinct()
            if protected_days.exists():
                numbers = ", ".join(map(str, protected_days.values_list("day_number", flat=True)[:10]))
                raise CommandError(f"{plan.slug} 待删除的 Day {numbers} 已有用户数据，请先迁移这些记录。")
            obsolete_days.delete()
            skipped = f"，跳过 {len(edited)} 天已手工编辑的正文（--force 可覆盖）" if edited else ""
            self.stdout.write(self.style.SUCCESS(f"{plan.title}：已导入 {len(days) - len(edited)} 天{skipped}"))
