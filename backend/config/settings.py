import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
TESTING = "test" in sys.argv
ENVIRONMENT = os.getenv("DJANGO_ENV", "development").strip().lower()
PRODUCTION = ENVIRONMENT == "production"


def _setting(name, default=""):
    """读取普通环境变量或其 ``_FILE`` 指向的 Docker secret。"""
    secret_file = os.getenv(f"{name}_FILE", "").strip()
    if secret_file:
        try:
            return Path(secret_file).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ImproperlyConfigured(f"无法读取 {name}_FILE：{secret_file}") from exc
    return os.getenv(name, default)

SECRET_KEY = _setting("DJANGO_SECRET_KEY", "dev-only-secret-key-with-at-least-thirty-two-bytes")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [item.strip() for item in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if item.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "learning",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "learning.middleware.SecurityAuditMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if PRODUCTION:
    # WhiteNoise 只服务收集后的生产静态文件；开发和测试由 Django/Vite 提供，避免空目录告警。
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

if os.getenv("USE_SQLITE") == "1" and TESTING:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_DATABASE", "zhixu"),
            "USER": os.getenv("MYSQL_USER", "zhixu"),
            "PASSWORD": _setting("MYSQL_PASSWORD", "change-me"),
            "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
            "PORT": os.getenv("MYSQL_PORT", "3306"),
            "CONN_MAX_AGE": int(os.getenv("MYSQL_CONN_MAX_AGE", "60" if PRODUCTION else "0")),
            "CONN_HEALTH_CHECKS": PRODUCTION,
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL_TTL_SECONDS = int(os.getenv("MEDIA_URL_TTL_SECONDS", "600"))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024

_cache_backend = (
    "django.core.cache.backends.locmem.LocMemCache"
    if TESTING
    else "django.core.cache.backends.redis.RedisCache"
)
_redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CACHES = {
    "default": {
        "BACKEND": _cache_backend,
        "LOCATION": "zhixu-tests" if TESTING else _redis_url,
    },
    # 默认可复用现有 Redis；部署量增大后用 AI_REDIS_URL 隔离大附件与认证限流数据。
    "ai": {
        "BACKEND": _cache_backend,
        "LOCATION": "zhixu-ai-tests" if TESTING else os.getenv("AI_REDIS_URL", _redis_url),
    },
}

EMAIL_BACKEND = (
    "django.core.mail.backends.locmem.EmailBackend"
    if TESTING
    else os.getenv(
        "EMAIL_BACKEND",
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.smtp.EmailBackend",
    )
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = _setting("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "知序 <noreply@mail.stumyself.online>")
EMAIL_TIMEOUT = 10
TENCENT_SES_SECRET_ID = _setting("TENCENT_SES_SECRET_ID")
TENCENT_SES_SECRET_KEY = _setting("TENCENT_SES_SECRET_KEY")
TENCENT_SES_REGION = os.getenv("TENCENT_SES_REGION", "ap-hongkong")
TENCENT_SES_TEMPLATE_ID = 0 if TESTING else int(os.getenv("TENCENT_SES_TEMPLATE_ID", "0"))
EMAIL_CODE_TTL_SECONDS = int(os.getenv("EMAIL_CODE_TTL_SECONDS", "600"))
EMAIL_CODE_COOLDOWN_SECONDS = int(os.getenv("EMAIL_CODE_COOLDOWN_SECONDS", "60"))
EMAIL_CODE_IP_LIMIT_PER_HOUR = int(os.getenv("EMAIL_CODE_IP_LIMIT_PER_HOUR", "20"))
INVITE_ONLY_REGISTRATION = os.getenv("INVITE_ONLY_REGISTRATION", "0") == "1"


def _csv_setting(name, default):
    """把逗号分隔环境变量读取为去重后的非空元组。"""
    return tuple(dict.fromkeys(item.strip() for item in os.getenv(name, default).split(",") if item.strip()))


# 开发环境默认可见，生产环境必须显式开启，便于在上游故障时独立关闭 AI 而不影响学习功能。
AI_ASSISTANT_ENABLED = os.getenv("AI_ASSISTANT_ENABLED", "0" if PRODUCTION else "1") == "1"
AI_CREDENTIAL_ENCRYPTION_KEY = _setting("AI_CREDENTIAL_ENCRYPTION_KEY")
AI_CUSTOM_ALLOWED_HOSTS = tuple(
    item.lower() for item in _csv_setting("AI_CUSTOM_ALLOWED_HOSTS", "")
)
AI_REQUEST_TIMEOUT_SECONDS = min(50, max(5, int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "45"))))
AI_PROVIDER_RESPONSE_MAX_BYTES = min(
    16 * 1024 * 1024,
    max(256 * 1024, int(os.getenv("AI_PROVIDER_RESPONSE_MAX_BYTES", str(8 * 1024 * 1024)))),
)
AI_CONTEXT_CACHE_TTL_SECONDS = max(60, int(os.getenv("AI_CONTEXT_CACHE_TTL_SECONDS", "900")))
AI_ATTACHMENT_CACHE_TTL_SECONDS = max(300, int(os.getenv("AI_ATTACHMENT_CACHE_TTL_SECONDS", "3600")))
AI_CONTEXT_CHAR_BUDGET = max(8_000, int(os.getenv("AI_CONTEXT_CHAR_BUDGET", "32000")))
AI_MESSAGE_MAX_CHARS = max(1_000, int(os.getenv("AI_MESSAGE_MAX_CHARS", "6000")))
AI_RESPONSE_MAX_CHARS = min(100_000, max(1_000, int(os.getenv("AI_RESPONSE_MAX_CHARS", "50000"))))
AI_ATTACHMENT_MAX_BYTES = min(5 * 1024 * 1024, max(256 * 1024, int(os.getenv("AI_ATTACHMENT_MAX_BYTES", str(4 * 1024 * 1024)))))
AI_ATTACHMENT_MAX_FILES = min(4, max(1, int(os.getenv("AI_ATTACHMENT_MAX_FILES", "2"))))
AI_ATTACHMENT_TEXT_MAX_CHARS = min(30_000, max(2_000, int(os.getenv("AI_ATTACHMENT_TEXT_MAX_CHARS", "12000"))))
AI_PDF_MAX_PAGES = min(50, max(1, int(os.getenv("AI_PDF_MAX_PAGES", "20"))))
AI_IMAGE_CONTEXT_MAX_BYTES = min(
    16 * 1024 * 1024,
    max(0, int(os.getenv("AI_IMAGE_CONTEXT_MAX_BYTES", str(8 * 1024 * 1024)))),
)

# 旧会话继续使用这里的固定官方地址；新会话可保存经过公网 HTTPS 校验的用户地址。
AI_PROVIDERS = {
    "openai": {
        "display_name": "OpenAI",
        "adapter": "openai_responses",
        "api_url": "https://api.openai.com/v1/responses",
        "verify_url": "https://api.openai.com/v1/models",
        "models": _csv_setting("AI_OPENAI_MODELS", "gpt-5.6-luna,gpt-5.6-terra"),
        "supports_images": True,
    },
    "anthropic": {
        "display_name": "Anthropic",
        "adapter": "anthropic_messages",
        "api_url": "https://api.anthropic.com/v1/messages",
        "verify_url": "https://api.anthropic.com/v1/models",
        "models": _csv_setting("AI_ANTHROPIC_MODELS", "claude-haiku-4-5,claude-sonnet-5"),
        "supports_images": True,
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("THROTTLE_ANON", "60/min"),
        "user": os.getenv("THROTTLE_USER", "300/min"),
        "login": os.getenv("THROTTLE_LOGIN", "10/min"),
        "register": os.getenv("THROTTLE_REGISTER", "5/hour"),
        "token_refresh": os.getenv("THROTTLE_TOKEN_REFRESH", "30/min"),
        "email_code": os.getenv("THROTTLE_EMAIL_CODE", "5/min"),
        "upload": os.getenv("THROTTLE_UPLOAD", "20/hour"),
        "community_write": os.getenv("THROTTLE_COMMUNITY_WRITE", "60/hour"),
        "ai_chat": os.getenv("THROTTLE_AI_CHAT", "30/min"),
        "ai_credential": os.getenv("THROTTLE_AI_CREDENTIAL", "10/hour"),
    },
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "15"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "CHECK_REVOKE_TOKEN": True,
    "TOKEN_REFRESH_SERIALIZER": "learning.accounts.serializers.SafeTokenRefreshSerializer",
}
AUTH_REFRESH_COOKIE = "refresh_token"
AUTH_REFRESH_COOKIE_PATH = "/api/auth/"
AUTH_REFRESH_COOKIE_SECURE = PRODUCTION
AUTH_REFRESH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "Lax")

LOCAL_FRONTEND_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
origin_defaults = "" if PRODUCTION else LOCAL_FRONTEND_ORIGINS
CORS_ALLOWED_ORIGINS = [item.strip() for item in os.getenv("CORS_ALLOWED_ORIGINS", origin_defaults).split(",") if item.strip()]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [item.strip() for item in os.getenv("CSRF_TRUSTED_ORIGINS", origin_defaults).split(",") if item.strip()]
SECURE_DEPLOYMENT = os.getenv("DJANGO_SECURE_SSL", "0") == "1"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = SECURE_DEPLOYMENT
SESSION_COOKIE_SECURE = SECURE_DEPLOYMENT
CSRF_COOKIE_SECURE = SECURE_DEPLOYMENT
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", "3600")) if SECURE_DEPLOYMENT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_DEPLOYMENT and os.getenv("DJANGO_HSTS_INCLUDE_SUBDOMAINS", "0") == "1"
SECURE_HSTS_PRELOAD = SECURE_DEPLOYMENT and os.getenv("DJANGO_HSTS_PRELOAD", "0") == "1"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production": {"format": "{asctime} {levelname} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "production"},
    },
    "root": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO")},
    "loggers": {
        # Django 默认处理器会继续向根日志传播；显式截断可避免自动重载启动信息重复输出。
        "django.utils.autoreload": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

if PRODUCTION:
    # 生产环境宁可拒绝启动，也不能静默使用开发密钥、弱密码或明文 HTTP。
    invalid = []
    if DEBUG:
        invalid.append("DJANGO_DEBUG 必须为 0")
    if not SECURE_DEPLOYMENT:
        invalid.append("DJANGO_SECURE_SSL 必须为 1")
    if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("dev-only") or SECRET_KEY.startswith("replace-"):
        invalid.append("DJANGO_SECRET_KEY 必须是至少 50 字符的随机值")
    if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
        invalid.append("DJANGO_ALLOWED_HOSTS 必须明确列出正式域名")
    if not CSRF_TRUSTED_ORIGINS:
        invalid.append("CSRF_TRUSTED_ORIGINS 必须包含 HTTPS 正式来源")
    if DATABASES["default"]["PASSWORD"] in {"", "change-me"}:
        invalid.append("MYSQL_PASSWORD 必须使用非默认值")
    if invalid:
        raise ImproperlyConfigured("生产配置无效：" + "；".join(invalid))
