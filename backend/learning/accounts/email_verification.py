import hashlib
import json
import logging
import secrets
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.crypto import constant_time_compare, salted_hmac
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ses.v20201002 import models, ses_client


logger = logging.getLogger(__name__)


class EmailVerificationError(ValueError):
    """邮箱验证流程的基础业务异常。"""

    pass


class EmailRateLimitError(EmailVerificationError):
    """验证码请求超过业务限额时抛出的异常。"""

    pass


def normalize_email(email):
    return email.strip().casefold()


def _email_id(email):
    return hashlib.sha256(normalize_email(email).encode()).hexdigest()


def _code_digest(email, code):
    return salted_hmac("zhixu.email-code", f"{normalize_email(email)}:{code}").hexdigest()


def _code_key(email):
    return f"email-code:value:{_email_id(email)}"


def _send_verification_email(email, code, ttl):
    if settings.TENCENT_SES_TEMPLATE_ID:
        if not settings.TENCENT_SES_SECRET_ID or not settings.TENCENT_SES_SECRET_KEY:
            raise RuntimeError("腾讯云 SES API 凭证未配置。")
        template = models.Template()
        template.TemplateID = settings.TENCENT_SES_TEMPLATE_ID
        template.TemplateData = json.dumps({"code": code})
        request = models.SendEmailRequest()
        request.FromEmailAddress = settings.DEFAULT_FROM_EMAIL
        request.Subject = "知序邮箱验证码"
        request.Destination = [email]
        request.Template = template
        request.TriggerType = 1
        profile = ClientProfile(httpProfile=HttpProfile(reqTimeout=settings.EMAIL_TIMEOUT))
        client = ses_client.SesClient(
            credential.Credential(settings.TENCENT_SES_SECRET_ID, settings.TENCENT_SES_SECRET_KEY),
            settings.TENCENT_SES_REGION,
            profile,
        )
        client.SendEmail(request)
        return
    send_mail(
        "知序邮箱验证码",
        f"你的验证码是：{code}\n\n验证码 {ttl // 60} 分钟内有效，请勿转发给他人。",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_verification_code(email, client_ip=""):
    email = normalize_email(email)
    cooldown = settings.EMAIL_CODE_COOLDOWN_SECONDS
    cooldown_key = f"email-code:cooldown:{_email_id(email)}"
    if not cache.add(cooldown_key, 1, cooldown):
        raise EmailRateLimitError(f"请在 {cooldown} 秒后重新发送验证码。")

    ip_key = f"email-code:ip:{hashlib.sha256((client_ip or 'unknown').encode()).hexdigest()}"
    ip_count = 1 if cache.add(ip_key, 1, 3600) else cache.incr(ip_key)
    if ip_count > settings.EMAIL_CODE_IP_LIMIT_PER_HOUR:
        cache.delete(cooldown_key)
        raise EmailRateLimitError("发送请求过于频繁，请稍后再试。")

    code = f"{secrets.randbelow(1_000_000):06d}"
    ttl = settings.EMAIL_CODE_TTL_SECONDS
    cache.set(
        _code_key(email),
        {"digest": _code_digest(email, code), "attempts": 0, "expires_at": time.time() + ttl},
        ttl,
    )
    try:
        _send_verification_email(email, code, ttl)
    except Exception as exc:
        cache.delete_many([_code_key(email), cooldown_key])
        logger.exception("邮箱验证码发送失败")
        raise EmailVerificationError("验证码发送失败，请稍后再试。") from exc


def consume_verification_code(email, code):
    email = normalize_email(email)
    key = _code_key(email)
    record = cache.get(key)
    if not record:
        raise EmailVerificationError("验证码无效或已过期，请重新获取。")

    remaining = int(record["expires_at"] - time.time())
    if remaining <= 0:
        cache.delete(key)
        raise EmailVerificationError("验证码无效或已过期，请重新获取。")

    if not constant_time_compare(record["digest"], _code_digest(email, code)):
        record["attempts"] += 1
        if record["attempts"] >= 5:
            cache.delete(key)
            raise EmailVerificationError("验证码错误次数过多，请重新获取。")
        cache.set(key, record, remaining)
        raise EmailVerificationError("邮箱验证码不正确。")

    used_key = f"email-code:used:{record['digest']}"
    if not cache.add(used_key, 1, remaining):
        raise EmailVerificationError("验证码已使用，请重新获取。")
    cache.delete(key)


