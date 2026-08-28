"""进程健康检查和受保护媒体读取接口。"""

import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import FileResponse, HttpResponse
from django.utils.encoding import iri_to_uri
from django.utils.http import content_disposition_header
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import CommunityPostImage, Evidence
from .media import load_media_token

logger = logging.getLogger(__name__)


class LiveHealthView(APIView):
    """提供不依赖外部组件的进程存活探针。"""

    permission_classes = [permissions.AllowAny]
    throttle_classes = []

    def get(self, request):
        """返回 Web 进程存活状态。"""
        return Response({"status": "ok"})


class ReadyHealthView(APIView):
    """验证数据库和 Redis 可用后报告实例已就绪。"""

    permission_classes = [permissions.AllowAny]
    throttle_classes = []

    def get(self, request):
        """执行无业务写入的依赖检查，失败时返回 503。"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            cache.set("health:ready", "ok", 10)
            if cache.get("health:ready") != "ok":
                raise RuntimeError("cache round trip failed")
        except Exception:
            # 就绪探针不返回内部异常细节，具体根因只进入服务端日志。
            logger.exception("生产就绪检查失败")
            return Response({"status": "unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"status": "ok"})


class ProtectedMediaView(APIView):
    """验证短时签名后提供路线、社区和学习证据文件。"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        """验证令牌并以内联方式返回其唯一对应的文件。"""
        kind, object_id = load_media_token(token)
        file_field = self.get_file(kind, object_id)
        if not file_field or not file_field.name:
            return Response({"detail": "文件不存在。"}, status=404)
        content_type = mimetypes.guess_type(file_field.name)[0] or "application/octet-stream"
        filename = Path(file_field.name).name
        if settings.DEBUG:
            return FileResponse(file_field.open("rb"), content_type=content_type, filename=filename)
        response = HttpResponse(content_type=content_type)
        # 生产环境只允许 Nginx 的 internal location 响应真实文件，外部不能绕过签名接口。
        response["X-Accel-Redirect"] = iri_to_uri(f"/protected-media/{file_field.name}")
        response["Content-Disposition"] = content_disposition_header(False, filename)
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @staticmethod
    def get_file(kind, object_id):
        """按令牌声明的业务类型查找仍然存在的文件字段。"""
        lookups = {
            "community-image": (CommunityPostImage, "image"),
            "evidence": (Evidence, "attachment"),
        }
        model_and_field = lookups.get(kind)
        if not model_and_field:
            return None
        model, field_name = model_and_field
        instance = model.objects.filter(pk=object_id).only(field_name).first()
        return getattr(instance, field_name, None)
