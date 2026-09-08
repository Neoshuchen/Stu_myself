"""与明确课程主题绑定的首批闭卷题和离线实验，不执行学习者代码。"""

import hashlib
import json


# ponytail: 首批覆盖五个明确主题；题库扩大并需要后台编辑时再迁入课程内容管理。
# 同时核对路线、学习日和主题，课程改编后不能继续展示不匹配的题目。
PRACTICE = {
    ("python-foundation-60d", 2): {
        "topic": "变量绑定、对象、id、可变性",
        "questions": [
            {"id": "binding-alias-v1", "prompt": "a = [1]; b = a; b.append(2) 后，a 是什么？",
             "options": ["[1]", "[1, 2]", "[2]"], "answer": 1,
             "explanation": "赋值让两个名字指向同一个列表，append 修改这个共享对象。"},
            {"id": "binding-rebind-v1", "prompt": "a = [1]; b = a; b = [2] 后，a 是什么？",
             "options": ["[1]", "[2]", "[1, 2]"], "answer": 0,
             "explanation": "重新绑定 b 不会改变 a 指向的列表。"},
            {"id": "binding-copy-v1", "prompt": "要复制只含整数的列表 a，随后追加元素且不改变 a，应选哪种写法？",
             "options": ["b = a", "b = a.copy()", "b = id(a)"], "answer": 1,
             "explanation": "浅拷贝产生独立的外层列表；嵌套可变对象仍可能共享。"},
        ],
        "lab": {
            "id": "shared-list", "title": "案件一：被悄悄改写的原始清单",
            "brief": "调用函数只是想得到扩展清单，原清单却也变化了。定位共享对象，修复后证明输入保持不变。",
            "starter": 'def extend_items(items, extra):\n    """返回追加 extra 后的新列表，原 items 应保持不变。"""\n    result = items\n    result.append(extra)\n    return result\n',
            "checks": 'original = [1]\nassert extend_items(original, 2) == [1, 2]\nassert original == [1], "原始清单被修改"\nassert extend_items([], 3) == [3]\nassert extend_items([1], 1) == [1, 1]\n',
            "hint": "画出 items 和 result 指向哪个对象；区分复制对象与绑定名字。",
            "solution": "把 result = items 改为 result = items.copy()。这里只承诺复制外层列表，嵌套元素仍共享。",
        },
    },
    ("python-foundation-60d", 3): {
        "topic": "int、float、Decimal、算术与比较",
        "questions": [
            {"id": "numeric-float-v1", "prompt": "为什么 0.1 + 0.2 == 0.3 在 Python 中通常为 False？",
             "options": ["加法优先级不对", "二进制浮点不能精确表示部分十进制小数", "比较会转成字符串"], "answer": 1,
             "explanation": "浮点存储的是近似值，计算可能积累微小误差。"},
            {"id": "numeric-decimal-v1", "prompt": "想让 Decimal 表达精确的十进制 0.1，应如何构造？",
             "options": ["Decimal(0.1)", "Decimal('0.1')", "int(0.1)"], "answer": 1,
             "explanation": "从字符串构造避免把已有的浮点误差带进 Decimal。"},
            {"id": "numeric-divide-v1", "prompt": "Python 中 7 // 2 和 7 % 2 的结果分别是什么？",
             "options": ["3.5 和 0", "3 和 1", "4 和 -1"], "answer": 1,
             "explanation": "// 为向下取整除法，% 为余数；7 = 3 × 2 + 1。"},
        ],
        "lab": {
            "id": "decimal-total", "title": "案件二：对不上的小数总和",
            "brief": "输入为十进制数字字符串，合计必须保留精确小数语义。调查转换在哪一步丢失了精度。",
            "starter": 'from decimal import Decimal\n\ndef total(values):\n    """汇总十进制字符串 values，返回精确的 Decimal 总和。"""\n    return Decimal(sum(float(value) for value in values))\n',
            "checks": 'assert total(["0.1", "0.2"]) == Decimal("0.3"), "十进制精度丢失"\nassert total([]) == Decimal("0")\nassert total(["1.25", "-0.25"]) == Decimal("1.00")\nassert isinstance(total([]), Decimal)\n',
            "hint": "不要先转换成 float 再交给 Decimal。",
            "solution": "返回 sum((Decimal(value) for value in values), Decimal('0'))。从输入开始保持 Decimal，空输入也返回 Decimal。",
        },
    },
    ("python-foundation-60d", 6): {
        "topic": "if、elif、else、真值、短路、for、range、enumerate、zip",
        "questions": [
            {"id": "loop-range-v1", "prompt": "list(range(1, 4)) 的结果是什么？",
             "options": ["[1, 2, 3, 4]", "[1, 2, 3]", "[0, 1, 2, 3]"], "answer": 1,
             "explanation": "range 包含起点，不包含终点。"},
            {"id": "loop-short-circuit-v1", "prompt": "items = [] 时，bool(items) and items[0] > 0 会怎样？",
             "options": ["返回 False，不访问 items[0]", "抛出 IndexError", "返回 True"], "answer": 0,
             "explanation": "and 在左侧为假时短路，不会计算右侧。"},
            {"id": "loop-enumerate-v1", "prompt": "要同时获得列表元素及其从 1 开始的序号，应使用什么？",
             "options": ["zip(items)", "enumerate(items, start=1)", "range(items)"], "answer": 1,
             "explanation": "enumerate 的 start 参数指定起始计数。"},
        ],
        "lab": {
            "id": "missing-endpoint", "title": "案件三：消失的最后一个数",
            "brief": "函数应返回从 1 到 n（包含 n）的整数总和，n 为非负整数。用边界样例找出遗漏。",
            "starter": 'def sum_to(n):\n    """接收非负整数 n，返回从 1 到 n（含 n）的总和。"""\n    result = 0\n    # 逐项累加，检查循环是否覆盖约定中的终点。\n    for value in range(1, n):\n        result += value\n    return result\n',
            "checks": 'assert sum_to(1) == 1, "终点没有参与累加"\nassert sum_to(0) == 0\nassert sum_to(4) == 10\nassert sum_to(10) == 55\n',
            "hint": "写出 range(1, 1) 实际会产生哪些值。",
            "solution": "把 range(1, n) 改为 range(1, n + 1)。验证 n=0、1 和普通正整数。",
        },
    },
    ("web-scraping-foundation-60d", 2): {
        "topic": "URL、方法、状态码、请求头、响应体",
        "questions": [
            {"id": "http-status-v1", "prompt": "收到 HTTP 200，是否足以证明拿到了预期业务数据？",
             "options": ["足够，200 等于业务成功", "不够，还要核对响应体及业务语义", "只要响应体非空就够"], "answer": 1,
             "explanation": "200 只表明 HTTP 层请求成功，响应可能是登录页或业务错误。"},
            {"id": "http-content-type-v1", "prompt": "哪个响应头用于声明响应体的媒体类型？",
             "options": ["Content-Type", "User-Agent", "Referer"], "answer": 0,
             "explanation": "Content-Type 描述响应内容类型，例如 application/json。"},
            {"id": "http-get-v1", "prompt": "GET 请求的查询参数通常放在哪里？",
             "options": ["状态码中", "URL 的查询字符串中", "只能放在 Cookie 中"], "answer": 1,
             "explanation": "查询字符串位于 URL 的问号后，由参数名和值组成。"},
        ],
    },
    ("git-mastery-7d", 1): {
        "topic": "工作区、暂存区、HEAD、对象库、配置、初始化、忽略与原子提交",
        "questions": [
            {"id": "git-stage-v1", "prompt": "修改文件后 git add，再修改同一文件，然后 git commit（不带 -a），提交的是哪份内容？",
             "options": ["最后一次 git add 暂存的内容", "工作区最新内容", "两次内容都会提交"], "answer": 0,
             "explanation": "commit 记录暂存区快照，之后的工作区修改需再次暂存。"},
            {"id": "git-cached-v1", "prompt": "提交前查看暂存区相对 HEAD 的差异，应使用哪个命令？",
             "options": ["git diff", "git diff --cached", "git status --short"], "answer": 1,
             "explanation": "git diff --cached 展示即将提交的内容差异；普通 diff 比较工作区与暂存区。"},
            {"id": "git-ignore-v1", "prompt": "把已跟踪文件写入 .gitignore，会自动停止跟踪吗？",
             "options": ["会，并删除历史", "不会，忽略规则主要作用于未跟踪文件", "会，下一次提交后生效"], "answer": 1,
             "explanation": "已跟踪文件不会因新增忽略规则自动离开索引。"},
        ],
    },
}


def practice_for(day):
    """返回与学习日路线和主题完全匹配的练习；不匹配时返回空字典。"""
    practice = PRACTICE.get((day.plan.slug, day.day_number), {})
    return practice if practice.get("topic") == day.core_knowledge else {}


def review_quiz(day):
    """返回学习日的题目及版本标记，提交前不输出正确答案和解析。"""
    questions = practice_for(day).get("questions", [])
    if not questions:
        return None
    token = hashlib.sha256(json.dumps(questions, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {
        "token": token,
        "questions": [{key: question[key] for key in ("id", "prompt", "options")} for question in questions],
    }


def grade_review(day, answers, token):
    """校验并判定学习日全部题目，返回评级与答案快照；非法或过期提交抛出 ValueError。"""
    quiz = review_quiz(day)
    questions = practice_for(day).get("questions", [])
    if not quiz or token != quiz["token"]:
        raise ValueError("题目已更新，请刷新复习队列后重新作答。")
    if not isinstance(answers, dict) or set(answers) != {q["id"] for q in questions}:
        raise ValueError("请回答全部题目后再提交。")
    results = []
    # 在服务端核对选项和判分；客户端评级不能覆盖实际作答结果。
    for question in questions:
        selected = answers[question["id"]]
        if type(selected) is not int or not 0 <= selected < len(question["options"]):
            raise ValueError("存在无效选项，请重新选择。")
        results.append({
            "id": question["id"], "prompt": question["prompt"],
            "selected": question["options"][selected],
            "expected": question["options"][question["answer"]],
            "correct": selected == question["answer"], "explanation": question["explanation"],
        })
    correct = sum(item["correct"] for item in results)
    rating = "mastered" if correct == len(results) else "unsure" if correct else "forgot"
    return rating, results
