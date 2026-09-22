# 图片处理

## 飞书到本地 Markdown

飞书导出 Markdown 中的图片链接可能短期有效或需要鉴权。同步到本地时必须下载为长期附件，再改写引用；`drive +export --file-extension markdown` 不能替代附件落盘。

1. 用飞书文档客户端读取图片、附件或素材块。
2. 用 `lark-cli docs +media-download` 下载；预览需求才使用 `+media-preview`。以返回的 `saved_path` 和实际文件确定扩展名。
3. 保存到目标 Markdown 同目录的 `assets/`。
4. 文件名使用 `<md-stem>-<semantic-name>.<ext>`。描述优先来自题注、alt、附近标题或上下文，禁止默认使用 `image01`、`云端图片01` 等无语义名称。
5. 根据本地模式写引用：

代码仓库模式使用标准 Markdown 相对路径：

```markdown
![图片说明](assets/<md-stem>-<semantic-name>.png)
```

Vault 模式默认使用短 wikilink；只有同名歧义或无法解析时才加入 `assets/`：

```markdown
![[<md-stem>-<semantic-name>.png]]
![[assets/<md-stem>-<semantic-name>.png]]
```

代码仓库不要求存在 `.obsidian/`，不得仅为图片引用创建 Obsidian 配置。

## 图片匹配与分栏

- Markdown 图片链接与 XML `<img>` 建立顺序映射前先核对数量；数量不一致时改用 XML 结构或人工判断。
- 下载后记录实际文件名，正文只能引用真实存在的文件和扩展名。
- 飞书连续分栏组必须保留列关系：仓库和 Vault 均优先转成一张 Markdown 表格，不把并排图片简单顺序展开。
- 分栏包含文字和图片时，单元格同时保留图片与题注；仅同步文字时按 `text-only-import.md` 写图题。

## 本地 Markdown 到飞书

1. 仓库模式解析 `![alt](relative/path)`；Vault 模式同时解析 `![[...]]` 和 Obsidian 宽度语法。
2. 相对路径以当前 Markdown 所在目录为基准；wikilink 以目标 Vault 为基准解析。不得访问受限目录或上传无法定位的文件。
3. 图片必须位于允许访问的项目或 Vault 范围内并真实存在；不得上传 Vault 外文件或跟随可疑链接越过允许根目录。
4. 先创建或更新正文，再按飞书文档客户端的媒体插入流程上传本地图片。
5. 飞书侧保留图片说明，不把本地路径、绝对路径或 wikilink 写入正文。
6. 写后核对远端图片数量与题注；上传失败时明确报告缺失，不把文本占位误报为完整同步。

## 附件与白板

- 不把飞书临时 URL 保存在长期 Markdown 中，也不把本地绝对路径写入飞书。
- 同名文件落盘前比较内容；相同可复用，不同必须改名。
- 若 Mermaid／PlantUML 可完整复现白板，保留代码块；否则使用当前环境可用的白板导出工具生成 SVG，并按普通附件落盘。
- 图片下方的题注、来源或说明紧跟引用保留。
