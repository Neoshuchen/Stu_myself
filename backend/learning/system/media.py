import io
import mimetypes
import warnings
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core import signing
from django.core.files.base import ContentFile
from django.urls import reverse
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework import serializers

IMAGE_MAX_BYTES = 8 * 1024 * 1024
IMAGE_MAX_PIXELS = 25_000_000
IMAGE_MAX_EDGE = 2400
IMAGE_FORMATS = {"JPEG": ("JPEG", ".jpg"), "PNG": ("PNG", ".png"), "WEBP": ("WEBP", ".webp")}
MEDIA_SIGNING_SALT = "learning.protected-media.v1"


def normalize_image(upload):
    """校验并重编码用户图片，返回清除元数据后的文件、宽度和高度。"""
    if upload.size > IMAGE_MAX_BYTES:
        raise serializers.ValidationError("图片不能超过8MB。")
    try:
        upload.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(upload)
        if image.format not in IMAGE_FORMATS:
            raise serializers.ValidationError("仅支持 JPEG、PNG 或 WebP 图片。")
        source_format = image.format
        if getattr(image, "is_animated", False) and getattr(image, "n_frames", 1) > 1:
            raise serializers.ValidationError("暂不支持动图，请上传静态图片。")
        if image.width * image.height > IMAGE_MAX_PIXELS:
            raise serializers.ValidationError("图片像素过大，请控制在2500万像素以内。")
        image.load()
    except serializers.ValidationError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning, UnidentifiedImageError, OSError) as exc:
        raise serializers.ValidationError("图片文件已损坏或格式不受支持。") from exc

    # 自动应用拍摄方向并重编码，既避免横竖颠倒，也不会保留 EXIF/GPS 等隐私元数据。
    image = ImageOps.exif_transpose(image)
    image.thumbnail((IMAGE_MAX_EDGE, IMAGE_MAX_EDGE), Image.Resampling.LANCZOS)
    output_format, extension = IMAGE_FORMATS[source_format]
    if output_format == "JPEG":
        image = image.convert("RGB")
    elif image.mode not in ("RGB", "RGBA", "L"):
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")

    output = io.BytesIO()
    save_options = {"optimize": True}
    if output_format in ("JPEG", "WEBP"):
        save_options["quality"] = 88
    image.save(output, format=output_format, **save_options)
    content = ContentFile(output.getvalue(), name=f"{uuid4().hex}{extension}")
    content.content_type = Image.MIME.get(output_format) or mimetypes.guess_type(content.name)[0]
    return content, image.width, image.height


def protected_media_url(request, kind, object_id):
    """为已通过业务权限检查的文件生成短时有效的签名访问地址。"""
    token = signing.dumps({"kind": kind, "id": object_id}, salt=MEDIA_SIGNING_SALT, compress=True)
    path = reverse("protected_media", kwargs={"token": token})
    return request.build_absolute_uri(path) if request else path


def load_media_token(token):
    """验证签名媒体令牌并返回其中的文件类型与对象编号。"""
    try:
        payload = signing.loads(
            token,
            salt=MEDIA_SIGNING_SALT,
            max_age=settings.MEDIA_URL_TTL_SECONDS,
        )
        return str(payload["kind"]), int(payload["id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise serializers.ValidationError("文件链接无效或已过期。") from exc


def upload_extension(filename):
    """返回可安全复用的常见附件扩展名，未知扩展名不参与存储路径。"""
    extension = Path(filename).suffix.lower()
    return extension if extension in {".txt", ".json", ".pdf"} else ""

