from django.apps import AppConfig


class LearningConfig(AppConfig):
    """配置学习中心应用并加载文件生命周期信号。"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "learning"
    verbose_name = "学习中心"

    def ready(self):
        """在 Django 完成模型加载后注册附件清理信号。"""
        from . import signals  # noqa: F401
