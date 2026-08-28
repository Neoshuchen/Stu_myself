"""跨领域复用的学习成员查询与站内通知写入服务。"""

from .models import Enrollment, Notification


def notify(user, kind, title, body="", url=""):
    """为非空接收者写入一条站内通知并返回该记录。"""
    if not user:
        return None
    return Notification.objects.create(user=user, kind=kind, title=title, body=body, url=url)


def joined_enrollments(user):
    """用户仍然属于的报名记录。退出后的路线不再计入路线列表、小组成员和搭子匹配。"""
    return Enrollment.objects.filter(user=user, status__in=Enrollment.JOINED_STATUSES)
