#!/usr/bin/env python3
"""通过 Zotero 10 本地 API 添加附件并移动条目。"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_BASE_URL = "http://127.0.0.1:23119"
LOCAL_USER = "/api/users/0"
KEY_PATTERN = re.compile(r"^[23456789ABCDEFGHIJKLMNPQRSTUVWXYZ]{8}$")
MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024


class ZoteroError(RuntimeError):
    """表示可向用户说明的 Zotero 操作失败。"""


@dataclass
class Response:
    status: int | None
    headers: dict[str, str]
    body: bytes
    error: str | None = None

    def json(self) -> Any:
        try:
            return json.loads(self.body.decode("utf-8") or "null")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ZoteroError(f"响应不是有效 JSON：{exc}") from exc

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def header(self, name: str) -> str | None:
        target = name.lower()
        for key, value in self.headers.items():
            if key.lower() == target:
                return value
        return None


def dump(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def validate_key(value: str, label: str) -> str:
    normalized = value.strip().upper()
    if not KEY_PATTERN.fullmatch(normalized):
        raise ZoteroError(f"{label} 不是有效的 Zotero key：{value}")
    return normalized


class ZoteroClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        parsed = urllib.parse.urlsplit(self.base_url)
        if parsed.scheme != "http" or not self._is_loopback(parsed.hostname):
            raise ZoteroError("Zotero 本地服务必须使用 loopback HTTP 地址")

    @staticmethod
    def _is_loopback(hostname: str | None) -> bool:
        if not hostname:
            return False
        if hostname.lower() == "localhost":
            return True
        try:
            return ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            return False

    def upload_url(self, value: str) -> str:
        resolved = self.url(value)
        upload = urllib.parse.urlsplit(resolved)
        base = urllib.parse.urlsplit(self.base_url)
        upload_port = upload.port or 80
        base_port = base.port or 80
        if (
            upload.scheme != "http"
            or not self._is_loopback(upload.hostname)
            or upload_port != base_port
            or not upload.path.startswith("/api/local/uploads/")
        ):
            raise ZoteroError("Zotero 返回了非本机附件上传地址，已拒绝上传")
        return resolved

    def url(self, path_or_url: str) -> str:
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        return self.base_url + "/" + path_or_url.lstrip("/")

    def request(
        self,
        path_or_url: str,
        *,
        method: str = "GET",
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> Response:
        request_headers = dict(headers or {})
        if self.url(path_or_url).startswith(self.base_url + "/api"):
            request_headers.setdefault("Zotero-API-Version", "3")
        request = urllib.request.Request(
            self.url(path_or_url), data=data, method=method, headers=request_headers
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as result:
                return Response(
                    status=result.status,
                    headers=dict(result.headers.items()),
                    body=result.read(),
                )
        except urllib.error.HTTPError as exc:
            return Response(
                status=exc.code,
                headers=dict(exc.headers.items()),
                body=exc.read(),
                error=str(exc),
            )
        except Exception as exc:
            raise ZoteroError(f"无法连接 Zotero：{exc}") from exc

    def require(self, response: Response, allowed: set[int], action: str) -> Response:
        if response.status in allowed:
            return response
        detail = response.text().strip()[:1000] or response.error or "无响应正文"
        if response.status == 403 and action.startswith("读取"):
            detail += "；请在 Zotero 设置→高级中允许本机应用通信"
        if response.status == 412:
            detail += "；对象已变化，请重新读取并生成预览"
        raise ZoteroError(f"{action}失败：HTTP {response.status}，{detail}")

    def get_json(self, path: str, action: str) -> tuple[Any, Response]:
        response = self.require(self.request(path), {200}, action)
        return response.json(), response

    def server_info(self) -> dict[str, str | None]:
        response = self.require(self.request("/api/"), {200}, "读取本地 API")
        return {
            "zotero_version": response.header("X-Zotero-Version"),
            "api_version": response.header("Zotero-API-Version"),
            "schema_version": response.header("Zotero-Schema-Version"),
            "server_id": response.header("Zotero-Server-ID"),
        }

    def item(self, item_key: str) -> dict[str, Any]:
        payload, _ = self.get_json(f"{LOCAL_USER}/items/{item_key}", "读取条目")
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
            raise ZoteroError("条目响应缺少可编辑 data")
        return payload["data"]

    def collection(self, collection_key: str) -> dict[str, Any]:
        payload, _ = self.get_json(
            f"{LOCAL_USER}/collections/{collection_key}", "读取集合"
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
            raise ZoteroError("集合响应缺少可编辑 data")
        return payload["data"]


class WriteSession:
    def __init__(self, client: ZoteroClient, app_name: str) -> None:
        self.client = client
        info = client.server_info()
        server_id = info.get("server_id")
        if not server_id:
            raise ZoteroError("Zotero 响应缺少 Zotero-Server-ID，无法安全写入")
        self.server_id = server_id
        self.app_name = app_name
        self.key: str | None = None
        self.remembered = False

    def authorize(self) -> None:
        print("请在 Zotero 授权窗口中确认本次写入……", file=sys.stderr, flush=True)
        body = json.dumps({"appName": self.app_name}).encode("utf-8")
        response = self.client.request(
            "/api/local/authorize",
            method="POST",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Zotero-Server-ID": self.server_id,
            },
            timeout=120.0,
        )
        if response.status == 403:
            raise ZoteroError("用户拒绝了 Zotero 写入授权")
        self.client.require(response, {200}, "申请本地写入授权")
        payload = response.json()
        key = payload.get("key") if isinstance(payload, dict) else None
        if not isinstance(key, str) or not key:
            raise ZoteroError("授权响应缺少本地 API Key")
        self.key = key
        self.remembered = bool(payload.get("remember"))

    def request(
        self,
        path: str,
        *,
        method: str,
        data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        for _ in range(2):
            if self.key is None:
                self.authorize()
            request_headers = dict(headers or {})
            request_headers["Zotero-Server-ID"] = self.server_id
            request_headers["Zotero-API-Key"] = self.key or ""
            response = self.client.request(
                path, method=method, data=data, headers=request_headers, timeout=120.0
            )
            if response.status != 401:
                return response
            self.key = None
            self.remembered = False
        raise ZoteroError("本地写入授权已失效，重新授权后仍不可用")


def summarize_item(data: dict[str, Any]) -> dict[str, Any]:
    creators: list[str] = []
    for creator in data.get("creators", []):
        if not isinstance(creator, dict):
            continue
        name = creator.get("name") or " ".join(
            part for part in [creator.get("firstName"), creator.get("lastName")] if part
        )
        if name:
            creators.append(name)
    return {
        "key": data.get("key"),
        "item_type": data.get("itemType"),
        "title": data.get("title") or data.get("filename") or "",
        "creators": creators,
        "date": data.get("date") or "",
        "collections": data.get("collections", []),
        "parent_item": data.get("parentItem") or None,
    }


def collection_rows(client: ZoteroClient) -> list[dict[str, Any]]:
    payload, _ = client.get_json(f"{LOCAL_USER}/collections", "读取集合列表")
    rows = [row.get("data", {}) for row in payload if isinstance(row, dict)]
    by_key = {row.get("key"): row for row in rows if row.get("key")}

    def path_for(row: dict[str, Any], seen: set[str] | None = None) -> str:
        seen = set(seen or set())
        key = str(row.get("key") or "")
        if key in seen:
            return str(row.get("name") or key)
        seen.add(key)
        parent_key = row.get("parentCollection")
        parent = by_key.get(parent_key)
        name = str(row.get("name") or key)
        return f"{path_for(parent, seen)} / {name}" if parent else name

    return [
        {
            "key": row.get("key"),
            "name": row.get("name"),
            "path": path_for(row),
            "parent_collection": row.get("parentCollection") or None,
        }
        for row in rows
    ]


def cmd_status(args: argparse.Namespace) -> None:
    info = args.client.server_info()
    dump({"running": True, **info, "base_url": args.client.base_url})


def cmd_search(args: argparse.Namespace) -> None:
    query = urllib.parse.urlencode(
        {"q": args.query, "qmode": "titleCreatorYear", "limit": args.limit}
    )
    payload, _ = args.client.get_json(f"{LOCAL_USER}/items/top?{query}", "检索条目")
    rows = [
        summarize_item(row["data"])
        for row in payload
        if isinstance(row, dict) and isinstance(row.get("data"), dict)
    ]
    dump({"count": len(rows), "items": rows})


def cmd_collections(args: argparse.Namespace) -> None:
    rows = collection_rows(args.client)
    if args.query:
        needle = args.query.casefold()
        rows = [row for row in rows if needle in str(row["path"]).casefold()]
    dump({"count": len(rows), "collections": rows})


def move_plan(
    client: ZoteroClient, item_key: str, source_key: str, target_key: str
) -> tuple[dict[str, Any], list[str], list[str], dict[str, Any], dict[str, Any]]:
    item = client.item(item_key)
    source = client.collection(source_key)
    target = client.collection(target_key)
    if source_key == target_key:
        raise ZoteroError("来源集合与目标集合相同")
    before = list(item.get("collections") or [])
    if source_key not in before:
        raise ZoteroError(f"条目 {item_key} 当前不属于来源集合 {source_key}")
    after = [key for key in before if key != source_key]
    if target_key not in after:
        after.append(target_key)
    return item, before, after, source, target


def cmd_move(args: argparse.Namespace) -> None:
    item_key = validate_key(args.item, "item key")
    source_key = validate_key(args.source, "来源 collection key")
    target_key = validate_key(args.target, "目标 collection key")
    item, before, after, source, target = move_plan(
        args.client, item_key, source_key, target_key
    )
    result: dict[str, Any] = {
        "operation": "move",
        "executed": False,
        "item": summarize_item(item),
        "source": {"key": source_key, "name": source.get("name")},
        "target": {"key": target_key, "name": target.get("name")},
        "collections_before": before,
        "collections_after": after,
    }
    if not args.yes:
        dump(result)
        return

    version = item.get("version")
    if not isinstance(version, int):
        raise ZoteroError("条目缺少可用于并发保护的版本号")
    session = WriteSession(args.client, "Zotero Library Manager")
    body = json.dumps({"collections": after}).encode("utf-8")
    response = session.request(
        f"{LOCAL_USER}/items/{item_key}",
        method="PATCH",
        data=body,
        headers={
            "Content-Type": "application/json",
            "If-Unmodified-Since-Version": str(version),
        },
    )
    args.client.require(response, {204}, "移动条目")
    verified = args.client.item(item_key)
    actual = list(verified.get("collections") or [])
    if actual != after:
        raise ZoteroError(f"移动后验证不一致：期望 {after}，实际 {actual}")
    result.update({"executed": True, "verified": True, "new_version": verified.get("version")})
    dump(result)


def file_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upload_chunks(path: Path, prefix: bytes, suffix: bytes) -> Iterable[bytes]:
    if prefix:
        yield prefix
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            yield chunk
    if suffix:
        yield suffix


def created_item_key(payload: Any) -> str:
    if not isinstance(payload, dict):
        raise ZoteroError("创建附件响应格式无效")
    failed = payload.get("failed")
    if failed:
        raise ZoteroError(f"创建附件失败：{json.dumps(failed, ensure_ascii=False)}")
    for field in ("successful", "success"):
        values = payload.get(field)
        if not isinstance(values, dict) or "0" not in values:
            continue
        value = values["0"]
        if isinstance(value, str):
            return validate_key(value, "attachment key")
        if isinstance(value, dict):
            key = value.get("key")
            if not key and isinstance(value.get("data"), dict):
                key = value["data"].get("key")
            if isinstance(key, str):
                return validate_key(key, "attachment key")
    raise ZoteroError("创建附件响应中没有 attachment key")


def cleanup_attachment(
    client: ZoteroClient, session: WriteSession, attachment_key: str
) -> str:
    if not session.remembered or not session.key:
        return "未自动清理空附件：当前没有可复用授权"
    try:
        attachment = client.item(attachment_key)
        version = attachment.get("version")
        if not isinstance(version, int):
            return "未自动清理空附件：附件缺少版本号"
        response = session.request(
            f"{LOCAL_USER}/items/{attachment_key}",
            method="DELETE",
            headers={"If-Unmodified-Since-Version": str(version)},
        )
        client.require(response, {204}, "清理空附件")
        return "已清理本次创建的空附件"
    except Exception as exc:
        return f"自动清理空附件失败：{exc}"


def cmd_attach(args: argparse.Namespace) -> None:
    item_key = validate_key(args.item, "item key")
    path = Path(args.file).expanduser().resolve()
    if not path.is_file():
        raise ZoteroError(f"附件文件不存在：{path}")
    size = path.stat().st_size
    if size >= MAX_FILE_SIZE:
        raise ZoteroError("附件必须小于 4 GB")
    parent = args.client.item(item_key)
    if parent.get("parentItem"):
        raise ZoteroError("目标条目本身是子条目，不能作为附件父条目")
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    title = args.title or path.name
    result: dict[str, Any] = {
        "operation": "attach",
        "executed": False,
        "parent": summarize_item(parent),
        "file": str(path),
        "filename": path.name,
        "title": title,
        "content_type": content_type,
        "size": size,
        "source_file_unchanged": True,
    }
    if not args.yes:
        dump(result)
        return

    template_query = urllib.parse.urlencode(
        {"itemType": "attachment", "linkMode": "imported_file"}
    )
    template, _ = args.client.get_json(
        f"/api/items/new?{template_query}", "读取附件模板"
    )
    if not isinstance(template, dict):
        raise ZoteroError("附件模板响应格式无效")
    template.update(
        {
            "parentItem": item_key,
            "title": title,
            "accessDate": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
                "+00:00", "Z"
            ),
            "contentType": content_type,
            "filename": path.name,
        }
    )
    session = WriteSession(args.client, "Zotero Library Manager")
    attachment_key: str | None = None
    try:
        create_response = session.request(
            f"{LOCAL_USER}/items",
            method="POST",
            data=json.dumps([template]).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Zotero-Write-Token": uuid.uuid4().hex,
            },
        )
        args.client.require(create_response, {200}, "创建附件条目")
        attachment_key = created_item_key(create_response.json())

        md5 = file_md5(path)
        mtime = int(path.stat().st_mtime * 1000)
        upload_form = urllib.parse.urlencode(
            {
                "md5": md5,
                "filename": path.name,
                "filesize": size,
                "mtime": mtime,
            }
        ).encode("ascii")
        upload_response = session.request(
            f"{LOCAL_USER}/items/{attachment_key}/file",
            method="POST",
            data=upload_form,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "If-None-Match": "*",
            },
        )
        args.client.require(upload_response, {200}, "申请附件上传")
        upload = upload_response.json()
        if not isinstance(upload, dict):
            raise ZoteroError("附件上传授权响应格式无效")

        if not upload.get("exists"):
            upload_url = upload.get("url")
            upload_key = upload.get("uploadKey")
            if not isinstance(upload_url, str) or not isinstance(upload_key, str):
                raise ZoteroError("附件上传授权响应缺少 URL 或 upload key")
            prefix = str(upload.get("prefix") or "").encode("utf-8")
            suffix = str(upload.get("suffix") or "").encode("utf-8")
            binary_response = args.client.request(
                args.client.upload_url(upload_url),
                method="POST",
                data=upload_chunks(path, prefix, suffix),
                headers={
                    "Content-Type": str(upload.get("contentType") or content_type),
                    "Content-Length": str(len(prefix) + size + len(suffix)),
                },
                timeout=300.0,
            )
            args.client.require(binary_response, {201}, "上传附件文件")

            register_form = urllib.parse.urlencode({"upload": upload_key}).encode("ascii")
            register_response = session.request(
                f"{LOCAL_USER}/items/{attachment_key}/file",
                method="POST",
                data=register_form,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "If-None-Match": "*",
                },
            )
            args.client.require(register_response, {204}, "注册附件上传")

        verified = args.client.item(attachment_key)
        if verified.get("parentItem") != item_key or verified.get("filename") != path.name:
            raise ZoteroError(
                "附件验证不一致："
                f"parentItem={verified.get('parentItem')}，filename={verified.get('filename')}"
            )
        result.update(
            {
                "executed": True,
                "verified": True,
                "attachment_key": attachment_key,
                "md5": md5,
            }
        )
        dump(result)
    except Exception as exc:
        cleanup = (
            cleanup_attachment(args.client, session, attachment_key)
            if attachment_key
            else "尚未创建附件条目"
        )
        raise ZoteroError(f"添加附件失败：{exc}；{cleanup}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理 Zotero 条目附件与集合归属")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ZOTERO_LOCAL_BASE_URL", DEFAULT_BASE_URL),
        help="Zotero 本地服务地址",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    status = subcommands.add_parser("status", help="检查 Zotero 本地 API")
    status.set_defaults(func=cmd_status)

    search = subcommands.add_parser("search", help="按题名、作者和年份检索顶层条目")
    search.add_argument("query", help="检索词")
    search.add_argument("--limit", type=int, default=20, help="最多返回条目数")
    search.set_defaults(func=cmd_search)

    collections = subcommands.add_parser("collections", help="列出集合及层级路径")
    collections.add_argument("--query", help="按集合路径筛选")
    collections.set_defaults(func=cmd_collections)

    move = subcommands.add_parser("move", help="把条目从一个集合移动到另一个集合")
    move.add_argument("--item", required=True, help="Zotero item key")
    move.add_argument("--from", required=True, dest="source", help="来源 collection key")
    move.add_argument("--to", required=True, dest="target", help="目标 collection key")
    move.add_argument("--yes", action="store_true", help="执行写入；省略时只预览")
    move.set_defaults(func=cmd_move)

    attach = subcommands.add_parser("attach", help="把本地文件导入为条目的子附件")
    attach.add_argument("--item", required=True, help="父条目的 Zotero item key")
    attach.add_argument("--file", required=True, help="本地附件路径")
    attach.add_argument("--title", help="附件显示标题；默认使用文件名")
    attach.add_argument("--yes", action="store_true", help="执行写入；省略时只预览")
    attach.set_defaults(func=cmd_attach)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "limit", 1) < 1:
        parser.error("--limit 必须大于 0")
    try:
        args.client = ZoteroClient(args.base_url)
        args.func(args)
        return 0
    except ZoteroError as exc:
        dump({"error": str(exc), "command": args.command})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
