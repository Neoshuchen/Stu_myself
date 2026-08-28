from django.db import migrations


class Migration(migrations.Migration):
    """移除不属于本阶段需求的学习路线封面字段。"""

    dependencies = [("learning", "0009_learningplan_cover_communitypostimage")]

    operations = [
        migrations.RemoveField(model_name="learningplan", name="cover_alt"),
        migrations.RemoveField(model_name="learningplan", name="cover_image"),
    ]
