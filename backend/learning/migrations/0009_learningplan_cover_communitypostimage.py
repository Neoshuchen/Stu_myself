import django.db.models.deletion
import learning.models
from django.db import migrations, models


class Migration(migrations.Migration):
    """为学习路线封面和社区帖子图片增加持久化字段。"""

    dependencies = [("learning", "0008_planday_content_edited_at")]

    operations = [
        migrations.AddField(
            model_name="learningplan",
            name="cover_alt",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="learningplan",
            name="cover_image",
            field=models.ImageField(blank=True, upload_to="plan-covers/%Y/%m/"),
        ),
        migrations.CreateModel(
            name="CommunityPostImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to=learning.models.community_image_upload_path)),
                ("alt_text", models.CharField(blank=True, max_length=160)),
                ("width", models.PositiveSmallIntegerField()),
                ("height", models.PositiveSmallIntegerField()),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="learning.communitypost",
                    ),
                ),
            ],
            options={"ordering": ["position", "id"]},
        ),
    ]
