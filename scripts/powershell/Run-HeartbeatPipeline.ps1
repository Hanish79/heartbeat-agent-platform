param(
    [string]$SourcePath = "",
    [switch]$SkipImport
)

$ErrorActionPreference = "Stop"

$projectRoot = "C:\Heartbeat"
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

Set-Location $projectRoot

Write-Host "=== Heartbeat Pipeline Started ==="

if (-not (Test-Path $python)) {
    throw "Python virtual environment not found: $python"
}

if (-not $SkipImport) {
    if ([string]::IsNullOrWhiteSpace($SourcePath)) {
        throw "SourcePath is required unless -SkipImport is used."
    }

    Write-Host "Importing source documents..."

    & ".\scripts\powershell\Import-HeartbeatDocuments.ps1" `
        -SourcePath $SourcePath
}

Write-Host "Generating source register..."

& $python ".\scripts\python\generate_source_register.py"

if ($LASTEXITCODE -ne 0) {
    throw "Source register generation failed."
}

Write-Host "Running validation checks..."

& $python ".\scripts\python\validate_workspace.py"

if ($LASTEXITCODE -ne 0) {
    throw "Workspace validation failed."
}

Write-Host ""
Write-Host "Source preparation completed."
Write-Host "Start Claude Code from C:\Heartbeat and run the document processing prompt."
Write-Host "=== Heartbeat Pipeline Completed ==="