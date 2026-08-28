"""校验 AI 上传内容，并转换为不会永久落盘的模型输入。"""

import base64
import io
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from rest_framework import serializers

from ..system.media import normalize_image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TEXT_EXTENSIONS = {
    ".txt", ".md", ".log", ".csv", ".json", ".yaml", ".yml", ".xml",
    ".py", ".js", ".ts", ".vue", ".html", ".css", ".sql", ".sh", ".ps1",
    ".java", ".kt", ".swift", ".c", ".h", ".cpp", ".go", ".rs",
}
SAFE_NAME_PATTERN = re.compile(r"[^\w.()\-\u4e00-\u9fff ]+", re.UNICODE)


@dataclass(frozen=True)
class PreparedAttachment:
    """表示已经过边界校验、可直接交给供应商适配器的临时附件。"""

    name: str
    kind: str
    media_type: str
    text: str = ""
    data: str = ""
    truncated: bool = False

    def cache_payload(self):
        """返回可放入 Redis 的临时内容，不包含用户或消息标识。"""
        return {
            "name": self.name,
            "kind": self.kind,
            "media_type": self.media_type,
            "text": self.text,
            "data": self.data,
            "truncated": self.truncated,
        }

    def metadata(self):
        """返回可持久化到消息表的非敏感附件说明和缓存失效时间。"""
        expires_at = timezone.now() + timedelta(seconds=settings.AI_ATTACHMENT_CACHE_TTL_SECONDS)
        return {
            "name": self.name,
            "kind": self.kind,
            "media_type": self.media_type,
            "truncated": self.truncated,
            "expires_at": expires_at.isoformat(),
        }


def _safe_name(name):
    """移除目录、控制字符和供应商提示中无意义的文件名字符。"""
    basename = Path(name or "attachment").name[:120]
    cleaned = SAFE_NAME_PATTERN.sub("_", basename).strip(" .")
    return cleaned or "attachment"


def _read_limited(upload):
    """读取单个上传文件并执行单文件和请求总量之外的硬上限。"""
    if upload.size > settings.AI_ATTACHMENT_MAX_BYTES:
        raise serializers.ValidationError(
            f"附件 {upload.name} 超过 {settings.AI_ATTACHMENT_MAX_BYTES // (1024 * 1024)}MB。"
        )
    upload.seek(0)
    return upload.read(settings.AI_ATTACHMENT_MAX_BYTES + 1)


def _prepare_image(upload, name):
    """复用站点图片清洗逻辑并返回清除元数据后的 Base64 图片。"""
    normalized, _, _ = normalize_image(upload)
    normalized.seek(0)
    return PreparedAttachment(
        name=name,
        kind="image",
        media_type=getattr(normalized, "content_type", "") or "image/jpeg",
        data=base64.b64encode(normalized.read()).decode("ascii"),
    )


def _decode_text(raw, name):
    """按 UTF-8 或常见中文编码读取文本，拒绝不能可靠解码的二进制内容。"""
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(encoding).replace("\x00", "")
        except UnicodeDecodeError:
            continue
    raise serializers.ValidationError(f"附件 {name} 不是可读取的 UTF-8 或 GB18030 文本。")


def _truncate_text(text):
    """限制单个附件进入模型的字符数，并返回正文和是否发生截断。"""
    limit = settings.AI_ATTACHMENT_TEXT_MAX_CHARS
    return (text[:limit], len(text) > limit)


def _prepare_pdf(raw, name):
    """从未加密 PDF 的前若干页提取文本，不执行其中的脚本或外部引用。"""
    try:
        reader = PdfReader(io.BytesIO(raw), strict=False)
        if reader.is_encrypted:
            raise serializers.ValidationError(f"附件 {name} 已加密，无法读取。")
        page_limit = settings.AI_PDF_MAX_PAGES
        parts = []
        # PDF 可能声明大量页面；只读取固定前缀，控制 CPU 和上下文开销。
        for page in reader.pages[:page_limit]:
            parts.append(page.extract_text() or "")
        text, text_truncated = _truncate_text("\n\n".join(parts).strip())
        if not text:
            raise serializers.ValidationError(f"附件 {name} 没有可提取文本，扫描版 PDF 请改为上传图片。")
        return PreparedAttachment(
            name=name,
            kind="text",
            media_type="application/pdf",
            text=text,
            truncated=len(reader.pages) > page_limit or text_truncated,
        )
    except serializers.ValidationError:
        raise
    except (PdfReadError, OSError, ValueError, TypeError) as exc:
        raise serializers.ValidationError(f"附件 {name} 不是可读取的 PDF。") from exc


def prepare_attachments(files):
    """校验一组图片、文本、源码或 PDF，返回临时模型输入列表。"""
    uploads = list(files)
    if len(uploads) > settings.AI_ATTACHMENT_MAX_FILES:
        raise serializers.ValidationError(f"每次最多上传 {settings.AI_ATTACHMENT_MAX_FILES} 个附件。")
    if sum(getattr(upload, "size", 0) for upload in uploads) > settings.AI_ATTACHMENT_MAX_BYTES * settings.AI_ATTACHMENT_MAX_FILES:
        raise serializers.ValidationError("本次附件总大小超过允许范围。")

    prepared = []
    for upload in uploads:
        name = _safe_name(upload.name)
        if upload.size > settings.AI_ATTACHMENT_MAX_BYTES:
            raise serializers.ValidationError(
                f"附件 {name} 超过 {settings.AI_ATTACHMENT_MAX_BYTES // (1024 * 1024)}MB。"
            )
        extension = Path(name).suffix.lower()
        if extension in IMAGE_EXTENSIONS:
            prepared.append(_prepare_image(upload, name))
            continue

        raw = _read_limited(upload)
        if extension == ".pdf":
            prepared.append(_prepare_pdf(raw, name))
        elif extension in TEXT_EXTENSIONS:
            text, truncated = _truncate_text(_decode_text(raw, name))
            prepared.append(
                PreparedAttachment(
                    name=name,
                    kind="text",
                    media_type=getattr(upload, "content_type", "") or "text/plain",
                    text=text,
                    truncated=truncated,
                )
            )
        else:
            raise serializers.ValidationError(
                f"附件 {name} 格式不受支持；请上传常见图片、PDF、文本或源码文件。"
            )
    return prepared
