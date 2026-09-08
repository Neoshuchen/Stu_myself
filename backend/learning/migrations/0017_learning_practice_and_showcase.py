from django.db import migrations, models


class Migration(migrations.Migration):
    """为接续提示、客观复习快照和私人成果选择增加带默认值的字段。"""

    dependencies = [("learning", "0016_ai_multiple_user_credentials")]

    operations = [
        migrations.AddField(
            model_name="dayprogress", name="resume_note",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="reviewattempt", name="quiz_results",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="evidence", name="is_featured",
            field=models.BooleanField(default=False),
        ),
    ]
