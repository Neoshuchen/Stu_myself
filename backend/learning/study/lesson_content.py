import re

from .teaching_content import build_teaching_sections, concept_notes, example_for, infer_accelerated_kind, track_kind


def split_knowledge_points(core_knowledge):
    return [part.strip(" `") for part in re.split(r"[、，,/]", core_knowledge) if part.strip(" `")]


def detail(
    name, summary, basic, mechanism, tools, pitfalls, requirement, code, language, command, expected, mastery,
    resources=None, practice_steps=None,
):
    return {
        "name": name,
        "summary": summary,
        "basic": basic,
        "mechanism": mechanism,
        "tools": tools,
        "pitfalls": pitfalls,
        "implementation_requirement": requirement,
        "reference_code": code.strip(),
        "language": language,
        "run_command": command,
        "expected_results": expected,
        "mastery": mastery,
        "resources": resources or [],
        "practice_steps": practice_steps or [],
    }


TRACK_GUIDES = {
    "python": {
        "label": "Python 工程实践",
        "summary": "通过可运行代码、断言和错误输入掌握语言行为，而不是停留在语法名称。",
        "basic": "先把知识点放进一个输入和输出都明确的小函数，再用类型、值、异常和资源状态观察实际行为。Python 名称绑定、可变对象、迭代协议和异常传播等概念，都应由解释器输出或测试证明。",
        "mechanism": "按“输入解析 → 核心处理 → 输出/异常”拆分调用链；正常值、边界值和非法值各运行一次。涉及文件、网络或并发时，还要证明资源关闭、超时和取消路径可控。",
        "tools": ["Python 3.12", "assert/unittest", "REPL", "标准库文档"],
        "pitfalls": ["只抄语法示例，不验证输入输出", "只跑成功路径，异常契约不明确", "示例依赖当前目录、全局状态或未固定版本"],
        "language": "python",
        "command": "python practice.py",
        "code": '''from dataclasses import asdict, dataclass

TOPIC = {point!r}


@dataclass(frozen=True)
class Observation:
    case: str
    value_type: str
    value_repr: str


def observe(case, value):
    return Observation(case, type(value).__name__, repr(value))


if __name__ == "__main__":
    normal = observe("normal", {{"topic": TOPIC, "items": [1, 2]}})
    boundary = observe("boundary", None)
    assert normal.value_type == "dict"
    assert boundary.value_repr == "None"
    print(asdict(normal))
    print(asdict(boundary))
''',
        "resources": [
            {"title": "Python 3.12 官方教程", "url": "https://docs.python.org/zh-cn/3.12/tutorial/"},
            {"title": "Python 3.12 标准库", "url": "https://docs.python.org/zh-cn/3.12/library/"},
            {"title": "Python 3.12 语言参考", "url": "https://docs.python.org/zh-cn/3.12/reference/"},
        ],
    },
    "crawler": {
        "label": "数据采集实践",
        "summary": "在本地或明确授权的靶场中，用请求快照、解析结果和失败记录还原完整采集链路。",
        "basic": "一个可维护的采集任务至少包含请求、响应校验、解析、去重、持久化和失败恢复。学习知识点时要指出它位于哪一层、消费什么数据、向下一层交付什么结构。",
        "mechanism": "先在 Network 或本地服务中固定请求样本，再离线解析保存的响应；请求阶段设置超时和频率，解析阶段处理缺字段，写入阶段保证幂等。这样网络变化与解析错误可以分别定位。",
        "tools": ["Chrome Network", "requests", "Scrapy", "本地 HTTP 靶场"],
        "pitfalls": ["没有授权、频率和退出机制", "边请求边调解析导致样本不可复现", "忽略状态码、编码、分页终止与重复写入"],
        "language": "python",
        "command": "python practice.py",
        "code": '''from html.parser import HTMLParser
from urllib.parse import urljoin

TOPIC = {point!r}
HTML = '<a href="/detail/1">first</a><a href="/detail/1">repeat</a>'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.items.append(urljoin("http://127.0.0.1:8000/list", href))


parser = Links()
parser.feed(HTML)
result = list(dict.fromkeys(parser.items))
assert result == ["http://127.0.0.1:8000/detail/1"]
print({{"topic": TOPIC, "result": result}})
''',
        "resources": [
            {"title": "MDN HTTP 指南", "url": "https://developer.mozilla.org/zh-CN/docs/Web/HTTP"},
            {"title": "Requests 高级用法", "url": "https://requests.readthedocs.io/en/stable/user/advanced/"},
            {"title": "Scrapy 官方文档", "url": "https://docs.scrapy.org/en/latest/"},
        ],
    },
    "javascript": {
        "label": "JavaScript 授权分析",
        "summary": "用断点、调用栈和固定测试向量追踪真实数据流，再完成可对拍的最小复现。",
        "basic": "先确认知识点在浏览器、Node.js 或构建工具中的运行位置，再记录输入、返回值、异常、this、闭包状态或字节序。逆向分析的结论必须能回到断点、调用栈或测试向量。",
        "mechanism": "从 Network 的目标字段反向寻找 Initiator，在 Sources 中用条件断点缩小到首次生成位置；保存未改动样本，再做 Hook 或 AST 变换。每次只验证一个假设，并与原实现对拍。",
        "tools": ["Chrome DevTools", "Node.js", "Babel AST", "固定测试向量"],
        "pitfalls": ["全局搜索后直接猜算法，没有调用证据", "格式化或改写样本后丢失原始语义", "只对拍一组输入，忽略编码、时间与随机状态"],
        "language": "javascript",
        "command": "node practice.mjs",
        "code": '''const TOPIC = {point_json};

function observe(label, fn, input) {{
  try {{
    const output = fn(input);
    return {{ label, input, output, error: null }};
  }} catch (error) {{
    return {{ label, input, output: null, error: error.name }};
  }}
}}

const target = value => new TextEncoder().encode(String(value)).length;
const vectors = [observe("ascii", target, "abc"), observe("unicode", target, "学习")];
console.assert(vectors[0].output === 3 && vectors[1].output === 6);
console.table(vectors.map(item => ({{ topic: TOPIC, ...item }})));
''',
        "resources": [
            {"title": "Chrome DevTools JavaScript 调试", "url": "https://developer.chrome.com/docs/devtools/javascript/"},
            {"title": "Chrome DevTools Network", "url": "https://developer.chrome.com/docs/devtools/network/"},
            {"title": "Babel Parser 文档", "url": "https://babeljs.io/docs/babel-parser"},
        ],
    },
    "android": {
        "label": "Android 授权实验",
        "summary": "把 APK 静态证据、运行时日志和 Hook 结果连成可复现链路，并严格限定自有或授权样本。",
        "basic": "先冻结 APK、系统镜像、ABI、包名与 SHA256，再判断知识点属于组件、DEX/Java、网络、存储还是 Native 层。每个结论同时保留静态位置和至少一种运行时证据。",
        "mechanism": "以界面操作为起点，通过 logcat、Network、调用栈或 Frida 消息定位真实入口；静态工具用于提出候选，动态实验用于排除候选。版本、ClassLoader、进程和重载签名必须进入记录。",
        "tools": ["adb/logcat", "JADX/Apktool", "Frida", "SHA256 证据清单"],
        "pitfalls": ["分析未授权应用或真实用户数据", "客户端与 frida-server 版本/架构不匹配", "只保留 Hook 输出，无法对应 APK 版本和触发步骤"],
        "language": "javascript",
        "command": "frida -U -f com.example.lab -l observe.js",
        "code": '''const TOPIC = {point_json};

setImmediate(() => {{
  if (!Java.available) {{
    send({{ topic: TOPIC, ok: false, reason: "Java VM unavailable" }});
    return;
  }}
  Java.perform(() => {{
    send({{
      topic: TOPIC,
      ok: true,
      android: Java.androidVersion,
      process: Process.id,
      note: "在本人 Debug App 中替换为当天确认的最小 Hook 点"
    }});
  }});
}});
''',
        "resources": [
            {"title": "Android 应用基础", "url": "https://developer.android.com/guide/components/fundamentals"},
            {"title": "Frida JavaScript API", "url": "https://frida.re/docs/javascript-api/"},
            {"title": "OWASP MASTG", "url": "https://mas.owasp.org/MASTG/"},
        ],
    },
    "ios": {
        "label": "iOS 授权实验",
        "summary": "将签名、Mach-O 静态位置、LLDB/Frida 运行时证据与固定测试向量对应起来。",
        "basic": "先记录自有或授权 IPA/App 的 Bundle ID、架构、系统版本、签名与哈希，再判断知识点位于 Objective-C/Swift 运行时、Mach-O、网络、存储或加载链的哪一层。",
        "mechanism": "静态字符串和交叉引用只产生候选；用 LLDB 断点、调用栈或最小 Frida 脚本验证接收者、参数和返回值。ASLR 下保存模块基址与偏移，不把一次绝对地址写成通用结论。",
        "tools": ["Xcode/LLDB", "codesign/otool", "Frida", "测试向量"],
        "pitfalls": ["把模拟器结果直接等同于真机", "混淆签名身份、Entitlement 与完整性校验", "忽略架构、ASLR、Swift 符号和系统版本差异"],
        "language": "text",
        "command": "lldb /path/to/AuthorizedLab.app",
        "code": '''# LLDB 最小观测脚本（仅用于本人或授权测试 App）
# 知识点：{point}
target create /path/to/AuthorizedLab.app
breakpoint set --name main
run
thread backtrace
register read
# 将当天确认的方法名或“模块 + 偏移”替换到新断点，并保存命中次数、参数和返回值。
''',
        "resources": [
            {"title": "Apple Code Signing", "url": "https://developer.apple.com/documentation/xcode/using-the-latest-code-signature-format"},
            {"title": "LLDB 官方教程", "url": "https://lldb.llvm.org/use/tutorial.html"},
            {"title": "Frida JavaScript API", "url": "https://frida.re/docs/javascript-api/"},
        ],
    },
}


def track_key(track, point, task):
    if track == "python-foundation-60d":
        return "python"
    if track == "web-scraping-foundation-60d":
        return "crawler"
    if track == "javascript-reverse-60d":
        return "javascript"
    if track == "android-reverse-60d":
        return "android"
    if track == "ios-reverse-60d":
        return "ios"
    text = f"{point} {task}".lower()
    if any(word in text for word in ("android", "apk", "adb", "smali", "dex", "frida", "java hook", "jni", "elf", "arm64", "jadx", "okhttp")):
        return "android"
    if any(word in text for word in ("ios", "ipa", "mach-o", "lldb", "objective-c", "swift", "xcode", "keychain")):
        return "ios"
    if any(word in text for word in ("javascript", "node", "promise", "ast", "浏览器", "补环境", "hook", "webpack", "source map")):
        return "javascript"
    if any(word in text for word in ("http", "爬虫", "采集", "scrapy", "requests", "xpath", "css选择器", "cookie", "代理")):
        return "crawler"
    return "python"


def contextual_detail(point, task, criteria, track=""):
    guide = TRACK_GUIDES[track_key(track, point, task)]
    kind = track_kind(track)
    if kind == "accelerated":
        kind = infer_accelerated_kind(f"{point} {task}")
    teaching_example = example_for(kind, point) if kind else None
    concepts = concept_notes(kind, point) if kind else []
    teaching_note = " ".join(item["explanation"] for item in concepts[:2]) if concepts else guide["basic"]
    resources = list(guide["resources"])
    point_json = repr(point).replace("'", '"')
    code = teaching_example["code"] if teaching_example else guide["code"].format(point=point, point_json=point_json)
    expected = list(criteria) or ["产物可由他人复现", "结论与证据能够相互对应"]
    item = detail(
        point,
        f"{teaching_note} 今日通过“{task}”把原理落实为可运行、可验证的能力。",
        f"{teaching_note} 本日把这个原理用于“{task}”。",
        guide["mechanism"],
        guide["tools"],
        guide["pitfalls"],
        f"先独立完成“{task}”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。",
        code,
        teaching_example["language"] if teaching_example else guide["language"],
        teaching_example["command"] if teaching_example else guide["command"],
        expected + ["失败样例能稳定触发且原因可解释", "运行命令、环境版本与关键输出已保存"],
        [f"闭卷说明{point}的输入、输出、依赖状态和不适用边界", "不看参考实现完成正常与失败两条路径", "能用断言、调用栈、日志或测试向量证明结论", "能把失败收敛为下一步可执行的问题"],
        resources,
        ["阅读前置要求与概念图，写出当天输入、处理和输出", "逐段运行参考骨架并解释每一步状态变化", "关闭参考答案，独立完成正常路径", "加入失败或边界输入，保存命令、输出并按验收条件复盘"],
    )
    item["code_explanation"] = teaching_example["explanation"] if teaching_example else ["先辨认示例输入与预期输出。", "替换成当天任务数据，并增加失败输入验证边界。"]
    item["what_it_solves"] = teaching_note
    return item


def build_lesson_content(day_number, core_knowledge, task, criteria, track=""):
    # A system lesson is one coherent topic, not several disconnected cards for
    # every comma-separated term. The concept map still explains each term.
    points = split_knowledge_points(core_knowledge) if not track_kind(track) else [core_knowledge.strip(" `")]
    details = [contextual_detail(point, task, criteria, track) for point in points]
    for item in details:
        item["role"] = f"在本日综合任务中，它直接服务于：{task}"
        guide = TRACK_GUIDES[track_key(track, item["name"], task)]
        if not item.get("resources"):
            item["resources"] = list(guide["resources"])
        if not item.get("practice_steps"):
            item["practice_steps"] = [
                "先写下预期结果和一个可能失败的边界",
                "不看参考实现完成最小实验并保存命令",
                "加入失败输入，记录异常、日志或调用轨迹",
                "按验收条件自测，最后核对参考资料并复盘",
            ]
        item.setdefault("code_explanation", ["逐段运行参考实现，记录每段对数据或状态造成的变化。", "替换为当天任务的真实输入后，再补充失败路径。"])
    kind = track_kind(track)
    if kind == "accelerated":
        kind = infer_accelerated_kind(f"{core_knowledge} {task}")
    teaching = build_teaching_sections(day_number, core_knowledge, task, criteria, kind) if kind else {
        "workflow": [
            {"title": "闭卷回忆", "body": f"先不查资料，写下你对“{core_knowledge}”的理解、适用范围和一个仍不确定的问题。"},
            {"title": "独立复现", "body": f"围绕“{task}”先独立完成最小实现或实验，再打开知识详情核对参考实现。"},
            {"title": "保存证据", "body": "记录输入、输出、错误路径、环境版本和中间产物。"},
        ]
    }
    return {
        "version": 5,
        "knowledge_details": details,
        **teaching,
    }

