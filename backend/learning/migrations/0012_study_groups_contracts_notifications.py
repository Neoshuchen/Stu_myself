import django.core.validators
import django.db.models.deletion
import learning.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0011_reviewattempt"),
    ]

    operations = [
        migrations.AddField(
            model_name="gap",
            name="verification_note",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name="gap",
            name="verification_requested_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gap",
            name="verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gap",
            name="verified_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="verified_gaps",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="gap",
            name="status",
            field=models.CharField(
                choices=[("open", "待解决"), ("verifying", "等待验证"), ("resolved", "已解决")],
                default="open",
                max_length=12,
            ),
        ),
        migrations.CreateModel(
            name="StudyGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("invite_code", models.CharField(default=learning.models.generate_invite_code, max_length=12, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("members", models.ManyToManyField(blank=True, related_name="study_groups", to=settings.AUTH_USER_MODEL)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_study_groups", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="gap",
            name="verification_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="gap_verifications",
                to="learning.studygroup",
            ),
        ),
        migrations.CreateModel(
            name="WeeklyContract",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("week_start", models.DateField(default=learning.models.current_week_start)),
                (
                    "target_days",
                    models.PositiveSmallIntegerField(
                        default=3,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(7),
                        ],
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=240)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("enrollment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="weekly_contracts", to="learning.enrollment")),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contracts", to="learning.studygroup")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="weekly_contracts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-week_start", "user__username"],
                "constraints": [
                    models.UniqueConstraint(fields=("group", "user", "week_start"), name="unique_group_week_contract")
                ],
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("community", "社区互动"),
                            ("review", "同伴互评"),
                            ("help", "公开答疑"),
                            ("course", "课程共建"),
                            ("gap", "缺口验证"),
                            ("system", "系统通知"),
                        ],
                        default="system",
                        max_length=16,
                    ),
                ),
                ("title", models.CharField(max_length=160)),
                ("body", models.CharField(blank=True, max_length=300)),
                ("url", models.CharField(blank=True, max_length=240)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["user", "read_at", "-created_at"], name="notice_user_unread_idx")],
            },
        ),
    ]
