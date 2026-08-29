# AI Agent 工程：60 日详细学习课件

内容版本：5
适用人群：掌握 Python、JSON、HTTP API 基础，希望系统构建可靠 Agent 应用的学习者
学习周期：60 天（约 9 周，每天建议 120 分钟；毕业项目日建议 150 分钟）

## 使用方法

本课件与系统学习路径逐日一致。每天先阅读本日定位和公开资料，再运行不依赖真实 API 的参考骨架；随后关闭答案完成独立任务，最后用失败样例、断言、轨迹或评估报告验收。真实模型、GPU 训练和外部 MCP/A2A 服务均为可选条件，先用假模型、固定夹具和本地服务建立可重复基线。

所有工具输入、检索资料和模型输出都按不可信数据处理；涉及文件写入、外部消息、账号资源或其他不可逆动作时，必须使用最小权限、执行前预览和人工审批。

## 路线阶段

- 阶段一：智能体与大语言模型基础
- 阶段二：经典范式、工具与框架
- 阶段三：记忆、上下文与协作协议
- 阶段四：安全、评估与生产工程
- 阶段五：综合场景与毕业设计

## 资料口径

课程以 [Hello-Agents](https://github.com/datawhalechina/hello-agents) 的十六章结构为主线，并使用 ReAct、Reflexion、RAG 原始论文及 MCP、A2A、OWASP、NIST、LangGraph 等公开一手资料校正协议、安全和生产工程边界。框架版本会变化，验收重点是数据流、状态、权限、停止条件和可观测证据，而不是记忆某个版本的 API。

## Day 1 · Agent 与工作流边界

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作流”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础

学习目标：

- 能用自己的话说明“Agent”解决什么问题，而不是只记名称
- 能独立完成：为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Agent | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| 工作流 | “工作流”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 自主性 | “自主性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 反馈闭环 | “反馈闭环”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据

实现要求：先独立完成“为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 能指出至少三处由模型动态决策和三处应保持确定性的步骤
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 2 · 用 PEAS 定义任务环境

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “性能度量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为个人学习助理编写 PEAS 表和明确的不允许动作清单”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“PEAS”解决什么问题，而不是只记名称
- 能独立完成：为个人学习助理编写 PEAS 表和明确的不允许动作清单
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| PEAS | PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 |
| 性能度量 | “性能度量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 环境 | “环境”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 执行器 | “执行器”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 传感器 | “传感器”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为个人学习助理编写 PEAS 表和明确的不允许动作清单

实现要求：先独立完成“为个人学习助理编写 PEAS 表和明确的不允许动作清单”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('PEAS、性能度量、环境、执行器、传感器')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 性能指标、可观察输入、允许动作和禁止动作均可独立核对
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 3 · LLM 是无状态组件

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

LLM 是无状态的概率模型调用；消息历史、工具结果、预算和持久状态都由应用程序负责管理。 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 今日通过“用假模型记录 system、user、assistant 消息如何组成一次请求”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“LLM”解决什么问题，而不是只记名称
- 能独立完成：用假模型记录 system、user、assistant 消息如何组成一次请求
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| LLM | LLM 是无状态的概率模型调用；消息历史、工具结果、预算和持久状态都由应用程序负责管理。 |
| 消息 | 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 |
| 角色 | “角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| token | “token”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 采样 | “采样”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用假模型记录 system、user、assistant 消息如何组成一次请求

实现要求：先独立完成“用假模型记录 system、user、assistant 消息如何组成一次请求”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

运行命令：`python practice.py`

代码讲解：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 相同夹具可复现消息顺序并统计输入长度
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 4 · 提示层级与不可信数据

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

“系统提示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “用户输入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“系统提示”解决什么问题，而不是只记名称
- 能独立完成：把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 系统提示 | “系统提示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 用户输入 | “用户输入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 工具结果 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 提示注入 | 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则

实现要求：先独立完成“把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 可信指令与不可信资料在结构和日志中可区分
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 5 · 结构化输出契约

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。 JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。 今日通过“定义任务分解 JSON 契约并校验缺字段、越界值和多余动作”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“结构化输出”解决什么问题，而不是只记名称
- 能独立完成：定义任务分解 JSON 契约并校验缺字段、越界值和多余动作
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 结构化输出 | 结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。 |
| JSON Schema | JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。 |
| 解析 | “解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 业务校验 | “业务校验”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：定义任务分解 JSON 契约并校验缺字段、越界值和多余动作

实现要求：先独立完成“定义任务分解 JSON 契约并校验缺字段、越界值和多余动作”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 合法输出可解析，三类非法输出在执行前被拒绝
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 6 · 模型客户端的可靠边界

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

“超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用假传输层模拟超时、429、永久错误和部分响应”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“超时”解决什么问题，而不是只记名称
- 能独立完成：用假传输层模拟超时、429、永久错误和部分响应
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 超时 | “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 重试 | “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 速率限制 | “速率限制”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| token预算 | “token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 错误分类 | “错误分类”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用假传输层模拟超时、429、永久错误和部分响应

实现要求：先独立完成“用假传输层模拟超时、429、永久错误和部分响应”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

运行命令：`python practice.py`

代码讲解：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 重试仅覆盖暂时错误且总次数、等待和 token 预算可证明
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 7 · 第一个最小 Agent

> 阶段一：智能体与大语言模型基础｜第 1 周：Agent、LLM 与最小执行闭环｜建议 120 分钟

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“实现最多四步的本地问答 Agent，只允许查询固定字典工具”把原理落实为可运行、可验证的能力。

前置要求：

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Agent Loop”解决什么问题，而不是只记名称
- 能独立完成：实现最多四步的本地问答 Agent，只允许查询固定字典工具
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Agent Loop | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| 状态 | “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 行动 | “行动”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 观察 | “观察”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 停止条件 | “停止条件”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：实现最多四步的本地问答 Agent，只允许查询固定字典工具

实现要求：先独立完成“实现最多四步的本地问答 Agent，只允许查询固定字典工具”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):
    observations = []
    for _ in range(max_steps):
        action = decide(goal, observations)
        if action['name'] == 'finish': return action['answer'], observations
        if action['name'] not in tools: raise ValueError('unknown tool')
        observations.append(tools[action['name']](action['argument']))
    raise RuntimeError('step budget exhausted')

def fake_decide(goal, observations):
    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}

answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})
assert answer == 'AGENT' and trace == ['AGENT']
print(answer, trace)
```

运行命令：`python practice.py`

代码讲解：

- 假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。
- 步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 正常任务在预算内结束，未知问题以明确状态终止
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)

## Day 8 · 工具描述与参数模式

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “Function Calling”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为计算器和本地笔记查询设计互不重叠的工具描述与参数模式”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“工具”解决什么问题，而不是只记名称
- 能独立完成：为计算器和本地笔记查询设计互不重叠的工具描述与参数模式
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 工具 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| Function Calling | “Function Calling”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| JSON Schema | JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。 |
| 描述质量 | “描述质量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为计算器和本地笔记查询设计互不重叠的工具描述与参数模式

实现要求：先独立完成“为计算器和本地笔记查询设计互不重叠的工具描述与参数模式”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 固定问题能选中唯一工具且参数通过模式校验
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 9 · 工具注册表与执行器

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “分发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“实现白名单工具注册表，统一返回成功结果或结构化错误”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“工具注册”解决什么问题，而不是只记名称
- 能独立完成：实现白名单工具注册表，统一返回成功结果或结构化错误
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 工具注册 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 分发 | “分发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 参数校验 | “参数校验”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 返回协议 | “返回协议”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：实现白名单工具注册表，统一返回成功结果或结构化错误

实现要求：先独立完成“实现白名单工具注册表，统一返回成功结果或结构化错误”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 未知工具和缺失参数都不会调用底层函数
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 10 · 副作用与工具安全

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为“创建待办”工具加入幂等键、超时和只读预览模式”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“幂等”解决什么问题，而不是只记名称
- 能独立完成：为“创建待办”工具加入幂等键、超时和只读预览模式
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 幂等 | 幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 |
| 超时 | “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 重试 | “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 权限 | “权限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 副作用 | “副作用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为“创建待办”工具加入幂等键、超时和只读预览模式

实现要求：先独立完成“为“创建待办”工具加入幂等键、超时和只读预览模式”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('幂等、超时、重试、权限、副作用')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 重复请求只产生一条记录且超时不会留下半成品
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 11 · 实现 ReAct 循环

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 “Thought-Action-Observation”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“ReAct”解决什么问题，而不是只记名称
- 能独立完成：用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| ReAct | ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 |
| Thought-Action-Observation | “Thought-Action-Observation”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 动态纠错 | “动态纠错”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹

实现要求：先独立完成“用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):
    observations = []
    for _ in range(max_steps):
        action = decide(goal, observations)
        if action['name'] == 'finish': return action['answer'], observations
        if action['name'] not in tools: raise ValueError('unknown tool')
        observations.append(tools[action['name']](action['argument']))
    raise RuntimeError('step budget exhausted')

def fake_decide(goal, observations):
    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}

answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})
assert answer == 'AGENT' and trace == ['AGENT']
print(answer, trace)
```

运行命令：`python practice.py`

代码讲解：

- 假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。
- 步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 工具失败后能基于 Observation 修正一次且不会无限循环
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 12 · 实现 Plan-and-Solve

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 “任务分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把资料整理任务拆成可验证步骤，逐步执行并记录中间产物”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Plan-and-Solve”解决什么问题，而不是只记名称
- 能独立完成：把资料整理任务拆成可验证步骤，逐步执行并记录中间产物
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Plan-and-Solve | Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 |
| 任务分解 | “任务分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 依赖 | “依赖”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 重规划 | “重规划”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把资料整理任务拆成可验证步骤，逐步执行并记录中间产物

实现要求：先独立完成“把资料整理任务拆成可验证步骤，逐步执行并记录中间产物”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
def validate_plan(plan: list[str]) -> list[str]:
    cleaned = [step.strip() for step in plan if step.strip()]
    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')
    return cleaned

def reflect(result: str, checks: list[str]) -> list[str]:
    return [check for check in checks if check not in result]

plan = validate_plan(['收集输入', '执行任务', '验证结果'])
missing = reflect('执行任务完成', plan)
assert missing == ['收集输入', '验证结果']
print({'plan': plan, 'missing': missing})
```

运行命令：`python practice.py`

代码讲解：

- 计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。
- 反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 计划无循环依赖且任一步失败会停止或产生显式重规划
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 13 · 实现 Reflection

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。 “Evaluator”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用固定检查表评审一段初稿并最多修订两轮”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Reflection”解决什么问题，而不是只记名称
- 能独立完成：用固定检查表评审一段初稿并最多修订两轮
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Reflection | Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。 |
| Evaluator | “Evaluator”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 反馈 | “反馈”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 修订上限 | “修订上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用固定检查表评审一段初稿并最多修订两轮

实现要求：先独立完成“用固定检查表评审一段初稿并最多修订两轮”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
def validate_plan(plan: list[str]) -> list[str]:
    cleaned = [step.strip() for step in plan if step.strip()]
    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')
    return cleaned

def reflect(result: str, checks: list[str]) -> list[str]:
    return [check for check in checks if check not in result]

plan = validate_plan(['收集输入', '执行任务', '验证结果'])
missing = reflect('执行任务完成', plan)
assert missing == ['收集输入', '验证结果']
print({'plan': plan, 'missing': missing})
```

运行命令：`python practice.py`

代码讲解：

- 计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。
- 反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每条修订可追溯到检查项且达到轮数上限后停止
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 14 · 经典范式选型实验

> 阶段二：经典范式、工具与框架｜第 2 周：工具调用与经典智能体范式｜建议 120 分钟

### 本日定位

ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 今日通过“让三种范式运行同一组本地任务，对比成功率、步骤数和成本”把原理落实为可运行、可验证的能力。

前置要求：

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“ReAct”解决什么问题，而不是只记名称
- 能独立完成：让三种范式运行同一组本地任务，对比成功率、步骤数和成本
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| ReAct | ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 |
| Plan-and-Solve | Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 |
| Reflection | Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。 |
| 混合范式 | “混合范式”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：让三种范式运行同一组本地任务，对比成功率、步骤数和成本

实现要求：先独立完成“让三种范式运行同一组本地任务，对比成功率、步骤数和成本”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
def validate_plan(plan: list[str]) -> list[str]:
    cleaned = [step.strip() for step in plan if step.strip()]
    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')
    return cleaned

def reflect(result: str, checks: list[str]) -> list[str]:
    return [check for check in checks if check not in result]

plan = validate_plan(['收集输入', '执行任务', '验证结果'])
missing = reflect('执行任务完成', plan)
assert missing == ['收集输入', '验证结果']
print({'plan': plan, 'missing': missing})
```

运行命令：`python practice.py`

代码讲解：

- 计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。
- 反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 形成基于证据的选型表而不是只按框架名称判断
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)

## Day 15 · 低代码、框架还是原生代码

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

“Dify”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “n8n”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为三个业务场景分别选择固定流程、框架或自研循环并记录理由”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Dify”解决什么问题，而不是只记名称
- 能独立完成：为三个业务场景分别选择固定流程、框架或自研循环并记录理由
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Dify | “Dify”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| n8n | “n8n”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Agent框架 | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| 原生API | “原生API”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 选型 | “选型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为三个业务场景分别选择固定流程、框架或自研循环并记录理由

实现要求：先独立完成“为三个业务场景分别选择固定流程、框架或自研循环并记录理由”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Dify、n8n、Agent框架、原生API、选型')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每个选择都包含复杂度、可控性和退出成本
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 16 · 用状态图表达执行

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。 “节点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“LangGraph”解决什么问题，而不是只记名称
- 能独立完成：将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| LangGraph | LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。 |
| 节点 | “节点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 边 | “边”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 状态 | “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 条件路由 | “条件路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点

实现要求：先独立完成“将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 所有状态都有进入与退出条件且不存在无界环
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 17 · 检查点与恢复

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

“检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “持久化”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“在每个节点后保存 JSON 检查点，模拟进程中断后继续执行”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“检查点”解决什么问题，而不是只记名称
- 能独立完成：在每个节点后保存 JSON 检查点，模拟进程中断后继续执行
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 检查点 | “检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 持久化 | “持久化”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 恢复 | “恢复”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 幂等重放 | 幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：在每个节点后保存 JSON 检查点，模拟进程中断后继续执行

实现要求：先独立完成“在每个节点后保存 JSON 检查点，模拟进程中断后继续执行”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 恢复不会重复已经完成的副作用节点
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 18 · 人工审批是一等状态

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 “中断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“在发送消息前暂停并展示动作、参数、依据和影响”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“人工审批”解决什么问题，而不是只记名称
- 能独立完成：在发送消息前暂停并展示动作、参数、依据和影响
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 人工审批 | 人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 |
| 中断 | “中断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 恢复 | “恢复”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 高风险动作 | “高风险动作”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：在发送消息前暂停并展示动作、参数、依据和影响

实现要求：先独立完成“在发送消息前暂停并展示动作、参数、依据和影响”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 拒绝审批后不执行动作，修改参数后从检查点恢复
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 19 · 多智能体角色与消息

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。 “角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“设计研究员、撰写员和审核员的输入输出契约”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“多智能体”解决什么问题，而不是只记名称
- 能独立完成：设计研究员、撰写员和审核员的输入输出契约
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 多智能体 | 多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。 |
| 角色 | “角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 消息传递 | 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 |
| 上下文隔离 | 上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：设计研究员、撰写员和审核员的输入输出契约

实现要求：先独立完成“设计研究员、撰写员和审核员的输入输出契约”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

运行命令：`python practice.py`

代码讲解：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每个角色只接收完成职责所需的最小上下文
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 20 · 自研最小 Agent 骨架

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

“Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Config”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Message”解决什么问题，而不是只记名称
- 能独立完成：参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Message | “Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Config | “Config”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Agent基类 | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| Tool | “Tool”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 错误契约 | “错误契约”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架

实现要求：先独立完成“参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Message、Config、Agent基类、Tool、错误契约')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 假模型、假工具和真实实现可通过相同契约替换
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 21 · 框架阶段综合验收

> 阶段二：经典范式、工具与框架｜第 3 周：框架选型、状态图与自研骨架｜建议 120 分钟

### 本日定位

“状态图”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“构建可暂停恢复的本地研究助理，生成带工具证据的短报告”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“状态图”解决什么问题，而不是只记名称
- 能独立完成：构建可暂停恢复的本地研究助理，生成带工具证据的短报告
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 状态图 | “状态图”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 工具 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 检查点 | “检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 人工审批 | 人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 |
| 轨迹 | “轨迹”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：构建可暂停恢复的本地研究助理，生成带工具证据的短报告

实现要求：先独立完成“构建可暂停恢复的本地研究助理，生成带工具证据的短报告”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 中断恢复、工具失败和人工拒绝三条路径均有测试
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Day 22 · 记忆类型与生命周期

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

“工作记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “情景记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为学习助理定义写入、读取、更新、过期和删除规则”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“工作记忆”解决什么问题，而不是只记名称
- 能独立完成：为学习助理定义写入、读取、更新、过期和删除规则
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 工作记忆 | “工作记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 情景记忆 | “情景记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 语义记忆 | “语义记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 遗忘 | “遗忘”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为学习助理定义写入、读取、更新、过期和删除规则

实现要求：先独立完成“为学习助理定义写入、读取、更新、过期和删除规则”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('工作记忆、情景记忆、语义记忆、遗忘')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 敏感数据、临时状态和长期事实有不同保存策略
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 23 · 短期记忆与摘要

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 “摘要”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“实现最近消息窗口并在超预算时生成可核对的确定性摘要”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“消息窗口”解决什么问题，而不是只记名称
- 能独立完成：实现最近消息窗口并在超预算时生成可核对的确定性摘要
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 消息窗口 | 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 |
| 摘要 | “摘要”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 事实保留 | “事实保留”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 上下文漂移 | 上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：实现最近消息窗口并在超预算时生成可核对的确定性摘要

实现要求：先独立完成“实现最近消息窗口并在超预算时生成可核对的确定性摘要”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

运行命令：`python practice.py`

代码讲解：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 关键约束在压缩前后保持一致且原始记录仍可追溯
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 24 · 长期记忆存储

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

“SQLite”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 今日通过“用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“SQLite”解决什么问题，而不是只记名称
- 能独立完成：用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| SQLite | “SQLite”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 记忆键 | 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 |
| 作用域 | “作用域”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 更新 | “更新”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 删除 | “删除”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询

实现要求：先独立完成“用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

运行命令：`python practice.py`

代码讲解：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 不同用户数据不串读且删除后无法再检索
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 25 · RAG 数据准备

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 “文档解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“将三份本地 Markdown 按标题分块并保存文件、章节和块编号”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“RAG”解决什么问题，而不是只记名称
- 能独立完成：将三份本地 Markdown 按标题分块并保存文件、章节和块编号
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| RAG | RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 |
| 文档解析 | “文档解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 分块 | “分块”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 元数据 | “元数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 来源 | “来源”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：将三份本地 Markdown 按标题分块并保存文件、章节和块编号

实现要求：先独立完成“将三份本地 Markdown 按标题分块并保存文件、章节和块编号”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

运行命令：`python practice.py`

代码讲解：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每个块可回到原文位置且空块、超长块被处理
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 26 · 检索、重排与拒答

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

“关键词检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “向量检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用固定问答集比较关键词基线和语义检索结果”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“关键词检索”解决什么问题，而不是只记名称
- 能独立完成：用固定问答集比较关键词基线和语义检索结果
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 关键词检索 | “关键词检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 向量检索 | “向量检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 混合检索 | “混合检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 重排 | “重排”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 阈值 | “阈值”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用固定问答集比较关键词基线和语义检索结果

实现要求：先独立完成“用固定问答集比较关键词基线和语义检索结果”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('关键词检索、向量检索、混合检索、重排、阈值')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 无相关证据时返回拒答而不是编造来源
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 27 · GSSC 上下文流水线

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。 “Gather”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为候选消息、记忆和检索块分配相关性与 token 预算”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“上下文工程”解决什么问题，而不是只记名称
- 能独立完成：为候选消息、记忆和检索块分配相关性与 token 预算
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 上下文工程 | 上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。 |
| Gather | “Gather”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Select | “Select”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Structure | “Structure”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Compress | “Compress”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为候选消息、记忆和检索块分配相关性与 token 预算

实现要求：先独立完成“为候选消息、记忆和检索块分配相关性与 token 预算”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

运行命令：`python practice.py`

代码讲解：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 系统规则始终保留且总上下文不超过预算
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 28 · 有依据的知识助手

> 阶段三：记忆、上下文与协作协议｜第 4 周：记忆、RAG 与上下文工程｜建议 120 分钟

### 本日定位

短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 今日通过“组合记忆和本地 RAG，回答五个问题并返回精确来源”把原理落实为可运行、可验证的能力。

前置要求：

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“记忆”解决什么问题，而不是只记名称
- 能独立完成：组合记忆和本地 RAG，回答五个问题并返回精确来源
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 记忆 | 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 |
| RAG | RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 |
| 上下文 | 上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。 |
| 引用 | “引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 事实核验 | “事实核验”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：组合记忆和本地 RAG，回答五个问题并返回精确来源

实现要求：先独立完成“组合记忆和本地 RAG，回答五个问题并返回精确来源”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

运行命令：`python practice.py`

代码讲解：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 答案中的关键事实均能定位到检索块，证据不足时拒答
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)

## Day 29 · MCP 架构与能力边界

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “Host”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“画出桌面 Host 调用本地资料 Server 的完整消息链”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“MCP”解决什么问题，而不是只记名称
- 能独立完成：画出桌面 Host 调用本地资料 Server 的完整消息链
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| MCP | MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 |
| Host | “Host”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Client | “Client”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Server | “Server”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Tools | “Tools”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Resources | “Resources”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Prompts | “Prompts”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：画出桌面 Host 调用本地资料 Server 的完整消息链

实现要求：先独立完成“画出桌面 Host 调用本地资料 Server 的完整消息链”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

运行命令：`python practice.py`

代码讲解：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 能区分工具副作用、只读资源和提示模板的职责
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 30 · 构建最小 MCP Server

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“实现只读笔记搜索工具和课程目录资源”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“MCP Server”解决什么问题，而不是只记名称
- 能独立完成：实现只读笔记搜索工具和课程目录资源
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| MCP Server | MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 |
| 工具发现 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 资源读取 | “资源读取”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 参数模式 | “参数模式”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：实现只读笔记搜索工具和课程目录资源

实现要求：先独立完成“实现只读笔记搜索工具和课程目录资源”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

运行命令：`python practice.py`

代码讲解：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 客户端能发现能力，非法路径和未知参数被拒绝
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 31 · MCP Client 与传输安全

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “stdio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“MCP Client”解决什么问题，而不是只记名称
- 能独立完成：比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| MCP Client | MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 |
| stdio | “stdio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Streamable HTTP | “Streamable HTTP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 认证 | “认证”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 超时 | “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略

实现要求：先独立完成“比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

运行命令：`python practice.py`

代码讲解：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 服务不可用、认证失败和响应超限都有确定错误
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 32 · A2A 核心对象

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 今日通过“定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“A2A”解决什么问题，而不是只记名称
- 能独立完成：定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| A2A | A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 |
| Agent Card | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| Task | “Task”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Message | “Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Artifact | “Artifact”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移

实现要求：先独立完成“定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

运行命令：`python practice.py`

代码讲解：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 非法状态跳转和能力不匹配都会失败
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 33 · 多智能体拓扑与路由

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

“顺序”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并行”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为资料研究任务比较顺序、并行和协调器三种拓扑”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“顺序”解决什么问题，而不是只记名称
- 能独立完成：为资料研究任务比较顺序、并行和协调器三种拓扑
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 顺序 | “顺序”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 并行 | “并行”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 路由 | “路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 协调器 | “协调器”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 点对点 | “点对点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为资料研究任务比较顺序、并行和协调器三种拓扑

实现要求：先独立完成“为资料研究任务比较顺序、并行和协调器三种拓扑”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('顺序、并行、路由、协调器、点对点')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 选择方案包含通信次数、故障点和终止条件
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 34 · 协作终止与故障处理

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

“任务生命周期”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“任务生命周期”解决什么问题，而不是只记名称
- 能独立完成：用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 任务生命周期 | “任务生命周期”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 超时 | “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 死锁 | “死锁”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 重复消息 | “重复消息”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 补偿 | “补偿”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级

实现要求：先独立完成“用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('任务生命周期、超时、死锁、重复消息、补偿')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 系统不会无限等待且重复工件不会进入最终结果
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 35 · 多智能体研究小队

> 阶段三：记忆、上下文与协作协议｜第 5 周：MCP、A2A 与多智能体协作｜建议 120 分钟

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 今日通过“实现研究员、事实核验员和编辑协作生成一页报告”把原理落实为可运行、可验证的能力。

前置要求：

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“MCP”解决什么问题，而不是只记名称
- 能独立完成：实现研究员、事实核验员和编辑协作生成一页报告
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| MCP | MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 |
| A2A | A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 |
| 多智能体 | 多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。 |
| Artifact | “Artifact”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 引用 | “引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：实现研究员、事实核验员和编辑协作生成一页报告

实现要求：先独立完成“实现研究员、事实核验员和编辑协作生成一页报告”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

运行命令：`python practice.py`

代码讲解：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 最终报告、来源清单和每个角色的工件均可追踪
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [MCP 官方架构规范](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [A2A 官方规范](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)

## Day 36 · Agent 威胁建模

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 “间接注入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“对 RAG 与 MCP 场景制作数据流图并标出信任边界”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“提示注入”解决什么问题，而不是只记名称
- 能独立完成：对 RAG 与 MCP 场景制作数据流图并标出信任边界
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 提示注入 | 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 |
| 间接注入 | “间接注入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 数据外泄 | “数据外泄”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 越权工具 | “越权工具”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：对 RAG 与 MCP 场景制作数据流图并标出信任边界

实现要求：先独立完成“对 RAG 与 MCP 场景制作数据流图并标出信任边界”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('提示注入、间接注入、数据外泄、越权工具')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 至少覆盖直接注入、工具结果注入和记忆污染
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 37 · 最小权限与人工控制

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“把文件工具拆成只读与写入能力，并为删除动作增加预览和审批”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“最小权限”解决什么问题，而不是只记名称
- 能独立完成：把文件工具拆成只读与写入能力，并为删除动作增加预览和审批
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 最小权限 | 每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。 |
| 工具白名单 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 沙箱 | “沙箱”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 人工审批 | 人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把文件工具拆成只读与写入能力，并为删除动作增加预览和审批

实现要求：先独立完成“把文件工具拆成只读与写入能力，并为删除动作增加预览和审批”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 模型无法通过参数逃逸目录或跳过审批
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 38 · 秘密、隐私与审计

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

“密钥管理”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “日志脱敏”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“设计不记录提示正文的审计事件并验证密钥不会进入日志”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“密钥管理”解决什么问题，而不是只记名称
- 能独立完成：设计不记录提示正文的审计事件并验证密钥不会进入日志
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 密钥管理 | “密钥管理”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 日志脱敏 | “日志脱敏”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 数据保留 | “数据保留”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 租户隔离 | “租户隔离”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：设计不记录提示正文的审计事件并验证密钥不会进入日志

实现要求：先独立完成“设计不记录提示正文的审计事件并验证密钥不会进入日志”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('密钥管理、日志脱敏、数据保留、租户隔离')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 审计仍能关联运行、工具和结果但不泄漏敏感数据
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 39 · 建立 Agent 评估集

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 “ground truth”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为本地 Agent 编写二十条正常、边界和对抗任务”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“评估集”解决什么问题，而不是只记名称
- 能独立完成：为本地 Agent 编写二十条正常、边界和对抗任务
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 评估集 | Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 |
| ground truth | “ground truth”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 确定性判定 | “确定性判定”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 版本 | “版本”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为本地 Agent 编写二十条正常、边界和对抗任务

实现要求：先独立完成“为本地 Agent 编写二十条正常、边界和对抗任务”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

运行命令：`python practice.py`

代码讲解：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每条样例都有可机器判定结果并固定版本
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 40 · 结果与轨迹指标

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

“任务成功率”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“实现评估脚本统计最终答案和工具轨迹的核心指标”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“任务成功率”解决什么问题，而不是只记名称
- 能独立完成：实现评估脚本统计最终答案和工具轨迹的核心指标
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 任务成功率 | “任务成功率”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 工具准确率 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 步骤数 | “步骤数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 延迟 | “延迟”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 成本 | “成本”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| BFCL | “BFCL”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| GAIA | “GAIA”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：实现评估脚本统计最终答案和工具轨迹的核心指标

实现要求：先独立完成“实现评估脚本统计最终答案和工具轨迹的核心指标”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 同一结果可按任务类别和失败类型切分
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 41 · 可观测性与回放

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

“Trace”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Span”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Trace”解决什么问题，而不是只记名称
- 能独立完成：为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Trace | “Trace”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| Span | “Span”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 模型调用 | “模型调用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 工具调用 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| token成本 | “token成本”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放

实现要求：先独立完成“为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

运行命令：`python practice.py`

代码讲解：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 错误能定位到具体步骤且日志中没有密钥和原文隐私
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 42 · 对抗回归门禁

> 阶段四：安全、评估与生产工程｜第 6 周：安全、评估与可观测性｜建议 120 分钟

### 本日定位

“红队”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 今日通过“把已知攻击和故障加入评估集并设置发布阈值”把原理落实为可运行、可验证的能力。

前置要求：

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“红队”解决什么问题，而不是只记名称
- 能独立完成：把已知攻击和故障加入评估集并设置发布阈值
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 红队 | “红队”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 提示注入 | 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 |
| 权限越界 | “权限越界”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 预算耗尽 | “预算耗尽”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 回归阈值 | “回归阈值”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把已知攻击和故障加入评估集并设置发布阈值

实现要求：先独立完成“把已知攻击和故障加入评估集并设置发布阈值”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('红队、提示注入、权限越界、预算耗尽、回归阈值')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 安全失败会阻止发布且报告保留最小复现
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)

## Day 43 · Agentic RL 的序贯视角

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。 “MDP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把工具问答 Agent 表示为状态、行动、观察和奖励序列”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Agentic RL”解决什么问题，而不是只记名称
- 能独立完成：把工具问答 Agent 表示为状态、行动、观察和奖励序列
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Agentic RL | Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。 |
| MDP | “MDP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 状态 | “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 行动 | “行动”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 轨迹 | “轨迹”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 累计奖励 | “累计奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把工具问答 Agent 表示为状态、行动、观察和奖励序列

实现要求：先独立完成“把工具问答 Agent 表示为状态、行动、观察和奖励序列”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

运行命令：`python practice.py`

代码讲解：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 正常与失败轨迹都能计算累计奖励并解释差异
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 44 · SFT 数据与行为示范

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。 “示范数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“SFT”解决什么问题，而不是只记名称
- 能独立完成：把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| SFT | 监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。 |
| 示范数据 | “示范数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 消息格式 | 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 |
| 工具轨迹 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| LoRA | “LoRA”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构

实现要求：先独立完成“把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

运行命令：`python practice.py`

代码讲解：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 缺消息、非法工具和泄漏秘密的样本在训练前被拒绝
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 45 · 奖励设计与奖励漏洞

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

“奖励函数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “稀疏奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为正确性、工具成本和安全约束设计组合奖励并运行反例”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“奖励函数”解决什么问题，而不是只记名称
- 能独立完成：为正确性、工具成本和安全约束设计组合奖励并运行反例
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 奖励函数 | “奖励函数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 稀疏奖励 | “稀疏奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 过程奖励 | “过程奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| reward hacking | “reward hacking”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为正确性、工具成本和安全约束设计组合奖励并运行反例

实现要求：先独立完成“为正确性、工具成本和安全约束设计组合奖励并运行反例”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

运行命令：`python practice.py`

代码讲解：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 投机缩短步骤或跳过验证不会获得更高奖励
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 46 · GRPO 小型模拟

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。 “组内相对奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“不用 GPU，用固定候选和分数计算组内相对优势”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“GRPO”解决什么问题，而不是只记名称
- 能独立完成：不用 GPU，用固定候选和分数计算组内相对优势
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| GRPO | GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。 |
| 组内相对奖励 | “组内相对奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 候选采样 | “候选采样”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 优势 | “优势”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：不用 GPU，用固定候选和分数计算组内相对优势

实现要求：先独立完成“不用 GPU，用固定候选和分数计算组内相对优势”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('GRPO、组内相对奖励、候选采样、优势')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 相同奖励、异常值和安全违规三类边界都有断言
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 47 · 可靠执行与恢复

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

“重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “退避”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为含两个副作用工具的流程设计故障矩阵并实现恢复”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“重试”解决什么问题，而不是只记名称
- 能独立完成：为含两个副作用工具的流程设计故障矩阵并实现恢复
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 重试 | “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 退避 | “退避”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 检查点 | “检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 幂等 | 幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 |
| 补偿 | “补偿”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 熔断 | “熔断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为含两个副作用工具的流程设计故障矩阵并实现恢复

实现要求：先独立完成“为含两个副作用工具的流程设计故障矩阵并实现恢复”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 暂时错误可恢复，永久错误快速失败且无重复副作用
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 48 · 并发、流式与取消

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

“asyncio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并发上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“并行执行三个只读工具并在用户取消时回收所有任务”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“asyncio”解决什么问题，而不是只记名称
- 能独立完成：并行执行三个只读工具并在用户取消时回收所有任务
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| asyncio | “asyncio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 并发上限 | “并发上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 流式输出 | “流式输出”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 取消 | “取消”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 速率限制 | “速率限制”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：并行执行三个只读工具并在用户取消时回收所有任务

实现要求：先独立完成“并行执行三个只读工具并在用户取消时回收所有任务”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('asyncio、并发上限、流式输出、取消、速率限制')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 并发峰值受限且取消后没有悬挂 Task
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 49 · 模型路由与成本控制

> 阶段四：安全、评估与生产工程｜第 7 周：Agentic RL、可靠性与成本｜建议 120 分钟

### 本日定位

“模型路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“按任务难度选择假模型层级并对重复只读请求缓存”把原理落实为可运行、可验证的能力。

前置要求：

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“模型路由”解决什么问题，而不是只记名称
- 能独立完成：按任务难度选择假模型层级并对重复只读请求缓存
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 模型路由 | “模型路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| token预算 | “token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 缓存 | “缓存”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 降级 | “降级”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 费用上限 | “费用上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：按任务难度选择假模型层级并对重复只读请求缓存

实现要求：先独立完成“按任务难度选择假模型层级并对重复只读请求缓存”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

运行命令：`python practice.py`

代码讲解：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每次运行可预测最大成本且降级不会绕过质量门禁
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)

## Day 50 · 旅行助手需求拆解

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

“旅行助手”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “约束收集”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“设计只查询不预订的旅行助理，输出带预算和偏好的行程草案”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“旅行助手”解决什么问题，而不是只记名称
- 能独立完成：设计只查询不预订的旅行助理，输出带预算和偏好的行程草案
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 旅行助手 | “旅行助手”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 约束收集 | “约束收集”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 工具边界 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 人工确认 | “人工确认”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：设计只查询不预订的旅行助理，输出带预算和偏好的行程草案

实现要求：先独立完成“设计只查询不预订的旅行助理，输出带预算和偏好的行程草案”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 缺日期或预算时先追问，任何预订动作都停在审批前
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 51 · Deep Research 查询规划

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

“Deep Research”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “问题分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把一个开放问题拆成相互独立的检索子问题和停止条件”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Deep Research”解决什么问题，而不是只记名称
- 能独立完成：把一个开放问题拆成相互独立的检索子问题和停止条件
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Deep Research | “Deep Research”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 问题分解 | “问题分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 搜索计划 | “搜索计划”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 并行研究 | “并行研究”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把一个开放问题拆成相互独立的检索子问题和停止条件

实现要求：先独立完成“把一个开放问题拆成相互独立的检索子问题和停止条件”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Deep Research、问题分解、搜索计划、并行研究')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 子问题覆盖目标且不会重复搜索同一证据
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 52 · 来源质量与证据去重

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

“来源可信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “时效性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为十条搜索结果评分并优先保留一手来源”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“来源可信度”解决什么问题，而不是只记名称
- 能独立完成：为十条搜索结果评分并优先保留一手来源
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 来源可信度 | “来源可信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 时效性 | “时效性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 原始资料 | “原始资料”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 去重 | “去重”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 引用 | “引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为十条搜索结果评分并优先保留一手来源

实现要求：先独立完成“为十条搜索结果评分并优先保留一手来源”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('来源可信度、时效性、原始资料、去重、引用')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 重复转载不会被当作多份独立证据
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 53 · 综合写作与矛盾处理

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

“证据综合”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “冲突”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“从含冲突的固定资料生成报告并明确分歧和不确定性”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“证据综合”解决什么问题，而不是只记名称
- 能独立完成：从含冲突的固定资料生成报告并明确分歧和不确定性
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 证据综合 | “证据综合”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 冲突 | “冲突”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 置信度 | “置信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 引用 | “引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 拒答 | “拒答”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：从含冲突的固定资料生成报告并明确分歧和不确定性

实现要求：先独立完成“从含冲突的固定资料生成报告并明确分歧和不确定性”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('证据综合、冲突、置信度、引用、拒答')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 每个结论带来源，无法消解的冲突不会被静默合并
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 54 · 编码 Agent 的安全闭环

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作区”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“让假 Agent 只生成补丁，在隔离目录应用并运行最小测试”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“编码Agent”解决什么问题，而不是只记名称
- 能独立完成：让假 Agent 只生成补丁，在隔离目录应用并运行最小测试
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 编码Agent | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| 工作区 | “工作区”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 补丁 | “补丁”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 测试 | “测试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 沙箱 | “沙箱”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 回滚 | “回滚”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：让假 Agent 只生成补丁，在隔离目录应用并运行最小测试

实现要求：先独立完成“让假 Agent 只生成补丁，在隔离目录应用并运行最小测试”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('编码Agent、工作区、补丁、测试、沙箱、回滚')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 测试失败不覆盖原文件且补丁不能越出目标目录
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 55 · GUI 与 Web Agent 状态

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 今日通过“在本地静态页面用有限状态机完成登录表单夹具”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“GUI Agent”解决什么问题，而不是只记名称
- 能独立完成：在本地静态页面用有限状态机完成登录表单夹具
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| GUI Agent | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| Web Agent | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| 观察 | “观察”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 动作 | “动作”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 页面状态 | “页面状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 等待 | “等待”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：在本地静态页面用有限状态机完成登录表单夹具

实现要求：先独立完成“在本地静态页面用有限状态机完成登录表单夹具”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):
    observations = []
    for _ in range(max_steps):
        action = decide(goal, observations)
        if action['name'] == 'finish': return action['answer'], observations
        if action['name'] not in tools: raise ValueError('unknown tool')
        observations.append(tools[action['name']](action['argument']))
    raise RuntimeError('step budget exhausted')

def fake_decide(goal, observations):
    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}

answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})
assert answer == 'AGENT' and trace == ['AGENT']
print(answer, trace)
```

运行命令：`python practice.py`

代码讲解：

- 假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。
- 步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 页面异常、元素缺失和超时都会停止并保存当前状态
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 56 · 用 Skill 封装可复用能力

> 阶段五：综合场景与毕业设计｜第 8 周：旅行、研究、编码与能力封装｜建议 120 分钟

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “指令”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界”把原理落实为可运行、可验证的能力。

前置要求：

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“Agent Skill”解决什么问题，而不是只记名称
- 能独立完成：把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| Agent Skill | Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 |
| 指令 | “指令”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 资源 | “资源”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 触发条件 | “触发条件”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 渐进披露 | “渐进披露”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界

实现要求：先独立完成“把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Agent Skill、指令、资源、触发条件、渐进披露')
assert result.status == 'completed'
print(result)
```

运行命令：`python practice.py`

代码讲解：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 适用任务能复用，不适用任务不会被强制套用
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)

## Day 57 · 毕业项目规格与评估设计

> 阶段五：综合场景与毕业设计｜第 9 周：毕业设计、红队与交付｜建议 150 分钟

### 本日定位

PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “用户故事”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务”把原理落实为可运行、可验证的能力。

前置要求：

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“PEAS”解决什么问题，而不是只记名称
- 能独立完成：为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| PEAS | PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 |
| 用户故事 | “用户故事”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 风险 | “风险”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 评估集 | Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 |
| 成本预算 | “成本预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务

实现要求：先独立完成“为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

运行命令：`python practice.py`

代码讲解：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 范围、非目标、权限、数据、预算和发布阈值齐全
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

## Day 58 · 完成端到端垂直切片

> 阶段五：综合场景与毕业设计｜第 9 周：毕业设计、红队与交付｜建议 150 分钟

### 本日定位

“模型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“只实现一条从输入到可验证结果的完整主路径”把原理落实为可运行、可验证的能力。

前置要求：

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“模型”解决什么问题，而不是只记名称
- 能独立完成：只实现一条从输入到可验证结果的完整主路径
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 模型 | “模型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 工具 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 状态 | “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 记忆 | 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 |
| 人工审批 | 人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 |
| 接口 | “接口”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：只实现一条从输入到可验证结果的完整主路径

实现要求：先独立完成“只实现一条从输入到可验证结果的完整主路径”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

运行命令：`python practice.py`

代码讲解：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 主路径可运行且每个外部边界都有超时和错误结果
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

## Day 59 · 红队、故障与容量验收

> 阶段五：综合场景与毕业设计｜第 9 周：毕业设计、红队与交付｜建议 150 分钟

### 本日定位

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“运行对抗集、故障注入和小规模并发测试，修复最高风险问题”把原理落实为可运行、可验证的能力。

前置要求：

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“提示注入”解决什么问题，而不是只记名称
- 能独立完成：运行对抗集、故障注入和小规模并发测试，修复最高风险问题
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 提示注入 | 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 |
| 工具故障 | 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 |
| 恢复 | “恢复”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 并发 | “并发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 成本上限 | “成本上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：运行对抗集、故障注入和小规模并发测试，修复最高风险问题

实现要求：先独立完成“运行对抗集、故障注入和小规模并发测试，修复最高风险问题”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

运行命令：`python practice.py`

代码讲解：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 安全门禁全部通过且失败运行不留下不可逆副作用
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

## Day 60 · 交付、复盘与后续路线

> 阶段五：综合场景与毕业设计｜第 9 周：毕业设计、红队与交付｜建议 150 分钟

### 本日定位

“演示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “运行手册”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“完成现场演示、部署或运行说明、指标报告和失败复盘”把原理落实为可运行、可验证的能力。

前置要求：

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

学习目标：

- 能用自己的话说明“演示”解决什么问题，而不是只记名称
- 能独立完成：完成现场演示、部署或运行说明、指标报告和失败复盘
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 核心知识

| 知识点 | 严谨解释 |
| --- | --- |
| 演示 | “演示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 运行手册 | “运行手册”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 评估报告 | Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 |
| 复盘 | “复盘”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |
| 迭代 | “迭代”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 |

运行机制：先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

易错边界：

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 跟做与独立实验

综合任务：完成现场演示、部署或运行说明、指标报告和失败复盘

实现要求：先独立完成“完成现场演示、部署或运行说明、指标报告和失败复盘”；至少保留一个正常输入、一个边界或失败输入、实际运行命令、环境版本和关键输出。参考代码只作为实验骨架，必须替换成当天真实实现。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

运行命令：`python practice.py`

代码讲解：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

练习步骤：

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 验收、证据与资料

验收条件：

- 陌生人能按文档运行，已知限制和下一步触发条件明确
- 失败样例可稳定触发并记录原因

应保留证据：

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

公开资料：

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP GenAI 安全项目](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

## Day 1：Agent 与工作流边界

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：Agent、工作流、自主性、反馈闭环

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作流”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础

### 学习目标

- 能用自己的话说明“Agent”解决什么问题，而不是只记名称
- 能独立完成：为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Agent

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### 工作流

“工作流”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 自主性

“自主性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 反馈闭环

“反馈闭环”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作流”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作流”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Agent、工作流、自主性、反馈闭环”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为学习资料整理场景画出普通工作流与 Agent 两套流程，并写出选择依据”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 能指出至少三处由模型动态决策和三处应保持确定性的步骤
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Agent、工作流、自主性、反馈闭环的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 2：用 PEAS 定义任务环境

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：PEAS、性能度量、环境、执行器、传感器

### 本日定位

PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “性能度量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为个人学习助理编写 PEAS 表和明确的不允许动作清单”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“PEAS”解决什么问题，而不是只记名称
- 能独立完成：为个人学习助理编写 PEAS 表和明确的不允许动作清单
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### PEAS

PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。

#### 性能度量

“性能度量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 环境

“环境”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 执行器

“执行器”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 传感器

“传感器”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “性能度量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为个人学习助理编写 PEAS 表和明确的不允许动作清单”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “性能度量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('PEAS、性能度量、环境、执行器、传感器')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为个人学习助理编写 PEAS 表和明确的不允许动作清单
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“PEAS、性能度量、环境、执行器、传感器”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为个人学习助理编写 PEAS 表和明确的不允许动作清单”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 性能指标、可观察输入、允许动作和禁止动作均可独立核对
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明PEAS、性能度量、环境、执行器、传感器的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 3：区分模型调用与会话状态

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：单次模型调用、消息历史、角色、token、采样

### 本日定位

“单次模型调用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 今日通过“用假模型记录 system、user、assistant 消息如何组成一次请求”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“单次模型调用”解决什么问题，而不是只记名称
- 能独立完成：用假模型记录 system、user、assistant 消息如何组成一次请求
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 单次模型调用

“单次模型调用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 消息历史

系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。

#### 角色

“角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### token

“token”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 采样

“采样”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “单次模型调用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 本日把这个原理用于“用假模型记录 system、user、assistant 消息如何组成一次请求”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “单次模型调用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

代码/命令说明：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用假模型记录 system、user、assistant 消息如何组成一次请求
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“单次模型调用、消息历史、角色、token、采样”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用假模型记录 system、user、assistant 消息如何组成一次请求”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 相同夹具可复现消息顺序并统计输入长度
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明单次模型调用、消息历史、角色、token、采样的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 4：提示层级与不可信数据

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：系统提示、用户输入、工具结果、提示注入

### 本日定位

“系统提示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “用户输入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“系统提示”解决什么问题，而不是只记名称
- 能独立完成：把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 系统提示

“系统提示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 用户输入

“用户输入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 工具结果

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 提示注入

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。

### 原理与边界

**基础说明：** “系统提示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “用户输入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “系统提示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “用户输入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“系统提示、用户输入、工具结果、提示注入”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把文档内容作为带来源的数据块放入提示，验证其中伪指令不会改变系统规则”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 可信指令与不可信资料在结构和日志中可区分
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明系统提示、用户输入、工具结果、提示注入的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 5：结构化输出契约

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：结构化输出、JSON Schema、解析、业务校验

### 本日定位

结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。 JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。 今日通过“定义任务分解 JSON 契约并校验缺字段、越界值和多余动作”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“结构化输出”解决什么问题，而不是只记名称
- 能独立完成：定义任务分解 JSON 契约并校验缺字段、越界值和多余动作
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 结构化输出

结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。

#### JSON Schema

JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。

#### 解析

“解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 业务校验

“业务校验”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。 JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。 本日把这个原理用于“定义任务分解 JSON 契约并校验缺字段、越界值和多余动作”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 结构化输出只约束模型返回形状，反序列化后仍要进行类型、范围、权限和业务校验。 JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：定义任务分解 JSON 契约并校验缺字段、越界值和多余动作
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“结构化输出、JSON Schema、解析、业务校验”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“定义任务分解 JSON 契约并校验缺字段、越界值和多余动作”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 合法输出可解析，三类非法输出在执行前被拒绝
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明结构化输出、JSON Schema、解析、业务校验的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 6：模型客户端的可靠边界

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：超时、重试、速率限制、token预算、错误分类

### 本日定位

“超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用假传输层模拟超时、429、永久错误和部分响应”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“超时”解决什么问题，而不是只记名称
- 能独立完成：用假传输层模拟超时、429、永久错误和部分响应
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 超时

“超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 重试

“重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 速率限制

“速率限制”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### token预算

“token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 错误分类

“错误分类”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“用假传输层模拟超时、429、永久错误和部分响应”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

代码/命令说明：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用假传输层模拟超时、429、永久错误和部分响应
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“超时、重试、速率限制、token预算、错误分类”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用假传输层模拟超时、429、永久错误和部分响应”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 重试仅覆盖暂时错误且总次数、等待和 token 预算可证明
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明超时、重试、速率限制、token预算、错误分类的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 7：第一个最小 Agent

- 阶段：阶段一：智能体与大语言模型基础
- 周次：第 1 周 · Agent、LLM 与最小执行闭环
- 建议时长：120 分钟
- 核心知识：Agent Loop、状态、行动、观察、停止条件

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“实现最多四步的本地问答 Agent，只允许查询固定字典工具”把原理落实为可运行、可验证的能力。

### 前置要求

- 具备 Python 函数、类、异常、JSON 和 HTTP API 基础
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Agent Loop”解决什么问题，而不是只记名称
- 能独立完成：实现最多四步的本地问答 Agent，只允许查询固定字典工具
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Agent Loop

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### 状态

“状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 行动

“行动”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 观察

“观察”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 停止条件

“停止条件”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“实现最多四步的本地问答 Agent，只允许查询固定字典工具”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):
    observations = []
    for _ in range(max_steps):
        action = decide(goal, observations)
        if action['name'] == 'finish': return action['answer'], observations
        if action['name'] not in tools: raise ValueError('unknown tool')
        observations.append(tools[action['name']](action['argument']))
    raise RuntimeError('step budget exhausted')

def fake_decide(goal, observations):
    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}

answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})
assert answer == 'AGENT' and trace == ['AGENT']
print(answer, trace)
```

代码/命令说明：

- 假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。
- 步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：实现最多四步的本地问答 Agent，只允许查询固定字典工具
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Agent Loop、状态、行动、观察、停止条件”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“实现最多四步的本地问答 Agent，只允许查询固定字典工具”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 正常任务在预算内结束，未知问题以明确状态终止
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Agent Loop、状态、行动、观察、停止条件的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents：内容导航与学习建议](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents 第一章：初识智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第三章：大语言模型基础](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80.md)


## Day 8：工具描述与参数模式

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：工具、Function Calling、JSON Schema、描述质量

### 本日定位

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “Function Calling”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为计算器和本地笔记查询设计互不重叠的工具描述与参数模式”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“工具”解决什么问题，而不是只记名称
- 能独立完成：为计算器和本地笔记查询设计互不重叠的工具描述与参数模式
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 工具

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### Function Calling

“Function Calling”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### JSON Schema

JSON Schema 描述工具参数的类型和必需字段，但授权、幂等、超时和副作用仍需业务代码控制。

#### 描述质量

“描述质量”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “Function Calling”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为计算器和本地笔记查询设计互不重叠的工具描述与参数模式”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “Function Calling”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为计算器和本地笔记查询设计互不重叠的工具描述与参数模式
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“工具、Function Calling、JSON Schema、描述质量”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为计算器和本地笔记查询设计互不重叠的工具描述与参数模式”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 固定问题能选中唯一工具且参数通过模式校验
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明工具、Function Calling、JSON Schema、描述质量的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 9：工具注册表与执行器

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：工具注册、分发、参数校验、返回协议

### 本日定位

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “分发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“实现白名单工具注册表，统一返回成功结果或结构化错误”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“工具注册”解决什么问题，而不是只记名称
- 能独立完成：实现白名单工具注册表，统一返回成功结果或结构化错误
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 工具注册

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 分发

“分发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 参数校验

“参数校验”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 返回协议

“返回协议”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “分发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“实现白名单工具注册表，统一返回成功结果或结构化错误”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 “分发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：实现白名单工具注册表，统一返回成功结果或结构化错误
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“工具注册、分发、参数校验、返回协议”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“实现白名单工具注册表，统一返回成功结果或结构化错误”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 未知工具和缺失参数都不会调用底层函数
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明工具注册、分发、参数校验、返回协议的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 10：副作用与工具安全

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：幂等、超时、重试、权限、副作用

### 本日定位

幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为“创建待办”工具加入幂等键、超时和只读预览模式”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“幂等”解决什么问题，而不是只记名称
- 能独立完成：为“创建待办”工具加入幂等键、超时和只读预览模式
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 幂等

幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。

#### 超时

“超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 重试

“重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 权限

“权限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 副作用

“副作用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为“创建待办”工具加入幂等键、超时和只读预览模式”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('幂等、超时、重试、权限、副作用')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为“创建待办”工具加入幂等键、超时和只读预览模式
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“幂等、超时、重试、权限、副作用”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为“创建待办”工具加入幂等键、超时和只读预览模式”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 重复请求只产生一条记录且超时不会留下半成品
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明幂等、超时、重试、权限、副作用的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 11：实现 ReAct 循环

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：ReAct、Thought-Action-Observation、动态纠错

### 本日定位

ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 “Thought-Action-Observation”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“ReAct”解决什么问题，而不是只记名称
- 能独立完成：用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### ReAct

ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。

#### Thought-Action-Observation

“Thought-Action-Observation”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 动态纠错

“动态纠错”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 “Thought-Action-Observation”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 “Thought-Action-Observation”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):
    observations = []
    for _ in range(max_steps):
        action = decide(goal, observations)
        if action['name'] == 'finish': return action['answer'], observations
        if action['name'] not in tools: raise ValueError('unknown tool')
        observations.append(tools[action['name']](action['argument']))
    raise RuntimeError('step budget exhausted')

def fake_decide(goal, observations):
    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}

answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})
assert answer == 'AGENT' and trace == ['AGENT']
print(answer, trace)
```

代码/命令说明：

- 假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。
- 步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“ReAct、Thought-Action-Observation、动态纠错”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用假模型和本地搜索工具完成两轮 ReAct，并保存完整轨迹”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 工具失败后能基于 Observation 修正一次且不会无限循环
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明ReAct、Thought-Action-Observation、动态纠错的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 12：实现 Plan-and-Solve

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：Plan-and-Solve、任务分解、依赖、重规划

### 本日定位

Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 “任务分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把资料整理任务拆成可验证步骤，逐步执行并记录中间产物”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Plan-and-Solve”解决什么问题，而不是只记名称
- 能独立完成：把资料整理任务拆成可验证步骤，逐步执行并记录中间产物
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Plan-and-Solve

Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。

#### 任务分解

“任务分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 依赖

“依赖”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 重规划

“重规划”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 “任务分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“把资料整理任务拆成可验证步骤，逐步执行并记录中间产物”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 “任务分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
def validate_plan(plan: list[str]) -> list[str]:
    cleaned = [step.strip() for step in plan if step.strip()]
    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')
    return cleaned

def reflect(result: str, checks: list[str]) -> list[str]:
    return [check for check in checks if check not in result]

plan = validate_plan(['收集输入', '执行任务', '验证结果'])
missing = reflect('执行任务完成', plan)
assert missing == ['收集输入', '验证结果']
print({'plan': plan, 'missing': missing})
```

代码/命令说明：

- 计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。
- 反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把资料整理任务拆成可验证步骤，逐步执行并记录中间产物
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Plan-and-Solve、任务分解、依赖、重规划”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把资料整理任务拆成可验证步骤，逐步执行并记录中间产物”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 计划无循环依赖且任一步失败会停止或产生显式重规划
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Plan-and-Solve、任务分解、依赖、重规划的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 13：实现 Reflection

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：Reflection、Evaluator、反馈、修订上限

### 本日定位

Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。 “Evaluator”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用固定检查表评审一段初稿并最多修订两轮”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Reflection”解决什么问题，而不是只记名称
- 能独立完成：用固定检查表评审一段初稿并最多修订两轮
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Reflection

Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。

#### Evaluator

“Evaluator”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 反馈

“反馈”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 修订上限

“修订上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。 “Evaluator”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“用固定检查表评审一段初稿并最多修订两轮”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。 “Evaluator”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
def validate_plan(plan: list[str]) -> list[str]:
    cleaned = [step.strip() for step in plan if step.strip()]
    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')
    return cleaned

def reflect(result: str, checks: list[str]) -> list[str]:
    return [check for check in checks if check not in result]

plan = validate_plan(['收集输入', '执行任务', '验证结果'])
missing = reflect('执行任务完成', plan)
assert missing == ['收集输入', '验证结果']
print({'plan': plan, 'missing': missing})
```

代码/命令说明：

- 计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。
- 反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用固定检查表评审一段初稿并最多修订两轮
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Reflection、Evaluator、反馈、修订上限”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用固定检查表评审一段初稿并最多修订两轮”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每条修订可追溯到检查项且达到轮数上限后停止
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Reflection、Evaluator、反馈、修订上限的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 14：经典范式选型实验

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 2 周 · 工具调用与经典智能体范式
- 建议时长：120 分钟
- 核心知识：ReAct、Plan-and-Solve、Reflection、混合范式

### 本日定位

ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 今日通过“让三种范式运行同一组本地任务，对比成功率、步骤数和成本”把原理落实为可运行、可验证的能力。

### 前置要求

- 能用假模型完成一次有边界的消息调用
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“ReAct”解决什么问题，而不是只记名称
- 能独立完成：让三种范式运行同一组本地任务，对比成功率、步骤数和成本
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### ReAct

ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。

#### Plan-and-Solve

Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。

#### Reflection

Reflection 用执行、评审、修订循环改进结果，应设置轮数上限并用外部验收防止自我确认。

#### 混合范式

“混合范式”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。 本日把这个原理用于“让三种范式运行同一组本地任务，对比成功率、步骤数和成本”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** ReAct 交替进行推理、行动和观察，使计划能依据真实工具结果动态修正。 Plan-and-Solve 先产生可检查的计划再逐步执行，适合结构清晰的多步骤任务。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
def validate_plan(plan: list[str]) -> list[str]:
    cleaned = [step.strip() for step in plan if step.strip()]
    if not cleaned or len(cleaned) > 5: raise ValueError('invalid plan')
    return cleaned

def reflect(result: str, checks: list[str]) -> list[str]:
    return [check for check in checks if check not in result]

plan = validate_plan(['收集输入', '执行任务', '验证结果'])
missing = reflect('执行任务完成', plan)
assert missing == ['收集输入', '验证结果']
print({'plan': plan, 'missing': missing})
```

代码/命令说明：

- 计划先验证步数和空步骤，避免模型一次生成无限或不可执行的任务。
- 反思以外部检查项为依据；若没有验收标准，自我评价只会制造新的文本。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：让三种范式运行同一组本地任务，对比成功率、步骤数和成本
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“ReAct、Plan-and-Solve、Reflection、混合范式”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“让三种范式运行同一组本地任务，对比成功率、步骤数和成本”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 形成基于证据的选型表而不是只按框架名称判断
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明ReAct、Plan-and-Solve、Reflection、混合范式的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)


## Day 15：低代码、框架还是原生代码

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：Dify、n8n、Agent框架、原生API、选型

### 本日定位

“Dify”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “n8n”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为三个业务场景分别选择固定流程、框架或自研循环并记录理由”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Dify”解决什么问题，而不是只记名称
- 能独立完成：为三个业务场景分别选择固定流程、框架或自研循环并记录理由
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Dify

“Dify”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### n8n

“n8n”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Agent框架

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### 原生API

“原生API”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 选型

“选型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “Dify”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “n8n”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为三个业务场景分别选择固定流程、框架或自研循环并记录理由”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “Dify”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “n8n”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Dify、n8n、Agent框架、原生API、选型')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为三个业务场景分别选择固定流程、框架或自研循环并记录理由
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Dify、n8n、Agent框架、原生API、选型”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为三个业务场景分别选择固定流程、框架或自研循环并记录理由”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每个选择都包含复杂度、可控性和退出成本
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Dify、n8n、Agent框架、原生API、选型的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 16：用状态图表达执行

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：LangGraph、节点、边、状态、条件路由

### 本日定位

LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。 “节点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“LangGraph”解决什么问题，而不是只记名称
- 能独立完成：将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### LangGraph

LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。

#### 节点

“节点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 边

“边”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 状态

“状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 条件路由

“条件路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。 “节点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** LangGraph 用显式状态和图节点描述长时程执行，检查点与中断让流程可以恢复和人工审批。 “节点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“LangGraph、节点、边、状态、条件路由”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“将审核式写作 Agent 建模为草稿、检查、人工确认和完成节点”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 所有状态都有进入与退出条件且不存在无界环
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明LangGraph、节点、边、状态、条件路由的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 17：检查点与恢复

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：检查点、持久化、恢复、幂等重放

### 本日定位

“检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “持久化”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“在每个节点后保存 JSON 检查点，模拟进程中断后继续执行”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“检查点”解决什么问题，而不是只记名称
- 能独立完成：在每个节点后保存 JSON 检查点，模拟进程中断后继续执行
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 检查点

“检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 持久化

“持久化”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 恢复

“恢复”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 幂等重放

幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。

### 原理与边界

**基础说明：** “检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “持久化”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“在每个节点后保存 JSON 检查点，模拟进程中断后继续执行”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “持久化”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：在每个节点后保存 JSON 检查点，模拟进程中断后继续执行
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“检查点、持久化、恢复、幂等重放”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“在每个节点后保存 JSON 检查点，模拟进程中断后继续执行”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 恢复不会重复已经完成的副作用节点
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明检查点、持久化、恢复、幂等重放的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 18：人工审批是一等状态

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：人工审批、中断、恢复、高风险动作

### 本日定位

人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 “中断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“在发送消息前暂停并展示动作、参数、依据和影响”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“人工审批”解决什么问题，而不是只记名称
- 能独立完成：在发送消息前暂停并展示动作、参数、依据和影响
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 人工审批

人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。

#### 中断

“中断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 恢复

“恢复”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 高风险动作

“高风险动作”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 “中断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“在发送消息前暂停并展示动作、参数、依据和影响”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。 “中断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：在发送消息前暂停并展示动作、参数、依据和影响
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“人工审批、中断、恢复、高风险动作”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“在发送消息前暂停并展示动作、参数、依据和影响”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 拒绝审批后不执行动作，修改参数后从检查点恢复
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明人工审批、中断、恢复、高风险动作的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 19：多智能体角色与消息

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：多智能体、角色、消息传递、上下文隔离

### 本日定位

多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。 “角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“设计研究员、撰写员和审核员的输入输出契约”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“多智能体”解决什么问题，而不是只记名称
- 能独立完成：设计研究员、撰写员和审核员的输入输出契约
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 多智能体

多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。

#### 角色

“角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 消息传递

系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。

#### 上下文隔离

上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。

### 原理与边界

**基础说明：** 多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。 “角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“设计研究员、撰写员和审核员的输入输出契约”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。 “角色”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

代码/命令说明：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：设计研究员、撰写员和审核员的输入输出契约
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“多智能体、角色、消息传递、上下文隔离”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“设计研究员、撰写员和审核员的输入输出契约”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每个角色只接收完成职责所需的最小上下文
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明多智能体、角色、消息传递、上下文隔离的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 20：自研最小 Agent 骨架

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：Message、Config、Agent基类、Tool、错误契约

### 本日定位

“Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Config”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Message”解决什么问题，而不是只记名称
- 能独立完成：参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Message

“Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Config

“Config”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Agent基类

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### Tool

“Tool”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 错误契约

“错误契约”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Config”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Config”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Message、Config、Agent基类、Tool、错误契约')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Message、Config、Agent基类、Tool、错误契约”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“参考 HelloAgents 实现消息对象、配置读取、工具接口和循环骨架”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 假模型、假工具和真实实现可通过相同契约替换
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Message、Config、Agent基类、Tool、错误契约的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 21：框架阶段综合验收

- 阶段：阶段二：经典范式、工具与框架
- 周次：第 3 周 · 框架选型、状态图与自研骨架
- 建议时长：120 分钟
- 核心知识：状态图、工具、检查点、人工审批、轨迹

### 本日定位

“状态图”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“构建可暂停恢复的本地研究助理，生成带工具证据的短报告”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现带参数校验和停止条件的工具循环
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“状态图”解决什么问题，而不是只记名称
- 能独立完成：构建可暂停恢复的本地研究助理，生成带工具证据的短报告
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 状态图

“状态图”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 工具

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 检查点

“检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 人工审批

人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。

#### 轨迹

“轨迹”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “状态图”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 本日把这个原理用于“构建可暂停恢复的本地研究助理，生成带工具证据的短报告”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “状态图”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：构建可暂停恢复的本地研究助理，生成带工具证据的短报告
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“状态图、工具、检查点、人工审批、轨迹”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“构建可暂停恢复的本地研究助理，生成带工具证据的短报告”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 中断恢复、工具失败和人工拒绝三条路径均有测试
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明状态图、工具、检查点、人工审批、轨迹的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第七章：构建你的 Agent 框架](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)


## Day 22：记忆类型与生命周期

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：工作记忆、情景记忆、语义记忆、遗忘

### 本日定位

“工作记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “情景记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为学习助理定义写入、读取、更新、过期和删除规则”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“工作记忆”解决什么问题，而不是只记名称
- 能独立完成：为学习助理定义写入、读取、更新、过期和删除规则
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 工作记忆

“工作记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 情景记忆

“情景记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 语义记忆

“语义记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 遗忘

“遗忘”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “工作记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “情景记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为学习助理定义写入、读取、更新、过期和删除规则”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “工作记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “情景记忆”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('工作记忆、情景记忆、语义记忆、遗忘')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为学习助理定义写入、读取、更新、过期和删除规则
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“工作记忆、情景记忆、语义记忆、遗忘”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为学习助理定义写入、读取、更新、过期和删除规则”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 敏感数据、临时状态和长期事实有不同保存策略
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明工作记忆、情景记忆、语义记忆、遗忘的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 23：短期记忆与摘要

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：消息窗口、摘要、事实保留、上下文漂移

### 本日定位

系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 “摘要”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“实现最近消息窗口并在超预算时生成可核对的确定性摘要”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“消息窗口”解决什么问题，而不是只记名称
- 能独立完成：实现最近消息窗口并在超预算时生成可核对的确定性摘要
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 消息窗口

系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。

#### 摘要

“摘要”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 事实保留

“事实保留”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 上下文漂移

上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。

### 原理与边界

**基础说明：** 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 “摘要”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“实现最近消息窗口并在超预算时生成可核对的确定性摘要”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。 “摘要”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

代码/命令说明：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：实现最近消息窗口并在超预算时生成可核对的确定性摘要
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“消息窗口、摘要、事实保留、上下文漂移”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“实现最近消息窗口并在超预算时生成可核对的确定性摘要”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 关键约束在压缩前后保持一致且原始记录仍可追溯
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明消息窗口、摘要、事实保留、上下文漂移的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 24：长期记忆存储

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：SQLite、记忆键、作用域、更新、删除

### 本日定位

“SQLite”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 今日通过“用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“SQLite”解决什么问题，而不是只记名称
- 能独立完成：用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### SQLite

“SQLite”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 记忆键

短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。

#### 作用域

“作用域”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 更新

“更新”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 删除

“删除”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “SQLite”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 本日把这个原理用于“用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “SQLite”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

代码/命令说明：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“SQLite、记忆键、作用域、更新、删除”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用 SQLite 保存用户明确确认的偏好并支持按用户隔离查询”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 不同用户数据不串读且删除后无法再检索
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明SQLite、记忆键、作用域、更新、删除的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 25：RAG 数据准备

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：RAG、文档解析、分块、元数据、来源

### 本日定位

RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 “文档解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“将三份本地 Markdown 按标题分块并保存文件、章节和块编号”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“RAG”解决什么问题，而不是只记名称
- 能独立完成：将三份本地 Markdown 按标题分块并保存文件、章节和块编号
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### RAG

RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。

#### 文档解析

“文档解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 分块

“分块”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 元数据

“元数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 来源

“来源”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 “文档解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“将三份本地 Markdown 按标题分块并保存文件、章节和块编号”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 “文档解析”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

代码/命令说明：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：将三份本地 Markdown 按标题分块并保存文件、章节和块编号
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“RAG、文档解析、分块、元数据、来源”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“将三份本地 Markdown 按标题分块并保存文件、章节和块编号”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每个块可回到原文位置且空块、超长块被处理
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明RAG、文档解析、分块、元数据、来源的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 26：检索、重排与拒答

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：关键词检索、向量检索、混合检索、重排、阈值

### 本日定位

“关键词检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “向量检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用固定问答集比较关键词基线和语义检索结果”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“关键词检索”解决什么问题，而不是只记名称
- 能独立完成：用固定问答集比较关键词基线和语义检索结果
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 关键词检索

“关键词检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 向量检索

“向量检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 混合检索

“混合检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 重排

“重排”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 阈值

“阈值”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “关键词检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “向量检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“用固定问答集比较关键词基线和语义检索结果”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “关键词检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “向量检索”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('关键词检索、向量检索、混合检索、重排、阈值')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用固定问答集比较关键词基线和语义检索结果
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“关键词检索、向量检索、混合检索、重排、阈值”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用固定问答集比较关键词基线和语义检索结果”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 无相关证据时返回拒答而不是编造来源
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明关键词检索、向量检索、混合检索、重排、阈值的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 27：实践 Hello-Agents GSSC 上下文流水线

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：Hello-Agents GSSC、Gather、Select、Structure、Compress

### 本日定位

“Hello-Agents GSSC”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Gather”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为候选消息、记忆和检索块分配相关性与 token 预算”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Hello-Agents GSSC”解决什么问题，而不是只记名称
- 能独立完成：为候选消息、记忆和检索块分配相关性与 token 预算
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Hello-Agents GSSC

“Hello-Agents GSSC”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Gather

“Gather”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Select

“Select”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Structure

“Structure”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Compress

“Compress”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “Hello-Agents GSSC”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Gather”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为候选消息、记忆和检索块分配相关性与 token 预算”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “Hello-Agents GSSC”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Gather”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

代码/命令说明：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为候选消息、记忆和检索块分配相关性与 token 预算
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Hello-Agents GSSC、Gather、Select、Structure、Compress”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为候选消息、记忆和检索块分配相关性与 token 预算”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 系统规则始终保留且总上下文不超过预算
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Hello-Agents GSSC、Gather、Select、Structure、Compress的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 28：有依据的知识助手

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 4 周 · 记忆、RAG 与上下文工程
- 建议时长：120 分钟
- 核心知识：记忆、RAG、上下文、引用、事实核验

### 本日定位

短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 今日通过“组合记忆和本地 RAG，回答五个问题并返回精确来源”把原理落实为可运行、可验证的能力。

### 前置要求

- 理解状态图、检查点与人工审批
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“记忆”解决什么问题，而不是只记名称
- 能独立完成：组合记忆和本地 RAG，回答五个问题并返回精确来源
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 记忆

短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。

#### RAG

RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。

#### 上下文

上下文工程在每次调用前汇集、筛选、组织和压缩最相关信息，把 token 窗口视为有限预算。

#### 引用

“引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 事实核验

“事实核验”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。 本日把这个原理用于“组合记忆和本地 RAG，回答五个问题并返回精确来源”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。 RAG 在生成前检索外部知识并保留来源，质量取决于分块、召回、排序和引用验证的完整链路。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    text: str
    score: float
    tokens: int

def select(packets, budget):
    chosen, used = [], 0
    for packet in sorted(packets, key=lambda item: item.score, reverse=True):
        if used + packet.tokens <= budget:
            chosen.append(packet); used += packet.tokens
    return chosen

packets = [Packet('无关历史', .1, 4), Packet('有来源的答案', .9, 6)]
result = select(packets, 6)
assert [item.text for item in result] == ['有来源的答案']
print(result)
```

代码/命令说明：

- 候选信息先带来源、相关性和 token 成本，再按预算选择。
- 仅扩大上下文不会提高质量；低相关历史会挤占真正证据。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：组合记忆和本地 RAG，回答五个问题并返回精确来源
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“记忆、RAG、上下文、引用、事实核验”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“组合记忆和本地 RAG，回答五个问题并返回精确来源”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 答案中的关键事实均能定位到检索块，证据不足时拒答
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明记忆、RAG、上下文、引用、事实核验的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第八章：记忆与检索](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/%E7%AC%AC%E5%85%AB%E7%AB%A0%20%E8%AE%B0%E5%BF%86%E4%B8%8E%E6%A3%80%E7%B4%A2.md)
- [Hello-Agents 第九章：上下文工程](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/%E7%AC%AC%E4%B9%9D%E7%AB%A0%20%E4%B8%8A%E4%B8%8B%E6%96%87%E5%B7%A5%E7%A8%8B.md)
- [RAG 原始论文](https://arxiv.org/abs/2005.11401)


## Day 29：MCP 架构与能力边界

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：MCP、Host、Client、Server、Tools、Resources、Prompts

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “Host”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“画出桌面 Host 调用本地资料 Server 的完整消息链”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“MCP”解决什么问题，而不是只记名称
- 能独立完成：画出桌面 Host 调用本地资料 Server 的完整消息链
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### MCP

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。

#### Host

“Host”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Client

“Client”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Server

“Server”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Tools

“Tools”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Resources

“Resources”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Prompts

“Prompts”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “Host”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“画出桌面 Host 调用本地资料 Server 的完整消息链”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “Host”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

代码/命令说明：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：画出桌面 Host 调用本地资料 Server 的完整消息链
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“MCP、Host、Client、Server、Tools、Resources、Prompts”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“画出桌面 Host 调用本地资料 Server 的完整消息链”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 能区分工具副作用、只读资源和提示模板的职责
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明MCP、Host、Client、Server、Tools、Resources、Prompts的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 30：构建最小 MCP Server

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：MCP Server、工具发现、资源读取、参数模式

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“实现只读笔记搜索工具和课程目录资源”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“MCP Server”解决什么问题，而不是只记名称
- 能独立完成：实现只读笔记搜索工具和课程目录资源
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### MCP Server

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。

#### 工具发现

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 资源读取

“资源读取”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 参数模式

“参数模式”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 本日把这个原理用于“实现只读笔记搜索工具和课程目录资源”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

代码/命令说明：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：实现只读笔记搜索工具和课程目录资源
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“MCP Server、工具发现、资源读取、参数模式”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“实现只读笔记搜索工具和课程目录资源”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 客户端能发现能力，非法路径和未知参数被拒绝
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明MCP Server、工具发现、资源读取、参数模式的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 31：MCP Client 与传输安全

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：MCP Client、stdio、Streamable HTTP、认证、超时

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “stdio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“MCP Client”解决什么问题，而不是只记名称
- 能独立完成：比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### MCP Client

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。

#### stdio

“stdio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Streamable HTTP

“Streamable HTTP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 认证

“认证”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 超时

“超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “stdio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 “stdio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

代码/命令说明：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“MCP Client、stdio、Streamable HTTP、认证、超时”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“比较 stdio 与 HTTP 传输并为远程调用加入认证和超时策略”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 服务不可用、认证失败和响应超限都有确定错误
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明MCP Client、stdio、Streamable HTTP、认证、超时的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 32：A2A 核心对象

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：A2A、Agent Card、Task、Message、Artifact

### 本日定位

A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 今日通过“定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“A2A”解决什么问题，而不是只记名称
- 能独立完成：定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### A2A

A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。

#### Agent Card

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### Task

“Task”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Message

“Message”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Artifact

“Artifact”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 本日把这个原理用于“定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

代码/命令说明：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“A2A、Agent Card、Task、Message、Artifact”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“定义研究 Agent 的能力卡并完成任务提交、执行、完成状态迁移”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 非法状态跳转和能力不匹配都会失败
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明A2A、Agent Card、Task、Message、Artifact的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 33：多智能体拓扑与路由

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：顺序、并行、路由、协调器、点对点

### 本日定位

“顺序”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并行”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为资料研究任务比较顺序、并行和协调器三种拓扑”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“顺序”解决什么问题，而不是只记名称
- 能独立完成：为资料研究任务比较顺序、并行和协调器三种拓扑
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 顺序

“顺序”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 并行

“并行”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 路由

“路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 协调器

“协调器”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 点对点

“点对点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “顺序”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并行”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为资料研究任务比较顺序、并行和协调器三种拓扑”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “顺序”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并行”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('顺序、并行、路由、协调器、点对点')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为资料研究任务比较顺序、并行和协调器三种拓扑
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“顺序、并行、路由、协调器、点对点”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为资料研究任务比较顺序、并行和协调器三种拓扑”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 选择方案包含通信次数、故障点和终止条件
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明顺序、并行、路由、协调器、点对点的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 34：协作终止与故障处理

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：任务生命周期、超时、死锁、重复消息、补偿

### 本日定位

“任务生命周期”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“任务生命周期”解决什么问题，而不是只记名称
- 能独立完成：用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 任务生命周期

“任务生命周期”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 超时

“超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 死锁

“死锁”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 重复消息

“重复消息”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 补偿

“补偿”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “任务生命周期”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “任务生命周期”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “超时”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('任务生命周期、超时、死锁、重复消息、补偿')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“任务生命周期、超时、死锁、重复消息、补偿”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“用夹具模拟一个 Agent 超时和重复提交，完成恢复或降级”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 系统不会无限等待且重复工件不会进入最终结果
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明任务生命周期、超时、死锁、重复消息、补偿的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 35：多智能体研究小队

- 阶段：阶段三：记忆、上下文与协作协议
- 周次：第 5 周 · MCP、A2A 与多智能体协作
- 建议时长：120 分钟
- 核心知识：MCP、A2A、多智能体、Artifact、引用

### 本日定位

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 今日通过“实现研究员、事实核验员和编辑协作生成一页报告”把原理落实为可运行、可验证的能力。

### 前置要求

- 能区分短期记忆、长期记忆、RAG 与上下文
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“MCP”解决什么问题，而不是只记名称
- 能独立完成：实现研究员、事实核验员和编辑协作生成一页报告
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### MCP

MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。

#### A2A

A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。

#### 多智能体

多智能体只有在角色能力或上下文可以真正分离时才值得使用；协调成本和错误传播必须计入预算。

#### Artifact

“Artifact”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 引用

“引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。 本日把这个原理用于“实现研究员、事实核验员和编辑协作生成一页报告”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** MCP 采用 Host、Client、Server 架构，以 Tools、Resources 和 Prompts 标准化智能体与外部能力的连接。 A2A 以 Agent Card、Task、Message 和 Artifact 描述独立智能体之间的发现、委托和协作状态。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    status: str = 'submitted'

def delegate(task, cards):
    matches = [card for card in cards if task.capability in card['skills']]
    if len(matches) != 1:
        raise ValueError('capability must resolve to one agent')
    return matches[0]['name']

cards = [{'name':'researcher','skills':['search']}, {'name':'writer','skills':['write']}]
assert delegate(Task('t-1','search'), cards) == 'researcher'
print('task routed')
```

代码/命令说明：

- 能力卡用于发现候选智能体，任务状态和最终工件应独立于聊天文本。
- 零个或多个匹配都显式失败，避免把模糊路由交给随机对话轮次。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：实现研究员、事实核验员和编辑协作生成一页报告
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“MCP、A2A、多智能体、Artifact、引用”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“实现研究员、事实核验员和编辑协作生成一页报告”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 最终报告、来源清单和每个角色的工件均可追踪
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明MCP、A2A、多智能体、Artifact、引用的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十章：智能体通信协议](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/%E7%AC%AC%E5%8D%81%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E9%80%9A%E4%BF%A1%E5%8D%8F%E8%AE%AE.md)
- [Model Context Protocol 最新规范](https://modelcontextprotocol.io/specification/latest/architecture)
- [A2A Protocol 最新规范](https://a2a-protocol.org/latest/specification/)


## Day 36：Agent 威胁建模

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：提示注入、间接注入、数据外泄、越权工具

### 本日定位

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 “间接注入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“对 RAG 与 MCP 场景制作数据流图并标出信任边界”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“提示注入”解决什么问题，而不是只记名称
- 能独立完成：对 RAG 与 MCP 场景制作数据流图并标出信任边界
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 提示注入

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。

#### 间接注入

“间接注入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 数据外泄

“数据外泄”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 越权工具

“越权工具”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 “间接注入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“对 RAG 与 MCP 场景制作数据流图并标出信任边界”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 “间接注入”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('提示注入、间接注入、数据外泄、越权工具')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：对 RAG 与 MCP 场景制作数据流图并标出信任边界
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“提示注入、间接注入、数据外泄、越权工具”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“对 RAG 与 MCP 场景制作数据流图并标出信任边界”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 至少覆盖直接注入、工具结果注入和记忆污染
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明提示注入、间接注入、数据外泄、越权工具的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 37：最小权限与人工控制

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：最小权限、工具白名单、沙箱、人工审批

### 本日定位

每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“把文件工具拆成只读与写入能力，并为删除动作增加预览和审批”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“最小权限”解决什么问题，而不是只记名称
- 能独立完成：把文件工具拆成只读与写入能力，并为删除动作增加预览和审批
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 最小权限

每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。

#### 工具白名单

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 沙箱

“沙箱”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 人工审批

人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。

### 原理与边界

**基础说明：** 每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 本日把这个原理用于“把文件工具拆成只读与写入能力，并为删除动作增加预览和审批”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 每个工具只获得完成当前动作所需的资源、参数范围和凭据，读取与写入能力应分开授权。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把文件工具拆成只读与写入能力，并为删除动作增加预览和审批
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“最小权限、工具白名单、沙箱、人工审批”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把文件工具拆成只读与写入能力，并为删除动作增加预览和审批”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 模型无法通过参数逃逸目录或跳过审批
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明最小权限、工具白名单、沙箱、人工审批的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 38：秘密、隐私与审计

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：密钥管理、日志脱敏、数据保留、租户隔离

### 本日定位

“密钥管理”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “日志脱敏”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“设计不记录提示正文的审计事件并验证密钥不会进入日志”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“密钥管理”解决什么问题，而不是只记名称
- 能独立完成：设计不记录提示正文的审计事件并验证密钥不会进入日志
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 密钥管理

“密钥管理”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 日志脱敏

“日志脱敏”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 数据保留

“数据保留”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 租户隔离

“租户隔离”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “密钥管理”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “日志脱敏”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“设计不记录提示正文的审计事件并验证密钥不会进入日志”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “密钥管理”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “日志脱敏”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('密钥管理、日志脱敏、数据保留、租户隔离')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：设计不记录提示正文的审计事件并验证密钥不会进入日志
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“密钥管理、日志脱敏、数据保留、租户隔离”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“设计不记录提示正文的审计事件并验证密钥不会进入日志”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 审计仍能关联运行、工具和结果但不泄漏敏感数据
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明密钥管理、日志脱敏、数据保留、租户隔离的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 39：建立 Agent 评估集

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：评估集、ground truth、确定性判定、版本

### 本日定位

Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 “ground truth”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为本地 Agent 编写二十条正常、边界和对抗任务”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“评估集”解决什么问题，而不是只记名称
- 能独立完成：为本地 Agent 编写二十条正常、边界和对抗任务
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 评估集

Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。

#### ground truth

“ground truth”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 确定性判定

“确定性判定”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 版本

“版本”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 “ground truth”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为本地 Agent 编写二十条正常、边界和对抗任务”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。 “ground truth”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

代码/命令说明：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为本地 Agent 编写二十条正常、边界和对抗任务
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“评估集、ground truth、确定性判定、版本”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为本地 Agent 编写二十条正常、边界和对抗任务”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每条样例都有可机器判定结果并固定版本
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明评估集、ground truth、确定性判定、版本的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 40：结果与轨迹指标

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：任务成功率、工具准确率、步骤数、延迟、成本、BFCL、GAIA

### 本日定位

“任务成功率”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“实现评估脚本统计最终答案和工具轨迹的核心指标”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“任务成功率”解决什么问题，而不是只记名称
- 能独立完成：实现评估脚本统计最终答案和工具轨迹的核心指标
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 任务成功率

“任务成功率”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 工具准确率

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 步骤数

“步骤数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 延迟

“延迟”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 成本

“成本”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### BFCL

“BFCL”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### GAIA

“GAIA”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “任务成功率”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 本日把这个原理用于“实现评估脚本统计最终答案和工具轨迹的核心指标”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “任务成功率”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：实现评估脚本统计最终答案和工具轨迹的核心指标
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“任务成功率、工具准确率、步骤数、延迟、成本、BFCL、GAIA”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“实现评估脚本统计最终答案和工具轨迹的核心指标”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 同一结果可按任务类别和失败类型切分
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明任务成功率、工具准确率、步骤数、延迟、成本、BFCL、GAIA的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 41：可观测性与回放

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：Trace、Span、模型调用、工具调用、token成本

### 本日定位

“Trace”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Span”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Trace”解决什么问题，而不是只记名称
- 能独立完成：为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Trace

“Trace”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### Span

“Span”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 模型调用

“模型调用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 工具调用

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### token成本

“token成本”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “Trace”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Span”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “Trace”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “Span”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

代码/命令说明：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Trace、Span、模型调用、工具调用、token成本”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为一次 Agent 运行生成关联 ID 和结构化事件并支持离线回放”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 错误能定位到具体步骤且日志中没有密钥和原文隐私
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Trace、Span、模型调用、工具调用、token成本的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 42：对抗回归门禁

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 6 周 · 安全、评估与可观测性
- 建议时长：120 分钟
- 核心知识：红队、提示注入、权限越界、预算耗尽、回归阈值

### 本日定位

“红队”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 今日通过“把已知攻击和故障加入评估集并设置发布阈值”把原理落实为可运行、可验证的能力。

### 前置要求

- 能实现 MCP 工具或多智能体任务夹具
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“红队”解决什么问题，而不是只记名称
- 能独立完成：把已知攻击和故障加入评估集并设置发布阈值
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 红队

“红队”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 提示注入

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。

#### 权限越界

“权限越界”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 预算耗尽

“预算耗尽”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 回归阈值

“回归阈值”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “红队”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 本日把这个原理用于“把已知攻击和故障加入评估集并设置发布阈值”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “红队”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('红队、提示注入、权限越界、预算耗尽、回归阈值')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把已知攻击和故障加入评估集并设置发布阈值
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“红队、提示注入、权限越界、预算耗尽、回归阈值”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把已知攻击和故障加入评估集并设置发布阈值”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 安全失败会阻止发布且报告保留最小复现
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明红队、提示注入、权限越界、预算耗尽、回归阈值的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十二章：智能体性能评估](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter12/%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E6%80%A7%E8%83%BD%E8%AF%84%E4%BC%B0.md)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
- [NIST AI 风险管理框架](https://www.nist.gov/itl/ai-risk-management-framework)


## Day 43：Agentic RL 的序贯视角

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：Agentic RL、MDP、状态、行动、轨迹、累计奖励

### 本日定位

Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。 “MDP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把工具问答 Agent 表示为状态、行动、观察和奖励序列”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Agentic RL”解决什么问题，而不是只记名称
- 能独立完成：把工具问答 Agent 表示为状态、行动、观察和奖励序列
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Agentic RL

Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。

#### MDP

“MDP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 状态

“状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 行动

“行动”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 轨迹

“轨迹”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 累计奖励

“累计奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。 “MDP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“把工具问答 Agent 表示为状态、行动、观察和奖励序列”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agentic RL 把多步工具使用建模为序贯决策，通过轨迹和奖励优化长期任务完成度。 “MDP”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

代码/命令说明：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把工具问答 Agent 表示为状态、行动、观察和奖励序列
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Agentic RL、MDP、状态、行动、轨迹、累计奖励”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把工具问答 Agent 表示为状态、行动、观察和奖励序列”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 正常与失败轨迹都能计算累计奖励并解释差异
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Agentic RL、MDP、状态、行动、轨迹、累计奖励的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 44：SFT 数据与行为示范

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：SFT、示范数据、消息格式、工具轨迹、LoRA

### 本日定位

监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。 “示范数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“SFT”解决什么问题，而不是只记名称
- 能独立完成：把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### SFT

监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。

#### 示范数据

“示范数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 消息格式

系统、用户、助手和工具消息承担不同信任级别与数据职责，拼装前必须保留来源和顺序。

#### 工具轨迹

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### LoRA

“LoRA”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。 “示范数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 监督微调让模型学习任务格式和示范行为，但不会自动发现示范之外的更优策略。 “示范数据”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

代码/命令说明：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“SFT、示范数据、消息格式、工具轨迹、LoRA”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把十条高质量任务轨迹转换为训练前可校验的 JSONL 结构”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 缺消息、非法工具和泄漏秘密的样本在训练前被拒绝
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明SFT、示范数据、消息格式、工具轨迹、LoRA的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 45：奖励设计与奖励漏洞

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：奖励函数、稀疏奖励、过程奖励、reward hacking

### 本日定位

“奖励函数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “稀疏奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为正确性、工具成本和安全约束设计组合奖励并运行反例”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“奖励函数”解决什么问题，而不是只记名称
- 能独立完成：为正确性、工具成本和安全约束设计组合奖励并运行反例
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 奖励函数

“奖励函数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 稀疏奖励

“稀疏奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 过程奖励

“过程奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### reward hacking

“reward hacking”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “奖励函数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “稀疏奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为正确性、工具成本和安全约束设计组合奖励并运行反例”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “奖励函数”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “稀疏奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

代码/命令说明：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为正确性、工具成本和安全约束设计组合奖励并运行反例
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“奖励函数、稀疏奖励、过程奖励、reward hacking”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为正确性、工具成本和安全约束设计组合奖励并运行反例”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 投机缩短步骤或跳过验证不会获得更高奖励
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明奖励函数、稀疏奖励、过程奖励、reward hacking的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 46：GRPO 小型模拟

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：GRPO、组内相对奖励、候选采样、优势

### 本日定位

GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。 “组内相对奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“不用 GPU，用固定候选和分数计算组内相对优势”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“GRPO”解决什么问题，而不是只记名称
- 能独立完成：不用 GPU，用固定候选和分数计算组内相对优势
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### GRPO

GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。

#### 组内相对奖励

“组内相对奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 候选采样

“候选采样”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 优势

“优势”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。 “组内相对奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“不用 GPU，用固定候选和分数计算组内相对优势”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** GRPO 比较同一问题的多个候选输出并利用组内相对奖励更新策略，仍需警惕奖励漏洞。 “组内相对奖励”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('GRPO、组内相对奖励、候选采样、优势')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：不用 GPU，用固定候选和分数计算组内相对优势
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“GRPO、组内相对奖励、候选采样、优势”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“不用 GPU，用固定候选和分数计算组内相对优势”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 相同奖励、异常值和安全违规三类边界都有断言
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明GRPO、组内相对奖励、候选采样、优势的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 47：可靠执行与恢复

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：重试、退避、检查点、幂等、补偿、熔断

### 本日定位

“重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “退避”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为含两个副作用工具的流程设计故障矩阵并实现恢复”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“重试”解决什么问题，而不是只记名称
- 能独立完成：为含两个副作用工具的流程设计故障矩阵并实现恢复
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 重试

“重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 退避

“退避”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 检查点

“检查点”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 幂等

幂等工具在重试后不会重复产生副作用，是检查点恢复和网络重试能够安全成立的前提。

#### 补偿

“补偿”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 熔断

“熔断”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “退避”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为含两个副作用工具的流程设计故障矩阵并实现恢复”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “重试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “退避”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为含两个副作用工具的流程设计故障矩阵并实现恢复
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“重试、退避、检查点、幂等、补偿、熔断”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为含两个副作用工具的流程设计故障矩阵并实现恢复”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 暂时错误可恢复，永久错误快速失败且无重复副作用
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明重试、退避、检查点、幂等、补偿、熔断的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 48：并发、流式与取消

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：asyncio、并发上限、流式输出、取消、速率限制

### 本日定位

“asyncio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并发上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“并行执行三个只读工具并在用户取消时回收所有任务”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“asyncio”解决什么问题，而不是只记名称
- 能独立完成：并行执行三个只读工具并在用户取消时回收所有任务
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### asyncio

“asyncio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 并发上限

“并发上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 流式输出

“流式输出”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 取消

“取消”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 速率限制

“速率限制”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “asyncio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并发上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“并行执行三个只读工具并在用户取消时回收所有任务”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “asyncio”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “并发上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('asyncio、并发上限、流式输出、取消、速率限制')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：并行执行三个只读工具并在用户取消时回收所有任务
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“asyncio、并发上限、流式输出、取消、速率限制”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“并行执行三个只读工具并在用户取消时回收所有任务”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 并发峰值受限且取消后没有悬挂 Task
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明asyncio、并发上限、流式输出、取消、速率限制的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 49：模型路由与成本控制

- 阶段：阶段四：安全、评估与生产工程
- 周次：第 7 周 · Agentic RL、可靠性与成本
- 建议时长：120 分钟
- 核心知识：模型路由、token预算、缓存、降级、费用上限

### 本日定位

“模型路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“按任务难度选择假模型层级并对重复只读请求缓存”把原理落实为可运行、可验证的能力。

### 前置要求

- 已建立安全、评估和可观测性基线
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“模型路由”解决什么问题，而不是只记名称
- 能独立完成：按任务难度选择假模型层级并对重复只读请求缓存
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 模型路由

“模型路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### token预算

“token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 缓存

“缓存”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 降级

“降级”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 费用上限

“费用上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “模型路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“按任务难度选择假模型层级并对重复只读请求缓存”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “模型路由”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “token预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reply:
    answer: str
    confidence: float

def parse_reply(data: dict) -> Reply:
    answer = str(data.get('answer', '')).strip()
    confidence = float(data.get('confidence', -1))
    if not answer or not 0 <= confidence <= 1:
        raise ValueError('invalid model reply')
    return Reply(answer, confidence)

reply = parse_reply({'answer':'完成','confidence':0.8})
assert reply.answer == '完成'
print(reply)
```

代码/命令说明：

- 模型输出先作为不可信字典解析，再验证必需字段和数值范围。
- 结构化格式减少解析歧义，但不能替代业务校验和权限检查。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：按任务难度选择假模型层级并对重复只读请求缓存
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“模型路由、token预算、缓存、降级、费用上限”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“按任务难度选择假模型层级并对重复只读请求缓存”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每次运行可预测最大成本且降级不会绕过质量门禁
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明模型路由、token预算、缓存、降级、费用上限的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十一章：Agentic RL](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%20Agentic-RL.md)
- [Hugging Face TRL 文档](https://huggingface.co/docs/trl/index)
- [Python asyncio 文档](https://docs.python.org/zh-cn/3.12/library/asyncio.html)


## Day 50：旅行助手需求拆解

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：旅行助手、约束收集、工具边界、人工确认

### 本日定位

“旅行助手”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “约束收集”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“设计只查询不预订的旅行助理，输出带预算和偏好的行程草案”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“旅行助手”解决什么问题，而不是只记名称
- 能独立完成：设计只查询不预订的旅行助理，输出带预算和偏好的行程草案
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 旅行助手

“旅行助手”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 约束收集

“约束收集”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 工具边界

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 人工确认

“人工确认”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “旅行助手”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “约束收集”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“设计只查询不预订的旅行助理，输出带预算和偏好的行程草案”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “旅行助手”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “约束收集”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：设计只查询不预订的旅行助理，输出带预算和偏好的行程草案
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“旅行助手、约束收集、工具边界、人工确认”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“设计只查询不预订的旅行助理，输出带预算和偏好的行程草案”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 缺日期或预算时先追问，任何预订动作都停在审批前
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明旅行助手、约束收集、工具边界、人工确认的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 51：Deep Research 查询规划

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：Deep Research、问题分解、搜索计划、并行研究

### 本日定位

“Deep Research”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “问题分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把一个开放问题拆成相互独立的检索子问题和停止条件”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Deep Research”解决什么问题，而不是只记名称
- 能独立完成：把一个开放问题拆成相互独立的检索子问题和停止条件
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Deep Research

“Deep Research”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 问题分解

“问题分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 搜索计划

“搜索计划”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 并行研究

“并行研究”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “Deep Research”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “问题分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“把一个开放问题拆成相互独立的检索子问题和停止条件”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “Deep Research”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “问题分解”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Deep Research、问题分解、搜索计划、并行研究')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把一个开放问题拆成相互独立的检索子问题和停止条件
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Deep Research、问题分解、搜索计划、并行研究”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把一个开放问题拆成相互独立的检索子问题和停止条件”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 子问题覆盖目标且不会重复搜索同一证据
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Deep Research、问题分解、搜索计划、并行研究的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 52：来源质量与证据去重

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：来源可信度、时效性、原始资料、去重、引用

### 本日定位

“来源可信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “时效性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为十条搜索结果评分并优先保留一手来源”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“来源可信度”解决什么问题，而不是只记名称
- 能独立完成：为十条搜索结果评分并优先保留一手来源
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 来源可信度

“来源可信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 时效性

“时效性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 原始资料

“原始资料”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 去重

“去重”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 引用

“引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “来源可信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “时效性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为十条搜索结果评分并优先保留一手来源”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “来源可信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “时效性”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('来源可信度、时效性、原始资料、去重、引用')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为十条搜索结果评分并优先保留一手来源
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“来源可信度、时效性、原始资料、去重、引用”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为十条搜索结果评分并优先保留一手来源”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 重复转载不会被当作多份独立证据
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明来源可信度、时效性、原始资料、去重、引用的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 53：综合写作与矛盾处理

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：证据综合、冲突、置信度、引用、拒答

### 本日定位

“证据综合”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “冲突”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“从含冲突的固定资料生成报告并明确分歧和不确定性”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“证据综合”解决什么问题，而不是只记名称
- 能独立完成：从含冲突的固定资料生成报告并明确分歧和不确定性
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 证据综合

“证据综合”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 冲突

“冲突”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 置信度

“置信度”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 引用

“引用”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 拒答

“拒答”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “证据综合”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “冲突”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“从含冲突的固定资料生成报告并明确分歧和不确定性”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “证据综合”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “冲突”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('证据综合、冲突、置信度、引用、拒答')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：从含冲突的固定资料生成报告并明确分歧和不确定性
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“证据综合、冲突、置信度、引用、拒答”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“从含冲突的固定资料生成报告并明确分歧和不确定性”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 每个结论带来源，无法消解的冲突不会被静默合并
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明证据综合、冲突、置信度、引用、拒答的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 54：编码 Agent 的安全闭环

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：编码Agent、工作区、补丁、测试、沙箱、回滚

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作区”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“让假 Agent 只生成补丁，在隔离目录应用并运行最小测试”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“编码Agent”解决什么问题，而不是只记名称
- 能独立完成：让假 Agent 只生成补丁，在隔离目录应用并运行最小测试
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 编码Agent

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### 工作区

“工作区”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 补丁

“补丁”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 测试

“测试”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 沙箱

“沙箱”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 回滚

“回滚”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作区”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“让假 Agent 只生成补丁，在隔离目录应用并运行最小测试”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “工作区”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('编码Agent、工作区、补丁、测试、沙箱、回滚')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：让假 Agent 只生成补丁，在隔离目录应用并运行最小测试
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“编码Agent、工作区、补丁、测试、沙箱、回滚”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“让假 Agent 只生成补丁，在隔离目录应用并运行最小测试”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 测试失败不覆盖原文件且补丁不能越出目标目录
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明编码Agent、工作区、补丁、测试、沙箱、回滚的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 55：GUI 与 Web Agent 状态

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：GUI Agent、Web Agent、观察、动作、页面状态、等待

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 今日通过“在本地静态页面用有限状态机完成登录表单夹具”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“GUI Agent”解决什么问题，而不是只记名称
- 能独立完成：在本地静态页面用有限状态机完成登录表单夹具
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### GUI Agent

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### Web Agent

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### 观察

“观察”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 动作

“动作”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 页面状态

“页面状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 等待

“等待”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 本日把这个原理用于“在本地静态页面用有限状态机完成登录表单夹具”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
def run_agent(goal: str, decide, tools: dict, max_steps: int = 4):
    observations = []
    for _ in range(max_steps):
        action = decide(goal, observations)
        if action['name'] == 'finish': return action['answer'], observations
        if action['name'] not in tools: raise ValueError('unknown tool')
        observations.append(tools[action['name']](action['argument']))
    raise RuntimeError('step budget exhausted')

def fake_decide(goal, observations):
    return {'name':'finish','answer':observations[-1]} if observations else {'name':'lookup','argument':goal}

answer, trace = run_agent('Agent', fake_decide, {'lookup': str.upper})
assert answer == 'AGENT' and trace == ['AGENT']
print(answer, trace)
```

代码/命令说明：

- 假模型让行动、观察和终止路径可重复测试，不必先消耗真实 API。
- 步骤上限是费用和无限循环的硬边界，达到上限必须显式失败。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：在本地静态页面用有限状态机完成登录表单夹具
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“GUI Agent、Web Agent、观察、动作、页面状态、等待”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“在本地静态页面用有限状态机完成登录表单夹具”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 页面异常、元素缺失和超时都会停止并保存当前状态
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明GUI Agent、Web Agent、观察、动作、页面状态、等待的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 56：用 Skill 封装可复用能力

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 8 周 · 旅行、研究、编码与能力封装
- 建议时长：120 分钟
- 核心知识：Agent Skill、指令、资源、触发条件、渐进披露

### 本日定位

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “指令”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界”把原理落实为可运行、可验证的能力。

### 前置要求

- 能在预算内完成可靠的端到端 Agent 原型
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“Agent Skill”解决什么问题，而不是只记名称
- 能独立完成：把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### Agent Skill

Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。

#### 指令

“指令”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 资源

“资源”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 触发条件

“触发条件”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 渐进披露

“渐进披露”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “指令”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** Agent 让模型根据目标和环境反馈选择下一步行动；固定且可预测的步骤更适合普通工作流。 “指令”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepResult:
    topic: str
    status: str
    evidence: str

def run(topic: str) -> StepResult:
    if not topic.strip(): raise ValueError('topic is required')
    return StepResult(topic, 'completed', '固定夹具与断言已通过')

result = run('Agent Skill、指令、资源、触发条件、渐进披露')
assert result.status == 'completed'
print(result)
```

代码/命令说明：

- StepResult 固定记录主题、状态和证据，使实验结果可回放。
- 将 run 的核心处理替换为当天 Agent 步骤，并保留空输入、预算或权限失败路径。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“Agent Skill、指令、资源、触发条件、渐进披露”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“把来源核验流程写成一份小型 Skill，并用两个任务验证触发边界”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 适用任务能复用，不适用任务不会被强制套用
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明Agent Skill、指令、资源、触发条件、渐进披露的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十三章：智能旅行助手](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0%20%E6%99%BA%E8%83%BD%E6%97%85%E8%A1%8C%E5%8A%A9%E6%89%8B.md)
- [Hello-Agents 第十四章：自动化深度研究智能体](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/%E7%AC%AC%E5%8D%81%E5%9B%9B%E7%AB%A0%20%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%99%BA%E8%83%BD%E4%BD%93.md)
- [Hello-Agents 第十五章：构建赛博小镇](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/%E7%AC%AC%E5%8D%81%E4%BA%94%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E8%B5%9B%E5%8D%9A%E5%B0%8F%E9%95%87.md)


## Day 57：毕业项目规格与评估设计

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 9 周 · 毕业设计、红队与交付
- 建议时长：150 分钟
- 核心知识：PEAS、用户故事、风险、评估集、成本预算

### 本日定位

PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “用户故事”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务”把原理落实为可运行、可验证的能力。

### 前置要求

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“PEAS”解决什么问题，而不是只记名称
- 能独立完成：为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### PEAS

PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。

#### 用户故事

“用户故事”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 风险

“风险”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 评估集

Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。

#### 成本预算

“成本预算”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “用户故事”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** PEAS 用性能度量、环境、执行器和传感器描述任务边界，能在编码前明确智能体可以观察和改变什么。 “用户故事”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

代码/命令说明：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“PEAS、用户故事、风险、评估集、成本预算”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“为一个真实但低风险场景提交 Agent 项目规格和二十条验收任务”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 范围、非目标、权限、数据、预算和发布阈值齐全
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明PEAS、用户故事、风险、评估集、成本预算的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
## Day 58：完成端到端垂直切片

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 9 周 · 毕业设计、红队与交付
- 建议时长：150 分钟
- 核心知识：模型、工具、状态、记忆、人工审批、接口

### 本日定位

“模型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“只实现一条从输入到可验证结果的完整主路径”把原理落实为可运行、可验证的能力。

### 前置要求

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“模型”解决什么问题，而不是只记名称
- 能独立完成：只实现一条从输入到可验证结果的完整主路径
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 模型

“模型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 工具

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 状态

“状态”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 记忆

短期记忆维持当前任务状态，长期记忆保存跨会话事实；写入、检索、更新和遗忘都需要策略。

#### 人工审批

人工审批应位于不可逆或高风险动作之前，并展示动作、参数、依据和影响，而不是只提供模糊确认按钮。

#### 接口

“接口”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “模型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 本日把这个原理用于“只实现一条从输入到可验证结果的完整主路径”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “模型”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TRANSITIONS = {'draft':'review', 'review':'approved', 'approved':'done'}

def advance(state: dict, approved=False):
    current = state['status']
    if current == 'review' and not approved:
        return {**state, 'paused': True}
    return {**state, 'status': TRANSITIONS[current], 'paused': False}

state = advance({'status':'draft'})
state = advance(state)
assert state['paused'] is True
state = advance(state, approved=True)
assert state['status'] == 'approved'
print(state)
```

代码/命令说明：

- 显式状态和转换表使执行路径可以检查、持久化和恢复。
- 高风险转换在动作发生前暂停；批准信息成为状态的一部分而不是口头约定。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：只实现一条从输入到可验证结果的完整主路径
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“模型、工具、状态、记忆、人工审批、接口”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“只实现一条从输入到可验证结果的完整主路径”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 主路径可运行且每个外部边界都有超时和错误结果
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明模型、工具、状态、记忆、人工审批、接口的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)


## Day 59：红队、故障与容量验收

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 9 周 · 毕业设计、红队与交付
- 建议时长：150 分钟
- 核心知识：提示注入、工具故障、恢复、并发、成本上限

### 本日定位

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 今日通过“运行对抗集、故障注入和小规模并发测试，修复最高风险问题”把原理落实为可运行、可验证的能力。

### 前置要求

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“提示注入”解决什么问题，而不是只记名称
- 能独立完成：运行对抗集、故障注入和小规模并发测试，修复最高风险问题
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 提示注入

提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。

#### 工具故障

工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

#### 恢复

“恢复”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 并发

“并发”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 成本上限

“成本上限”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。 本日把这个原理用于“运行对抗集、故障注入和小规模并发测试，修复最高风险问题”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** 提示注入把不可信内容伪装成指令；模型无法单独建立安全边界，必须依靠权限隔离、审批和输出校验。 工具把可执行能力暴露给模型；名称、描述和参数模式决定模型能否正确选择，执行器仍是最终安全边界。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
TOOLS = {'add': lambda a, b: a + b}

def execute(call: dict):
    name = call.get('name')
    arguments = call.get('arguments')
    if name not in TOOLS:
        raise ValueError('unknown tool')
    if not isinstance(arguments, dict) or set(arguments) != {'a', 'b'}:
        raise ValueError('invalid arguments')
    return TOOLS[name](int(arguments['a']), int(arguments['b']))

assert execute({'name':'add','arguments':{'a':2,'b':3}}) == 5
print('unknown tool and invalid arguments are rejected')
```

代码/命令说明：

- 注册表只暴露允许调用的工具，模型给出的任意名称不会自动变成代码执行。
- 参数集合和类型在工具边界验证，失败不会进入真实副作用。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：运行对抗集、故障注入和小规模并发测试，修复最高风险问题
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“提示注入、工具故障、恢复、并发、成本上限”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“运行对抗集、故障注入和小规模并发测试，修复最高风险问题”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 安全门禁全部通过且失败运行不留下不可逆副作用
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明提示注入、工具故障、恢复、并发、成本上限的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)


## Day 60：交付、复盘与后续路线

- 阶段：阶段五：综合场景与毕业设计
- 周次：第 9 周 · 毕业设计、红队与交付
- 建议时长：150 分钟
- 核心知识：演示、运行手册、评估报告、复盘、迭代

### 本日定位

“演示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “运行手册”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 今日通过“完成现场演示、部署或运行说明、指标报告和失败复盘”把原理落实为可运行、可验证的能力。

### 前置要求

- 已选定毕业项目场景、数据和验收集
- 能够运行上一学习日的最小示例并解释其正常与失败路径

### 学习目标

- 能用自己的话说明“演示”解决什么问题，而不是只记名称
- 能独立完成：完成现场演示、部署或运行说明、指标报告和失败复盘
- 能运行正常、边界和失败输入，并用输出或调用证据解释结果

### 概念说明

#### 演示

“演示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 运行手册

“运行手册”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 评估报告

Agent 评估同时检查最终结果、工具调用、轨迹、延迟和成本，并使用固定数据集保证版本间可比较。

#### 复盘

“复盘”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

#### 迭代

“迭代”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

### 原理与边界

**基础说明：** “演示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “运行手册”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 本日把这个原理用于“完成现场演示、部署或运行说明、指标报告和失败复盘”。

**运行机制：** 先用假模型和本地工具跑通“输入 → 决策 → 工具执行 → 观察 → 状态更新 → 终止”闭环，再接真实模型。所有外部调用都设置参数校验、超时、步骤与费用预算；高风险动作必须经过人工确认。

**解决的问题：** “演示”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。 “运行手册”应放进一次可回放的 Agent 运行中理解：明确它消费的消息或状态、产生的动作、允许的工具、停止条件与失败去向。

**常用工具：**

- Python 3.12
- 假模型与固定夹具
- JSON Schema
- pytest/unittest

**常见误区：**

- 没有步骤上限导致无限循环或费用失控
- 把模型输出直接当可信参数执行
- 只看最终答案而不保存工具轨迹与失败原因

### 官方命令或练习骨架

建议核对命令：`python practice.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Run:
    success: bool
    tool_calls: int
    cost: float
    unsafe_actions: int = 0

def reward(run: Run) -> float:
    if run.unsafe_actions: return -1.0
    return float(run.success) - .05 * run.tool_calls - run.cost

safe = Run(True, 2, .1)
unsafe = Run(True, 1, .01, 1)
assert reward(safe) > 0 and reward(unsafe) == -1
print(reward(safe), reward(unsafe))
```

代码/命令说明：

- 评估同时记录成功、工具步数、费用和不安全动作，避免只优化最终文本。
- 安全违规使用硬惩罚；若奖励遗漏关键约束，训练或搜索会主动利用漏洞。

### 实践步骤

1. 阅读前置要求与概念图，写出当天输入、处理和输出
2. 逐段运行参考骨架并解释每一步状态变化
3. 关闭参考答案，独立完成正常路径
4. 加入失败或边界输入，保存命令、输出并按验收条件复盘

### 独立任务

- 目标：完成现场演示、部署或运行说明、指标报告和失败复盘
- 输入：使用固定、可重复且不含真实敏感信息的输入，覆盖“演示、运行手册、评估报告、复盘、迭代”涉及的数据与状态。
- 输出：提交可运行产物、关键输出，以及一份说明输入如何经过各步骤变成结果的简短记录。
- 必须满足：
  - 先完成跟做示例，再关闭参考答案独立实现
  - 核心处理与输入输出分开，关键边界有明确校验
  - 至少包含一条正常路径和一条失败或边界路径
- 失败与边界：
  - 缺少必需输入时给出可理解的错误
  - 输入格式或状态不合法时不留下半成品

### 推荐工作流

#### 先建立上下文

阅读前置要求与今日目标，先写下输入会经过哪些步骤、最终应得到什么结果。

#### 跟做并理解示例

逐段运行知识卡中的参考示例；每运行一段，就对照代码讲解写下数据或状态的变化。

#### 关闭答案独立完成

不复制参考代码，独立完成“完成现场演示、部署或运行说明、指标报告和失败复盘”。卡住时只回看对应概念，不整段照抄。

#### 用失败证明掌握

加入边界和非法输入，运行验证清单并保存输出；最后闭卷解释结果为什么成立。

### 验收条件

- 陌生人能按文档运行，已知限制和下一步触发条件明确
- 失败样例可稳定触发并记录原因
- 正常、边界、失败三类结果均已保存
- 能闭卷解释关键数据流和失败原因

### 证据清单

- 源代码或实验脚本
- 实际运行命令与环境版本
- 关键输出、日志、断言或调用栈
- 100 字以上复盘与一个待解决问题

### 掌握标准

- 闭卷说明演示、运行手册、评估报告、复盘、迭代的输入、输出、依赖状态和不适用边界
- 不看参考实现完成正常与失败两条路径
- 能用断言、调用栈、日志或测试向量证明结论
- 能把失败收敛为下一步可执行的问题

### 官方资料

- [Hello-Agents 第十六章：毕业设计](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter16/%E7%AC%AC%E5%8D%81%E5%85%AD%E7%AB%A0%20%E6%AF%95%E4%B8%9A%E8%AE%BE%E8%AE%A1.md)
- [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OWASP LLM 应用风险](https://genai.owasp.org/llm-top-10/)
