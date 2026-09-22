# Agent Skills

[English](README.en.md)

一组面向项目协作、知识管理和研究工作流的 Agent Skills。

## Skills

| Skill | 简介 |
| --- | --- |
| [`handoff-project`](skills/handoff-project/) | 保存、移交和恢复项目现场，覆盖消息中继、中途检查点、阶段收尾与任务恢复。 |
| [`visual-explain`](skills/visual-explain/) | 为关系、流程、结构、比较和状态变化选择最小充分的视觉表达。 |
| [`markdown-metadata`](skills/markdown-metadata/) | 为 Markdown 文档建立精简、可路由、可追溯且便于持续维护的元数据契约。 |
| [`zotero-library-manager`](skills/zotero-library-manager/) | 管理 Zotero Desktop 中的本地附件和集合归属，并在写入前预览、写入后验证。 |
| [`obsidian-lark-sync`](skills/obsidian-lark-sync/) | 同步本地 Markdown／Obsidian 与飞书文档，处理版本、图片、Mermaid、评论和格式差异。 |

## Skill 介绍

### `handoff-project`

把项目交接整理成可恢复的工作现场，而不是简单的聊天摘要。它根据任务状态在消息中继、检查点、阶段收尾和恢复四种模式之间路由，并记录真实停点、验证边界、遗留事项与下一步动作。

适合在以下情况使用：

- 把另一个 Agent 的结果接入当前任务并继续处理；
- 暂停一项尚未完成的工作，为下一次会话保存现场；
- 完成一个阶段后整理知识、状态和交接信息；
- 从已有 handoff 接手项目并核对当前状态。

### `visual-explain`

判断一个问题是否值得用视觉方式解释，并选择复杂度最低但足以表达重点的形式。它可以在文字、表格、流程图、结构图、数据图表、确定性渲染和解释性图像之间路由，同时保护精确数据与原始证据不被装饰性表达改变。

适合在以下情况使用：

- 解释流程、层级、依赖关系或状态变化；
- 比较多个对象或展示数据中的关键差异；
- 标注图像证据或把抽象概念转化为更易理解的视图；
- 判断是否需要可交互表达，而不是默认制作复杂图形。

### `markdown-metadata`

把 Markdown frontmatter 视为一份最小字段契约：只保留无法从路径、文件名或正文可靠推导，并且会影响路由、更新、定位或追溯的元数据。它区分文档职责、外部资源对象、来源追溯和飞书同步副本，避免字段无限扩张。

适合在以下情况使用：

- 创建或整理目录说明页、文件说明页和知识笔记；
- 设计或调整 Markdown frontmatter 字段规范；
- 为外部文件、目录或云端资源建立稳定入口；
- 批量迁移元数据，并验证 YAML、日期、链接和字段约束。

### `zotero-library-manager`

通过 Zotero Desktop 本地 API 管理已有条目的附件与集合归属。所有写入操作先生成确定性预览，再由明确授权执行，并在完成后重新读取资料库验证结果。

适合在以下情况使用：

- 把本地 PDF 或其他文件添加为既有 Zotero 条目的附件；
- 将条目从一个集合移动到另一个集合，同时保留其他集合归属；
- 在写入前解析并确认唯一的条目、集合和文件目标；
- 对资料库变更执行写后验证，避免静默失败或误操作。

### `obsidian-lark-sync`

维护本地 Markdown／Obsidian 笔记与飞书文档之间的一对一同步关系。它区分代码仓库与 Obsidian Vault 两种模式，通过官方 `lark-cli` 或功能等价的飞书文档 API 客户端处理 revision 冲突、图片与附件、Mermaid、评论及格式差异。

适合在以下情况使用：

- 将本地 Markdown 或 Obsidian 笔记发布到飞书；
- 把飞书文档导入本地，并保存图片和结构；
- 在两端内容发生变化时检查版本、识别冲突并安全合并；
- 维护长期汇报、会议总结等本地底稿与飞书协作文档。

具体触发条件和完整工作流程见各目录中的 `SKILL.md`。

## License

本项目采用 [MIT License](LICENSE)。
