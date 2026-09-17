# Gemini Source Records

把后续导出的 Gemini 对话记录放在这个目录。建议使用以下命名规则：

```text
YYYY-MM-DD-topic.txt
YYYY-MM-DD-topic.md
```

原始记录保持只读，不要为了整理知识网而覆盖或改写来源文件。

## 新旧历史增量流程

后续调用 `$nori-design-system-knowledge-updater` 时，只提供旧版与新版两份对话历史即可，例如：

```text
使用 $nori-design-system-knowledge-updater，
根据 sources/history_1.txt 和 sources/history_2.txt 更新 outputs/index.html。
```

Skill 会自动：

1. 读取旧文件的最后一个用户消息时间。
2. 在新累积文件中定位同一时间点。
3. 只提取边界之后的用户消息和 Gemini 回复。
4. 对完整知识网重新去重、归类和调整父子关系。
5. 更新 `outputs/index.html` 与 review 状态。

如新版导出与旧版前缀差异较大，skill 会依次尝试消息文本匹配和相似度匹配，并在结果中说明。
