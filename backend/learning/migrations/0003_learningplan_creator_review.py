from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0002_dayprogress_knowledge_checks"),
    ]

    operations = [
        migrations.AddField(
            model_name="learningplan",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_learning_plans",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="learningplan",
            name="review_note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="learningplan",
            name="review_status",
            field=models.CharField(
                choices=[
                    ("draft", "草稿"),
                    ("pending", "待审核"),
                    ("approved", "审核通过"),
                    ("rejected", "审核退回"),
                ],
                default="approved",
                max_length=12,
            ),
        ),
    ]
