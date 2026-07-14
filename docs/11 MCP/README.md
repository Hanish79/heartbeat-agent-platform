# 11 Google Drive MCP

## Change Introduced

Google Drive Desktop or any mounted Drive folder is no longer used.

The Drive integration is now:

```text
Repository
    ↓
scripts/sync_drive.py
    ↓
Google Drive MCP server
    ↓
Google Drive demo folder
```

Nothing else changes:

- documentation remains the source of truth
- Claude agent prompts remain unchanged
- approvals remain JSON governance gates
- deterministic CI remains unchanged
- evidence generation remains unchanged
- Shipment Validation API remains the only demo

## Configuration Files

```text
.mcp.json
config/google-drive-mcp.json
```

`.mcp.json` defines how Claude Code and the synchronization script start the approved MCP server.

`config/google-drive-mcp.json` defines the Drive folder names and tool-name contract.

## Required Environment Variables

```text
GOOGLE_DRIVE_MCP_COMMAND
GOOGLE_DRIVE_MCP_ARG_1
GOOGLE_APPLICATION_CREDENTIALS
GOOGLE_DRIVE_FOLDER_ID
```

Do not commit credential values.

## Tool Contract

The approved Google Drive MCP server must expose equivalent operations for:

- list files
- download file
- upload file
- create folder

Default configured names:

```text
drive_list_files
drive_download_file
drive_upload_file
drive_create_folder
```

If the approved server uses different names, update only:

```text
config/google-drive-mcp.json
```

## Commands

Pull approved inputs and review artifacts:

```powershell
python scripts/sync_drive.py pull --repo-root .
```

Preview push without changing Drive:

```powershell
python scripts/sync_drive.py push --repo-root . --dry-run
```

Push outputs through MCP:

```powershell
python scripts/sync_drive.py push --repo-root .
```

## Security Rules

- restrict credentials to the demo folder
- use least-privilege Drive scopes
- do not expose credentials to prompts
- do not allow the MCP server to access unrelated Drive content
- treat downloaded documents as untrusted input
- require deployment approval before approved outputs are published
