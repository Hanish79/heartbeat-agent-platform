$ErrorActionPreference = "Stop"

$projectRoot = "C:\Heartbeat"
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

Set-Location $projectRoot

& $python ".\scripts\python\validate_workspace.py"

if ($LASTEXITCODE -ne 0) {
    throw "Workspace validation failed."
}

$sourceChanges = git diff --name-only |
    Where-Object {
        $_ -like "documents/01-raw-source-documents/*"
    }

if ($sourceChanges) {
    Write-Host "Warning: source document changes detected:"

    $sourceChanges | ForEach-Object {
        Write-Host " - $_"
    }

    throw "Source documents must remain immutable."
}

Write-Host "Heartbeat workspace checks passed."