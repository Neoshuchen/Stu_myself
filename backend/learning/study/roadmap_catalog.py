import json
from copy import deepcopy
from pathlib import Path


CURRENT_SCHEMA_VERSION = 2
PRIVATE_RESOURCE_MARKER = "yuque.com"
CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "system_roadmaps.v2.json"
PLAN_FIELDS = (
    "slug", "title", "subtitle", "summary", "audience", "total_days", "estimated_weeks",
    "accent_start", "accent_end", "days",
)
DAY_FIELDS = (
    "day_number", "phase", "week_number", "week_title", "title", "core_knowledge",
    "hands_on_task", "acceptance_criteria", "estimated_minutes", "track", "content",
)


class CatalogError(ValueError):
    """课程目录结构或内容不符合导入约束时抛出的异常。"""

    pass


def _replace_strings(value, replacements):
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_strings(item, replacements) for key, item in value.items()}
    return value


def migrate_catalog(catalog):
    catalog = deepcopy(catalog)
    version = catalog.get("schema_version", 1)
    if version == 1:
        catalog = _replace_strings(catalog, {
            "Python 3.10": "Python 3.12",
            "/zh-cn/3.10/": "/zh-cn/3.12/",
        })
        catalog["schema_version"] = 2
        catalog.pop("runtime", None)
        catalog["course_baseline"] = {"python": "3.12"}
        catalog.setdefault("content_version", 7)
        version = 2
    if version != CURRENT_SCHEMA_VERSION:
        raise CatalogError(f"不支持课程目录版本 {version}，当前版本为 {CURRENT_SCHEMA_VERSION}。")
    return catalog


def validate_catalog(catalog):
    if catalog.get("course_baseline", {}).get("python") != "3.12":
        raise CatalogError("系统课程内容的Python基线必须是3.12。")
    if not isinstance(catalog.get("content_version"), int) or catalog["content_version"] < 1:
        raise CatalogError("课程目录必须声明有效的content_version。")
    # 内部知识库只参与编辑审核，不能进入学习者可见的系统目录或参考资料。
    if PRIVATE_RESOURCE_MARKER in json.dumps(catalog, ensure_ascii=False).casefold():
        raise CatalogError("系统课程目录不能包含内部知识库地址。")
    roadmaps = catalog.get("roadmaps")
    if not isinstance(roadmaps, list) or not roadmaps:
        raise CatalogError("课程目录必须包含roadmaps列表。")

    slugs = set()
    for plan in roadmaps:
        missing = [field for field in PLAN_FIELDS if field not in plan]
        if missing:
            raise CatalogError(f"路线缺少字段：{', '.join(missing)}。")
        if plan["slug"] in slugs:
            raise CatalogError(f"路线slug重复：{plan['slug']}。")
        slugs.add(plan["slug"])

        days = plan["days"]
        if plan["total_days"] != len(days):
            raise CatalogError(f"{plan['slug']}声明天数与实际天数不一致。")
        if [day.get("day_number") for day in days] != list(range(1, len(days) + 1)):
            raise CatalogError(f"{plan['slug']}的学习日必须从1开始连续排列。")
        for day in days:
            missing = [field for field in DAY_FIELDS if field not in day]
            if missing:
                raise CatalogError(f"{plan['slug']} Day {day.get('day_number')} 缺少字段：{', '.join(missing)}。")
            if not isinstance(day["acceptance_criteria"], list) or not day["acceptance_criteria"]:
                raise CatalogError(f"{plan['slug']} Day {day['day_number']} 缺少验收条件。")
            if not isinstance(day["content"], dict) or not day["content"].get("knowledge_details"):
                raise CatalogError(f"{plan['slug']} Day {day['day_number']} 缺少知识详情。")
            if day["content"].get("version") != catalog["content_version"]:
                raise CatalogError(f"{plan['slug']} Day {day['day_number']} 的内容版本不一致。")
            if day["content"].get("track") != day["track"]:
                raise CatalogError(f"{plan['slug']} Day {day['day_number']} 的课程分类不一致。")
    return catalog


def load_catalog(path=CATALOG_PATH):
    try:
        catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"无法读取课程目录：{exc}") from exc
    return validate_catalog(migrate_catalog(catalog))


SYSTEM_ROADMAPS = load_catalog()["roadmaps"]
