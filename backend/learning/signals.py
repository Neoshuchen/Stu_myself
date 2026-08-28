from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import CommunityPostImage, Evidence


def delete_field_file(field_file):
    """删除 FileField 指向的实际文件；空字段保持无操作。"""
    if field_file and field_file.name:
        field_file.storage.delete(field_file.name)


@receiver(post_delete, sender=Evidence)
def delete_evidence_attachment(sender, instance, **kwargs):
    """证据记录删除时同步删除附件，避免产生孤儿文件。"""
    delete_field_file(instance.attachment)


@receiver(post_delete, sender=CommunityPostImage)
def delete_community_image(sender, instance, **kwargs):
    """帖子图片记录被删除或级联删除时同步清理文件。"""
    delete_field_file(instance.image)
