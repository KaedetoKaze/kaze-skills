# Lark CLI 同步注意事项

本文只记录本地 Markdown 与飞书同步的取舍。具体参数以当前安装的飞书文档客户端帮助和实际返回结果为准；命令示例使用 `lark-cli`。

## 同步通道

- Vault 与代码仓库文档都通过官方 `lark-cli` 或功能等价的飞书文档 API 客户端同步。
- 客户端负责认证和远程读写；凭据保留在客户端安全存储中，不写入 Markdown 或仓库。
- 文档在本地由 `lark_doc_url` 标识，版本记录使用 `lark_doc_revision`；公开文件改用已忽略的 sidecar 状态，不再使用 `source` 保存同步绑定。
- 单次同步只使用一个远程写入客户端，写前检查 revision，写后重新 fetch 验证。

## Revision 防冲突

- fetch 使用 JSON 输出读取 `data.document.revision_id`。
- 本地 `lark_doc_revision` 为空时先全文核对并建立基线。
- 本地 revision 与云端不同，说明飞书在上次同步后发生修改；不得直接 overwrite。
- 写入时通过 `--revision-id <已核对版本>` 提交，写后重新 fetch，再把新 revision 写回本地。
- 写入失败或只部分成功时不得提前更新本地 revision。

## Markdown 与 XML

| 场景 | 优先模式 |
| --- | --- |
| 新建或整段发布纯文字长文 | Markdown |
| 纯文字局部替换 | Markdown `str_replace` |
| Callout、颜色、分栏、复杂表格 | XML |
| 精准编辑已有富格式块 | XML + block 操作 |
| 白板 | 已验证的 Mermaid／PlantUML，或 XML token／SVG |

全量覆盖可能丢失图片、评论和资源块；只在用户明确要求整篇替换且已完成结构核对时使用。

## 工作目录与媒体路径

- `--file`、`--output`、`@file` 只使用当前工作目录下的相对路径。
- 命令从目标项目或安全临时工作目录执行，不假设当前目录是 Vault 根目录。
- 仓库图片路径相对目标 Markdown；Vault wikilink 按 Vault 语义解析。
- 图片下载优先使用 `docs +media-download`，不依赖 fetch 返回的临时 CDN／authcode URL。

## Block 生命周期

- `overwrite`、`block_replace`、`block_delete` 后不复用受影响的 block ID。
- 插入或移动后，继续依赖位置时重新 fetch。
- XML `str_replace` 不跨 block；跨段纯文字可使用 Markdown，结构性修改优先 block 操作。

## 成本边界

- 日常 AI 编辑只改本地，不为保持“实时一致”自动调用飞书。
- 用户明确同步时才串行执行 fetch、差异判断、写入和写后复核。
- CLI 的版本提示不是同步失败；只有命令失败或行为异常时才处理。
