# Callout 映射

> 本映射用于飞书文档客户端的 XML 写入路径；客户端无法完整表达折叠等语义时，保留本地原文并明确报告差异。

## Obsidian 到飞书

将 Obsidian Callout 块转换为飞书 XML callout。保留标题文本和正文；折叠状态可记录为标题文字的一部分，但飞书不一定能表达完全相同的展开/折叠语义。

| Obsidian | 飞书 |
| --- | --- |
| `[!note]` | `<callout emoji="✅">` |
| `[!tip]` | `<callout emoji="🤖">` |
| `[!question]` | `<callout emoji="❓">` |
| `[!warning]` | `<callout emoji="⚠️">` |
| 其他类型 | 优先按语义选择相近 emoji；无法判断时用 `<callout emoji="📌">` |

示例：

```markdown
> [!tip]+ 🤖 AI 建议
> 这里是建议内容。
> **✏️ 补充说明：**（待补充）
```

转换为：

```xml
<callout emoji="🤖">
  <p><b>AI 建议</b></p>
  <p>这里是建议内容。</p>
  <p><b>✏️ 补充说明：</b>（待补充）</p>
</callout>
```

## 飞书到 Obsidian

按 emoji 和标题语义反向转换：

| 飞书 emoji / 标题语义 | Obsidian |
| --- | --- |
| `✅`、确认、意见 | `[!note]+` |
| `🤖`、AI、建议、修改 | `[!tip]+` |
| `❓`、待确认、问题 | `[!question]+` |
| `⚠️`、警告、风险、注意 | `[!warning]` |
| 其他 | `[!note]+` |

## 保真规则

- 保留 callout 中的原始表述，尤其是确认意见、团队反馈和问答中的观点。
- 长操作摘要优先用 `[!summary]-` 折叠，避免干扰正文阅读。
- 将飞书 callout 转回 Obsidian 时，每行正文都加 `>`，避免块被截断。
