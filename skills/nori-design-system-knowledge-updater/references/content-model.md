# Nori Knowledge Content Model

这份参考用于更新已有知识网时的判断，不要求把网站实现成某一种特定技术栈。

## Topic shape

每个主题至少应包含：

```text
id: stable-kebab-case-id
title: 面向用户的中文标题
parent: optional topic id
status: insight | candidate-rule | verified-rule | open-question
source: conversation date or source file
user_understanding: 用户形成的理解、判断或认知变化
dialogue_synthesis: Gemini 对问题的解释和有价值的比较
actionable_spec: 可落成 Token、Props、States、Behavior、A11y 或流程的内容
open_questions: 仍需 Nori / Figma / code / Agent 验证的问题
relations: related topic ids
evidence: short quotes or source pointers
```

在现有单页 HTML 中，这些字段可以映射为主题卡片、左右分栏、代码块或 review board。不要为了追求字段完整而展示空字段。

## Evidence status

- `insight`：用户的学习收获或方向性理解，可信地表达为“我理解到”。
- `candidate-rule`：对话推导出的候选规范，可供 Nori 采用，但尚未核对现有实现。
- `verified-rule`：已由 Nori 的 Figma、代码、设计评审或 Agent 测试确认。
- `open-question`：问题本身比结论更重要，保留为下一轮研究任务。

不要把 Gemini 的肯定语气当作 `verified-rule` 的证据。

## Parent and child promotion

主题层级应随知识成熟度变化：

1. 如果新内容与已有主题共享同一个核心问题，把它合并到已有主题，并保留为子点或证据。
2. 如果一个子点出现自己的术语、规则、反例和验证方式，再提升为独立主题，并在原主题留下链接。
3. 如果多个主题都依赖同一底层概念，例如 `Portal` 同时影响 Modal、Sheet、Tooltip，则将其提升为跨组件协议，而不是在每个组件里重复解释。
4. 如果一个主题只是某个具体组件的例子，例如 Actionsheet 只是 Sheet 的业务预设，就放在父主题下，不要与父主题平级占据主要导航。
5. 历史上曾经独立展示的主题可以降级，但不要删除其有价值的证据或用户原话。

## Deduplication test

新增条目写入前检查：

- 核心问题是否已经存在？
- 是否只是同一判断的另一种措辞？
- 新内容是否增加了新的维度：行为、渲染、状态、A11y、Token、例外或验证证据？
- 如果只是增加例子，是否更适合追加到已有主题？
- 是否应该更新父子关系，而不是新增导航项？

## Review output

每次更新后，网站应能让用户快速回答：

- 这次新增了什么理解？
- 哪些内容已经可以写进 Nori 规范？
- 哪些内容只是 Gemini 的候选解释？
- 哪些问题要通过 Figma、代码或 Agent 试验确认？
- 下一次继续对话时，应该从哪个节点接着问？
