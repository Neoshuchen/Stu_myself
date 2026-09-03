"""Pedagogical content used by system roadmaps.

The route catalogs decide *what* to study.  This module turns that outline into
an actual lesson: prerequisites, plain-language concepts, a guided example, an
independent task and observable verification.  Internal source notes are only
used during editorial review; learner-facing resources point to public docs.
"""

import re


SYSTEM_TRACKS = {
    "personal-finance-60d": "finance",
    "health-emergency-60d": "health",
    "communication-problem-solving-60d": "communication",
    "digital-safety-literacy-60d": "digital_literacy",
    "coding-agent-tools-60d": "agent_tools",
    "agent-engineering-60d": "agent",
    "python-foundation-60d": "python",
    "web-scraping-foundation-60d": "crawler",
    "javascript-reverse-60d": "javascript",
    "android-reverse-60d": "android",
    "ios-reverse-60d": "ios",
    "web-reverse-android-accelerated": "accelerated",
}

LIFESTYLE_TRACKS = frozenset({"finance", "health", "communication", "digital_literacy"})




TERM_NOTES = {
    "finance": [
        ("财务快照", "财务快照在同一日期记录资产、负债、收入、固定责任和近期目标；只比较同口径数据，避免把信用额度、未实现收益或未来工资当成现有资产。"),
        ("净资产", "净资产等于资产减负债，适合观察长期方向但不能替代现金流；房产等难变现资产和短期应付账款都要按实际流动性解释。"),
        ("现金流", "现金流按实际到账和支付日期记录收入与支出，能暴露月度结余、账单错位和季节性压力；预算必须以真实现金流而不是理想月份为起点。"),
        ("固定支出", "固定与可变支出按短期能否调整区分；还要单列低频但必然发生的年度费用，避免把它们误判为意外。"),
        ("需要与想要", "需要与想要不是永久标签，应结合健康、安全、责任和目标判断；分类的目的在于看清取舍，不是制造羞耻。"),
        ("预算", "预算是给未来现金分配任务的计划，执行后必须用实际数回填并解释偏差；无法长期执行的预算需要调整假设而不是隐瞒支出。"),
        ("沉淀基金", "沉淀基金把可预见的大额支出按剩余月份分摊，例如保险、维修和旅行，使低频支出不再挤占应急储备。"),
        ("应急金", "应急金服务于失业、医疗或必要维修等不可预见事件，应关注安全性和可取用性；目标金额取决于基本支出、收入稳定性和家庭责任。"),
        ("债务", "债务评估至少记录剩余本金、年化成本、最低还款、到期日、违约后果和提前还款条件，再决定优先级。"),
        ("年化成本", "日利率、月费率和分期手续费必须换算到同一时间口径，并把服务费、违约金和复利规则纳入总成本。"),
        ("征信", "征信记录应通过所在地官方渠道查询，发现错误按正规异议流程处理；任何承诺删除真实负面记录的“征信修复”都需高度警惕。"),
        ("合同", "签署金融合同前核对交易实质、总成本、期限、退出条件、违约责任、争议渠道和个人信息授权；不在催促下完成刷脸、验证码或共享屏幕。"),
        ("保险", "保险用于转移本人难以承受的特定损失，不等同于储蓄或保证收益；先确认保障需求，再看责任、除外、等待期、免赔额、续保和退保损失。"),
        ("复利", "复利既能放大长期储蓄收益，也能放大高息债务成本；任何演示都要同时写明本金、期限、利率、费用和收益不确定性。"),
        ("风险收益", "预期收益上升通常伴随更高的不确定性、期限或流动性约束；“保本高收益、稳赚不赔”与基本风险规律冲突。"),
        ("分散", "分散把风险暴露到不同资产和来源，但多个名称不同、底层持仓相同的产品并不是真正分散，也不能消除市场整体风险。"),
        ("费用", "申购、管理、交易、赎回、顾问和税费都会侵蚀长期结果；比较方案时同时计算一次性和持续性费用。"),
        ("投资骗局", "陌生高收益、内部消息、代操作、远程控制和要求转入个人账户都是高风险信号；暂停操作并通过已知官方渠道独立核实。"),
        ("财务目标", "财务目标应写清金额、期限、优先级和允许风险，并与现金流、应急储备和家庭责任一起复核。"),
    ],
    "health": [
        ("健康素养", "健康素养包括获取、理解、甄别和应用健康信息的能力；来源、适用人群、证据日期和何时求医与结论同样重要。"),
        ("健康基线", "健康基线记录一段时间内的睡眠、活动、饮食、症状和已知诊疗信息，用于就医沟通和习惯复盘，不用于自行下诊断。"),
        ("危险信号", "意识或呼吸异常、严重胸痛、大出血等紧急信号应优先呼叫当地急救；课程无法穷举所有情况，拿不准时应向专业人员求助。"),
        ("睡眠", "健康睡眠同时关注时长、规律和质量；持续失眠、夜间呼吸异常或白天严重嗜睡需要与医疗人员沟通。"),
        ("睡眠日记", "睡眠日记按实际时间记录上床、入睡估计、醒来、午睡、咖啡因、活动和主观精神，至少连续观察一周再判断模式。"),
        ("健康饮食", "健康饮食以适足、平衡、适度和多样为原则，优先低限度加工食物；具体需求会随年龄、疾病、妊娠和活动水平变化。"),
        ("食品标签", "阅读预包装食品标签时核对每份与每100克口径、配料顺序、能量、钠、糖和过敏原，不能只看正面营销语。"),
        ("食品安全", "生熟分开、充分加热、清洁双手和器具、控制储存温度并检查保质期，是家庭食品安全的基础链路。"),
        ("身体活动", "任何活动都比完全不动好；成年人通常应逐步达到有氧与抗阻建议，但慢性病、孕产期或伤病人群应按专业建议调整。"),
        ("抗阻", "抗阻训练通过可控负荷刺激主要肌群；先学动作和呼吸，再逐步增加难度，疼痛、眩晕或异常不适时立即停止。"),
        ("久坐", "久坐风险不能只靠一次集中运动抵消；将步行、站立和活动休息嵌入工作日更容易形成稳定习惯。"),
        ("压力", "压力记录关注触发、身体反应、想法、行为和恢复方式；持续影响睡眠、工作或安全时应主动寻求专业帮助。"),
        ("心理健康", "短期情绪波动很常见，但持续痛苦、功能明显受损或自伤风险不是靠意志硬扛的问题，应及时联系专业支持和可信赖的人。"),
        ("科学就医", "就医前整理主诉、起始时间、变化、用药、过敏史和问题清单；就医后复述诊断计划、用药方法、复诊与警示信号。"),
        ("合理用药", "药品按说明书和医嘱使用，核对通用名、剂量、频次、禁忌和有效期；不分享处方药、不自行停药或混用抗菌药。"),
        ("120", "在中国需要紧急医疗救助时拨打120，清楚说明地点、人数、意识呼吸和主要危险，并按调度员指示行动；其他地区使用当地号码。"),
        ("现场安全", "急救第一步是确认现场对施救者、伤病员和旁观者安全，使用必要防护并取得同意；超出训练能力时以呼救和避免二次伤害为主。"),
        ("CPR", "心肺复苏和AED属于需要规范实操训练的技能；文字课只帮助识别流程，必须参加合格课程并在教具上练习。"),
        ("止血", "严重出血需要立即呼救，并在训练范围内采用直接压迫等方法；不要随意移除已固定异物或反复掀开敷料检查。"),
        ("家庭应急", "家庭应急计划包含疏散路线、集合点、联系人、特殊成员需求、重要文件副本、设施关闭方法和定期更新的应急包。"),
    ],
    "communication": [
        ("沟通目标", "沟通前先定义希望对方知道、感受或采取的行动，以及不可接受的结果；目标不清会让信息越说越多却无法验收。"),
        ("受众", "同一信息要根据对方的背景、关注点、可用时间和决策权限调整术语、顺序、细节和媒介。"),
        ("观察与解释", "观察是可由第三方核对的行为或数据，解释是对原因和意图的推断；把二者分开能减少指责和误判。"),
        ("积极倾听", "积极倾听通过专注、开放问题、复述和确认情绪来理解对方，而不是等待轮到自己反驳。"),
        ("复述", "复述应抓住事实、意义和对方最在意的点，并邀请纠正；重复原句却没有确认理解不等于倾听。"),
        ("开放问题", "开放问题帮助对方描述事实、影响和需求，封闭问题适合确认具体信息；带结论的诱导问题会降低信息质量。"),
        ("清晰表达", "清晰表达把结论、依据、必要背景和下一步按受众需要排列，删除不能改变理解或行动的内容。"),
        ("简明语言", "简明语言使用受众熟悉的词、主动句、短段落和清晰标题，并通过真实读者测试是否理解，而不是简单删字。"),
        ("请求", "可执行请求应说明具体行为、负责人、期限和完成标准，同时允许对方提出限制或替代方案。"),
        ("边界", "边界描述自己会接受什么、不会接受什么以及必要时采取的行动，不是控制他人情绪或强迫其同意。"),
        ("反馈", "高质量反馈围绕具体行为、可观察影响和未来行动，并在合适时间私下沟通；人格标签和动机猜测难以改进。"),
        ("接受反馈", "接收反馈时先澄清例子与影响，再区分事实、偏好和建议；理解反馈不代表必须同意全部结论。"),
        ("困难对话", "困难对话前分别准备事实、自己的贡献、对方可能的视角、共同目标和暂停条件，避免在高唤醒状态下追求一次解决。"),
        ("冲突", "冲突处理中先保障安全，再区分议题、关系和流程；重复升级、威胁或权力失衡场景可能需要第三方和正式渠道。"),
        ("利益与立场", "立场是表面的要求，利益是要求背后的需要、担忧和限制；识别利益有助于产生不只输赢两种选择。"),
        ("BATNA", "BATNA 是谈不成时可实际执行的最佳替代方案；它需要提前验证成本和可行性，不能把愿望写成退路。"),
        ("论点", "完整论点包含主张、证据和证据为何支持主张的推理；只罗列数据或重复结论都不足以建立论证。"),
        ("决策矩阵", "决策矩阵先定义互不重复的标准和权重，再用证据评分；结果用于暴露取舍，不能替代对错误假设和伦理边界的检查。"),
        ("问题定义", "问题定义写清当前状态、期望状态、差距、影响范围和证据；过早跳到方案会把症状当根因。"),
        ("会议", "有效会议在会前说明目的、输入和决策人，会中记录结论与异议，会后留下负责人、期限和未决问题。"),
        ("表达复盘", "沟通复盘比较预期与实际理解、行动和关系影响，寻找下一次可改变的一项行为，而不是只评价自己表现好坏。"),
    ],
    "digital_literacy": [
        ("数字资产", "数字资产清单记录关键账号、设备、重要数据、管理员和恢复渠道；先保护邮箱、支付和身份账号等高影响入口。"),
        ("威胁模型", "个人威胁模型用资产、可能对手、攻击路径、影响和可接受成本决定优先级，不追求对所有风险一视同仁。"),
        ("密码管理器", "密码管理器帮助每个账号使用长且唯一的口令；主口令、恢复方式和设备解锁必须单独保护并演练。"),
        ("多因素认证", "多因素认证在口令之外增加独立凭据；能选时优先抗钓鱼方式，并安全保存一次性恢复码。"),
        ("更新", "系统、浏览器、应用和路由器更新用于修复已知缺陷；关键设备应开启自动安全更新并移除不再支持的软件。"),
        ("最小权限", "日常使用标准账户，应用只获得完成当前功能所需的文件、相机、麦克风、位置和联系人权限。"),
        ("隐私设置", "隐私设置应按数据敏感度、分享对象、保留时间和平台用途逐项审查，默认公开或一次授权不应永久沿用。"),
        ("家庭网络", "家庭路由器应更改默认管理员凭据、启用当前加密、更新固件并隔离不可信设备；访客网络不能替代所有设备更新。"),
        ("钓鱼", "钓鱼利用紧迫、权威、利益或恐惧诱导点击、登录或转账；应通过已知官网或电话独立核实，而不是使用消息中的入口。"),
        ("链接", "检查链接时关注实际域名、协议、拼写和跳转，短链与二维码先在隔离环境解析；页面外观相似不能证明归属。"),
        ("社会工程", "社会工程攻击人的信任和流程缺口；验证码、远程控制、共享屏幕、秘密转账和绕过正规渠道都是高风险请求。"),
        ("备份", "备份至少要与原设备故障隔离，并定期恢复抽查；只看到同步成功图标不能证明历史版本和恢复密钥可用。"),
        ("加密", "加密保护设备丢失或介质被读取时的数据，但恢复密钥丢失也可能造成永久数据损失；先备份并单独保存恢复材料。"),
        ("事件响应", "账号或设备异常时先隔离风险、保留证据、从可信设备改密和撤销会话，再联系平台、金融机构或执法渠道并复盘入口。"),
        ("横向阅读", "横向阅读会离开当前页面，在新标签搜索发布者、原始来源和其他独立报道，避免被单个页面的设计和自我介绍困住。"),
        ("点击克制", "搜索结果前列可能是广告或优化内容；点击前先比较域名、发布者和摘要，必要时直接寻找机构官网或原始资料。"),
        ("证据", "证据评估关注原始数据、采集方法、样本、日期、上下文和能否由其他来源复核，不因图表精美或引用众多就默认可靠。"),
        ("图片与视频", "图片和视频核验应查找原始发布、拍摄时间地点、反向搜索和前后帧；截图会丢失来源和上下文。"),
        ("推荐算法", "推荐系统优化停留、互动或商业目标，不代表内容真实、重要或适合个人；主动调整关注源和使用时段。"),
        ("AI 生成", "AI 输出可能流畅但虚构事实、来源和确定性；高影响结论必须回到可访问的一手资料并人工复核。"),
        ("个人信息", "收集、上传或分享个人信息前评估必要性、接收者、保存期限和泄露后果，优先脱敏、最少披露和可撤销授权。"),
    ],
    "agent_tools": [
        ("Codex CLI", "Codex CLI 可在项目目录中检查、编辑和运行代码；安装方式、登录入口、权限与命令应以 OpenAI Docs 当前页面为准，首次任务先用 `/status`、`/permissions` 和只读仓库说明确认边界。"),
        ("AGENTS.md", "AGENTS.md 把构建命令、测试方式、代码规范和禁止事项放进仓库；内容要短、可验证并随代码评审，不能把自然语言约定误当成操作系统级权限。"),
        ("codex exec", "`codex exec` 用于可重复的非交互任务；脚本必须固定工作目录、输入、权限、超时、退出码和产物检查，不能在无人监督时放大可写范围。"),
        ("Claude Code", "Claude Code 官方提供原生安装、Homebrew 和 WinGet 等方式；首次运行在目标仓库执行 `claude`，并先确认登录、工作目录及当前权限模式。"),
        ("CLAUDE.md", "CLAUDE.md 在会话开始时提供项目约定，适合记录架构、常用命令和验收清单；敏感值、易过期版本号和无法执行的口号不应写入。"),
        ("Claude 权限", "Claude Code 的权限规则按 deny、ask、allow 控制工具；读、写、Shell 和额外目录要分别评估，高风险命令保留逐次确认。"),
        ("Hooks", "Hooks 在代理动作前后运行确定性命令，适合格式化、测试或阻止受保护文件；Hook 自身也是可执行代码，必须版本控制、超时并验证失败行为。"),
        ("OpenCode", "OpenCode 可用官方安装脚本、npm、包管理器或发行二进制安装；Windows 官方建议优先 WSL，初始化项目后 `/init` 会生成可评审的 AGENTS.md。"),
        ("Provider", "Provider 配置决定模型、认证和端点；凭据应通过受支持的登录流程或环境变量提供，配置文件只引用变量，不能提交真实 API Key。"),
        ("OpenCode Agent", "OpenCode 可用 Markdown 或配置定义主代理和子代理；角色说明、可用工具、权限和最大步骤必须与实际职责一致。"),
        ("OpenCode Permission", "OpenCode 的工具和权限配置应从只读最小集开始，再按任务增加写入或 Shell 能力；项目配置必须与用户级配置的覆盖关系一起检查。"),
        ("Gemini CLI", "Gemini CLI 官方 npm 包是 `@google/gemini-cli`，安装后用 `gemini --version` 核对；个人登录、API Key 与 Vertex AI 的认证条件不同，按账号场景选择。"),
        ("GEMINI.md", "GEMINI.md 提供项目上下文和长期约定；结合 `.geminiignore` 控制无关或敏感文件进入上下文，并用可信文件夹机制限制未审查仓库。"),
        ("Gemini 沙箱", "Gemini CLI 可使用沙箱隔离有副作用的工具；沙箱、可信目录和审批分别控制执行环境、上下文信任与动作授权，三者不能互相替代。"),
        ("Copilot CLI", "GitHub Copilot CLI 可通过 npm、WinGet 或 Homebrew 安装，首次运行 `copilot` 后用 `/login` 认证；组织账号还需确认管理员策略是否允许 CLI。"),
        ("Aider", "Aider 官方优先推荐隔离安装方式，例如 aider-install、uv tool 或 pipx；进入 Git 仓库后再选择模型和 Provider，并先核对版本与仓库状态。"),
        ("Cline", "Cline 可作为 IDE 扩展或 CLI 使用；CLI 需要 Node.js 20+，安装后执行 `cline auth`，IDE 中则要先审查 Provider、自动批准和工作区访问设置。"),
        ("goose", "goose 提供桌面端与 CLI，并通过 Provider、MCP 扩展和 ACP 连接能力；Windows 安装要按当前官方前置条件核对 Shell、PATH 与凭据存储。"),
        ("安装来源", "安装前只从产品官网、官方包仓库或官方发布页取得命令；管道执行远程脚本前先下载、检查来源和内容，并保存版本与卸载路径。"),
        ("版本核对", "安装完成后同时记录命令路径、版本、运行时和更新渠道；排障先确认当前调用的不是旧 PATH、别名或另一个环境中的同名程序。"),
        ("认证", "交互式登录、订阅、API Key 和云服务身份具有不同配额与数据边界；只选择当前任务所需方式，并验证登出、轮换和失效流程。"),
        ("API Key", "API Key 只通过环境变量、系统凭据库或产品支持的安全存储提供；不写入仓库、指令文件、终端历史、截图和共享会话。"),
        ("Git 基线", "代理写代码前先确认仓库、分支和 `git status`，保留可恢复检查点；完成后只审查本轮 diff，不覆盖用户原有未提交修改。"),
        ("工作目录", "Coding Agent 的可见文件、项目指令和可写范围通常取决于启动目录；进入任务前要打印绝对路径并确认仓库根目录。"),
        ("只读", "陌生仓库先用只读解释、搜索和计划任务建立调用链，确认测试与风险后才开放编辑；只读模式可显著降低误改和提示注入的影响。"),
        ("Plan 模式", "Plan 模式应产出文件范围、调用链、风险、测试和停止条件；计划仍需由人检查，不能因为模式名称而默认结论正确。"),
        ("diff", "diff 是代理改动的主要验收边界：检查需求相关性、意外删除、敏感信息、生成文件和测试变化，再决定接受、继续修改或回滚。"),
        ("MCP", "MCP 给 Coding Agent 连接外部工具和数据；安装服务器前核对发布者、命令、环境变量、暴露工具和网络范围，并先在测试数据上验证。"),
        ("Agent Skills", "Agent Skills 把可重复流程和资源组织为可发现指令；跨工具复用前要核对各客户端支持范围、权限继承和依赖，而不是假设同名能力完全一致。"),
        ("跨工具", "跨工具迁移时先抽取共同的任务说明、仓库约定、验证命令和权限矩阵，再分别映射到 AGENTS.md、CLAUDE.md、GEMINI.md 或产品配置。"),
        ("提示注入", "仓库文件、网页、Issue 和工具输出都可能夹带恶意指令；外部内容只作为数据处理，敏感读取、网络发送和副作用动作必须由权限和人工审批阻断。"),
        ("回滚", "回滚依靠独立分支、清晰 diff、检查点和可重复测试；不要用会覆盖用户工作区的破坏性 Git 命令制造干净状态。"),
        ("成本", "不同订阅、模型和 Provider 的计费与配额会变化；记录任务耗时、轮次、上下文和调用量，用代表性任务比较而不硬编码价格。"),
        ("评估", "工具评估应在同一仓库、同一任务和同一验收集上比较成功率、误改、测试、耗时、人工介入和成本，而不是只比较生成文本观感。"),
        ("Coding Agent", "Coding Agent 能读取代码、编辑文件和运行工具；安全使用依赖清晰任务、最小权限、Git 检查点、测试与人工 diff 审查。"),
    ],
    "agent": [
        ("Agent", "Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。"),
        ("PEAS", "PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。"),
        ("LLM", "单次模型调用不会自动保存业务会话状态；多轮连续性来自应用重新提供消息、服务端会话能力或外部状态存储。"),
        ("消息", "系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。"),
        ("结构化输出", "结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。"),
        ("工具", "工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。"),
        ("JSON Schema", "JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。"),
        ("ReAct", "ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。"),
        ("Plan-and-Solve", "Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。"),
        ("Reflection", "Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。"),
        ("LangGraph", "LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。"),
        ("记忆", "短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。"),
        ("RAG", "RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。"),
        ("上下文", "上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。"),
        ("MCP", "MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。"),
        ("A2A", "A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。"),
        ("多智能体", "多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。"),
        ("提示注入", "提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。"),
        ("最小权限", "每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。"),
        ("评估", "Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。"),
        ("可观测", "可观测性需要关联一次运行中的模型调用、工具调用、状态变化、错误与费用，且日志必须脱敏。"),
        ("Agentic RL", "Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。"),
        ("SFT", "监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。"),
        ("GRPO", "GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。"),
        ("幂等", "幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。"),
        ("人工审批", "人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。"),
    ],
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
        ("Headers", "Headers 展示所选请求的 HTTP 头；重点核对内容类型、认证、Cookie、缓存以及服务端返回的响应元数据。"),
        ("Payload", "Payload 展示查询参数、表单数据或请求体；复现时要保持字段层级、编码方式和 Content-Type 一致。"),
        ("Preview", "Preview 是浏览器对响应内容的格式化预览，Response 才是原始响应；解析前应同时核对状态码和真实响应体。"),
        ("Initiator", "Initiator 显示请求的发起位置或调用栈，可用于从目标请求反向定位生成参数的脚本。"),
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
    "finance": [(1, "准备一份使用虚拟或脱敏金额的个人财务练习表"), (8, "能解释资产、负债和现金流基线"), (15, "已连续记录一周支出并完成预算复盘"), (22, "能计算应急储备和债务年化成本"), (29, "会核对合同、保险责任和诈骗信号"), (36, "理解风险、收益、期限、费用和分散"), (43, "能把住房、教育、养老等目标纳入现金流"), (50, "已建立月度财务检查流程"), (57, "准备好完整但脱敏的年度财务方案")],
    "health": [(1, "准备健康记录表；本路线不能替代诊疗或认证急救培训"), (8, "能区分低风险自我照护与需要就医的情况"), (15, "完成一周睡眠和日常活动基线"), (22, "能阅读食品标签并制定可执行饮食调整"), (29, "已建立循序渐进的活动与久坐中断计划"), (36, "能识别压力、社会支持和专业求助边界"), (43, "会准备就医问题并安全管理家庭药物"), (50, "已核对家庭急救、联系人和应急物资"), (57, "准备进行家庭健康与应急综合演练")],
    "communication": [(1, "准备一个低风险真实场景和可录音或书写的练习环境"), (8, "能区分观察、解释、感受和请求"), (15, "能通过复述和开放问题确认理解"), (22, "能写清结论、依据、行动和期限"), (29, "能给出并接收基于行为的反馈"), (36, "能为困难对话设置安全与暂停条件"), (43, "能区分立场、利益、选项和替代方案"), (50, "能用证据定义问题并比较方案"), (57, "准备完成真实沟通问题的综合改进")],
    "digital_literacy": [(1, "仅使用本人账号、测试账户和离线可疑样例"), (8, "完成关键账号、设备和数据资产清单"), (15, "关键账号已使用唯一口令、多因素认证和恢复码"), (22, "能审查设备、应用、网络和隐私权限"), (29, "能识别并独立核实钓鱼与诈骗请求"), (36, "已完成一次隔离备份和恢复抽查"), (43, "能用横向阅读核验发布者、证据和其他来源"), (50, "能标注 AI、图片、视频和统计结论的不确定性"), (57, "准备完成家庭数字安全与信息核验演练")],
    "agent_tools": [(1, "会使用 PowerShell 或终端、Git 和编辑器，并准备一个不含敏感数据的练习仓库"), (8, "已建立版本、凭据、权限和 Git 回滚基线"), (15, "能安全完成 Codex CLI 的只读、修改与审查闭环"), (22, "能配置 Claude Code 的指令、权限和 Hooks"), (29, "能使用 OpenCode 的 Provider、模式、Agent 与权限"), (36, "能安装并使用 Gemini CLI 与 Copilot CLI"), (43, "能比较 Aider、Cline 和 goose 的交互与配置边界"), (50, "能迁移项目指令、MCP 和 Skills，并用统一指标评估工具"), (57, "已选定真实项目、主工具、备用工具与验收集")],
    "agent": [(1, "具备 Python 函数、类、异常、JSON 和 HTTP API 基础"), (8, "能用假模型完成一次有边界的消息调用"), (15, "能实现带参数校验和停止条件的工具循环"), (22, "理解状态图、检查点与人工审批"), (29, "能区分短期记忆、长期记忆、RAG 与上下文"), (36, "能实现 MCP 工具或多智能体任务夹具"), (43, "已建立安全、评估和可观测性基线"), (50, "能在预算内完成可靠的端到端 Agent 原型"), (57, "已选定毕业项目场景、数据和验收集")],
    "python": [(1, "无需编程基础；会使用终端即可"), (13, "已掌握容器、条件与循环"), (25, "会用函数拆分和处理文件异常"), (37, "理解类、迭代器、生成器与上下文"), (49, "会写 pytest 并理解并发基础"), (55, "能独立编写模块、测试与数据存储代码")],
    "crawler": [(1, "具备 Python 变量、函数和文件读写基础"), (13, "能用 requests 获取并保存响应"), (25, "能解析 HTML/JSON 并幂等入库"), (33, "理解 Cookie、认证和动态接口"), (37, "能写可靠的串行下载器"), (49, "能说明完整采集管道和故障证据")],
    "javascript": [(1, "具备 Python 与 HTTP 基础"), (19, "能独立运行 JavaScript 并解释异步和编码"), (25, "会用 Network、断点和调用栈定位入口"), (31, "能写可恢复的 Hook 并保存测试向量"), (37, "理解 AST 节点和小步反混淆"), (43, "能区分纯算法与浏览器环境依赖"), (55, "能完成单点定位、还原与对拍")],
    "android": [(1, "具备 JavaScript/Python 与 HTTP 基础，仅使用自有或授权 APK"), (7, "ADB、安装、日志和抓包环境已验收"), (13, "能阅读 Java 的类、集合与异常"), (25, "能用 JADX/Apktool 完成静态画像"), (31, "Frida 版本、架构和基本 Hook 已通过"), (40, "能从调用栈追踪 Java 参数来源"), (49, "理解 JNI、ELF、ARM64 与模块偏移")],
    "ios": [(1, "有可用 macOS/Xcode 环境，仅使用自有或授权 App"), (7, "能构建、签名、安装并读取测试 App 日志"), (13, "能阅读 Objective-C/Swift 基础代码"), (19, "能解释 IPA、Mach-O、依赖与 Entitlement"), (25, "能在静态工具中定位字符串和交叉引用"), (31, "能用 LLDB、代理和日志验证运行行为"), (37, "能编写可恢复的最小 Hook"), (43, "理解加载、ASLR、砸壳与重签的关系"), (49, "能采集固定字节向量并跨语言对拍")],
}


FALLBACK_CONCEPT_NOTES = {
    "finance": "“{term}”需要放进个人财务系统理解：写清金额口径、期限、流动性、费用、最坏损失、合同来源和可复核计算，不做具体产品推荐。",
    "health": "“{term}”需要放进安全的健康或应急场景理解：记录观察、适用人群、低风险行动、停止条件、就医信号和专业来源，不自行诊断。",
    "communication": "“{term}”需要通过低风险角色演练理解：明确对象、目标、可核对事实、对方视角、请求、边界、下一步和复盘证据。",
    "digital_literacy": "“{term}”需要在本人测试账号或离线样例中验证：明确资产或主张、威胁、证据、保护动作、恢复路径和剩余不确定性。",
    "agent_tools": "“{term}”应放进一次可回滚的 Coding Agent 任务中理解：确认官方来源、版本、工作目录、凭据、权限、输入上下文、实际 diff、测试与失败恢复。",
    "agent": "“{term}”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。",
    "python": "“{term}”需要放进可运行函数或模块中理解：明确对象类型、输入输出、异常契约与资源状态，再用断言验证正常和失败路径。",
    "crawler": "“{term}”应定位到请求、响应校验、解析、清洗、去重、存储或恢复中的具体一层，并声明输入结构、输出结构与失败去向。",
    "javascript": "“{term}”应在浏览器或 Node 的真实调用链中确认：记录值与字节表示、作用域或宿主状态，再用固定向量证明复现前后语义一致。",
    "android": "“{term}”应先判断属于组件、DEX/Java、网络、存储还是 Native 层，再以 APK 版本、静态位置和运行时证据共同验证。",
    "ios": "“{term}”应先判断属于签名、Objective-C/Swift 运行时、Mach-O、网络、存储还是加载链，并用镜像偏移与运行证据验证。",
}


def track_kind(track):
    """把路线标识转换为教学类型。

    Args:
        track: 系统路线 slug 或综合路线学习日的基础分类。

    Returns:
        对应教学类型；未知分类返回空字符串。
    """
    return SYSTEM_TRACKS.get(track, track if track in SYSTEM_TRACKS.values() else "")


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
    """返回指定课程类型和学习日的可验证前置要求。"""
    result = STAGE_PREREQUISITES.get(kind, [(1, "具备上一学习日要求的基础")])[0][1]
    for start, note in STAGE_PREREQUISITES.get(kind, []):
        if day_number >= start:
            result = note
    if day_number == 1:
        return [result]
    if kind in LIFESTYLE_TRACKS:
        return [result, "已完成上一学习日的练习记录，并能说明一个常规情境、边界情境和改进点"]
    return [result, "能够运行上一学习日的最小示例并解释其正常与失败路径"]


def concept_notes(kind, core):
    """把课程核心术语映射为经过编辑核对的概念解释。"""
    terms = [part.strip(" `") for part in re.split(r"[、，,/+]", core) if part.strip(" `")]
    notes = []
    unmatched = []
    for term in terms:
        match = next((note for key, note in TERM_NOTES.get(kind, []) if keyword_matches(key, term)), None)
        # 生活课程只展示与当天主题直接匹配的编辑说明，避免用泛化套话冒充具体知识。
        if kind in LIFESTYLE_TRACKS and not match:
            continue
        if match:
            existing = next((item for item in notes if item["explanation"] == match), None)
            if existing:
                existing["term"] += f" / {term}"
            else:
                notes.append({"term": term, "explanation": match})
        else:
            unmatched.append(term)
    # 多个未收录术语属于同一个当天主题，只给一次通用导读，避免逐词复制同一句模板。
    if unmatched:
        combined = "、".join(unmatched)
        notes.append({"term": combined, "explanation": FALLBACK_CONCEPT_NOTES[kind].format(term=combined)})
    return notes or [{"term": core, "explanation": FALLBACK_CONCEPT_NOTES[kind].format(term=core)}]


def code(lines):
    return "\n".join(lines)


# 安装和登录会修改用户环境，因此课件只提供可审查的命令清单，不在自动测试中执行第三方安装。
AGENT_TOOL_EXAMPLES = [
    (("Coding Agent", "安装来源", "版本核对", "认证", "API Key", "Git 基线", "工作目录", "只读", "Plan 模式", "diff", "提示注入", "回滚", "成本", "评估"), code([
        "$ErrorActionPreference = 'Stop'", "$repo = (Get-Location).Path", "git rev-parse --show-toplevel",
        "git status --short", "git branch --show-current", "node --version", "python --version",
        "# 只在练习仓库继续；保存上述输出后再按官方文档安装目标工具。",
    ]), ["先证明当前目录、分支和未提交状态，再允许代理读取或修改仓库。", "版本和环境清单是排查 PATH、运行时与旧配置问题的第一份证据。"]),
    (("Codex CLI", "AGENTS.md", "codex exec"), code([
        "codex --version", "codex", "# 交互界面依次检查：/status、/permissions、/init、/review",
        "# 非交互任务先在练习仓库验证 codex exec 的权限、退出码与 diff。",
    ]), ["Codex 首次运行先确认会话状态和权限，再创建或评审 AGENTS.md。", "任何写入任务完成后都运行测试并审查 Git diff，不能只接受最终回答。"]),
    (("Claude Code", "CLAUDE.md", "Claude 权限", "Hooks"), code([
        "winget install Anthropic.ClaudeCode", "claude --version", "claude",
        "# 会话内先运行 /permissions，再让 Claude 只读解释项目并生成可评审计划。",
    ]), ["WinGet 是官方列出的 Windows 安装方式之一；安装后立即记录版本。", "CLAUDE.md、权限规则和 Hooks 分别负责项目上下文、能力边界与确定性检查。"]),
    (("OpenCode", "Provider", "OpenCode Agent", "OpenCode Permission"), code([
        "npm install -g opencode-ai", "opencode --version", "opencode", "# TUI 中执行 /connect，再在练习仓库执行 /init。",
        "# 先使用 Plan 模式，审查计划后再切换 Build；错误改动用 /undo。",
    ]), ["Provider 凭据通过产品登录或环境变量提供，不写进 opencode.json。", "Plan/Build、权限、Agent 和 `/undo` 共同组成可审查、可恢复的操作闭环。"]),
    (("Gemini CLI", "GEMINI.md", "Gemini 沙箱"), code([
        "npm install -g @google/gemini-cli", "gemini --version", "gemini",
        "# 选择与账号匹配的认证方式；先检查可信目录、GEMINI.md 与沙箱设置。",
    ]), ["稳定版 npm 包和版本命令用于建立可复现安装记录。", "个人登录、API Key 与 Vertex AI 的身份和数据边界不同，不能混用配置。"]),
    (("Copilot CLI",), code([
        "winget install GitHub.Copilot", "copilot --version", "copilot", "# 首次进入后运行 /login、/help，并确认目录信任提示。",
        "# 非交互模式先用只读问题验证输出和退出码，再接入脚本。",
    ]), ["组织账号需先确认管理员已启用 Copilot CLI 策略。", "目录信任和显式批准是首次使用的重要边界，自动化不能绕过。"]),
    (("Aider",), code([
        "python -m pip install aider-install", "aider-install", "aider --version", "git status --short",
        "# 在练习仓库启动 aider，先选择 Provider/模型并限制加入上下文的文件。",
    ]), ["aider-install 会把 Aider 放入隔离环境，避免污染项目依赖。", "Aider 与 Git 深度集成，开始前和每轮修改后都要核对提交与 diff。"]),
    (("Cline",), code([
        "npm install -g cline", "cline --version", "cline auth", "cline", "# IDE 用户改为从官方扩展市场安装，并先关闭宽泛自动批准。",
    ]), ["CLI 与 IDE 扩展是不同入口，先选择一种完成最小闭环。", "Provider、Rules、自动批准和工作区范围应分别检查。"]),
    (("goose",), code([
        "goose --version", "goose configure", "# Windows 先按当前官方文档选择桌面端或满足前置条件的 CLI 安装。",
        "# 只启用完成练习所需的 Provider 和扩展，再运行只读项目说明任务。",
    ]), ["Windows 的 Shell、PATH 和凭据存储是 goose 安装后的首要排查点。", "Provider 与 MCP 扩展扩大能力面，启用前要审查命令、网络和数据范围。"]),
    (("MCP", "Agent Skills", "跨工具"), code([
        "Get-ChildItem -Force AGENTS.md,CLAUDE.md,GEMINI.md -ErrorAction SilentlyContinue",
        "git diff -- AGENTS.md CLAUDE.md GEMINI.md", "# 对每个客户端分别列出 MCP、Skills、权限和配置来源，不假设自动兼容。",
    ]), ["共同规则先写成短小、可执行的项目事实，再映射到各工具的指令文件。", "MCP 和 Skills 的发现机制相似，但支持范围、权限继承与配置位置必须逐工具验证。"]),
]


AGENT_EXAMPLES = [
    (("LLM", "消息", "Prompt", "结构化输出", "token", "模型"), code([
        "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Reply:",
        "    answer: str", "    confidence: float", "", "def parse_reply(data: dict) -> Reply:",
        "    answer = str(data.get('answer', '')).strip()", "    confidence = float(data.get('confidence', -1))",
        "    if not answer or not 0 <= confidence <= 1:", "        raise ValueError('invalid model reply')",
        "    return Reply(answer, confidence)", "", "reply = parse_reply({'answer':'完成','confidence':0.8})",
        "assert reply.answer == '完成'", "print(reply)",
    ]), ["模型输出先作为不可信字典解析，再验证必需字段和数值范围。", "结构化格式减少解析歧义，但不能替代业务校验和权限检查。"]),
    (("工具", "Function Calling", "JSON Schema", "参数", "注册"), code([
        "TOOLS = {'add': lambda a, b: a + b}", "", "def execute(call: dict):",
        "    name = call.get('name')", "    arguments = call.get('arguments')", "    if name not in TOOLS:",
        "        raise ValueError('unknown tool')", "    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:",
        "        raise ValueError('invalid arguments')", "    return TOOLS[name](int(arguments['a']), int(arguments['b']))", "",
        "assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5",
        "print('unknown tool and invalid arguments are rejected')",
    ]), ["注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。", "参数集合和类型在工具边界验证，失败不会进入真实副作用。"]),
    (("ReAct", "Agent Loop", "行动", "观察", "停止条件"), code([
        "def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):", "    observations = []",
        "    for _ in range(max_steps):", "        action = decide(goal, observations)",
        "        if action['name'] == 'finish': return action['answer'], observations",
        "        if action['name'] not in tools: raise ValueError('unknown tool')",
        "        observations.append(tools[action['name']](action['argument']))",
        "    raise RuntimeError('step budget exhausted')", "", "def fake_decide(goal, observations):",
        "    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}", "",
        "answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})",
        "assert answer == 'AGENT' and trace == ['AGENT']", "print(answer, trace)",
    ]), ["假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。", "步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。"]),
    (("Plan-and-Solve", "Reflection", "计划", "反思", "评审"), code([
        "def validate_plan(plan: list[str]) -> list[str]:", "    cleaned = [step.strip() for step in plan if step.strip()]",
        "    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')", "    return cleaned", "",
        "def reflect(result: str, checks: list[str]) -> list[str]:",
        "    return [check for check in checks if check not in result]", "",
        "plan = validate_plan(['收集输入', '执行任务', '验证结果'])",
        "missing = reflect('执行任务完成', plan)", "assert missing == ['收集输入', '验证结果']",
        "print({'plan': plan, 'missing': missing})",
    ]), ["计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。", "反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。"]),
    (("LangGraph", "状态图", "检查点", "人工审批", "工作流"), code([
        "TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}", "", "def advance(state: dict, approved=False):",
        "    current = state['status']", "    if current == 'review' and not approved:",
        "        return {**state, 'paused': True}", "    return {**state, 'status': TRANSITIONS[current], 'paused': False}", "",
        "state = advance({'status':'draft'})", "state = advance(state)", "assert state['paused'] is True",
        "state = advance(state, approved=True)", "assert state['status'] == 'approved'", "print(state)",
    ]), ["显式状态和转换表使执行路径可以检查、持久化和恢复。", "高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。"]),
    (("记忆", "RAG", "检索", "上下文", "GSSC", "分块"), code([
        "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Packet:",
        "    text: str", "    score: float", "    tokens: int", "", "def select(packets, budget):",
        "    chosen, used = [], 0", "    for packet in sorted(packets, key=lambda item: item.score, reverse=True):",
        "        if used + packet.tokens <= budget:", "            chosen.append(packet); used += packet.tokens",
        "    return chosen", "", "packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]",
        "result = select(packets, 6)", "assert [item.text for item in result] == ['有来源的答案']", "print(result)",
    ]), ["候选信息先带来源、相关性和 token 成本，再按预算选择。", "仅扩大上下文不会提高质量；低相关历史会挤占真正证据。"]),
    (("MCP", "A2A", "Agent Card", "Task", "Artifact", "多智能体"), code([
        "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Task:",
        "    task_id: str", "    capability: str", "    status: str = 'submitted'", "", "def delegate(task, cards):",
        "    matches = [card for card in cards if task.capability in card['skills']]", "    if len(matches) != 1:",
        "        raise ValueError('capability must resolve to one agent')", "    return matches[0]['name']", "",
        "cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]",
        "assert delegate(Task('t-1','search'), cards) == 'researcher'", "print('task routed')",
    ]), ["能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。", "零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。"]),
    (("评估", "可观测", "轨迹", "成本", "Agentic RL", "奖励", "安全"), code([
        "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class Run:",
        "    success: bool", "    tool_calls: int", "    cost: float", "    unsafe_actions: int = 0", "",
        "def reward(run: Run) -> float:", "    if run.unsafe_actions: return -1.0",
        "    return float(run.success) - .05 * run.tool_calls - run.cost", "",
        "safe = Run(True, 2, .1)", "unsafe = Run(True, 1, .01, 1)",
        "assert reward(safe) > 0 and reward(unsafe) == -1", "print(reward(safe), reward(unsafe))",
    ]), ["评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。", "安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。"]),
]


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
    "agent_tools": AGENT_TOOL_EXAMPLES,
    "agent": AGENT_EXAMPLES,
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
    if kind in ("finance", "health", "communication", "digital_literacy"):
        templates = {
            "finance": ("填写财务练习表并复核合计", ["事实与金额口径：", "计算过程与假设：", "风险、费用和最坏情形：", "决定、复核日期与证据："]),
            "health": ("填写健康练习表并完成安全边界核对", ["观察与适用条件：", "低风险行动：", "停止条件、就医或呼救信号：", "专业来源与复盘日期："]),
            "communication": ("完成沟通角色演练并保存复盘", ["对象、目标与可核对事实：", "对方观点复述：", "请求、边界与替代方案：", "下一步、期限与复盘："]),
            "digital_literacy": ("在测试账户完成数字安全检查并保存证据", ["资产、主张或风险：", "发布者、证据与独立来源：", "保护、查证或恢复动作：", "剩余风险与报告路径："]),
        }
        command, sections = templates[kind]
        sample = code([f"主题：{text}", *sections])
        return {"code": sample, "language": "text", "command": command, "explanation": ["模板把当天主题转成可检查的事实、行动和边界，避免只写心得。", "所有记录使用脱敏数据，并保存能由本人或同伴复核的证据。"]}
    if kind == "agent_tools":
        sample = code([
            "$ErrorActionPreference = 'Stop'", "$root = git rev-parse --show-toplevel",
            "Write-Host \"repository=$root\"", "git status --short",
            f"# 今日主题：{text}", "# 按官方文档完成配置或任务后，保存版本、实际命令、diff、测试与失败输出。",
        ])
        return {"code": sample, "language": "text", "command": "git rev-parse --show-toplevel", "explanation": ["先确认仓库根目录和未提交状态，避免在错误目录操作。", "今日主题完成后仍使用同一证据清单验收，便于跨工具比较与回滚。"]}
    if kind == "agent":
        sample = code([
            "from dataclasses import dataclass", "", "@dataclass(frozen=True)", "class StepResult:",
            "    topic: str", "    status: str", "    evidence: str", "", "def run(topic: str) -> StepResult:",
            "    if not topic.strip(): raise ValueError('topic is required')",
            "    return StepResult(topic, 'completed', '固定夹具与断言已通过')", "",
            f"result = run({text!r})", "assert result.status == 'completed'", "print(result)",
        ])
        return {"code": sample, "language": "python", "command": "python practice.py", "explanation": ["StepResult 固定记录主题、状态和证据，使实验结果可回放。", "将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。"]}
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
    """按课程类型与知识点选择最贴近的可运行示例。"""
    matches = []
    for keywords, sample, explanation in EXAMPLES.get(kind, []):
        matched = [keyword for keyword in keywords if keyword_matches(keyword, text)]
        if matched:
            matches.append((max(len(keyword) for keyword in matched), sample, explanation))
    if kind == "agent_tools":
        product_markers = {
            "Codex CLI": "codex --version",
            "Claude Code": "claude --version",
            "OpenCode": "opencode --version",
            "Gemini CLI": "gemini --version",
            "Copilot CLI": "copilot --version",
            "Aider": "aider --version",
            "Cline": "cline --version",
            "goose": "goose --version",
        }
        product_matches = [
            match
            for match in matches
            if any(
                keyword_matches(product, text) and marker in match[1]
                for product, marker in product_markers.items()
            )
        ]
        if product_matches:
            matches = product_matches
    for _, sample, explanation in sorted(matches, key=lambda item: item[0], reverse=True)[:1]:
        language = "javascript" if kind in ("javascript", "android", "ios") else "python"
        command = {"agent": "python practice.py", "python": "python practice.py", "crawler": "python practice.py", "javascript": "node practice.mjs", "android": "frida -U -f com.example.lab -l practice.js", "ios": "lldb /path/to/AuthorizedLab.app/AuthorizedLab"}.get(kind, "python practice.py")
        if kind == "agent_tools":
            language = "text"
            command = next(line for line in sample.splitlines() if line and not line.startswith("#"))
        if kind == "android" and "public class" in sample:
            language, command = "java", "javac Lab.java && java -ea Lab"
        if sample.startswith(("adb ", "# 仅对", "xcodebuild", "unzip ", "lldb ", "otool ")):
            language, command = "text", sample.splitlines()[0]
        return {"code": sample, "language": language, "command": command, "explanation": explanation}
    return fallback_example(kind, text)


def build_teaching_sections(day_number, core, task, criteria, kind):
    concepts = concept_notes(kind, core)
    first_term = concepts[0]["term"] if concepts else core
    if kind in LIFESTYLE_TRACKS:
        safety_boundaries = {
            "finance": "涉及具体产品、税务或法律判断时停止代替专业意见，只保留比较框架并转向持牌或官方渠道。",
            "health": "出现急症信号、持续恶化或超出自我照护范围时停止练习，立即联系当地急救或医疗专业人员。",
            "communication": "出现威胁、骚扰、暴力或严重权力失衡时停止角色演练，优先离开风险并使用正式支持渠道。",
            "digital_literacy": "只操作本人或明确授权的账号、设备和数据；可疑链接使用离线样例，不测试攻击或绕过。",
        }
        return {
            "prerequisites": prerequisites(kind, day_number),
            "learning_objectives": [
                f"能用自己的话说明“{first_term}”解决什么问题，而不是只记名称",
                f"能独立完成：{task}",
                "能用脱敏记录、对照证据和安全边界解释结果，并指出仍需核实的信息",
            ],
            "concept_map": concepts,
            "comprehensive_task": {
                "goal": task,
                "input": f"使用本人脱敏记录、虚拟案例或双方同意的低风险场景，覆盖“{core}”涉及的事实与条件。",
                "output": "提交填写完整的练习表或角色演练记录，并标出判断依据、安全边界、下一步和复盘日期。",
                "requirements": [
                    "先按模板完成一次引导练习，再关闭参考内容独立完成",
                    "把可核对事实、个人判断和后续行动分开记录",
                    "至少包含一个常规情境和一个边界或失败情境",
                ],
                "error_cases": [
                    "资料不足或来源冲突时明确标注未知，不用猜测补齐结论",
                    safety_boundaries[kind],
                ],
            },
            "verification": {
                "checks": list(criteria) + ["常规与边界或失败情境均已保存", "能闭卷解释判断依据、适用范围和停止条件"],
                "evidence": [
                    "填写完整的脱敏练习表或角色演练记录",
                    "关键事实、计算、来源或观察证据",
                    "边界或失败样例及其安全处理",
                    "100 字以上复盘与一个下一步行动",
                ],
            },
            "workflow": [
                {"title": "先建立边界", "body": "阅读前置要求和安全边界，写下今天可以练什么、遇到什么情况必须停止或求助。"},
                {"title": "跟做并核对", "body": "使用脱敏记录、虚拟案例或低风险场景填写模板，逐项区分事实、判断和行动。"},
                {"title": "关闭答案独立完成", "body": f"不复制参考内容，独立完成“{task}”；资料不足时明确写出未知项。"},
                {"title": "用边界证明掌握", "body": "加入一个失败或边界情境，保存处理证据，并按验收条件复盘下一步。"},
            ],
        }
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
