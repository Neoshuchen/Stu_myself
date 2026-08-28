import logging
import re
import time
from uuid import uuid4


logger = logging.getLogger("learning.audit")

# 只接受便于日志检索的短请求编号，避免把任意请求头原样写入日志。
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
AUDITED_PREFIXES = ("/api/admin/", "/api/auth/", "/api/community/", "/api/evidence/", "/api/ai/")
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class SecurityAuditMiddleware:
    """为响应添加请求编号，并记录敏感写操作的脱敏审计信息。"""

    def __init__(self, get_response):
        """保存下游处理器；参数为 Django 提供的响应可调用对象。"""
        self.get_response = get_response

    def __call__(self, request):
        """处理请求并记录用户编号、路径、状态和耗时，不记录正文与令牌。"""
        supplied_id = request.META.get("HTTP_X_REQUEST_ID", "")
        request_id = supplied_id if REQUEST_ID_PATTERN.fullmatch(supplied_id) else uuid4().hex
        request.request_id = request_id
        started = time.monotonic()
        response = self.get_response(request)
        response["X-Request-ID"] = request_id

        # 只审计可能改变账号、管理数据、社区内容或附件的请求，避免普通读取淹没安全日志。
        if request.method not in SAFE_METHODS and request.path.startswith(AUDITED_PREFIXES):
            user = getattr(request, "user", None)
            logger.info(
                "audit request_id=%s user_id=%s method=%s path=%s status=%s duration_ms=%s",
                request_id,
                getattr(user, "pk", None),
                request.method,
                request.path,
                response.status_code,
                round((time.monotonic() - started) * 1000),
            )
        return response
