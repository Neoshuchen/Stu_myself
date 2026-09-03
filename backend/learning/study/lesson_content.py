import re

from .teaching_content import (
    LIFESTYLE_TRACKS,
    build_teaching_sections,
    concept_notes,
    example_for,
    infer_accelerated_kind,
    track_kind,
)


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
    "agent": {
        "label": "Agent 工程实践",
        "summary": "把模型调用、工具、状态和终止条件组成可观测、可测试的执行闭环，而不是把多轮提示词误当成智能体。",
        "basic": "Agent 以目标和环境反馈驱动下一步行动；每一步都要明确输入消息、允许的工具、状态更新、停止条件与失败去向。固定流程优先使用普通代码，只有路径需要由模型动态选择时才引入 Agent。",
        "mechanism": "先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。",
        "tools": ["Python 3.12", "假模型与固定夹具", "JSON Schema", "pytest/unittest"],
        "pitfalls": ["没有步骤上限导致无限循环或费用失控", "把模型输出直接当可信参数执行", "只看最终答案而不保存工具轨迹与失败原因"],
        "language": "python",
        "command": "python practice.py",
        "code": '''from dataclasses import dataclass

TOPIC = {point!r}


@dataclass(frozen=True)
class Step:
    action: str
    argument: str


def decide(goal: str) -> Step:
    if not goal.strip():
        raise ValueError("goal is required")
    return Step("finish", f"已完成最小验证：{{goal}}")


result = decide(TOPIC)
assert result.action == "finish"
print(result)
''',
        "resources": [
            {"title": "Hello-Agents 教程", "url": "https://github.com/datawhalechina/hello-agents"},
            {"title": "Anthropic：Building effective agents", "url": "https://www.anthropic.com/engineering/building-effective-agents"},
            {"title": "Model Context Protocol 最新规范", "url": "https://modelcontextprotocol.io/specification/latest/architecture"},
        ],
    },
    "agent_tools": {
        "label": "Coding Agent 工具实践",
        "summary": "把安装、认证、项目指令、权限、上下文、执行和验收组成可回滚的日常开发流程，而不是把代码代理当成无需监督的自动写码器。",
        "basic": "Coding Agent 可以读取仓库、编辑文件并运行本机命令。每次使用前都要确认官方安装来源、当前版本、登录方式、工作目录、可写范围和审批策略；指令文件用于补充项目约定，不能替代沙箱与权限控制。",
        "mechanism": "先在测试仓库建立 Git 基线，再按官方文档安装并记录版本。任务按“只读理解 → 计划 → 小范围修改 → 测试 → diff 审查 → 提交或回滚”推进；外部连接、密钥、网络访问和不可逆命令始终使用最小权限与人工确认。",
        "tools": ["PowerShell/终端", "Git 测试仓库", "官方安装文档", "版本与差异记录"],
        "pitfalls": ["从非官方镜像复制过时或被篡改的安装命令", "把 API Key 写进仓库、提示词或共享会话", "未检查工作目录、权限和 diff 就允许代理执行高风险操作"],
        "language": "python",
        "command": "python practice.py",
        "code": '''from dataclasses import dataclass

TOPIC = {point!r}


@dataclass(frozen=True)
class AgentRun:
    tool: str
    repository_clean: bool
    approval_required: bool


run = AgentRun(TOPIC, repository_clean=True, approval_required=True)
assert run.repository_clean and run.approval_required
print(run)
''',
        "resources": [
            {"title": "Codex CLI 官方文档", "url": "https://developers.openai.com/codex/cli"},
            {"title": "Claude Code 官方文档", "url": "https://code.claude.com/docs/en/overview"},
            {"title": "OpenCode 官方文档", "url": "https://opencode.ai/docs/"},
        ],
    },
    "finance": {
        "label": "个人财务实践",
        "summary": "把收入、支出、债务、保障和长期目标放进同一套可核对的个人财务系统，而不是追逐短期收益或具体产品。",
        "basic": "个人财务学习先建立真实但脱敏的资产负债、现金流和目标基线，再依次处理预算、应急储备、债务、保险、投资与反诈骗。所有税务、征信和金融产品规则都要回到本人所在地监管机构和合同原文核验。",
        "mechanism": "每天只改变一个可观察变量，并保留计算过程、合同字段或决策依据。金额实验使用虚拟或脱敏数据；涉及投资时先检查期限、流动性、费用和最坏损失，不把历史收益或宣传承诺当成保证。",
        "tools": ["脱敏财务台账", "计算器或电子表格", "合同与账单原件", "金融监管机构官网"],
        "pitfalls": ["把收入当成可支配现金而遗漏固定负担", "只比较宣传收益而忽略费用、期限和本金损失", "在催促、保本高收益或共享屏幕话术下转账"],
        "language": "text",
        "command": "填写财务练习表并复核合计",
        "code": """主题：{point}\n已知事实：\n计算过程：\n风险与最坏情形：\n下一步行动：\n复核证据：""",
        "resources": [
            {"title": "CFPB Your Money, Your Goals", "url": "https://www.consumerfinance.gov/consumer-tools/educator-tools/your-money-your-goals/toolkit/"},
            {"title": "Investor.gov 投资入门", "url": "https://www.investor.gov/introduction-investing"},
            {"title": "金融监管总局风险提示", "url": "https://app.www.gov.cn/govdata/gov/202407/25/517630/article.html"},
        ],
    },
    "health": {
        "label": "健康与应急实践",
        "summary": "用可持续的睡眠、饮食、活动、就医和家庭应急习惯提升健康素养，同时明确自我照护不能替代专业诊疗和认证急救培训。",
        "basic": "健康管理从记录和环境调整开始，不自行诊断或擅自停药。持续或严重症状、意识或呼吸异常、胸痛、大出血等情况应及时联系当地急救和专业人员；急救动作只在合格培训、教具或明确指导下练习。",
        "mechanism": "使用睡眠、活动、饮食和症状记录寻找稳定模式，每次只尝试低风险、可逆的生活方式调整。应急学习按现场安全、呼救、能力范围内施救、交接和复盘推进，并定期检查家庭联系人与物资有效期。",
        "tools": ["健康记录表", "食品和药品标签", "家庭急救与应急清单", "国家卫健委及专业机构资料"],
        "pitfalls": ["根据单次指标自我诊断或擅自用药", "用保健品和网络偏方替代正规医疗", "未确认现场安全或超出训练范围实施急救"],
        "language": "text",
        "command": "填写健康练习表并完成安全边界核对",
        "code": """主题：{point}\n观察记录：\n低风险行动：\n停止条件或就医信号：\n专业来源：\n复盘日期：""",
        "resources": [
            {"title": "中国公民健康素养 66 条", "url": "https://www.nhc.gov.cn/xcs/c100123/202405/73a4927142f34152abed875634a3c13b.shtml"},
            {"title": "WHO 自我护理", "url": "https://www.who.int/zh/news-room/fact-sheets/detail/self-care-health-interventions"},
            {"title": "中国红十字会应急救护培训", "url": "https://www.redcross.org.cn/html/2026-05/114304.html"},
        ],
    },
    "communication": {
        "label": "沟通与问题解决实践",
        "summary": "把倾听、清晰表达、反馈、冲突、协商和决策练成可观察行为，而不是背诵话术或追求压服对方。",
        "basic": "有效沟通先区分事实、解释、感受、需要和请求，再根据对象选择信息结构与媒介。分歧处理中优先确认共同问题、双方利益和安全边界；不把操纵、威胁或模糊承诺包装成沟通技巧。",
        "mechanism": "每个主题都通过真实低风险场景、角色演练或录音回放验证。练习前定义目标和停止条件，练习后从对方复述准确度、行动是否清楚、误解是否减少和关系成本四方面复盘。",
        "tools": ["沟通观察表", "录音或书面草稿", "角色演练", "决策与复盘模板"],
        "pitfalls": ["急于给建议而没有确认对方真正的问题", "用模糊形容词代替具体事实和请求", "把一次妥协当成长期解决而不记录责任与期限"],
        "language": "text",
        "command": "完成沟通角色演练并保存复盘",
        "code": """场景：{point}\n沟通目标：\n观察到的事实：\n对方观点复述：\n我的请求与边界：\n下一步、负责人和期限：\n复盘：""",
        "resources": [
            {"title": "Digital.gov 简明语言指南", "url": "https://digital.gov/guides/plain-language/"},
            {"title": "Purdue OWL 论证逻辑", "url": "https://owl.purdue.edu/owl/general_writing/academic_writing/logic_in_argumentative_writing/index.html"},
            {"title": "Harvard Program on Negotiation", "url": "https://www.pon.harvard.edu/"},
        ],
    },
    "digital_literacy": {
        "label": "数字安全与信息素养实践",
        "summary": "同时保护账号、设备和数据，并用横向阅读与证据核验降低诈骗、误导信息和 AI 生成内容带来的风险。",
        "basic": "数字安全从资产清单、唯一口令、多因素认证、及时更新和可恢复备份开始；信息判断则先查发布者、原始证据和独立来源。所有练习使用本人账号、测试账户或离线样例，不点击真实可疑链接。",
        "mechanism": "先建立账号和数据的风险优先级，再逐项收紧权限并验证恢复路径。面对消息、网页、图片或 AI 回答时离开原页面横向查证，记录来源、日期、证据和不确定性，再决定保存、分享或行动。",
        "tools": ["密码管理器", "多因素认证与恢复码", "离线备份", "浏览器横向查证"],
        "pitfalls": ["多个重要账号复用口令或只依赖短信验证码", "备份从未做恢复演练或恢复密钥只存一处", "只看页面外观、域名后缀或 AI 语气就判断可信"],
        "language": "text",
        "command": "在测试账户完成数字安全检查并保存证据",
        "code": """主题：{point}\n资产或信息对象：\n威胁与影响：\n已核验的来源：\n保护或查证动作：\n恢复与报告路径：\n剩余风险：""",
        "resources": [
            {"title": "CISA Secure Our World", "url": "https://www.cisa.gov/secure-our-world"},
            {"title": "UNESCO 媒体与信息素养", "url": "https://www.unesco.org/en/media-information-literacy"},
            {"title": "Civic Online Reasoning", "url": "https://cor.inquirygroup.org/"},
        ],
    },
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


# 生活课程按主题选择一手资料，避免把“权威但无关”的链接机械轮换到每一天。
VERIFIED_RESOURCES = {
    "cfpb_toolkit": {"title": "CFPB 个人财务工具包", "url": "https://www.consumerfinance.gov/consumer-tools/educator-tools/your-money-your-goals/toolkit/"},
    "cfpb_debt": {"title": "CFPB 债务行动计划", "url": "https://files.consumerfinance.gov/f/documents/cfpb_your-money-your-goals_debt-action-plan_tool_2018-11.pdf"},
    "cfpb_savings": {"title": "CFPB 应急储蓄练习", "url": "https://www.consumerfinance.gov/consumer-tools/educator-tools/youth-financial-education/teach/activities/creating-savings-first-aid-kit/"},
    "pbccrc_query": {"title": "中国人民银行征信中心查询指南", "url": "https://www.pbccrc.org.cn/zxfw/gr/cx/20241029/6bb3ada5b92641779ee33e06c30f1e4c.html"},
    "pbccrc_dispute": {"title": "中国人民银行征信中心异议申请", "url": "https://www.pbccrc.org.cn/xczl/fwzy/20241102/f9dd936695874a5b8292095bc787317e.html"},
    "pboc_credit_rules": {"title": "征信业管理条例", "url": "https://www.pbccrc.org.cn/zcfg/20210701/357ba41f1c49929fe4d536f4b5f8cf06.html"},
    "investor_allocation": {"title": "Investor.gov 资产配置与再平衡", "url": "https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset"},
    "investor_dca": {"title": "Investor.gov 定期定额说明", "url": "https://www.investor.gov/introduction-investing/investing-basics/glossary/dollar-cost-averaging"},
    "investor_fees": {"title": "Investor.gov 投资费用提示", "url": "https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/updated"},
    "tax_policy": {"title": "国家税务总局税收政策库", "url": "https://fgk.chinatax.gov.cn/"},
    "tax_personal": {"title": "国家税务总局个人所得税法规", "url": "https://www.chinatax.gov.cn/chinatax/n363/ssfgk.html"},
    "insurance": {"title": "金融监管总局保险消费提示", "url": "https://www.nfra.gov.cn/chinese/OFFICE/PDF/958198.pdf"},
    "finance_fraud": {"title": "金融监管总局风险提示", "url": "https://app.www.gov.cn/govdata/gov/202407/25/517630/article.html"},
    "csrc_fraud": {"title": "中国证监会非法证券期货风险警示", "url": "https://www.csrc.gov.cn/csrc/c106299/common_list.shtml"},
    "nhc_66": {"title": "中国公民健康素养 66 条", "url": "https://www.nhc.gov.cn/xcs/c100123/202405/73a4927142f34152abed875634a3c13b.shtml"},
    "nhc_explain": {"title": "健康素养 66 条官方释义", "url": "https://www.nhc.gov.cn/xcs/c100122/202405/f251e896a50a49ff8c632b4b3da93126.shtml"},
    "who_diet": {"title": "WHO 健康饮食事实清单", "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"},
    "who_activity": {"title": "WHO 身体活动事实清单", "url": "https://www.who.int/news-room/fact-sheets/detail/physical-activity"},
    "who_selfcare": {"title": "WHO 自我照护事实清单", "url": "https://www.who.int/zh/news-room/fact-sheets/detail/self-care-health-interventions"},
    "who_mental": {"title": "WHO 心理健康事实清单", "url": "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response"},
    "cdc_sleep": {"title": "CDC 睡眠基础", "url": "https://www.cdc.gov/sleep/about/index.html"},
    "redcross_cpr": {"title": "中国红十字会 CPR 与 AED 指南", "url": "https://www.redcross.org.cn/html/2022-04/85322.html"},
    "redcross_training": {"title": "中国红十字会应急救护培训", "url": "https://www.redcross.org.cn/html/2026-05/114304.html"},
    "mem_family": {"title": "应急管理部家庭应急计划", "url": "https://www.mem.gov.cn/kp/shaq/201904/t20190401_365926.shtml"},
    "plain_language": {"title": "Digital.gov 简明语言指南", "url": "https://digital.gov/guides/plain-language/"},
    "cdc_clear": {"title": "CDC Clear Communication Index", "url": "https://www.cdc.gov/ccindex/ccindex.html"},
    "purdue_logic": {"title": "Purdue OWL 论证逻辑", "url": "https://owl.purdue.edu/owl/general_writing/academic_writing/logic_in_argumentative_writing/index.html"},
    "pon_listening": {"title": "Harvard PON 积极倾听", "url": "https://www.pon.harvard.edu/daily/negotiation-skills-daily/listening-skills-for-maximum-success/"},
    "pon_batna": {"title": "Harvard PON BATNA", "url": "https://www.pon.harvard.edu/daily/batna/translate-your-batna-to-the-current-deal/"},
    "pon_interests": {"title": "Harvard PON 利益与客观标准", "url": "https://www.pon.harvard.edu/daily/negotiation-skills-daily/principled-negotiation-focus-interests-create-value/"},
    "asq_five_whys": {"title": "ASQ Five Whys", "url": "https://asq.org/quality-resources/five-whys"},
    "asq_problem": {"title": "ASQ 问题解决方法", "url": "https://asq.org/quality-resources/problem-solving"},
    "nist_auth": {"title": "NIST SP 800-63B-4 认证指南", "url": "https://pages.nist.gov/800-63-4/sp800-63b/authenticators/"},
    "nist_password": {"title": "NIST 口令建议", "url": "https://www.nist.gov/cybersecurity-and-privacy/how-do-i-create-good-password"},
    "cisa_world": {"title": "CISA Secure Our World", "url": "https://www.cisa.gov/secure-our-world"},
    "cisa_device": {"title": "CISA 设备数据保护", "url": "https://www.cisa.gov/resources-tools/training/how-protect-data-stored-your-devices"},
    "cisa_backup": {"title": "CISA 3-2-1 备份说明", "url": "https://www.cisa.gov/sites/default/files/publications/data_backup_options.pdf"},
    "ftc_hacked": {"title": "FTC 账号被入侵后的恢复", "url": "https://consumer.ftc.gov/articles/how-recover-your-hacked-email-or-social-media-account"},
    "ftc_scammed": {"title": "FTC 遭遇诈骗后的处置", "url": "https://consumer.ftc.gov/articles/what-do-if-you-were-scammed"},
    "ftc_privacy": {"title": "FTC 在线隐私与安全", "url": "https://consumer.ftc.gov/identity-theft-and-online-security/online-privacy-and-security"},
    "cor": {"title": "Civic Online Reasoning", "url": "https://cor.inquirygroup.org/"},
    "unesco_mil": {"title": "UNESCO 媒体与信息素养", "url": "https://www.unesco.org/en/media-information-literacy"},
    "nist_gai": {"title": "NIST 生成式 AI 风险管理框架", "url": "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence"},
}

LIFESTYLE_RESOURCE_GROUPS = {
    "finance": [
        (("征信",), ("pbccrc_query", "pbccrc_dispute", "pboc_credit_rules")),
        (("税", "专项附加"), ("tax_policy", "tax_personal", "cfpb_toolkit")),
        (("保险", "保单"), ("insurance", "finance_fraud", "cfpb_toolkit")),
        (("骗局", "诈骗", "远程控制"), ("finance_fraud", "csrc_fraud", "pbccrc_query")),
        (("投资", "复利", "定投", "再平衡", "资产配置", "分散", "风险收益", "费用"), ("investor_allocation", "investor_dca", "investor_fees")),
        ((), ("cfpb_toolkit", "cfpb_debt", "cfpb_savings")),
    ],
    "health": [
        (("急救", "120", "现场安全", "CPR", "AED", "止血", "包扎", "骨折", "烫伤", "烧伤", "气道"), ("nhc_explain", "redcross_cpr", "redcross_training")),
        (("应急", "火灾", "地震", "洪水", "疏散", "119"), ("mem_family", "nhc_66", "redcross_training")),
        (("心理", "压力", "情绪"), ("who_mental", "who_selfcare", "nhc_66")),
        (("活动", "运动", "抗阻", "久坐"), ("who_activity", "nhc_explain", "nhc_66")),
        (("饮食", "食品", "营养", "盐", "糖", "饮料", "烹饪"), ("who_diet", "nhc_explain", "nhc_66")),
        (("睡眠",), ("cdc_sleep", "nhc_66", "who_selfcare")),
        ((), ("nhc_66", "nhc_explain", "who_selfcare")),
    ],
    "communication": [
        (("五问", "根因", "问题定义", "决策", "复盘"), ("asq_five_whys", "asq_problem", "purdue_logic")),
        (("谈判", "协商", "BATNA", "利益", "冲突"), ("pon_batna", "pon_interests", "pon_listening")),
        (("倾听", "复述", "提问", "反馈", "困难对话"), ("pon_listening", "cdc_clear", "plain_language")),
        (("表达", "写作", "演示", "信息", "受众", "会议"), ("plain_language", "cdc_clear", "purdue_logic")),
        ((), ("plain_language", "cdc_clear", "purdue_logic")),
    ],
    "digital_literacy": [
        (("备份", "3-2-1", "加密", "恢复演练"), ("cisa_backup", "cisa_device", "ftc_privacy")),
        (("异常", "入侵", "事件响应", "恢复", "泄露"), ("ftc_hacked", "ftc_scammed", "cisa_device")),
        (("AI", "图片", "视频", "深度伪造", "生成内容"), ("nist_gai", "cor", "unesco_mil")),
        (("横向阅读", "证据", "来源", "搜索", "新闻", "推荐算法", "信息"), ("cor", "unesco_mil", "nist_gai")),
        (("钓鱼", "诈骗", "链接", "二维码", "社会工程"), ("cisa_world", "ftc_scammed", "cor")),
        (("口令", "密码", "多因素", "MFA", "恢复码", "账号"), ("nist_auth", "nist_password", "ftc_hacked")),
        ((), ("cisa_world", "cisa_device", "ftc_privacy")),
    ],
}


def relevant_resources(kind, point, fallback):
    """返回与生活课程当天主题直接相关的三条已核对资料。"""
    for keywords, resource_names in LIFESTYLE_RESOURCE_GROUPS.get(kind, []):
        if not keywords or any(keyword.casefold() in point.casefold() for keyword in keywords):
            return [dict(VERIFIED_RESOURCES[name]) for name in resource_names]
    return list(fallback)


def track_key(track, point, task):
    if track == "coding-agent-tools-60d":
        return "agent_tools"
    if track == "agent-engineering-60d":
        return "agent"
    if track == "personal-finance-60d":
        return "finance"
    if track == "health-emergency-60d":
        return "health"
    if track == "communication-problem-solving-60d":
        return "communication"
    if track == "digital-safety-literacy-60d":
        return "digital_literacy"
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
    """生成一个知识主题的讲解、练习、资料与验收详情。

    Args:
        point: 当天核心知识主题。
        task: 学习者需要独立完成的任务。
        criteria: 可观察的验收条件。
        track: 系统路线 slug 或综合路线的日分类。

    Returns:
        可直接写入课程正文的知识详情字典。
    """
    guide = TRACK_GUIDES[track_key(track, point, task)]
    kind = track_kind(track)
    if kind == "accelerated":
        kind = infer_accelerated_kind(f"{point} {task}")
    teaching_example = example_for(kind, point) if kind else None
    concepts = concept_notes(kind, point) if kind else []
    teaching_note = " ".join(item["explanation"] for item in concepts[:2]) if concepts else guide["basic"]
    resources = relevant_resources(kind, point, guide["resources"])
    point_json = repr(point).replace("'", '"')
    code = teaching_example["code"] if teaching_example else guide["code"].format(point=point, point_json=point_json)
    expected = list(criteria) or ["产物可由他人复现", "结论与证据能够相互对应"]
    if kind in LIFESTYLE_TRACKS:
        summary = f"今天聚焦“{point}”，通过“{task}”形成可核对、可复盘的日常能力。"
        requirement = f"先独立完成“{task}”；使用脱敏记录、虚拟案例或低风险场景，保留常规情境、边界或失败情境、判断依据与复盘。"
        expected += ["边界或失败情境能稳定呈现且处理理由可解释", "练习表、判断证据、安全边界与复盘已保存"]
        mastery = [
            f"闭卷说明{point}解决的问题、判断依据和不适用边界",
            "不看参考模板完成一个常规情境和一个边界或失败情境",
            "能用脱敏记录、计算、来源或观察证据支持结论",
            "能识别停止条件，并把复盘转成下一步行动",
        ]
        practice_steps = [
            "阅读前置要求和安全边界，写下今天允许使用的数据或场景",
            "按参考模板完成一次引导练习，并区分事实、判断和行动",
            "关闭参考内容，独立完成常规情境",
            "加入边界或失败情境，保存处理证据并按验收条件复盘",
        ]
    else:
        summary = f"今天聚焦“{point}”，通过“{task}”把原理落实为可运行、可验证的能力。"
        requirement = f"先独立完成“{task}”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。"
        expected += ["失败样例能稳定触发且原因可解释", "运行命令、环境版本与关键输出已保存"]
        mastery = [f"闭卷说明{point}的输入、输出、依赖状态和不适用边界", "不看参考实现完成正常与失败两条路径", "能用断言、调用栈、日志或测试向量证明结论", "能把失败收敛为下一步可执行的问题"]
        practice_steps = ["阅读前置要求与概念图，写出当天输入、处理和输出", "逐段运行参考骨架并解释每一步状态变化", "关闭参考答案，独立完成正常路径", "加入失败或边界输入，保存命令、输出并按验收条件复盘"]
    item = detail(
        point,
        summary,
        teaching_note,
        guide["mechanism"],
        guide["tools"],
        guide["pitfalls"],
        requirement,
        code,
        teaching_example["language"] if teaching_example else guide["language"],
        teaching_example["command"] if teaching_example else guide["command"],
        expected,
        mastery,
        resources,
        practice_steps,
    )
    item["code_explanation"] = teaching_example["explanation"] if teaching_example else ["先辨认示例输入与预期输出。", "替换成当天任务数据，并增加失败输入验证边界。"]
    item["what_it_solves"] = f"帮助你判断“{point}”何时适用，并让当天任务有明确的输入、边界和验收依据。"
    return item


def build_lesson_content(day_number, core_knowledge, task, criteria, track=""):
    """根据学习日定义生成完整课程正文。

    Args:
        day_number: 路线内从 1 开始的学习日编号。
        core_knowledge: 当天核心知识。
        task: 当天独立任务。
        criteria: 当天验收条件。
        track: 系统路线 slug 或综合路线的日分类。

    Returns:
        包含知识详情、教学流程和验证方式的版本化字典。
    """
    # 每日正文保持为一个连贯主题；逗号分隔的术语仍由概念图逐项解释，避免拆成互不关联的知识卡。
    points = split_knowledge_points(core_knowledge) if not track_kind(track) else [core_knowledge.strip(" `")]
    details = [contextual_detail(point, task, criteria, track) for point in points]
    for item in details:
        item["role"] = f"先用本知识点完成关键判断，再把结果用于验收当天的独立任务。"
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
        "version": 6,
        "track": track,
        "knowledge_details": details,
        **teaching,
    }
