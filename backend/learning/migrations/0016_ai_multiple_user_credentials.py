import django.db.models.deletion
from django.db import migrations, models


def name_existing_credentials(apps, schema_editor):
    """为升级前每用户每供应商唯一的凭据补充可识别名称。"""
    credential = apps.get_model("learning", "AIProviderCredential")
    credential.objects.filter(provider="openai").update(name="OpenAI 配置")
    credential.objects.filter(provider="anthropic").update(name="Anthropic 配置")


class Migration(migrations.Migration):
    """允许用户保存多个模型服务，并把新会话绑定到具体凭据。"""

    dependencies = [
        ("learning", "0015_ai_endpoint_configuration"),
    ]

    operations = [
        migrations.AddField(
            model_name="aiprovidercredential",
            name="name",
            field=models.CharField(default="模型配置", max_length=80),
        ),
        migrations.RunPython(name_existing_credentials, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name="aiprovidercredential",
            name="unique_user_ai_provider",
        ),
        migrations.AlterModelOptions(
            name="aiprovidercredential",
            options={"ordering": ["name", "id"]},
        ),
        migrations.AddField(
            model_name="aichatsession",
            name="credential",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="chat_sessions",
                to="learning.aiprovidercredential",
            ),
        ),
    ]
