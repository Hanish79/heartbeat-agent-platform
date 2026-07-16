param(
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"

$projectRoot = "C:\Heartbeat"
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

Set-Location $projectRoot

Write-Host "=== Heartbeat Local CI Started ==="

if (-not (Test-Path $python)) {
    throw "Python virtual environment not found: $python"
}

Write-Host "1. Validating workspace..."

& $python ".\scripts\python\validate_workspace.py"

if ($LASTEXITCODE -ne 0) {
    throw "Workspace validation failed."
}

Write-Host "2. Validating traceability..."

& $python ".\scripts\python\validate_traceability.py"

if ($LASTEXITCODE -ne 0) {
    throw "Traceability validation failed."
}

Write-Host "3. Checking source immutability..."

$sourceChanges = git diff --name-only HEAD |
    Where-Object {
        $_ -like "documents/01-raw-source-documents/*"
    }

if ($sourceChanges) {
    Write-Host "Source document changes detected:"

    $sourceChanges | ForEach-Object {
        Write-Host " - $_"
    }

    throw "Source documents are immutable and must not be modified."
}

Write-Host "4. Checking for secrets..."

$secretPatterns = @(
    "client_secret",
    "private_key",
    "access_token",
    "refresh_token",
    "GOCSPX-",
    "BEGIN PRIVATE KEY",
    "password="
)

$trackedFiles = git ls-files

foreach ($file in $trackedFiles) {
    if (-not (Test-Path $file -PathType Leaf)) {
        continue
    }

    $content = Get-Content $file -Raw -ErrorAction SilentlyContinue

    foreach ($pattern in $secretPatterns) {
        if ($content -match [regex]::Escape($pattern)) {
            throw "Possible secret found in tracked file: $file"
        }
    }
}

Write-Host "5. Checking register IDs..."

$registerFiles = @(
    ".\registers\source-register.csv",
    ".\registers\action-register.csv",
    ".\registers\decision-register.csv",
    ".\registers\risk-register.csv",
    ".\registers\artifact-register.csv"
)

foreach ($register in $registerFiles) {
    if (-not (Test-Path $register)) {
        throw "Missing register: $register"
    }
}

if ($RunTests) {
    Write-Host "6. Running Python tests..."

    & $python -m pytest ".\tests" -q

    if ($LASTEXITCODE -ne 0) {
        throw "Python tests failed."
    }
}

Write-Host ""
Write-Host "Heartbeat local CI passed."
Write-Host "=== Heartbeat Local CI Completed ==="