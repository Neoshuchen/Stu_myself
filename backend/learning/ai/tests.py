"""验证 AI 学习助手的权限、密钥、多模态、缓存和故障隔离边界。"""

import io
from unittest.mock import Mock, patch

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from ..models import (
    AIChatMessage,
    AIChatSession,
    AIProviderCredential,
    DayProgress,
    Enrollment,
    LearningPlan,
    PlanDay,
)
from .attachments import prepare_attachments
from .providers import (
    ProviderError,
    ProviderResult,
    _request_json,
    call_provider,
    provider_endpoint_url,
    validate_public_https_url,
)
from .services import build_provider_messages, decrypt_api_key, encrypt_api_key


User = get_user_model()
TEST_ENCRYPTION_KEY = Fernet.generate_key().decode("ascii")
cache = caches["ai"]


@override_settings(
    AI_ASSISTANT_ENABLED=True,
    AI_CREDENTIAL_ENCRYPTION_KEY=TEST_ENCRYPTION_KEY,
    AI_CONTEXT_CACHE_TTL_SECONDS=900,
    AI_ATTACHMENT_CACHE_TTL_SECONDS=3600,
)
class AIAssistantAPITests(TestCase):
    """覆盖 AI API 对现有学习状态和用户数据的关键安全边界。"""

    def setUp(self):
        """创建一条最小学习日和两个隔离用户。"""
        cache.clear()
        self.user = User.objects.create_user(username="ai-user", password="secret-pass")
        self.other = User.objects.create_user(username="ai-other", password="secret-pass")
        self.plan = LearningPlan.objects.create(
            slug="ai-course",
            title="AI 测试课程",
            summary="测试",
            total_days=1,
            estimated_weeks=1,
        )
        self.day = PlanDay.objects.create(
            plan=self.plan,
            day_number=1,
            phase="基础",
            week_number=1,
            week_title="第一周",
            title="理解上下文",
            core_knowledge="上下文与边界",
            hands_on_task="解释一次失败路径",
            acceptance_criteria=["能够说明边界"],
            content={"knowledge_details": [{"name": "上下文"}]},
        )
        enrollment = Enrollment.objects.create(user=self.user, plan=self.plan)
        self.progress = DayProgress.objects.create(
            enrollment=enrollment,
            plan_day=self.day,
            status=DayProgress.Status.IN_PROGRESS,
            acceptance_checks=[False],
            knowledge_checks=[False],
        )
        other_enrollment = Enrollment.objects.create(user=self.other, plan=self.plan)
        self.other_progress = DayProgress.objects.create(
            enrollment=other_enrollment,
            plan_day=self.day,
            acceptance_checks=[False],
            knowledge_checks=[False],
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def create_session(self, **overrides):
        """通过公开 API 创建会话并返回数据库对象。"""
        payload = {
            "progress": self.progress.pk,
            "title": "Day 1 学习助手",
            "provider": "openai",
            "model": "gpt-5.6-luna",
            "context_rounds": 8,
            "max_output_tokens": 1024,
            "teaching_mode": "hint",
            "include_current_lesson": True,
            **overrides,
        }
        response = self.client.post("/api/ai/chats/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return AIChatSession.objects.get(pk=response.data["id"])

    @staticmethod
    def image_upload(name="question.jpg"):
        """返回带 EXIF 容器能力的最小合法 JPEG 上传对象。"""
        stream = io.BytesIO()
        Image.new("RGB", (40, 30), "#3b7d6b").save(stream, format="JPEG")
        return SimpleUploadedFile(name, stream.getvalue(), content_type="image/jpeg")

    def test_provider_catalog_does_not_expose_urls(self):
        response = self.client.get("/api/ai/providers/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["enabled"])
        self.assertEqual({item["id"] for item in response.data["providers"]}, {"openai", "anthropic"})
        self.assertNotIn("api_url", str(response.data))
        self.assertNotIn("api.openai.com", str(response.data))

    def test_session_rejects_other_users_progress_and_unlisted_model(self):
        response = self.client.post(
            "/api/ai/chats/",
            {
                "progress": self.other_progress.pk,
                "title": "越权",
                "provider": "openai",
                "model": "gpt-5.6-luna",
                "context_rounds": 8,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            "/api/ai/chats/",
            {
                "progress": self.progress.pk,
                "title": "未知模型",
                "provider": "openai",
                "model": "user-controlled-model",
                "context_rounds": 8,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    @patch(
        "learning.ai.providers.socket.getaddrinfo",
        return_value=[(2, 1, 6, "", ("8.8.8.8", 443))],
    )
    def test_global_session_accepts_user_model_endpoint_without_daily_progress(self, _resolve):
        """全局助手会话不依赖学习日，并保存经过校验的模型调用快照。"""
        response = self.client.post(
            "/api/ai/chats/",
            {
                "title": "全局学习对话",
                "provider": "openai",
                "adapter": "openai_chat_completions",
                "api_url": "https://MODEL.EXAMPLE/v1",
                "model": "provider/model-v1",
                "context_rounds": 8,
                "include_current_lesson": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data["progress"])
        self.assertEqual(response.data["api_url"], "https://model.example/v1/chat/completions")

    def test_custom_endpoint_rejects_private_network(self):
        """拒绝把用户可配置 URL 变成访问本机或内网的服务端代理。"""
        response = self.client.post(
            "/api/ai/chats/",
            {
                "title": "危险地址",
                "provider": "openai",
                "adapter": "openai_chat_completions",
                "api_url": "https://127.0.0.1:8443/v1/chat/completions",
                "model": "model-v1",
                "context_rounds": 8,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("内网", str(response.data))

    def test_credential_rejects_request_header_injection(self):
        """API Key 中的换行不能进入供应商认证请求头。"""
        response = self.client.post(
            "/api/ai/credentials/test/",
            {"provider": "openai", "api_key": "safe-key\r\nX-Injected: yes"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("ASCII", str(response.data))

    def test_other_user_cannot_read_or_delete_session(self):
        session = self.create_session()
        outsider = APIClient()
        outsider.force_authenticate(self.other)
        self.assertEqual(outsider.get(f"/api/ai/chats/{session.pk}/").status_code, 404)
        self.assertEqual(outsider.delete(f"/api/ai/chats/{session.pk}/").status_code, 404)

    @patch("learning.ai.services.cache.delete_many", side_effect=OSError("redis unavailable"))
    def test_owner_can_delete_session_when_cache_is_unavailable(self, _delete_many):
        session = self.create_session()
        response = self.client.delete(f"/api/ai/chats/{session.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AIChatSession.objects.filter(pk=session.pk).exists())

    @patch("learning.ai.views.verify_provider_key")
    def test_saved_credential_is_encrypted_and_never_returned(self, verify):
        verify.return_value = None
        secret = "sk-test-super-secret-1234"
        response = self.client.post(
            "/api/ai/credentials/",
            {"provider": "openai", "api_key": secret},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn(secret, str(response.data))
        self.assertNotIn("encrypted_api_key", response.data)
        credential = AIProviderCredential.objects.get(user=self.user, provider="openai")
        self.assertNotEqual(credential.encrypted_api_key, secret)
        self.assertEqual(credential.key_last_four, "1234")
        self.assertEqual(decrypt_api_key(credential), secret)

    @patch("learning.ai.providers.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("8.8.8.8", 443))])
    @patch("learning.ai.views.verify_provider_key")
    def test_custom_credential_preserves_non_secret_connection_fields(self, verify, _resolve):
        """保存 OpenCode 风格 Base URL 时补齐端点，同时仍不返回密钥或密文。"""
        response = self.client.post(
            "/api/ai/credentials/",
            {
                "provider": "openai",
                "adapter": "openai_chat_completions",
                "api_url": "https://model.example/v1",
                "model": "provider/model-v1",
                "api_key": "custom-provider-key",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["adapter"], "openai_chat_completions")
        self.assertEqual(response.data["api_url"], "https://model.example/v1/chat/completions")
        self.assertEqual(response.data["model"], "provider/model-v1")
        self.assertEqual(verify.call_args.args[0]["api_url"], "https://model.example/v1/chat/completions")
        self.assertNotIn("custom-provider-key", str(response.data))

    @patch("learning.ai.providers.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("8.8.8.8", 443))])
    @patch("learning.ai.views.verify_provider_key")
    def test_user_can_keep_edit_and_delete_multiple_openai_compatible_services(self, verify, _resolve):
        """同一用户可长期保存多条 OpenAI 兼容配置，并按稳定 ID 修改和删除。"""
        first = self.client.post(
            "/api/ai/credentials/",
            {
                "name": "服务一",
                "provider": "openai",
                "adapter": "openai_chat_completions",
                "api_url": "https://one.example/v1/chat/completions",
                "model": "model-one",
                "api_key": "first-provider-key",
            },
            format="json",
        )
        second = self.client.post(
            "/api/ai/credentials/",
            {
                "name": "服务二",
                "provider": "openai",
                "adapter": "openai_chat_completions",
                "api_url": "https://two.example/v1/chat/completions",
                "model": "model-two",
                "api_key": "second-provider-key",
            },
            format="json",
        )
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertNotEqual(first.data["id"], second.data["id"])
        self.assertEqual(AIProviderCredential.objects.filter(user=self.user, provider="openai").count(), 2)

        changed = self.client.patch(
            f"/api/ai/credentials/{first.data['id']}/",
            {"model": "model-one-v2"},
            format="json",
        )
        self.assertEqual(changed.status_code, 200, changed.data)
        self.assertEqual(changed.data["model"], "model-one-v2")
        self.assertEqual(verify.call_args.args[1], "first-provider-key")

        renamed = self.client.patch(
            f"/api/ai/credentials/{first.data['id']}/",
            {"name": "主力模型"},
            format="json",
        )
        self.assertEqual(renamed.status_code, 200, renamed.data)
        self.assertEqual(renamed.data["name"], "主力模型")
        self.assertEqual(verify.call_count, 3)
        self.assertEqual(self.client.delete(f"/api/ai/credentials/{second.data['id']}/").status_code, 204)
        self.assertEqual(AIProviderCredential.objects.filter(user=self.user).count(), 1)

    @patch("learning.ai.views.call_provider")
    def test_session_uses_the_selected_owned_credential(self, call):
        """会话只解密其绑定的用户配置，而不是同供应商任意一条。"""
        credential = AIProviderCredential.objects.create(
            user=self.user,
            name="官方账号",
            provider="openai",
            encrypted_api_key=encrypt_api_key("selected-saved-key"),
            key_last_four="-key",
        )
        session = self.create_session(credential=credential.pk)
        call.return_value = ProviderResult("已使用保存配置。", 8, 4, "resp-saved")
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "使用保存的模型"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(session.credential_id, credential.pk)
        self.assertEqual(call.call_args.args[1], "selected-saved-key")

    def test_session_rejects_another_users_credential(self):
        """会话创建不能枚举或绑定其他用户的长期模型配置。"""
        credential = AIProviderCredential.objects.create(
            user=self.other,
            name="他人配置",
            provider="openai",
            encrypted_api_key=encrypt_api_key("other-users-key"),
            key_last_four="-key",
        )
        response = self.client.post(
            "/api/ai/chats/",
            {
                "credential": credential.pk,
                "title": "越权配置",
                "provider": "openai",
                "model": "gpt-5.6-luna",
                "context_rounds": 8,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("learning.ai.providers.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("8.8.8.8", 443))])
    @patch("learning.ai.views.call_provider")
    def test_saved_key_is_not_sent_to_a_different_endpoint(self, call, _resolve):
        """会话 URL 与密钥绑定 URL 不同时，在供应商调用前拒绝请求。"""
        session = self.create_session(
            progress=None,
            provider="openai",
            adapter="openai_chat_completions",
            api_url="https://model.example/v1/chat/completions",
            model="model-v1",
            include_current_lesson=False,
        )
        AIProviderCredential.objects.create(
            user=self.user,
            provider="openai",
            adapter="openai_chat_completions",
            api_url="https://other.example/v1/chat/completions",
            model="model-v1",
            encrypted_api_key=encrypt_api_key("saved-key"),
            key_last_four="-key",
        )
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "不要泄露密钥"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("不匹配", str(response.data))
        call.assert_not_called()

    @patch("learning.ai.views.call_provider")
    def test_text_message_uses_course_context_without_changing_progress(self, call):
        session = self.create_session()
        call.return_value = ProviderResult("先解释边界，再验证。", 120, 24, "resp-1")
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "我为什么会卡住？", "api_key": "temporary-key"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(session.messages.count(), 2)
        messages = call.call_args.args[4]
        self.assertIn("AI 测试课程", messages[-1]["content"])
        self.assertIn("我为什么会卡住", messages[-1]["content"])
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, DayProgress.Status.IN_PROGRESS)
        self.assertEqual(self.progress.acceptance_checks, [False])
        self.assertFalse(AIProviderCredential.objects.exists())

    @patch("learning.ai.views.call_provider")
    def test_image_and_text_are_temporary_multimodal_context(self, call):
        session = self.create_session()
        call.return_value = ProviderResult("图中是一个错误输出。", 210, 32, "resp-image")
        source = SimpleUploadedFile("trace.py", b"raise ValueError('broken')", content_type="text/x-python")
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {
                "content": "分析这些附件",
                "api_key": "temporary-key",
                "attachments": [self.image_upload(), source],
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 201, response.data)
        provider_attachments = call.call_args.args[4][-1]["attachments"]
        self.assertEqual({item["kind"] for item in provider_attachments}, {"image", "text"})
        self.assertTrue(next(item for item in provider_attachments if item["kind"] == "image")["data"])
        user_message = AIChatMessage.objects.get(session=session, role=AIChatMessage.Role.USER)
        self.assertEqual([item["name"] for item in user_message.attachments], ["question.jpg", "trace.py"])
        self.assertNotIn("data", str(user_message.attachments))
        self.assertNotIn("raise ValueError", str(user_message.attachments))

    @patch("learning.ai.views.call_provider")
    def test_provider_failure_keeps_history_and_learning_state_unchanged(self, call):
        session = self.create_session()
        call.side_effect = ProviderError("上游不可用", status_code=502, code="provider_unavailable")
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "失败请求", "api_key": "temporary-key"},
            format="json",
        )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(session.messages.count(), 0)
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, DayProgress.Status.IN_PROGRESS)

    @patch("learning.ai.services.cache.delete", side_effect=OSError("redis unavailable"))
    @patch("learning.ai.views.call_provider")
    def test_cache_failure_after_provider_success_does_not_create_a_false_retry(self, call, _delete):
        session = self.create_session()
        call.return_value = ProviderResult("已成功回答。", 10, 5, "resp-cache")
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "成功后缓存断开", "api_key": "temporary-key"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(session.messages.count(), 2)

    def test_request_lock_and_invalid_attachment_are_rejected_before_provider(self):
        session = self.create_session()
        cache.set(f"ai:request-lock:{self.user.pk}", "1", 60)
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "重复请求", "api_key": "temporary-key"},
            format="json",
        )
        self.assertEqual(response.status_code, 409)
        cache.delete(f"ai:request-lock:{self.user.pk}")
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {
                "content": "危险附件",
                "api_key": "temporary-key",
                "attachments": SimpleUploadedFile("archive.zip", b"PK", content_type="application/zip"),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)

    @patch("learning.ai.views.call_provider")
    @patch("learning.ai.services.cache.add", side_effect=OSError("redis unavailable"))
    def test_cache_outage_fails_before_provider_without_changing_history(self, _cache_add, call_provider):
        session = self.create_session()
        response = self.client.post(
            f"/api/ai/chats/{session.pk}/messages/",
            {"content": "缓存故障", "api_key": "temporary-key"},
            format="json",
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["code"], "ai_cache_unavailable")
        call_provider.assert_not_called()
        self.assertFalse(session.messages.exists())

    @override_settings(AI_CONTEXT_CHAR_BUDGET=30)
    def test_context_budget_keeps_current_question_and_drops_oldest_messages(self):
        session = self.create_session(include_current_lesson=False, context_rounds=4)
        AIChatMessage.objects.create(session=session, role="user", content="很早的问题" * 10)
        AIChatMessage.objects.create(session=session, role="assistant", content="很早的回答" * 10)
        messages = build_provider_messages(session, "当前问题", [], {})
        self.assertEqual(messages, [{"role": "user", "content": "当前问题", "attachments": []}])

    @override_settings(AI_IMAGE_CONTEXT_MAX_BYTES=4)
    def test_historical_images_have_an_independent_payload_budget(self):
        session = self.create_session(include_current_lesson=False)
        message = AIChatMessage.objects.create(
            session=session,
            role="user",
            content="看图",
            attachments=[{"name": "large.jpg", "kind": "image"}],
        )
        cache.set(
            f"ai:attachments:{self.user.pk}:{message.pk}",
            [{"name": "large.jpg", "kind": "image", "media_type": "image/jpeg", "data": "12345"}],
            60,
        )
        messages = build_provider_messages(session, "继续解释", [], {})
        self.assertEqual(messages[0]["content"], "看图")
        self.assertEqual(messages[0]["attachments"], [])

    @override_settings(AI_ASSISTANT_ENABLED=False)
    def test_feature_flag_hides_chat_without_affecting_catalog(self):
        catalog = self.client.get("/api/ai/providers/")
        self.assertEqual(catalog.status_code, 200)
        self.assertFalse(catalog.data["enabled"])
        self.assertEqual(self.client.get("/api/ai/chats/").status_code, 404)


@override_settings(
    AI_ASSISTANT_ENABLED=True,
    AI_ATTACHMENT_TEXT_MAX_CHARS=12,
    AI_PDF_MAX_PAGES=2,
)
class AIAttachmentTests(TestCase):
    """验证文件读取只提取受限文本，并明确标记截断。"""

    def test_text_attachment_supports_gb18030_and_truncation(self):
        upload = SimpleUploadedFile("说明.txt", "这是一段超过限制的中文文本".encode("gb18030"), content_type="text/plain")
        prepared = prepare_attachments([upload])[0]
        self.assertEqual(prepared.kind, "text")
        self.assertTrue(prepared.truncated)
        self.assertLessEqual(len(prepared.text), 12)

    @override_settings(AI_ATTACHMENT_MAX_BYTES=1024 * 1024, AI_ATTACHMENT_MAX_FILES=2)
    def test_single_image_cannot_borrow_other_attachment_size_allowance(self):
        upload = SimpleUploadedFile("oversized.jpg", b"x" * (1024 * 1024 + 1), content_type="image/jpeg")
        with self.assertRaisesRegex(ValidationError, "超过"):
            prepare_attachments([upload])

    @patch("learning.ai.attachments.PdfReader")
    def test_pdf_reads_only_page_limit(self, reader_class):
        pages = [Mock(extract_text=Mock(return_value=f"第 {index} 页正文")) for index in range(3)]
        reader_class.return_value = Mock(is_encrypted=False, pages=pages)
        upload = SimpleUploadedFile("notes.pdf", b"%PDF-test", content_type="application/pdf")
        prepared = prepare_attachments([upload])[0]
        self.assertEqual(prepared.kind, "text")
        self.assertTrue(prepared.truncated)
        self.assertNotIn("第 2 页", prepared.text)


class AIProviderBoundaryTests(TestCase):
    """验证模型供应商响应在反序列化前受到硬边界保护。"""

    @override_settings(AI_REQUEST_TIMEOUT_SECONDS=5, AI_PROVIDER_RESPONSE_MAX_BYTES=4)
    @patch("learning.ai.providers.HTTP_OPENER")
    def test_oversized_provider_response_is_rejected(self, opener):
        """拒绝超过配置上限的上游正文，避免无界读取占满工作进程内存。"""
        response = opener.open.return_value.__enter__.return_value
        response.read.return_value = b"12345"
        with self.assertRaisesRegex(ProviderError, "数据过大"):
            _request_json("https://api.openai.com/v1/models", {})
        response.read.assert_called_once_with(5)

    @override_settings(AI_RESPONSE_MAX_CHARS=4)
    @patch("learning.ai.providers._request_json")
    def test_oversized_model_text_is_rejected_before_persistence(self, request_json):
        """拒绝超过文字上限的模型结果，即使整个 JSON 响应仍在网络上限内。"""
        request_json.return_value = {
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "12345"}]}]
        }
        with self.assertRaisesRegex(ProviderError, "文本超过"):
            call_provider(
                settings.AI_PROVIDERS["openai"],
                "temporary-key",
                "gpt-5.6-luna",
                "system",
                [{"role": "user", "content": "question", "attachments": []}],
                128,
                "anonymous",
            )

    @patch("learning.ai.providers._request_json")
    def test_invalid_usage_values_are_normalized(self, request_json):
        """供应商用量缺失或格式异常时保留回答，并把不可保存数值归零。"""
        request_json.return_value = {
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
            "usage": {"input_tokens": "invalid", "output_tokens": -3},
        }
        result = call_provider(
            settings.AI_PROVIDERS["openai"],
            "temporary-key",
            "gpt-5.6-luna",
            "system",
            [{"role": "user", "content": "question", "attachments": []}],
            128,
            "anonymous",
        )
        self.assertEqual((result.input_tokens, result.output_tokens), (0, 0))

    @patch("learning.ai.providers.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("8.8.8.8", 443))])
    def test_base_url_uses_each_adapter_endpoint_and_full_url_is_idempotent(self, _resolve):
        """按协议补全 Base URL，并避免旧的完整端点被重复拼接。"""
        cases = {
            "openai_chat_completions": "https://tokenrhythm.studio/v1/chat/completions",
            "openai_responses": "https://tokenrhythm.studio/v1/responses",
            "anthropic_messages": "https://tokenrhythm.studio/v1/messages",
        }
        for adapter, expected in cases.items():
            with self.subTest(adapter=adapter):
                self.assertEqual(provider_endpoint_url("https://TOKENRHYTHM.STUDIO/v1/", adapter), expected)
                self.assertEqual(provider_endpoint_url(expected, adapter), expected)

    def test_public_url_validator_blocks_loopback_and_credentials(self):
        """URL 校验同时拒绝内网目标和可隐藏真实目标的内嵌凭据。"""
        with self.assertRaisesRegex(ValueError, "内网"):
            validate_public_https_url("https://127.0.0.1/v1/chat/completions")
        with self.assertRaisesRegex(ValueError, "账号"):
            validate_public_https_url("https://user:secret@example.com/v1/chat/completions")
        with self.assertRaisesRegex(ValueError, "查询参数"):
            validate_public_https_url("https://example.com/v1/chat/completions?api-key=secret")

    @patch("learning.ai.providers._request_json")
    def test_openai_chat_compatible_adapter_normalizes_text_and_images(self, request_json):
        """OpenAI 兼容协议发送标准图片块并读取 Chat Completions 文本。"""
        request_json.return_value = {
            "id": "chat-1",
            "choices": [{"message": {"content": "看到了错误截图。"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        result = call_provider(
            {
                "adapter": "openai_chat_completions",
                "api_url": "https://tokenrhythm.studio/v1/chat/completions",
                "custom_url": False,
            },
            "temporary-key",
            "deepseek-v4-pro",
            "system",
            [{
                "role": "user",
                "content": "分析截图",
                "attachments": [{"kind": "image", "media_type": "image/png", "data": "YWJj"}],
            }],
            128,
            "anonymous",
        )
        payload = request_json.call_args.args[2]
        self.assertEqual(payload["model"], "deepseek-v4-pro")
        self.assertEqual(payload["messages"][1]["content"][1]["type"], "image_url")
        self.assertEqual((result.text, result.input_tokens, result.output_tokens), ("看到了错误截图。", 10, 5))
