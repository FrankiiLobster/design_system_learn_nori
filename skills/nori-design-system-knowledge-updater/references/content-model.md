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

洞察使用额外字段，不要与普通主题判断混写：

```text
insight_origin: user | dialogue | unverified
insight_statement: 一句可复述的原创判断
reasoning: 从观察、疑问或反例到判断的推理链
evidence_quote: 用户关键原话或对话中的最小证据
reusable_question: 后续可继续追问或验证的问题
prominence: vault | inline | both
```

## Evidence status

- `insight`：用户的学习收获或方向性理解，可信地表达为“我理解到”。
- `candidate-rule`：对话推导出的候选规范，可供 Nori 采用，但尚未核对现有实现。
- `verified-rule`：已由 Nori 的 Figma、代码、设计评审或 Agent 测试确认。
- `open-question`：问题本身比结论更重要，保留为下一轮研究任务。

不要把 Gemini 的肯定语气当作 `verified-rule` 的证据。

## Insight handling

- `user` 洞察来自用户自己的观察、质疑、类比、反例或认知转折。可以润色排版，但不能改写观点归属，也不能把 Gemini 的补充冒充为用户原话。
- `dialogue` 洞察是对话共同推导出的非显然边界或诊断原则。必须保留其适用条件、代价和反例。
- `unverified` 洞察应同时说明缺少哪类证据，例如 Nori Figma 现状、真实组件库实现、Agent 试验或业务数据。
- Insight Vault 只收录真正改变分类、组件边界、交互语义或协作方式的内容，通常每轮 4–8 条。
- 普通知识点即使重要，也不必全部使用洞察样式；洞察样式过载会失去重点。

## Long-history compression

长对话以“压缩表达，不压缩知识”为原则：

1. 删除纯寒暄、重复肯定、无信息量过渡和同一结论的机械复述。
2. 保留用户原始疑问、犹豫、反驳和认知转折，即使它们没有形成最终规范。
3. 保留例子、反例、边界条件、适用场景、实现差异、代价和未决问题。
4. Gemini 的长篇回答可改为短摘要、对照表或决策树，但不得删除会改变判断的限定词。
5. 同一原则反复出现时合并为一个完整版本，并把新证据和新例外并入同一节点。
6. 无法确定价值时保留并缩写，不直接删除。
7. 在 review 摘要中记录本轮只省略了哪些纯废话，以及哪些高价值细节被压缩保留。

## Parent and child promotion

主题层级应随知识成熟度变化：

1. 如果新内容与已有主题共享同一个核心问题，把它合并到已有主题，并保留为子点或证据。
2. 如果一个子点出现自己的术语、规则、反例和验证方式，再提升为独立主题，并在原主题留下链接。
3. 如果多个主题都依赖同一底层概念，例如 `Portal` 同时影响 Modal、Sheet、Tooltip，则将其提升为跨组件协议，而不是在每个组件里重复解释。
4. 如果一个主题只是某个具体组件的例子，例如 Actionsheet 只是 Sheet 的业务预设，就放在父主题下，不要与父主题平级占据主要导航。
5. 历史上曾经独立展示的主题可以降级，但不要删除其有价值的证据或用户原话。

每次增量更新都要做一次 promotion / demotion review：

- 新观点只有具备自己的核心问题、术语、规则和验证方式时，才提升为一级主题。
- 一级主题后来如果只是更大框架中的具体组件、预设或案例，应降级为父主题下的子节点，而不是与父主题并列占据主要导航。
- 子节点如果开始影响多个组件，例如 Portal、Slots、受控状态，应提升为跨组件协议，并在相关组件中引用。
- 合并或降级时优先保留稳定 `id` 和旧有证据；如果改变 `id`，同步修复站内导航、搜索关键词和关系描述。
- 不要因为两个知识点来自不同时间点就保留两份相同规则；保留信息更完整、边界更清楚的版本。

## Deduplication test

新增条目写入前检查：

- 核心问题是否已经存在？
- 是否只是同一判断的另一种措辞？
- 新内容是否增加了新的维度：行为、渲染、状态、A11y、Token、例外或验证证据？
- 如果只是增加例子，是否更适合追加到已有主题？
- 是否应该更新父子关系，而不是新增导航项？

## Two-file delta boundary

使用新旧两份累积导出时，边界判断遵循：

1. 旧文件最后一个用户消息时间点。
2. 新文件中相同时间点。
3. 找不到相同时间点时，匹配旧文件最后一条用户消息的规范化文本。
4. 文本有轻微编辑时，使用高相似度匹配。
5. 以上都失败时，使用第一个晚于旧时间点的消息，并在 review 摘要中标记为降级边界。

边界之后的内容才属于本轮新增来源；新文件里重复出现的旧内容不能再次生成相同卡片。

## Review output

每次更新后，网站应能让用户快速回答：

- 这次新增了什么理解？
- 哪些是我先提出、后来被证明有架构价值的原创洞察？
- 哪些内容已经可以写进 Nori 规范？
- 哪些内容只是 Gemini 的候选解释？
- 哪些问题要通过 Figma、代码或 Agent 试验确认？
- 下一次继续对话时，应该从哪个节点接着问？
