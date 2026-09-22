---
name: zotero-library-manager
description: 管理 Zotero Desktop 资料库中的本地附件和集合归属。用于给既有条目添加文件附件，或在集合之间移动条目；纯检索、引用导出和文稿插入使用当前环境可用的 Zotero 查询或引用能力。
disable-model-invocation: true
compatibility: Requires Python 3 and Zotero 10 or later with the local API enabled. Reads stay on the local machine; writes require runtime authorization in Zotero.
---

# Zotero 资料库管理

通过确定性脚本执行 Zotero 10 本地 API 写入。脚本默认只预览；`--yes` 才会修改资料库。

核心命令：

```text
python <skill-dir>/scripts/zotero_library.py <command>
```

## 操作步骤

1. 先运行 `status`。用 `search` 和 `collections` 将用户描述解析为唯一的 Zotero item key 与 collection key。只有候选唯一，或用户已经给出精确 key 时才进入下一步。
2. 运行不带 `--yes` 的 `move` 或 `attach`，向用户展示脚本返回的预览。预览必须包含条目、来源与目标，或条目、文件绝对路径与文件大小。
3. 用户原请求已明确授权该项写入时，或用户确认预览后，以相同参数加 `--yes` 执行。Zotero 弹出授权窗口时，让用户在 Zotero 中选择；添加附件通常应选择“始终允许”，否则多阶段上传可能需要多次授权。
4. 以脚本的验证结果为完成标准：移动后集合列表与计划一致；附件可重新读取且 `parentItem`、文件名与本地文件一致。报告变更后的 item key、collection key 或 attachment key。

Zotero 本地 API 只允许通过本机 loopback 地址访问，不转发或暴露 `23119` 端口。运行时 API Key 只保存在当前进程，不写文件、不打印。预览可能包含文献题名、作者和本地绝对路径，只向当前用户显示，不写入仓库、handoff 或长期日志。

## 常用命令

```text
# 状态与解析
python <skill-dir>/scripts/zotero_library.py status
python <skill-dir>/scripts/zotero_library.py search "topic" --limit 20
python <skill-dir>/scripts/zotero_library.py collections --query "Target Collection"

# 预览并移动；保留条目的其他集合归属
python <skill-dir>/scripts/zotero_library.py move --item ABCD2345 --from BCDE3456 --to CDEF4567
python <skill-dir>/scripts/zotero_library.py move --item ABCD2345 --from BCDE3456 --to CDEF4567 --yes

# 预览并把本地文件导入为子附件
python <skill-dir>/scripts/zotero_library.py attach --item ABCD2345 --file "/path/to/paper.pdf"
python <skill-dir>/scripts/zotero_library.py attach --item ABCD2345 --file "/path/to/paper.pdf" --yes
```

`move` 只移除 `--from` 指定的集合，并保留其他集合归属；目标集合已经存在时也会移除来源集合。`attach` 导入 Zotero 管理的文件副本，原文件不移动。

当脚本返回 `412` 时，重新读取条目并重新生成预览；这表示条目在预览后发生了变化。解析失败、授权被拒绝、上传失败或验证不一致时停止，并向用户报告脚本给出的精确阻断原因。

维护或排查协议时，读取 [references/api-contract.md](references/api-contract.md)。
