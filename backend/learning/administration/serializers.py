"""管理员用户治理和学习路线审核的输入输出契约。"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from ..models import Enrollment, LearningPlan, PlanDay
from ..study.serializers import CustomPlanDaySerializer

User = get_user_model()

# 知识点的全部可编辑字段。写回时按这个白名单过滤，避免前端往 content 里塞进无关键。
KNOWLEDGE_FIELDS = (
    "name", "summary", "what_it_solves", "role", "basic", "mechanism", "tools", "pitfalls",
    "implementation_requirement", "reference_code", "language", "run_command", "expected_results",
    "code_explanation", "mastery", "practice_steps", "resources",
)
KNOWLEDGE_LIST_FIELDS = (
    "tools", "pitfalls", "expected_results", "mastery", "practice_steps", "code_explanation", "resources",
)


class AdminUserSerializer(serializers.ModelSerializer):
    """输出管理员用户治理页面所需的账号和学习统计。"""

    name = serializers.SerializerMethodField()
    enrollment_count = serializers.IntegerField(read_only=True)
    completed_days = serializers.IntegerField(read_only=True)
    last_studied_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "name", "is_active", "is_staff", "date_joined",
            "last_login", "enrollment_count", "completed_days", "last_studied_at",
        )

    def get_name(self, obj):
        return obj.first_name or obj.username


class AdminLearningPlanSerializer(serializers.ModelSerializer):
    """校验并输出管理员审核的完整学习路线。"""

    days = CustomPlanDaySerializer(many=True, read_only=True)
    creator_name = serializers.SerializerMethodField()
    learner_count = serializers.SerializerMethodField()

    class Meta:
        model = LearningPlan
        fields = (
            "id",
            "slug",
            "title",
            "subtitle",
            "summary",
            "audience",
            "total_days",
            "estimated_weeks",
            "creator_name",
            "learner_count",
            "is_published",
            "review_status",
            "review_note",
            "created_at",
            "days",
        )
        # 审核状态只能走 approve/reject 动作，避免管理员直接 PATCH 绕过审核记录。
        read_only_fields = (
            "slug",
            "total_days",
            "estimated_weeks",
            "review_status",
            "review_note",
            "created_at",
        )

    def get_creator_name(self, obj):
        if not obj.creator:
            return "系统"
        return obj.creator.first_name or obj.creator.username

    def get_learner_count(self, obj):
        return obj.enrollments.filter(status__in=Enrollment.JOINED_STATUSES).count()


class AdminLearningPlanListSerializer(AdminLearningPlanSerializer):
    """路线管理列表：不带逐日正文，展开某条路线时再取详情。"""

    class Meta(AdminLearningPlanSerializer.Meta):
        fields = tuple(field for field in AdminLearningPlanSerializer.Meta.fields if field != "days")


# 知识点的全部可编辑字段。写回时按这个白名单过滤，避免前端往 content 里塞进无关键。
KNOWLEDGE_FIELDS = (
    "name", "summary", "what_it_solves", "role", "basic", "mechanism", "tools", "pitfalls",
    "implementation_requirement", "reference_code", "language", "run_command", "expected_results",
    "code_explanation", "mastery", "practice_steps", "resources",
)
KNOWLEDGE_LIST_FIELDS = (
    "tools", "pitfalls", "expected_results", "mastery", "practice_steps", "code_explanation", "resources",
)


class AdminPlanDayEditSerializer(serializers.ModelSerializer):
    """管理员编辑学习日正文。

    knowledge_details 存放在 content JSON 里，单独校验后合并写回，
    content 的其它键（learning_objectives、workflow 等）保持原样。
    """

    knowledge_details = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = PlanDay
        fields = (
            "title", "core_knowledge", "hands_on_task", "acceptance_criteria",
            "estimated_minutes", "commands", "reference_answer", "knowledge_details",
        )

    def validate_acceptance_criteria(self, value):
        items = self.clean_lines(value, "验收标准")
        if not items:
            raise serializers.ValidationError("至少需要一条验收标准。")
        return items

    def validate_commands(self, value):
        return self.clean_lines(value, "验证命令")

    def validate_knowledge_details(self, value):
        details = []
        for index, item in enumerate(value, start=1):
            cleaned = {key: item[key] for key in KNOWLEDGE_FIELDS if key in item}
            for key, item_value in cleaned.items():
                if key in KNOWLEDGE_LIST_FIELDS:
                    cleaned[key] = self.clean_lines(item_value, f"知识点 {index} 的 {key}")
                elif not isinstance(item_value, str):
                    raise serializers.ValidationError(f"知识点 {index} 的 {key} 必须是文本。")
            for key, label in (("name", "名称"), ("summary", "一句话说明")):
                if not cleaned.get(key, "").strip():
                    raise serializers.ValidationError(f"知识点 {index} 缺少{label}。")
            details.append(cleaned)
        if not details:
            raise serializers.ValidationError("至少保留一个知识点。")
        return details

    @staticmethod
    def clean_lines(value, label):
        """列表字段统一成去空白、去空行的字符串列表；resources 这类字典项原样保留。"""
        if not isinstance(value, list):
            raise serializers.ValidationError(f"{label}必须是列表。")
        cleaned = []
        for item in value:
            if isinstance(item, dict):
                cleaned.append(item)
            elif str(item).strip():
                cleaned.append(str(item).strip())
        return cleaned

    def update(self, instance, validated_data):
        details = validated_data.pop("knowledge_details", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if details is not None:
            content = instance.content if isinstance(instance.content, dict) else {}
            instance.content = {**content, "knowledge_details": details}
        instance.content_edited_at = timezone.now()
        instance.save()
        return instance

