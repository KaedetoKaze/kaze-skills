---
name: markdown-metadata
description: Markdown 元数据：创建或修改 frontmatter、目录说明页、文件说明页、知识笔记或字段规范时，建立可路由、可追溯、可持续更新的最小字段契约。
---

# Markdown 元数据

把 frontmatter 当作“最小契约”：只保留人和 Agent 无法从路径、文件名或正文可靠推导，却会改变路由、更新或资源定位行为的字段。

## 步骤

### 1．识别文档职责

读取现有 frontmatter、正文、所在路径和已知资源入口，确定：

- 本地 Markdown 的 `document_type`；
- 更新策略；
- 是否描述一个外部资源对象；
- 是否存在这份 Markdown 自身的飞书同步副本；
- 是否需要保留来源追溯。

目录路径已经表达业务域时，不再增加 `domain`。证据不足时保留原值或使用草稿状态，不根据目录名推断文件内容、负责人或主题。

完成条件：上述五项均有明确结论，资源对象与同步副本没有混用。

### 2．组装最小契约

从下文“字段契约”选择适用字段。必填字段齐全；条件字段只有在条件成立时出现；可选字段没有值时省略。

完成条件：每个字段都能说明它改变了哪一种路由、更新、定位或追溯行为，且没有字段重复路径已经表达的信息。

### 3．写入说明内容

`summary` 只概括有证据支持的内容和用途。`tags` 只补充跨目录主题。详细背景、子目录解释、相关知识、例外和人工核查事项写入正文。

完成条件：Agent 只读标题、路径、`summary` 和资源字段即可判断是否继续打开本文；正文没有把推测写成事实。

### 4．验证

解析 YAML，核对受控值、日期、链接和字段成对规则。批量迁移还要确认已有可回退 Git 基线，并将规范调整与内容迁移分成不同提交。

完成条件：所有改动文件均能解析；本地链接可达；外部入口不是临时下载地址；`lark_doc_url` 与 `lark_doc_revision` 同时出现或同时缺席。

## 字段契约

### 通用字段

| 字段 | 要求 | 语义 |
| --- | --- | --- |
| `title` | 必填 | 人类可读标题，与正文一级标题一致。 |
| `document_type` | 必填 | 本地 Markdown 自身承担的职责。 |
| `status` | 必填 | 文档生命周期，不表示外部业务或迁移状态。 |
| `updated` | 必填 | 本地正文最近修改日期，格式为 `YYYY-MM-DD`。 |
| `update_policy` | 必填 | 本文如何跟随事实变化。 |
| `summary` | 路由型文档必填 | 一至三句话说明对象、内容和用途。 |

目录说明页、文件说明页和知识笔记属于路由型文档。纯机械清单可以省略 `summary`，但应有自身明确的数据规范。

新建说明类文档优先使用：

- `directory-guide`：目录说明页；
- `asset-guide`：重要文件说明页；
- `knowledge-note`：主题知识笔记；
- `metadata-standard`：字段或元数据规范。

既有 `workspace-index`、`workspace-plan`、`inventory-report` 等准确类型可以保留。新类型应解决现有类型无法表达的职责，不为单个文件创造类型。

`status` 使用 `draft`（草稿或待人工确认）、`active`（已经确认并正常使用）或 `archived`（退出当前使用但保留历史）。既有 `planning`、`baseline` 等值在相关文档发生实质更新时再评审。

`update_policy` 使用：

- `snapshot`：固定反映一个时间点；
- `on-change`：相关结构、文件或业务事实变化时更新；
- `periodic`：按约定周期复核。

`updated` 只表示正文变化。外部资源核对日期使用 `resource_checked_at`。只有 `periodic` 文档确有下次复核日期时才增加 `next_review`。

### 路由字段

`summary` 应足以支持初步路由，不重复标题，不声称已经读过尚未读取的文件正文。

```yaml
summary: >-
  Reference materials for the current project, organized by topic and intended use.
```

`tags` 可选，用于路径无法表达的横向主题，通常零至五个。标签使用已有词汇，不重复一级目录、`document_type` 或 `status`。

`aliases` 可选，只记录真实存在的曾用名、简称、中英文名称或两侧命名差异。

### 资源对象

资源对象是本文主要说明的外部目录、文件或飞书资源。一份 Markdown 通常只写一组 `resource_*`：

| 字段 | 要求 | 语义 |
| --- | --- | --- |
| `resource_system` | 描述外部资源时必填 | 资源所在系统。 |
| `resource_type` | 描述外部资源时必填 | 资源的形态。 |
| `resource_path` | 描述外部资源时必填 | 可读、可追溯的完整业务路径或相对路径。 |
| `resource_url` | 已知稳定入口时填写 | 人和 Agent 可直接访问的入口。 |
| `resource_checked_at` | 实际核对后填写 | 最近一次确认路径、入口或对应关系的日期。 |

`resource_system` 使用稳定且可辨认的系统标识，例如 `local`、`git`、`lark-drive`、`lark-docx`、`lark-wiki`、`lark-sheets` 或 `lark-base`；沿用项目已有词汇，不把示例列表当作封闭枚举。

`resource_type` 优先使用 `folder`、`file`、`document`、`node`、`spreadsheet` 或 `base`。

其他资料入口写在正文“相关知识”或“相关资料”中，不扩张成多组 URL 字段。

### 来源追溯

资源已经迁往新的权威位置、仍需追溯原始目录时，按需使用：

```yaml
source_root: Legacy Archive
source_path: projects/example-project/reference-materials
source_snapshot_date: 2026-01-15
```

`source_snapshot_date` 只表示来源元数据快照日期，不表示迁移验收时间。没有来源迁移关系时省略整组字段。

### 飞书同步副本

同步副本是这份本地 Markdown 自身在飞书 Docx 或 Wiki 中的一对一页面，不是本文描述的资源对象。只有确实同步时才同时写入：

```yaml
lark_doc_url: https://……
lark_doc_revision: 23
```

相关知识页但不是同步副本时，在正文列链接。

## 文档分支

### 目录说明页

使用 `document_type: directory-guide`。一级、二级侧重分类边界和下级导航；三级或实际承载文件的末级补充业务介绍、资料范围、内部结构、权威位置和必要例外。

文件与所在目录同名，正文一级标题使用目录名称。不使用单一的 `目录索引.md` 作为所有文件名；同名文件以完整相对路径定位。

```yaml
---
title: Project Resources
document_type: directory-guide
status: draft
updated: 2026-01-15
update_policy: on-change
summary: >-
  Reference materials for the current project, organized by topic and intended use.
resource_system: local
resource_type: folder
resource_path: docs/resources
resource_checked_at: 2026-01-15
---
```

### 文件说明页

重要 DOCX、PPTX、PDF 或其他原始文件使用 `document_type: asset-guide`，沿用通用字段和资源对象字段；文件格式明确时可增加 `asset_format`。

内容抽取、OCR、派生笔记和人工校核字段在形成稳定工作流后再设计。工作流形成前，相关 Markdown 使用正文链接关联。

### 知识笔记与治理文档

知识笔记使用 `knowledge-note`，以 `summary` 和可选 `tags` 支持主题路由。方案、报告、标准和工作区入口保留准确的既有 `document_type`；只有它们主要说明一个外部对象时才增加 `resource_*`。

## 批量迁移

批量改名或字段迁移先保存可回退基线，再单独提交字段规范，最后迁移内容。迁移按语义评审：

- 版本字段只有明确的发布语义时才保留；否则使用 Git 历史和 `updated`；
- 文档审核状态转换为文档生命周期，迁移执行状态留在其权威系统；
- 外部盘点日期转换为 `resource_checked_at`，来源快照日期转换为 `source_snapshot_date`；
- 外部资源 URL 转换为 `resource_url`；
- 易变的外部修改时间放在正文目录事实中；
- `summary`、`tags` 和 `aliases` 只依据已核查事实生成。

技能字段发生变化时，先更新本技能并验证，再迁移使用它的文档。每个字段必须说明适用文档、触发条件、允许值和缺省行为；单个例外优先写入正文。
