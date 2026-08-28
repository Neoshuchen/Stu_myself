"""Pedagogical content used by system roadmaps.

The route catalogs decide *what* to study.  This module turns that outline into
an actual lesson: prerequisites, plain-language concepts, a guided example, an
independent task and observable verification.  Internal source notes are only
used during editorial review; learner-facing resources point to public docs.
"""

import re


SYSTEM_TRACKS = {
    "python-foundation-60d": "python",
    "web-scraping-foundation-60d": "crawler",
    "javascript-reverse-60d": "javascript",
    "android-reverse-60d": "android",
    "ios-reverse-60d": "ios",
    "web-reverse-android-accelerated": "accelerated",
}




TERM_NOTES = {
    "python": [
        ("解释器", "CPython 先把源码编译为字节码，再由虚拟机执行；`sys.executable` 能确认当前究竟用了哪个环境。"),
        ("变量", "Python 变量是指向对象的名字，不是固定类型的盒子；重新赋值是让名字改指另一个对象。"),
        ("可变", "列表、字典可原地修改，因此多个名字引用同一对象时会同时观察到变化；整数、字符串不可原地修改。"),
        ("Decimal", "二进制浮点不能精确表示多数十进制小数；金额应从字符串构造 Decimal 并明确舍入规则。"),
        ("input", "`input()` 永远返回字符串，业务计算前必须转换类型并处理空值与非法文本。"),
        ("字符串", "字符串是不可变 Unicode 字符序列；切片返回新字符串，编码才会把字符转换为字节。"),
        ("列表", "列表保存有顺序、可重复的对象引用，适合需要按位置读写和动态增删的数据。"),
        ("元组", "元组本身不可增删元素，适合表达字段数量和顺序固定的记录，但其内部对象仍可能可变。"),
        ("字典", "字典用可哈希键映射值；`get` 适合缺键有默认值，`[]` 适合缺键就是程序错误。"),
        ("集合", "集合只保留唯一的可哈希元素，交集、并集和差集能直接表达名单之间的关系。"),
        ("if", "条件分支根据表达式真值只执行一条路径；短路求值可以避免访问不存在的数据。"),
        ("循环", "循环把同一处理应用于一组输入；必须明确迭代对象、退出条件以及每轮更新的状态。"),
        ("推导式", "推导式适合把一个清晰的映射或过滤写成表达式；出现多层分支时应退回普通循环。"),
        ("函数", "函数用参数定义输入、返回值定义输出；单一职责让每个步骤可以单独测试和组合。"),
        ("参数", "位置、关键字、默认和可变参数决定调用契约；可变默认值会被多次调用共享，必须避免。"),
        ("作用域", "LEGB 按局部、闭包、全局、内置顺序查找名字；赋值默认创建当前局部名字。"),
        ("闭包", "闭包让函数记住定义时外层作用域的变量，可用于保存私有状态或生成配置化函数。"),
        ("lambda", "lambda 只是单表达式匿名函数，最适合临时作为 `sorted(key=...)` 等高阶函数的参数。"),
        ("递归", "递归必须同时有基线条件和规模缩小步骤；深层数据更适合显式栈迭代以避免递归深度限制。"),
        ("模块", "模块在首次导入时执行并缓存；可执行入口放在 `if __name__ == '__main__'` 下可避免导入副作用。"),
        ("文件", "文件操作需要明确路径、编码和关闭时机；`with` 会在成功与异常路径都关闭句柄。"),
        ("JSON", "JSON 只有对象、数组、字符串、数字、布尔和 null，反序列化后仍要校验必需字段与类型。"),
        ("异常", "异常是函数失败契约的一部分；只捕获能处理的具体异常，并保留原始原因与上下文。"),
        ("日志", "日志用于记录可检索的运行事实，应包含时间、级别和上下文，且不能泄漏口令等敏感数据。"),
        ("class", "类把状态和操作状态的方法放在一起；实例之间有独立状态，类属性则被所有实例共享。"),
        ("继承", "继承表达“是一种”关系并允许重写；若只是复用能力，组合通常更清晰且耦合更低。"),
        ("dataclasses", "`@dataclass` 可按配置生成初始化、比较和表示等方法，适合字段明确的数据记录。"),
        ("迭代器", "迭代器实现 `__iter__` 和 `__next__`，每次只产生一个值，耗尽后抛出 StopIteration。"),
        ("生成器", "包含 `yield` 的函数会暂停并保存局部状态，适合流式处理不能一次装入内存的数据。"),
        ("装饰器", "装饰器接收函数并返回包装函数，可集中处理计时、日志等横切逻辑；`wraps` 保留元数据。"),
        ("上下文", "上下文管理器把资源获取与释放绑定到 `with` 边界，异常发生时也能可靠清理。"),
        ("类型", "类型标注帮助静态工具检查调用契约，但不会自动校验运行时外部输入。"),
        ("正则", "正则适合有稳定文本模式的局部提取；先写边界样例，避免宽泛贪婪匹配和灾难回溯。"),
        ("线程", "线程共享进程内存，适合等待网络和文件的 I/O 任务；共享可变状态需要同步。"),
        ("进程", "多进程拥有独立内存，适合 CPU 密集任务；传参和返回值必须可序列化。"),
        ("asyncio", "协程在 `await` 处主动让出执行权，适合大量 I/O；阻塞调用会卡住整个事件循环。"),
        ("SQL", "参数化 SQL 把语句结构与数据分开；事务保证一组写入要么全成要么全退。"),
        ("HTTP", "HTTP 请求由方法、URL、头和正文构成，响应由状态码、头和正文构成。"),
    ],
    "crawler": [
        ("采集", "采集是“请求—校验响应—解析—清洗—去重—存储”的数据管道，每层都应保留可定位失败的证据。"),
        ("HTTP", "先看方法、URL、请求头和请求体，再看状态码、响应头和响应体；这些事实决定代码如何复现。"),
        ("Network", "Network 面板记录浏览器真实请求；Payload 看发送数据，Preview/Response 看返回结构，Initiator 看发起位置。"),
        ("requests", "requests 把 HTTP 请求映射为 Python API；生产代码必须设置 timeout 并检查状态码。"),
        ("Cookie", "Cookie 是客户端随匹配域名和路径自动回传的小段状态；Session 可在多次请求间持有它。"),
        ("超时", "连接超时限制建连等待，读取超时限制相邻数据等待；二者都不能替代整个任务预算。"),
        ("重试", "只重试短暂故障和幂等操作，并设置次数、退避和总预算；参数错误与授权失败不应盲重试。"),
        ("代理", "正向代理代客户端建立连接；它改变信任边界但不会天然解决授权、会话或指纹问题。"),
        ("DOM", "HTML 被解析为节点树；稳定选择器应依赖语义属性和结构，而不是易变的视觉层级。"),
        ("正则", "正则适合局部、稳定的文本模式，不适合承担完整 HTML 树解析。"),
        ("BeautifulSoup", "BeautifulSoup 提供容错 HTML 树和节点搜索，提取后仍需处理缺节点与空文本。"),
        ("XPath", "XPath 从当前节点按轴和谓词选择目标；相对路径比从根开始的绝对路径更抗页面变化。"),
        ("CSS", "CSS 选择器用标签、类、属性和层级定位节点；应为缺失字段提供显式默认或错误。"),
        ("规范化", "规范化把文本空白、日期、数字和 URL 转成稳定类型，是解析结果进入数据库前的契约层。"),
        ("JSON", "JSON 接口通常比页面 HTML 稳定，但必须验证状态字段、分页字段和数据列表的真实层级。"),
        ("分页", "分页可能使用页码、offset 或 cursor；结束条件必须来自空列表、总数或 next cursor，而非猜固定页数。"),
        ("Playwright", "浏览器自动化适合必须执行页面脚本的授权场景；优先复用其观察到的接口，避免把点击当成唯一方案。"),
        ("并发", "并发提高等待型任务吞吐，但必须用信号量、连接池和速率限制约束对目标与本机的压力。"),
        ("断点", "断点续爬保存业务唯一键与游标；恢复时依赖幂等写入避免重复数据。"),
        ("Scrapy", "Scrapy 由 Engine 协调 Scheduler、Downloader、Spider 和 Pipeline，让请求调度与数据处理解耦。"),
        ("中间件", "下载器中间件处理请求和响应，Spider 中间件处理 Spider 输入输出；先确认执行顺序再放逻辑。"),
        ("去重", "请求指纹避免重复调度，业务唯一键避免重复入库；两者解决的是不同层面的重复。"),
    ],
    "javascript": [
        ("宿主", "ECMAScript 定义语言规则，浏览器或 Node 提供 DOM、网络、文件等宿主能力；两者不能混为一谈。"),
        ("类型", "JavaScript 原始值与对象的比较、转换规则不同；逆向时要同时记录值、类型和字节表示。"),
        ("作用域", "`let/const` 是块级词法作用域且存在暂时性死区，`var` 是函数作用域并发生声明提升。"),
        ("闭包", "函数会保留定义处的词法环境，因此离开外层调用后仍能读取其中变量。"),
        ("this", "`this` 由调用方式决定，而不是函数定义位置；箭头函数则捕获外层 `this`。"),
        ("原型", "对象读取缺失属性时沿原型链向上查找；Hook 原型方法会影响所有继承该方法的实例。"),
        ("Promise", "Promise 状态只能从 pending 变为 fulfilled 或 rejected；then/catch 创建新的 Promise 链。"),
        ("事件循环", "同步栈清空后先执行微任务，再进入下一宏任务；这决定异步日志与签名参数的先后顺序。"),
        ("编码", "字符串、UTF-8 字节、十六进制和 Base64 是不同表示；加密前后必须对齐字节语义。"),
        ("摘要", "摘要把任意长度输入映射为固定长度结果且不可逆；复现时要对齐编码、盐和输出格式。"),
        ("AES", "AES 是 16 字节分组的对称加密；密钥、模式、IV、填充和输出编码缺一项都无法对拍。"),
        ("Network", "从目标请求字段反查 Initiator 和调用栈，能找到字段首次生成位置而不是猜函数名。"),
        ("断点", "条件/XHR/DOM 断点在满足事件时暂停；暂停后用 Scope 和 Call Stack 验证数据来源。"),
        ("Hook", "Hook 临时包装函数或属性以记录参数、返回值和调用栈；必须保存原实现并支持恢复。"),
        ("混淆", "混淆改变代码形态而尽量保持行为；反混淆应小步变换并用测试向量证明语义不变。"),
        ("AST", "AST 把源码解析成有类型的语法节点；遍历、匹配、替换、重新生成是基本变换闭环。"),
        ("补环境", "补环境只实现目标代码实际访问的浏览器能力；Proxy 访问日志用于发现缺口，描述符和原型决定兼容性。"),
        ("算法", "算法剥离把确定性计算与网络、时间、随机和浏览器状态分开，再用固定向量跨语言对拍。"),
    ],
    "android": [
        ("ADB", "ADB 通过服务端与设备守护进程通信，可完成设备发现、安装、shell 和日志观察。"),
        ("APK", "APK 是 ZIP 容器，核心包含 Manifest、DEX、资源、原生库与签名信息。"),
        ("Java", "先能读懂类型、分支、集合、类和异常，才能理解 JADX 反编译结果与 Frida Java 桥。"),
        ("Manifest", "Manifest 声明组件、权限与导出入口，是静态画像和后续动态触发的第一张地图。"),
        ("DEX", "DEX 使用寄存器式指令表示 Java/Kotlin 编译结果；Smali 是它的可读汇编形式。"),
        ("抓包", "代理抓包只观察经过该网络栈且信任证书的流量；失败要区分代理、信任链与证书锁定。"),
        ("Frida", "Frida 把脚本注入目标进程；spawn 决定启动前注入，attach 连接已运行进程。"),
        ("Java.perform", "Java.perform 等待 ART 可用并进入正确线程上下文，Java.use 才能取得类包装器。"),
        ("Hook", "Hook 方法时必须选对 ClassLoader 和 overload，并决定是否调用原方法以保持应用行为。"),
        ("JNI", "JNI 是 Java 与 native 代码边界；native 方法可按名称导出，也可在运行时动态注册。"),
        ("ELF", "Android so 是 ELF 文件，导入导出、字符串和交叉引用能提供 native 入口候选。"),
        ("ARM64", "ARM64 常用 x0-x7 传前八个参数，x0 也承载返回值；栈与链接寄存器用于恢复调用链。"),
        ("ASLR", "ASLR 会改变模块装载基址，因此应记录‘模块基址 + 相对偏移’，而不是一次绝对地址。"),
        ("ClassLoader", "多 DEX 和动态加载会产生多个 ClassLoader；类找不到时先枚举加载器，不要反复猜类名。"),
    ],
    "ios": [
        ("签名", "签名证明代码身份与完整性，Provisioning Profile 连接证书、设备和 Entitlement。"),
        ("Objective-C", "Objective-C 方法调用本质是向对象发送 Selector 消息，运行时再解析到 IMP。"),
        ("Runtime", "Objective-C Runtime 可枚举类和方法并动态替换 IMP，是理解 Hook 的基础。"),
        ("Swift", "Swift 符号会改名且大量使用值类型和泛型元数据，静态与动态工具都需先确认调用约定。"),
        ("IPA", "IPA 是包含 Payload/App、Info.plist、Frameworks 与资源的归档；先做包与权限画像。"),
        ("Mach-O", "Mach-O 的加载命令描述架构、段、依赖库和入口，是静态分析的骨架。"),
        ("LLDB", "LLDB 通过断点、单步、寄存器与内存读取验证静态猜测；异常断点适合定位崩溃入口。"),
        ("Frida", "Frida 可枚举 Objective-C 类并观察参数与返回值；Swift Hook 还需处理符号与地址。"),
        ("ASLR", "dyld 装载镜像时应用随机滑动，稳定位置应记录镜像与偏移。"),
        ("砸壳", "授权测试中的砸壳是从运行时内存取得已解密代码并重建可分析产物，之后还要验证 cryptid 与完整性。"),
        ("Keychain", "Keychain 条目受 access group 与 protection class 约束，不等同于普通 plist 文件。"),
        ("算法", "先 Hook 输入输出形成固定字节向量，再剥离最小函数并跨语言对拍。"),
    ],
}


STAGE_PREREQUISITES = {
    "python": [(1, "无需编程基础；会使用终端即可"), (13, "已掌握容器、条件与循环"), (25, "会用函数拆分和处理文件异常"), (37, "理解类、迭代器、生成器与上下文"), (49, "会写 pytest 并理解并发基础"), (55, "能独立编写模块、测试与数据存储代码")],
    "crawler": [(1, "具备 Python 变量、函数和文件读写基础"), (13, "能用 requests 获取并保存响应"), (25, "能解析 HTML/JSON 并幂等入库"), (33, "理解 Cookie、认证和动态接口"), (37, "能写可靠的串行下载器"), (49, "能说明完整采集管道和故障证据")],
    "javascript": [(1, "具备 Python 与 HTTP 基础"), (19, "能独立运行 JavaScript 并解释异步和编码"), (25, "会用 Network、断点和调用栈定位入口"), (31, "能写可恢复的 Hook 并保存测试向量"), (37, "理解 AST 节点和小步反混淆"), (43, "能区分纯算法与浏览器环境依赖"), (55, "能完成单点定位、还原与对拍")],
    "android": [(1, "具备 JavaScript/Python 与 HTTP 基础，仅使用自有或授权 APK"), (7, "ADB、安装、日志和抓包环境已验收"), (13, "能阅读 Java 的类、集合与异常"), (25, "能用 JADX/Apktool 完成静态画像"), (31, "Frida 版本、架构和基本 Hook 已通过"), (40, "能从调用栈追踪 Java 参数来源"), (49, "理解 JNI、ELF、ARM64 与模块偏移")],
    "ios": [(1, "有可用 macOS/Xcode 环境，仅使用自有或授权 App"), (7, "能构建、签名、安装并读取测试 App 日志"), (13, "能阅读 Objective-C/Swift 基础代码"), (19, "能解释 IPA、Mach-O、依赖与 Entitlement"), (25, "能在静态工具中定位字符串和交叉引用"), (31, "能用 LLDB、代理和日志验证运行行为"), (37, "能编写可恢复的最小 Hook"), (43, "理解加载、ASLR、砸壳与重签的关系"), (49, "能采集固定字节向量并跨语言对拍")],
}


FALLBACK_CONCEPT_NOTES = {
    "python": "“{term}”需要放进可运行函数或模块中理解：明确对象类型、输入输出、异常契约与资源状态，再用断言验证正常和失败路径。",
    "crawler": "“{term}”应定位到请求、响应校验、解析、清洗、去重、存储或恢复中的具体一层，并声明输入结构、输出结构与失败去向。",
    "javascript": "“{term}”应在浏览器或 Node 的真实调用链中确认：记录值与字节表示、作用域或宿主状态，再用固定向量证明复现前后语义一致。",
    "android": "“{term}”应先判断属于组件、DEX/Java、网络、存储还是 Native 层，再以 APK 版本、静态位置和运行时证据共同验证。",
    "ios": "“{term}”应先判断属于签名、Objective-C/Swift 运行时、Mach-O、网络、存储还是加载链，并用镜像偏移与运行证据验证。",
}


def track_kind(track):
    kind = SYSTEM_TRACKS.get(track, "")
    if kind == "accelerated":
        return "accelerated"
    return kind


def infer_accelerated_kind(text):
    lowered = text.casefold()
    if any(word in lowered for word in ("android", "apk", "adb", "smali", "dex", "frida", "jni", "elf", "arm64", "jadx", "okhttp", "java.perform")):
        return "android"
    if any(word in lowered for word in ("javascript", "node", "promise", "ast", "浏览器", "补环境", "hook", "webpack")):
        return "javascript"
    if any(word in lowered for word in ("http", "爬虫", "采集", "scrapy", "requests", "xpath", "cookie", "代理")):
        return "crawler"
    return "python"


def prerequisites(kind, day_number):
    result = STAGE_PREREQUISITES.get(kind, [(1, "具备上一学习日要求的基础")])[0][1]
    for start, note in STAGE_PREREQUISITES.get(kind, []):
        if day_number >= start:
            result = note
    return [result, "能够运行上一学习日的最小示例并解释其正常与失败路径"] if day_number > 1 else [result]


def concept_notes(kind, core):
    terms = [part.strip(" `") for part in re.split(r"[、，,/+]", core) if part.strip(" `")]
    notes = []
    for term in terms:
        match = next((note for key, note in TERM_NOTES.get(kind, []) if keyword_matches(key, term)), None)
        notes.append({
            "term": term,
            "explanation": match or FALLBACK_CONCEPT_NOTES[kind].format(term=term),
        })
    return notes


def code(lines):
    return "\n".join(lines)


PYTHON_EXAMPLES = [
    (("dataclass", "dataclasses"), code([
        "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Order:",
        "    number: str", "    amount: int", "", "order = Order('A-001', 120)",
        "assert order == Order('A-001', 120)", "print(order)",
        "try:", "    order.amount = 0", "except Exception as error:", "    print(type(error).__name__)",
    ]), ["dataclass 为字段明确的记录生成初始化、比较和可读表示。", "frozen=True 阻止普通字段重新赋值；失败路径证明不可变约束确实生效。"]),
    (("Python 3.12", "解释器", "REPL", "脚本", "环境"), code([
        "import sys", "", "print('Python:', sys.version.split()[0])",
        "print('解释器:', sys.executable)", "print('平台:', sys.platform)",
        "assert sys.version_info[:2] == (3, 12)",
    ]), ["`sys.executable` 是当前真正执行脚本的解释器路径，不只看终端环境名称。", "版本断言把 Python 3.12 要求变成可执行验收；不匹配时立即失败。"]),
    (("变量", "对象", "可变"), code([
        "a = [1, 2]", "b = a", "b.append(3)",
        "print('同一对象:', a is b, id(a), id(b), a)",
        "c = a.copy()", "c.append(4)",
        "print('复制容器:', a is c, a, c)", "assert a == [1, 2, 3]",
    ]), ["`b = a` 只复制引用，因此两者 id 相同。", "`copy()` 创建新列表容器，修改 c 不再影响 a。"]),
    (("数字", "Decimal", "金额", "运算"), code([
        "from decimal import Decimal, ROUND_HALF_UP", "",
        "def total(price: str, count: int) -> Decimal:",
        "    if count <= 0: raise ValueError('count must be positive')",
        "    value = Decimal(price) * count * Decimal('1.06')",
        "    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)", "",
        "assert total('19.90', 2) == Decimal('42.19')", "print(total('19.90', 2))",
    ]), ["从字符串构造 Decimal，避免先引入二进制浮点误差。", "计算、舍入和非法数量三项规则都可由代码验证。"]),
    (("字符串", "切片", "编码"), code([
        "def mask_phone(raw: str) -> str:",
        "    phone = raw.strip().replace(' ', '')",
        "    if not (phone.isdigit() and len(phone) == 11):",
        "        raise ValueError('phone must contain 11 digits')",
        "    return f'{phone[:3]}****{phone[-4:]}'", "",
        "assert mask_phone('138 0013 8000') == '138****8000'",
        "print('学习'.encode('utf-8'), mask_phone('13800138000'))",
    ]), ["先清洗再校验，避免切片把非法输入伪装成正常结果。", "切片按字符工作，encode 后才得到 UTF-8 字节。"]),
    (("列表", "元组", "字典", "集合", "容器"), code([
        "records = [('小林', 82), ('阿青', 95), ('小周', 82)]",
        "ranking = sorted(records, key=lambda item: (-item[1], item[0]))",
        "score_by_name = {name: score for name, score in ranking}",
        "for position, (name, score) in enumerate(ranking, start=1):",
        "    print(position, name, score)",
        "assert ranking[0] == ('阿青', 95)",
        "assert set(score_by_name) == {'小林', '阿青', '小周'}",
    ]), ["列表承载有序记录，元组表达固定字段。", "字典负责映射，集合负责唯一性验证，各容器职责不同。"]),
    (("if", "条件", "循环", "for", "while", "推导式"), code([
        "def valid_scores(values: list[str]) -> list[int]:", "    result = []",
        "    for index, raw in enumerate(values, start=1):",
        "        try: score = int(raw)",
        "        except ValueError:", "            print(f'第{index}项不是整数: {raw}')", "            continue",
        "        if 0 <= score <= 100: result.append(score)", "    return result", "",
        "assert valid_scores(['90', 'bad', '101', '60']) == [90, 60]",
    ]), ["循环逐项处理，序号让失败能对应原始输入。", "异常分支与范围分支都只处理当前项，不中断后续数据。"]),
    (("函数", "参数", "作用域", "lambda", "递归"), code([
        "def parse_score(raw: str, *, minimum: int = 0, maximum: int = 100) -> int:",
        "    score = int(raw)",
        "    if not minimum <= score <= maximum:", "        raise ValueError(f'score must be {minimum}..{maximum}')",
        "    return score", "", "assert parse_score('90') == 90",
        "assert parse_score('5', minimum=1, maximum=5) == 5",
    ]), ["函数只做文本分数解析，参数和返回值形成清晰边界。", "星号后的范围只能按关键字传入，调用处含义明确。"]),
    (("文件", "Path", "JSON", "CSV", "异常", "日志"), code([
        "import json", "from pathlib import Path", "from tempfile import TemporaryDirectory", "",
        "with TemporaryDirectory() as folder:", "    path = Path(folder) / 'result.json'",
        "    data = {'topic': '文件与JSON', 'done': True}",
        "    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')",
        "    loaded = json.loads(path.read_text(encoding='utf-8'))",
        "    assert loaded == data", "    print(loaded)",
    ]), ["临时目录使示例可重复运行且不污染工作区。", "读写都指定 UTF-8，反序列化后用断言对拍。"]),
    (("类", "继承", "对象", "dataclass", "封装"), code([
        "from dataclasses import dataclass", "from decimal import Decimal", "", "@dataclass", "class Account:",
        "    owner: str", "    balance: Decimal = Decimal('0')", "",
        "    def deposit(self, amount: Decimal) -> None:",
        "        if amount <= 0: raise ValueError('amount must be positive')", "        self.balance += amount", "",
        "account = Account('小林')", "account.deposit(Decimal('10.00'))",
        "assert account.balance == Decimal('10.00')", "print(account)",
    ]), ["dataclass 生成初始化与表示，字段直接表达对象状态。", "余额只通过校验过的方法修改，防止非法状态。"]),
    (("迭代器", "生成器", "yield", "装饰器", "上下文"), code([
        "from collections.abc import Iterable, Iterator", "",
        "def valid_numbers(lines: Iterable[str]) -> Iterator[int]:",
        "    for line in lines:", "        text = line.strip()", "        if text.isdigit(): yield int(text)", "",
        "stream = valid_numbers(['1', 'bad', '3'])", "print(next(stream), list(stream))",
        "assert list(valid_numbers(['1', 'bad', '3'])) == [1, 3]",
    ]), ["生成器在第一次 next 时才执行到 yield。", "首次消费后只剩后续值，说明它保存状态且只能向前。"]),
    (("线程", "进程", "asyncio", "协程", "并发", "取消"), code([
        "import asyncio", "", "async def fetch(name: str, delay: float) -> str:",
        "    await asyncio.sleep(delay)", "    return name", "", "async def main():",
        "    results = await asyncio.gather(fetch('a', .02), fetch('b', .01))",
        "    assert results == ['a', 'b']", "    print(results)", "", "asyncio.run(main())",
    ]), ["await 主动让出事件循环，两个等待可以重叠。", "gather 结果仍按传入顺序排列；真实 I/O 还需超时和并发上限。"]),
    (("SQL", "SQLite", "MySQL", "数据库"), code([
        "import sqlite3", "", "db = sqlite3.connect(':memory:')", "with db:",
        "    db.execute('CREATE TABLE note (id INTEGER PRIMARY KEY, title TEXT UNIQUE)')",
        "    db.execute('INSERT INTO note(title) VALUES (?)', ('第一课',))",
        "row = db.execute('SELECT id, title FROM note WHERE title = ?', ('第一课',)).fetchone()",
        "assert row == (1, '第一课')", "print(row)", "db.close()",
    ]), ["参数占位让驱动处理数据，避免拼接 SQL。", "with 管理事务，查询结果再用断言验收；MySQL 遵循相同原则。"]),
]


CRAWLER_EXAMPLES = [
    (("HTTP", "请求", "响应"), code([
        "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Snapshot:",
        "    method: str", "    url: str", "    status: int", "    content_type: str", "",
        "item = Snapshot('GET', 'http://127.0.0.1:8000/items', 200, 'application/json')",
        "assert item.status == 200 and item.content_type.startswith('application/json')", "print(item)",
    ]), ["请求与响应四要素先形成快照，解析代码才有稳定输入。", "使用本地靶场，不依赖外部网站或真实用户数据。"]),
    (("requests", "Cookie", "Session", "超时", "重试", "代理"), code([
        "import requests", "", "def download(url: str, session: requests.Session | None = None) -> str:",
        "    client = session or requests.Session()", "    response = client.get(url, timeout=(2, 5))",
        "    response.raise_for_status()", "    return response.text", "",
        "# 在本地靶场运行：download('http://127.0.0.1:8000/page')",
        "print('连接超时=2秒，读取超时=5秒；HTTP失败会抛出异常')",
    ]), ["Session 复用连接并持有 Cookie，连接与读取超时分别限制等待。", "raise_for_status 让错误响应进入失败路径，不能把错误页当正常数据。"]),
    (("HTML", "DOM", "BeautifulSoup", "XPath", "CSS", "选择器", "正则"), code([
        "from html.parser import HTMLParser", "", "class Titles(HTMLParser):",
        "    def __init__(self):", "        super().__init__(); self.active = False; self.items = []",
        "    def handle_starttag(self, tag, attrs):",
        "        self.active = tag == 'h2' and dict(attrs).get('class') == 'title'",
        "    def handle_data(self, data):",
        "        if self.active and data.strip(): self.items.append(data.strip())",
        "    def handle_endtag(self, tag):", "        if tag == 'h2': self.active = False", "",
        "parser = Titles(); parser.feed('<h2 class=\"title\"> 第一课 </h2><h2>忽略</h2>')",
        "assert parser.items == ['第一课']", "print(parser.items)",
    ]), ["定位条件依赖语义类名，并在提取时清理空白。", "缺节点得到空列表，调用方必须把它当可检测的数据质量问题。"]),
    (("JSON", "规范化", "清洗", "URL"), code([
        "from urllib.parse import urljoin", "", "def normalize(item: dict, base: str) -> dict:",
        "    title = str(item.get('title', '')).strip()", "    href = str(item.get('url', '')).strip()",
        "    if not title or not href: raise ValueError('title and url are required')",
        "    return {'title': title, 'url': urljoin(base, href)}", "",
        "assert normalize({'title':' A ','url':'/a'}, 'https://lab.test/list') == {'title':'A','url':'https://lab.test/a'}",
    ]), ["解析保留原字段，规范化统一处理空白、类型和 URL。", "缺字段明确失败，避免坏记录悄悄进入数据库。"]),
    (("分页", "下拉", "游标", "去重", "断点"), code([
        "def collect(fetch_page):", "    page, seen, result = 1, set(), []", "    while True:",
        "        items = fetch_page(page)", "        if not items: break", "        for item in items:",
        "            if item['id'] not in seen:", "                seen.add(item['id']); result.append(item)",
        "        page += 1", "    return result", "",
        "fixture = {1:[{'id':1}], 2:[{'id':1},{'id':2}], 3:[]}",
        "assert [x['id'] for x in collect(lambda p: fixture[p])] == [1, 2]",
    ]), ["空页是该夹具的终止契约；真实接口应使用其 total 或 next cursor。", "内存去重和数据库业务唯一键共同保证幂等。"]),
    (("并发", "线程池", "aiohttp", "速率", "队列"), code([
        "import asyncio", "", "async def worker(number: int, limit: asyncio.Semaphore):",
        "    async with limit:", "        await asyncio.sleep(.01)", "        return number * 2", "",
        "async def main():", "    limit = asyncio.Semaphore(2)",
        "    print(await asyncio.gather(*(worker(i, limit) for i in range(5))))", "", "asyncio.run(main())",
    ]), ["信号量把并发峰值限制为 2，防止压垮本地靶场。", "每个任务仍需独立超时和错误收集；并发不能取代合规限速。"]),
    (("Scrapy", "Pipeline", "中间件", "调度", "Response"), code([
        "# pipelines.py", "class RequiredFieldsPipeline:", "    def process_item(self, item, spider):",
        "        title = str(item.get('title', '')).strip()", "        url = str(item.get('url', '')).strip()",
        "        if not title or not url: raise ValueError('title and url are required')",
        "        item['title'], item['url'] = title, url", "        return item", "",
        "# settings.py: ITEM_PIPELINES = {'demo.pipelines.RequiredFieldsPipeline': 300}",
    ]), ["Spider 产生 Item，Pipeline 负责清洗和存储，不把数据库代码塞进解析函数。", "返回 item 才进入下一管道；错误应留下失败证据。"]),
]


JAVASCRIPT_EXAMPLES = [
    (("类型", "转换", "相等", "变量"), code([
        "const values = [0, '0', null, undefined, [], {}];",
        "console.table(values.map(value => ({", "  value: String(value),", "  type: typeof value,",
        "  truthy: Boolean(value),", "  strictZero: value === 0,", "})));",
        "console.assert('0' !== 0 && Number('0') === 0);",
    ]), ["同时输出值、类型、真值和严格比较，避免凭控制台外观猜类型。", "业务比较优先用严格相等；需要转换时显式执行。"]),
    (("作用域", "闭包", "函数", "this"), code([
        "function createCounter(start = 0) {", "  let value = start;", "  return () => ++value;", "}",
        "const first = createCounter(0);", "const second = createCounter(10);",
        "console.assert(first() === 1 && first() === 2);", "console.assert(second() === 11);",
    ]), ["返回函数继续引用定义时的 value 词法环境。", "两个闭包状态隔离，说明状态没有落在全局变量。"]),
    (("Promise", "事件循环", "async", "异步"), code([
        "console.log('sync-1');", "setTimeout(() => console.log('macro'), 0);",
        "Promise.resolve().then(() => console.log('micro'));", "console.log('sync-2');",
        "// 固定顺序：sync-1, sync-2, micro, macro",
    ]), ["当前同步栈先清空，Promise 回调进入微任务队列。", "下一轮宏任务才执行 timer，0 毫秒不等于立即执行。"]),
    (("编码", "Base64", "Unicode", "位运算"), code([
        "const text = '学习';", "const bytes = new TextEncoder().encode(text);",
        "const hex = [...bytes].map(v => v.toString(16).padStart(2, '0')).join('');",
        "const base64 = Buffer.from(bytes).toString('base64');",
        "console.log({ text, byteLength: bytes.length, hex, base64 });", "console.assert(bytes.length === 6);",
    ]), ["TextEncoder 固定产生 UTF-8 字节，两个中文字符在这里是 6 字节。", "十六进制和 Base64 只是同一字节数组的不同表示，不是加密。"]),
    (("Network", "断点", "调用栈", "Hook", "XHR"), code([
        "const originalFetch = globalThis.fetch;", "globalThis.fetch = async function (...args) {",
        "  console.group('fetch observed');", "  console.log('args', args);", "  console.trace('call stack');",
        "  try { return await originalFetch.apply(this, args); }", "  finally { console.groupEnd(); }", "};",
        "// 完成授权靶场定位后恢复：globalThis.fetch = originalFetch;",
    ]), ["保存原函数并用 apply 透传 this 与参数，尽量不改变请求语义。", "参数和调用栈把 Network 请求关联回字段生成代码。"]),
    (("AST", "混淆", "常量", "反混淆"), code([
        "import { parse } from '@babel/parser';", "import traverse from '@babel/traverse';",
        "import generate from '@babel/generator';", "", "const ast = parse('const answer = 20 + 22;');",
        "traverse(ast, { BinaryExpression(path) {", "  const result = path.evaluate();",
        "  if (result.confident) path.replaceWithSourceString(String(result.value));", "}});",
        "console.log(generate(ast).code); // const answer = 42;",
    ]), ["解析、遍历、匹配替换、生成构成 AST 变换闭环。", "只有 confident 才替换；不确定表达式原样保留，支持回退。"]),
    (("补环境", "Proxy", "环境", "指纹"), code([
        "const missing = new Set();", "const navigator = new Proxy({ userAgent: 'AuthorizedLab/1.0' }, {",
        "  get(target, key, receiver) {", "    if (!(key in target)) missing.add(String(key));",
        "    return Reflect.get(target, key, receiver);", "  },", "});",
        "console.log(navigator.userAgent, navigator.language);", "console.log('待补能力', [...missing]);",
    ]), ["Proxy 先记录目标真实访问的属性，不一开始伪造整套浏览器。", "Reflect.get 保持已有属性语义，缺失清单驱动最小实现。"]),
    (("算法", "摘要", "MD5", "SHA", "AES", "RSA", "复现"), code([
        "import { createHash } from 'node:crypto';", "function signature(payload) {",
        "  return createHash('sha256').update(Buffer.from(payload, 'utf8')).digest('hex');", "}",
        "const vectors = ['', 'abc', '学习'].map(input => ({ input, output: signature(input) }));",
        "console.table(vectors);", "console.assert(vectors[1].output.startsWith('ba7816bf'));",
    ]), ["纯函数固定用 UTF-8 转字节，网络、时间和随机状态没有混入。", "空串、ASCII、中文三组黄金向量能暴露编码和格式差异。"]),
]


ANDROID_EXAMPLES = [
    (("ADB", "设备", "环境", "日志"), code([
        "adb devices -l", "adb shell getprop ro.product.cpu.abi",
        "adb shell getprop ro.build.version.release", "adb shell pm list packages | findstr com.example.lab",
        "adb logcat --pid=$(adb shell pidof com.example.lab)",
    ]), ["先确认设备、ABI、系统版本和包名，后续工具版本都依赖这些事实。", "日志按进程过滤，并保存触发步骤与时间点。"]),
    (("APK", "Manifest", "JADX", "Apktool", "DEX", "Smali", "签名"), code([
        "# 仅对本人或授权的 lab.apk", "certutil -hashfile lab.apk SHA256",
        "apkanalyzer manifest print lab.apk > manifest.txt", "jadx -d jadx-out lab.apk",
        "apktool d lab.apk -o apktool-out", "# 从 Manifest 入口沿 JADX 引用追踪到 DEX/Smali",
    ]), ["哈希先冻结样本，Manifest 给出组件入口。", "JADX 用于语义阅读，Apktool 保留资源与 Smali 层证据。"]),
    (("Java", "JDK", "编译运行", "List", "Map", "Set"), code([
        "import java.util.Map;", "", "public class Lab {", "    static int score(Map<String, String> input) {",
        "        String raw = input.get(\"score\");", "        if (raw == null) throw new IllegalArgumentException(\"score required\");",
        "        int value = Integer.parseInt(raw);", "        if (value < 0 || value > 100) throw new IllegalArgumentException(\"score out of range\");",
        "        return value;", "    }", "    public static void main(String[] args) {",
        "        assert score(Map.of(\"score\", \"90\")) == 90;", "        System.out.println(score(Map.of(\"score\", \"90\")));", "    }", "}",
    ]), ["Map 模拟反编译代码常见键值输入，先处理缺字段和范围。", "用 `java -ea` 启用断言，保证正常路径有可执行验收。"]),
    (("Frida", "Java.perform", "Java.use", "Hook", "ClassLoader", "OkHttp"), code([
        "Java.perform(() => {", "  const Target = Java.use('com.example.lab.Signer');",
        "  const sign = Target.sign.overload('java.lang.String');", "  sign.implementation = function (input) {",
        "    const output = sign.call(this, input);", "    send({ method: 'Signer.sign', input, output });",
        "    return output;", "  };", "});",
    ]), ["overload 明确选择字符串签名，避免命中同名的其他重载。", "调用原实现后再记录输入输出，尽量保持授权测试 App 行为。"]),
    (("JNI", "ELF", "Native", "ARM64", "ASLR", "内存"), code([
        "const module = Process.getModuleByName('liblab.so');", "const offset = 0x1234; // 静态分析确认",
        "const address = module.base.add(offset);", "console.log({ base: module.base, offset, address });",
        "Interceptor.attach(address, {", "  onEnter(args) { console.log('x0/arg0', args[0]); },",
        "  onLeave(retval) { console.log('return', retval); },", "});",
    ]), ["运行地址由模块基址加静态偏移计算，可跨 ASLR 重启复现。", "参数解释必须依据 JNI/ARM64 调用约定，不能见到指针就直接当字符串。"]),
]


IOS_EXAMPLES = [
    (("环境", "设备", "签名", "Entitlement", "Xcode"), code([
        "xcodebuild -version", "xcrun simctl list devices available",
        "codesign -d --entitlements :- /path/to/AuthorizedLab.app",
        "codesign -dv --verbose=4 /path/to/AuthorizedLab.app",
        "# 记录 macOS、Xcode、系统版本、架构、Bundle ID 与签名身份",
    ]), ["工具版本、设备系统和架构共同决定后续环境是否匹配。", "签名身份与 Entitlement 分开查看：谁签名、授予什么能力。"]),
    (("IPA", "Mach-O", "符号", "静态", "依赖"), code([
        "unzip -l AuthorizedLab.ipa", "plutil -p Payload/AuthorizedLab.app/Info.plist",
        "file Payload/AuthorizedLab.app/AuthorizedLab",
        "otool -l Payload/AuthorizedLab.app/AuthorizedLab | head",
        "strings Payload/AuthorizedLab.app/AuthorizedLab | grep -i token",
    ]), ["从 Info.plist 确认可执行文件，再检查正确 Mach-O 的架构与加载命令。", "字符串只产生候选，仍需交叉引用或动态验证。"]),
    (("LLDB", "断点", "ARM64", "调用", "日志"), code([
        "lldb /path/to/AuthorizedLab.app/AuthorizedLab", "breakpoint set --name main", "run",
        "thread backtrace", "register read x0 x1 x29 x30",
        "# 下一断点替换为授权样本确认的方法名或模块偏移",
    ]), ["命中后先保存调用栈，再读取与调用约定相关的寄存器。", "报告使用符号或镜像偏移，不把一次绝对地址当通用结论。"]),
    (("Frida", "ObjC", "Hook", "Swift", "Objection"), code([
        "if (!ObjC.available) throw new Error('Objective-C runtime unavailable');",
        "const method = ObjC.classes.LabSigner['- sign:'];", "Interceptor.attach(method.implementation, {",
        "  onEnter(args) { this.input = new ObjC.Object(args[2]).toString(); },",
        "  onLeave(retval) { console.log({ input: this.input, output: new ObjC.Object(retval).toString() }); },", "});",
    ]), ["Objective-C 中 args[0] 是 self、args[1] 是 selector，显式参数从 args[2] 开始。", "Swift 原生函数需另行确认符号和调用约定，不能直接套用。"]),
    (("砸壳", "重签", "cryptid", "FairPlay", "加载"), code([
        "otool -l Payload/AuthorizedLab.app/AuthorizedLab | grep -A4 LC_ENCRYPTION_INFO",
        "codesign -d --entitlements :- Payload/AuthorizedLab.app",
        "# 在授权设备按正文完成运行时 dump 后", "file dumped/AuthorizedLab",
        "otool -l dumped/AuthorizedLab | grep -A4 LC_ENCRYPTION_INFO",
        "codesign --verify --deep --strict Payload/AuthorizedLab.app",
    ]), ["前后对比 cryptid 与架构，证明产物状态发生预期变化。", "dump、修复、重签、安装和启动分别验收，失败保留命令与输出。"]),
]


EXAMPLES = {
    "python": PYTHON_EXAMPLES,
    "crawler": CRAWLER_EXAMPLES,
    "javascript": JAVASCRIPT_EXAMPLES,
    "android": ANDROID_EXAMPLES,
    "ios": IOS_EXAMPLES,
}


def keyword_matches(keyword, text):
    if keyword.isascii() and keyword.replace(".", "").replace("_", "").isalnum():
        return re.search(rf"(?<![A-Za-z0-9_]){re.escape(keyword)}(?![A-Za-z0-9_])", text, re.IGNORECASE) is not None
    # 中文短词若在任意位置模糊命中，容易让“不可变对象”错误选择“变量与对象”示例。
    # 仅匹配知识点分项的开头，仍可覆盖“异常链”“生成器表达式”等自然扩展。
    terms = [part.strip(" `") for part in re.split(r"[、，,/+]", text) if part.strip(" `")]
    return any(term.casefold().startswith(keyword.casefold()) for term in terms)


def fallback_example(kind, text):
    if kind == "python":
        sample = code([
            "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Result:",
            "    topic: str", "    ok: bool", "    detail: str", "",
            f"def run() -> Result:", f"    topic = {text!r}",
            "    if not topic.strip(): raise ValueError('topic is required')",
            "    return Result(topic, True, '正常路径已运行')", "", "result = run()",
            "assert result.ok and result.topic", "print(result)",
        ])
        return {"code": sample, "language": "python", "command": "python practice.py", "explanation": ["Result 明确表达今日实验的主题、状态和输出，不用散乱 print 冒充结果。", "run 函数保留可替换的核心处理边界；先跑通后再换成当天真实实现并增加失败输入。"]}
    if kind == "crawler":
        sample = code([
            "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Record:",
            "    url: str", "    status: int", "    title: str", "",
            "def pipeline(item: dict) -> Record:", "    url = str(item.get('url', '')).strip()",
            "    title = str(item.get('title', '')).strip()", "    status = int(item.get('status', 0))",
            "    if not url or not title or status != 200: raise ValueError('invalid response record')",
            "    return Record(url, status, title)", "",
            "result = pipeline({'url':'http://127.0.0.1/item/1','status':200,'title':'第一课'})",
            "assert result.status == 200", "print(result)",
        ])
        return {"code": sample, "language": "python", "command": "python practice.py", "explanation": ["固定记录模拟请求到解析管道的交界，让示例脱离外网也可重复运行。", "校验在创建结构化记录前完成；把该函数替换为当天下载、解析或诊断环节即可。"]}
    if kind == "javascript":
        sample = code([
            f"const TOPIC = {text!r};", "", "function observe(label, fn, input) {", "  try {",
            "    return { label, input, output: fn(input), error: null };", "  } catch (error) {",
            "    return { label, input, output: null, error: error.message };", "  }", "}", "",
            "const normalize = value => String(value).trim();",
            "const vectors = [observe('normal', normalize, ' demo '), observe('boundary', normalize, null)];",
            "console.table(vectors.map(item => ({ topic: TOPIC, ...item })));",
            "console.assert(vectors[0].output === 'demo');",
        ])
        return {"code": sample, "language": "javascript", "command": "node practice.mjs", "explanation": ["观察器同时保存输入、输出与错误，让调试、还原和对拍使用同一证据结构。", "先替换 normalize 为当天真实入口，再加入编码、时间或环境边界向量。"]}
    if kind == "android":
        sample = code([
            "setImmediate(() => {", "  const evidence = {", f"    topic: {text!r},",
            "    processId: Process.id,", "    platform: Process.platform,", "    arch: Process.arch,", "    javaAvailable: Java.available,", "  };",
            "  send(evidence);", "  if (Java.available) Java.perform(() => send({ android: Java.androidVersion }));", "});",
        ])
        return {"code": sample, "language": "javascript", "command": "frida -U -f com.example.lab -l practice.js", "explanation": ["先输出进程、平台、架构和 Java VM 状态，证明脚本运行在预期样本环境。", "再将当天静态定位出的最小 Hook 点加入 Java.perform 或 Interceptor，并保留恢复方式。"]}
    sample = code([
        "# LLDB 授权实验通用骨架", "target create /path/to/AuthorizedLab.app/AuthorizedLab",
        "breakpoint set --name main", "run", "thread backtrace", "image list",
        f"# 今日主题：{text}", "# 把确认的方法名或‘镜像 + 偏移’加入新断点，再保存参数与返回值",
    ])
    return {"code": sample, "language": "text", "command": "lldb /path/to/AuthorizedLab.app/AuthorizedLab", "explanation": ["先验证可执行文件、主断点、调用栈和镜像列表，确认动态环境可用。", "当天主题只替换新断点，不改基础证据步骤；地址按镜像偏移记录以适应 ASLR。"]}


def example_for(kind, text):
    matches = []
    for keywords, sample, explanation in EXAMPLES.get(kind, []):
        matched = [keyword for keyword in keywords if keyword_matches(keyword, text)]
        if matched:
            matches.append((max(len(keyword) for keyword in matched), sample, explanation))
    for _, sample, explanation in sorted(matches, key=lambda item: item[0], reverse=True)[:1]:
            language = "javascript" if kind in ("javascript", "android", "ios") else "python"
            command = {"python": "python practice.py", "crawler": "python practice.py", "javascript": "node practice.mjs", "android": "frida -U -f com.example.lab -l practice.js", "ios": "lldb /path/to/AuthorizedLab.app/AuthorizedLab"}[kind]
            if kind == "android" and "public class" in sample:
                language, command = "java", "javac Lab.java && java -ea Lab"
            if sample.startswith(("adb ", "# 仅对", "xcodebuild", "unzip ", "lldb ", "otool ")):
                language, command = "text", sample.splitlines()[0]
            return {"code": sample, "language": language, "command": command, "explanation": explanation}
    return fallback_example(kind, text)


def build_teaching_sections(day_number, core, task, criteria, kind):
    concepts = concept_notes(kind, core)
    first_term = concepts[0]["term"] if concepts else core
    return {
        "prerequisites": prerequisites(kind, day_number),
        "learning_objectives": [
            f"能用自己的话说明“{first_term}”解决什么问题，而不是只记名称",
            f"能独立完成：{task}",
            "能运行正常、边界和失败输入，并用输出或调用证据解释结果",
        ],
        "concept_map": concepts,
        "comprehensive_task": {
            "goal": task,
            "input": f"使用固定、可重复且不含真实敏感信息的输入，覆盖“{core}”涉及的数据与状态。",
            "output": "提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。",
            "requirements": ["先完成跟做示例，再关闭参考答案独立实现", "核心处理与输入输出分开，关键边界有明确校验", "至少包含一条正常路径和一条失败或边界路径"],
            "error_cases": ["缺少必需输入时给出可理解的错误", "输入格式或状态不合法时不留下半成品"],
        },
        "verification": {
            "checks": list(criteria) + ["正常、边界、失败三类结果均已保存", "能闭卷解释关键数据流和失败原因"],
            "evidence": ["源代码或实验脚本", "实际运行命令与环境版本", "关键输出、日志、断言或调用栈", "100 字以上复盘与一个待解决问题"],
        },
        "workflow": [
            {"title": "先建立上下文", "body": "阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。"},
            {"title": "跟做并理解示例", "body": "逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。"},
            {"title": "关闭答案独立完成", "body": f"不复制参考代码，独立完成“{task}”。卡住时只回看对应概念，不整段照抄。"},
            {"title": "用失败证明掌握", "body": "加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。"},
        ],
    }

