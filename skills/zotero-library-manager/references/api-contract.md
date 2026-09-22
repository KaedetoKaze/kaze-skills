# Zotero 10 本地写入契约

仅在维护脚本、解释失败或扩展操作时读取本文件。

## 共同约束

- 基础地址为 `http://127.0.0.1:23119/api/`，请求 API v3。
- 仅允许 loopback 主机（`127.0.0.1`、`localhost` 或 `::1`）；不得端口转发、代理或绑定到外部接口。附件上传 URL 必须仍指向同一本机端口下的 `/api/local/uploads/`。
- 读取免认证；写入必须携带当前响应的 `Zotero-Server-ID` 和运行时授权得到的本地 API Key。
- API Key 只存在于当前脚本进程，不写文件、不打印。一次性 Key 被消费后，脚本会重新请求授权；附件上传选择“始终允许”可减少弹窗。
- 本地对象版本只属于当前 `Zotero-Server-ID`。更新条目使用最新对象版本作为 `If-Unmodified-Since-Version`，`412` 后重新读取和预览。
- 资料库写入完成后立即重新读取验证；验证结果，而不是 HTTP 成功状态，是操作完成标准。

## 移动条目

条目的 `collections` 是完整集合列表。脚本先读取当前列表，只删除来源 collection key，添加目标 collection key，并通过 `PATCH` 上传完整的新列表。这样不会移除未指定的其他集合归属。

## 添加附件

脚本创建 `linkMode=imported_file` 的子附件，然后执行本地 API 的完整上传协议：

1. 创建子附件条目。
2. 使用 MD5、文件名、大小和毫秒级修改时间申请上传。
3. 把文件内容上传到 Zotero 返回的本地上传 URL。
4. 注册 upload key。
5. 重新读取附件并验证父条目和文件名。

本地 API 不使用二进制差异上传。文件上限为 4 GB。脚本创建的是 Zotero 管理的副本，不改变原文件。

官方规范：

- <https://www.zotero.org/support/dev/web_api/v3/local_api>
- <https://www.zotero.org/support/dev/web_api/v3/write_requests>
- <https://www.zotero.org/support/dev/web_api/v3/file_upload>
