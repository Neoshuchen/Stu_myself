"""提供用户隔离的 AI 供应商、凭据、会话和多模态消息接口。"""

from django.conf import settings
from django.db.models import Count
from django.http import Http404
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import AIChatSession, AIProviderCredential
from .attachments import prepare_attachments
from .providers import ProviderError, call_provider, verify_provider_key
from .serializers import (
    AIChatMessageSerializer,
    AIChatSessionDetailSerializer,
    AIChatSessionSerializer,
    AICredentialInputSerializer,
    AIProviderCredentialSerializer,
    AIMessageInputSerializer,
)
from .services import (
    CredentialStorageUnavailable,
    acquire_request_lock,
    build_provider_messages,
    clear_session_cache,
    credential_storage_available,
    decrypt_api_key,
    encrypt_api_key,
    persist_exchange,
    provider_config,
    release_request_lock,
    resolve_api_key,
    safety_identifier,
    system_instruction,
)


CREDENTIAL_CONNECTION_FIELDS = {"provider", "adapter", "api_url", "model", "api_key"}
CREDENTIAL_INPUT_FIELDS = CREDENTIAL_CONNECTION_FIELDS | {"name"}


class AIEnabledMixin:
    """在所有 AI 写入和历史接口前统一执行运行时功能开关。"""

    def initial(self, request, *args, **kwargs):
        """AI 关闭时返回不存在，避免影响其余 API 和暴露未启用端点。"""
        if not settings.AI_ASSISTANT_ENABLED:
            raise Http404
        return super().initial(request, *args, **kwargs)


def provider_error_response(exc):
    """把脱敏后的供应商异常转换为稳定 API 响应。"""
    return Response(
        {"detail": exc.user_message, "code": exc.code},
        status=exc.status_code,
    )


class AIProviderCatalogView(APIView):
    """公开当前登录用户可用的供应商、模型和附件限制，不返回服务地址。"""

    def get(self, request):
        """返回运行时开关、允许模型及当前用户是否已经保存密钥。"""
        if not settings.AI_ASSISTANT_ENABLED:
            return Response({"enabled": False, "providers": []})
        saved = set(
            AIProviderCredential.objects.filter(user=request.user).values_list("provider", flat=True)
        )
        providers = [
            {
                "id": provider,
                "name": config["display_name"],
                "models": list(config["models"]),
                "supports_images": bool(config["supports_images"]),
                "has_saved_credential": provider in saved,
            }
            for provider, config in settings.AI_PROVIDERS.items()
            if config["models"]
        ]
        return Response(
            {
                "enabled": True,
                "credential_storage_available": credential_storage_available(),
                "attachment_cache_ttl_seconds": settings.AI_ATTACHMENT_CACHE_TTL_SECONDS,
                "attachment_max_files": settings.AI_ATTACHMENT_MAX_FILES,
                "attachment_max_bytes": settings.AI_ATTACHMENT_MAX_BYTES,
                "providers": providers,
            }
        )


class AICredentialTestView(AIEnabledMixin, APIView):
    """验证一次临时模型配置，不保存密钥和供应商响应正文。"""

    throttle_scope = "ai_credential"

    def post(self, request):
        """固定接口读取模型列表，自定义接口执行最小生成请求并返回结果。"""
        serializer = AICredentialInputSerializer(
            data=request.data,
            context={"request": request, "require_api_key": True},
        )
        serializer.is_valid(raise_exception=True)
        provider = serializer.validated_data["provider"]
        model = serializer.validated_data.get("model", "")
        config = provider_config(
            provider,
            model or None,
            serializer.validated_data.get("adapter", ""),
            serializer.validated_data.get("api_url", ""),
        )
        try:
            verify_provider_key(config, serializer.validated_data["api_key"], model)
        except ProviderError as exc:
            return provider_error_response(exc)
        return Response({"detail": "连接验证成功。"})


class AIProviderCredentialViewSet(
    AIEnabledMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """管理当前用户长期保存的多条加密模型服务配置。"""

    serializer_class = AIProviderCredentialSerializer
    throttle_scope = "ai_credential"
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):
        """只返回当前用户自己的凭据提示信息。"""
        return AIProviderCredential.objects.filter(user=self.request.user)

    def _verified_input(self, request, data):
        """统一校验并验证一份完整连接配置，避免创建和修改路径产生差异。"""
        input_serializer = AICredentialInputSerializer(
            data=data,
            context={"request": request, "require_api_key": True},
        )
        input_serializer.is_valid(raise_exception=True)
        values = input_serializer.validated_data
        config = provider_config(
            values["provider"],
            values.get("model") or None,
            values.get("adapter", ""),
            values.get("api_url", ""),
        )
        verify_provider_key(config, values["api_key"], values.get("model", ""))
        return values, config

    def create(self, request, *args, **kwargs):
        """验证并新增长期配置，不覆盖同一用户已有的其他服务。"""
        if not credential_storage_available():
            return Response(
                {"detail": "服务端未配置独立的 AI 凭据加密密钥，只能使用临时 Key。"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            values, config = self._verified_input(request, request.data)
            api_key = values["api_key"]
            encrypted = encrypt_api_key(api_key)
        except ProviderError as exc:
            return provider_error_response(exc)
        except CredentialStorageUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        credential = AIProviderCredential.objects.create(
            user=request.user,
            name=values.get("name") or f"{config['display_name']} 配置",
            provider=values["provider"],
            adapter=values.get("adapter", ""),
            api_url=config["api_url"] if values.get("api_url") else "",
            model=values.get("model", ""),
            encrypted_api_key=encrypted,
            key_last_four=api_key[-4:],
            last_verified_at=timezone.now(),
        )
        del api_key
        output = self.get_serializer(credential)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """修改配置名称或重新验证并替换连接信息，省略 Key 时复用原密文。"""
        unknown_fields = set(request.data) - CREDENTIAL_INPUT_FIELDS
        if unknown_fields:
            raise ValidationError({field: "不支持修改此字段。" for field in unknown_fields})
        credential = self.get_object()
        connection_changed = "api_key" in request.data or any(
            field in request.data and request.data[field] != getattr(credential, field)
            for field in CREDENTIAL_CONNECTION_FIELDS - {"api_key"}
        )
        if not connection_changed:
            output = self.get_serializer(credential, data=request.data, partial=True)
            output.is_valid(raise_exception=True)
            output.save()
            return Response(output.data)
        if not credential_storage_available():
            return Response(
                {"detail": "服务端未配置独立的 AI 凭据加密密钥，无法修改连接信息。"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        data = {
            "name": credential.name,
            "provider": credential.provider,
            "adapter": credential.adapter,
            "api_url": credential.api_url,
            "model": credential.model,
            **request.data,
        }
        try:
            if "api_key" not in request.data:
                data["api_key"] = decrypt_api_key(credential)
            values, config = self._verified_input(request, data)
            encrypted = (
                encrypt_api_key(values["api_key"])
                if "api_key" in request.data
                else credential.encrypted_api_key
            )
        except ProviderError as exc:
            return provider_error_response(exc)
        except CredentialStorageUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        credential.name = values.get("name") or credential.name
        credential.provider = values["provider"]
        credential.adapter = values.get("adapter", "")
        credential.api_url = config["api_url"] if values.get("api_url") else ""
        credential.model = values.get("model", "")
        credential.encrypted_api_key = encrypted
        credential.key_last_four = values["api_key"][-4:]
        credential.last_verified_at = timezone.now()
        credential.save()
        del data["api_key"]
        return Response(self.get_serializer(credential).data)


class AIChatSessionViewSet(AIEnabledMixin, viewsets.ModelViewSet):
    """创建、读取、重命名、删除用户会话并发送多模态学习消息。"""

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    throttle_scope = "ai_chat"
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):
        """按当前用户过滤会话，并预取课程关联以构造上下文。"""
        queryset = (
            AIChatSession.objects.filter(user=self.request.user)
            .select_related("credential", "progress", "progress__plan_day", "progress__plan_day__plan")
            .annotate(message_count=Count("messages"))
        )
        progress_id = self.request.query_params.get("progress")
        if progress_id:
            if not progress_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(progress_id=int(progress_id))
        return queryset

    def get_serializer_class(self):
        """详情接口返回消息，列表和写入接口只返回会话概要。"""
        return AIChatSessionDetailSerializer if self.action == "retrieve" else AIChatSessionSerializer

    def perform_create(self, serializer):
        """把新会话所有者固定为当前请求用户。"""
        instance = serializer.save(user=self.request.user)
        instance.message_count = 0

    def perform_destroy(self, instance):
        """删除数据库会话前清理其仍在 Redis 中的文本和附件缓存。"""
        message_ids = list(instance.messages.values_list("id", flat=True))
        clear_session_cache(instance, message_ids)
        instance.delete()

    @action(detail=True, methods=["post"], url_path="messages")
    def send_message(self, request, pk=None):
        """验证附件和密钥、调用供应商，并仅在成功后保存一对消息。"""
        session = self.get_object()
        input_serializer = AIMessageInputSerializer(data=request.data, context={"request": request})
        input_serializer.is_valid(raise_exception=True)
        lock_acquired = acquire_request_lock(request.user.pk)
        if lock_acquired is None:
            return Response(
                {"detail": "AI 临时缓存当前不可用，请稍后重试。", "code": "ai_cache_unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if not lock_acquired:
            return Response(
                {"detail": "已有一个 AI 请求正在处理中，请等待完成。", "code": "request_in_progress"},
                status=status.HTTP_409_CONFLICT,
            )

        api_key = ""
        try:
            attachments = prepare_attachments(request.FILES.getlist("attachments"))
            content = input_serializer.validated_data.get("content", "")
            if not content and not attachments:
                return Response({"detail": "请输入问题或至少上传一个附件。"}, status=status.HTTP_400_BAD_REQUEST)

            config = provider_config(
                session.provider,
                session.model,
                session.adapter,
                session.api_url,
            )
            if attachments and any(item.kind == "image" for item in attachments) and not config["supports_images"]:
                return Response({"detail": "当前供应商模型不支持图片输入。"}, status=status.HTTP_400_BAD_REQUEST)
            api_key = resolve_api_key(
                request.user,
                session,
                input_serializer.validated_data.get("api_key", ""),
            )
            focus = input_serializer.focus()
            messages = build_provider_messages(session, content, attachments, focus)
            result = call_provider(
                config,
                api_key,
                session.model,
                system_instruction(session),
                messages,
                session.max_output_tokens,
                safety_identifier(request.user),
            )
            user_message, assistant_message = persist_exchange(
                session, content, attachments, focus, result
            )
        except ProviderError as exc:
            return provider_error_response(exc)
        finally:
            api_key = ""
            release_request_lock(request.user.pk)

        return Response(
            {
                "user_message": AIChatMessageSerializer(user_message).data,
                "assistant_message": AIChatMessageSerializer(assistant_message).data,
            },
            status=status.HTTP_201_CREATED,
        )
