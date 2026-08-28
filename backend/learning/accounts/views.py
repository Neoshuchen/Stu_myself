"""账号注册、认证、会话和个人资料接口。"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .email_verification import EmailRateLimitError, EmailVerificationError, send_verification_code
from .serializers import EmailCodeRequestSerializer, ProfileUpdateSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


def token_payload(user):
    """创建新的浏览器会话载荷和对应刷新令牌。"""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "user": UserSerializer(user).data}, str(refresh)


def session_response(user, response_status=status.HTTP_200_OK):
    """返回短期访问令牌，并将刷新令牌限制在 HttpOnly Cookie 中。"""
    payload, refresh = token_payload(user)
    response = Response(payload, status=response_status)
    set_refresh_cookie(response, refresh)
    return response


def set_refresh_cookie(response, refresh):
    """使用统一安全属性写入浏览器刷新令牌 Cookie。"""
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE,
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    """创建已完成邮箱验证的用户，并建立安全浏览器会话。"""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"

    @transaction.atomic
    def post(self, request):
        """校验注册资料，创建用户并返回访问令牌。"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return session_response(serializer.save(), status.HTTP_201_CREATED)


@method_decorator(csrf_protect, name="dispatch")
class EmailCodeView(APIView):
    """向未被占用的邮箱发送一次性注册或换绑验证码。"""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "email_code"

    def post(self, request):
        """发送受邮箱、来源 IP 和 DRF 多层限流保护的验证码。"""
        serializer = EmailCodeRequestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        client_ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")
        try:
            send_verification_code(serializer.validated_data["email"], client_ip)
        except EmailRateLimitError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except EmailVerificationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        detail = (
            "开发环境验证码已输出到后端终端。"
            if settings.EMAIL_BACKEND.endswith("console.EmailBackend") and not settings.TENCENT_SES_TEMPLATE_ID
            else "验证码已发送，请及时完成验证。"
        )
        return Response({"detail": detail})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """为同源前端设置可用于变更请求的 CSRF Cookie。"""

    permission_classes = [permissions.AllowAny]
    throttle_classes = []

    def get(self, request):
        """确保 CSRF Cookie 已生成并返回无敏感信息的响应。"""
        get_token(request)
        return Response({"detail": "CSRF cookie ready."})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(TokenObtainPairView):
    """校验账号密码，将刷新令牌写入 HttpOnly Cookie。"""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        """返回短期访问令牌，避免向 JavaScript 暴露刷新令牌。"""
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", "")
        if refresh:
            set_refresh_cookie(response, refresh)
        return response


@method_decorator(csrf_protect, name="dispatch")
class RefreshView(TokenRefreshView):
    """使用 HttpOnly Cookie 轮换刷新令牌并返回新访问令牌。"""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "token_refresh"

    def post(self, request, *args, **kwargs):
        """验证刷新 Cookie；轮换成功后拉黑旧令牌并重写 Cookie。"""
        refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE, "")
        serializer = self.get_serializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            # 自定义 Cookie 刷新流程绕过了 SimpleJWT 视图的这层转换，旧令牌也必须稳定返回 401。
            raise InvalidToken(exc.args[0]) from exc
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        rotated = response.data.pop("refresh", "")
        if rotated:
            set_refresh_cookie(response, rotated)
        return response


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    """撤销当前浏览器刷新令牌并清除认证 Cookie。"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """将存在的刷新令牌加入黑名单；重复退出保持幂等。"""
        refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE, "")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                # 已过期、已拉黑或格式错误的 Cookie 都按“已退出”处理，避免泄露令牌状态。
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            settings.AUTH_REFRESH_COOKIE,
            path=settings.AUTH_REFRESH_COOKIE_PATH,
            samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        )
        return response


class MeView(APIView):
    """读取或更新当前登录用户资料。"""

    def get(self, request):
        """返回当前登录用户的公开资料。"""
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        """更新资料；密码变更后签发新的安全浏览器会话。"""
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        password_changed = bool(serializer.validated_data.get("new_password"))
        user = serializer.save()
        return session_response(user) if password_changed else Response(UserSerializer(user).data)
