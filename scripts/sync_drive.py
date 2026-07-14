#!/usr/bin/env python3
"""Google Drive MCP synchronization for the Heartbeat demo.

This replaces the mounted Google Drive Desktop folder implementation.
No AI calls are made. The script talks directly to a configured MCP server
using JSON-RPC over stdio.

The MCP tool names are configured in config/google-drive-mcp.json because
Google Drive MCP servers do not all expose identical tool names.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "2025-06-18"


@dataclass(frozen=True)
class SyncRecord:
    direction: str
    local_path: str
    drive_path: str
    action: str
    sha256: str


class MCPError(RuntimeError):
    pass


class StdioMCPClient:
    def __init__(self, command: str, args: list[str], env: dict[str, str]) -> None:
        if not command:
            raise MCPError("GOOGLE_DRIVE_MCP_COMMAND is not configured.")
        clean_args = [arg for arg in args if arg]
        merged_env = os.environ.copy()
        merged_env.update({k: v for k, v in env.items() if v})
        self.process = subprocess.Popen(
            [command, *clean_args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=merged_env,
        )
        self._next_id = 1
        self._responses: queue.Queue[dict[str, Any]] = queue.Queue()
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                self._responses.put(json.loads(line))
            except json.JSONDecodeError:
                continue

    def _read_stderr(self) -> None:
        assert self.process.stderr is not None
        for line in self.process.stderr:
            print(f"[google-drive-mcp] {line.rstrip()}", file=sys.stderr)

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

        while True:
            response = self._responses.get(timeout=60)
            if response.get("id") != request_id:
                continue
            if "error" in response:
                raise MCPError(f"MCP {method} failed: {response['error']}")
            return response.get("result", {})

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

    def initialize(self) -> None:
        self.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "heartbeat-drive-sync", "version": "1.0.0"},
            },
        )
        self.notify("notifications/initialized")

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expand(value: str) -> str:
    if value.startswith("${") and value.endswith("}"):
        return os.environ.get(value[2:-1], "")
    return value


def server_config(repo_root: Path) -> tuple[str, list[str], dict[str, str]]:
    project = load_json(repo_root / ".mcp.json")
    server = project["mcpServers"]["google-drive"]
    command = expand(server["command"])
    args = [expand(str(item)) for item in server.get("args", [])]
    env = {key: expand(str(value)) for key, value in server.get("env", {}).items()}
    return command, args, env


def extract_tool_payload(result: dict[str, Any]) -> Any:
    if "structuredContent" in result:
        return result["structuredContent"]
    content = result.get("content", [])
    for item in content:
        if item.get("type") == "text":
            text = item.get("text", "")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
    return result


def list_drive_files(client: StdioMCPClient, tool: str, root_id: str, folder: str) -> list[dict[str, Any]]:
    result = client.call_tool(tool, {"root_folder_id": root_id, "folder_path": folder, "recursive": True})
    payload = extract_tool_payload(result)
    if isinstance(payload, dict):
        return payload.get("files", [])
    if isinstance(payload, list):
        return payload
    raise MCPError("list_files tool returned an unsupported payload.")


def download_file(client: StdioMCPClient, tool: str, file_id: str) -> bytes:
    result = client.call_tool(tool, {"file_id": file_id})
    payload = extract_tool_payload(result)
    if isinstance(payload, dict):
        if "content_base64" in payload:
            return base64.b64decode(payload["content_base64"])
        if "content" in payload:
            return str(payload["content"]).encode("utf-8")
    if isinstance(payload, str):
        return payload.encode("utf-8")
    raise MCPError("download_file tool returned an unsupported payload.")


def upload_file(client: StdioMCPClient, tool: str, root_id: str, drive_path: str, data: bytes) -> None:
    client.call_tool(
        tool,
        {
            "root_folder_id": root_id,
            "path": drive_path,
            "content_base64": base64.b64encode(data).decode("ascii"),
            "overwrite": True,
        },
    )


def pull(client: StdioMCPClient, contract: dict[str, Any], repo_root: Path, dry_run: bool) -> list[SyncRecord]:
    root_id = os.environ.get(contract["root_folder_id_env"], "")
    if not root_id:
        raise MCPError(f"{contract['root_folder_id_env']} is not configured.")
    records: list[SyncRecord] = []
    mapping = {
        contract["folders"]["input"]: repo_root / "input",
        contract["folders"]["drafts"]: repo_root / "output",
        contract["folders"]["approvals"]: repo_root / "approvals",
    }
    for drive_folder, local_root in mapping.items():
        for item in list_drive_files(client, contract["tools"]["list_files"], root_id, drive_folder):
            if item.get("mime_type") == "application/vnd.google-apps.folder":
                continue
            relative = item.get("relative_path") or item.get("name")
            if not relative or not item.get("id"):
                raise MCPError("Drive file item must include id and relative_path or name.")
            destination = local_root / relative
            data = download_file(client, contract["tools"]["download_file"], item["id"])
            digest = sha256_bytes(data)
            action = "unchanged"
            if not destination.exists() or sha256_bytes(destination.read_bytes()) != digest:
                action = "updated" if destination.exists() else "created"
                if not dry_run:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
            records.append(SyncRecord("pull", str(destination), f"{drive_folder}/{relative}", action, digest))
    return records


def push(client: StdioMCPClient, contract: dict[str, Any], repo_root: Path, dry_run: bool) -> list[SyncRecord]:
    root_id = os.environ.get(contract["root_folder_id_env"], "")
    if not root_id:
        raise MCPError(f"{contract['root_folder_id_env']} is not configured.")
    mapping = {
        repo_root / "output": contract["folders"]["drafts"],
        repo_root / "approvals": contract["folders"]["approvals"],
        repo_root / "approved": contract["folders"]["approved"],
        repo_root / "rejected": contract["folders"]["rejected"],
    }
    records: list[SyncRecord] = []
    for local_root, drive_folder in mapping.items():
        if not local_root.exists():
            continue
        for source in sorted(local_root.rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(local_root).as_posix()
            drive_path = f"{drive_folder}/{relative}"
            data = source.read_bytes()
            if not dry_run:
                upload_file(client, contract["tools"]["upload_file"], root_id, drive_path, data)
            records.append(SyncRecord("push", str(source), drive_path, "uploaded" if not dry_run else "planned", sha256_bytes(data)))
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize Heartbeat files through Google Drive MCP.")
    parser.add_argument("direction", choices=("pull", "push"))
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--contract", default="config/google-drive-mcp.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", default="output/drive-sync-report.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    contract = load_json(repo_root / args.contract)
    command, command_args, env = server_config(repo_root)
    client = StdioMCPClient(command, command_args, env)

    try:
        client.initialize()
        records = pull(client, contract, repo_root, args.dry_run) if args.direction == "pull" else push(client, contract, repo_root, args.dry_run)
    except (MCPError, OSError, queue.Empty) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    finally:
        client.close()

    payload = {
        "success": True,
        "transport": "google-drive-mcp",
        "direction": args.direction,
        "dry_run": args.dry_run,
        "record_count": len(records),
        "records": [asdict(item) for item in records],
    }
    report = repo_root / args.report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
