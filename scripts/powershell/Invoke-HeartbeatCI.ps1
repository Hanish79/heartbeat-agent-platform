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

$excludedFiles = @(
    "scripts/powershell/Invoke-HeartbeatCI.ps1",
    ".gitignore",
    "README.md",
    "CLAUDE.md"
)

$secretRules = @(
    @{
        Name    = "Google OAuth client secret"
        Pattern = 'GOCSPX-[A-Za-z0-9_-]{20,}'
    },
    @{
        Name    = "Private key"
        Pattern = '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
    },
    @{
        Name    = "AWS access key"
        Pattern = 'AKIA[0-9A-Z]{16}'
    },
    @{
        Name    = "GitHub token"
        Pattern = 'gh[pousr]_[A-Za-z0-9]{30,}'
    },
    @{
        Name    = "Hard-coded password"
        Pattern = '(?i)(password|passwd|pwd)\s*[:=]\s*["''][^"'']{8,}["'']'
    },
    @{
        Name    = "Hard-coded client secret"
        Pattern = '(?i)client[_-]?secret\s*[:=]\s*["''][^"'']{8,}["'']'
    },
    @{
        Name    = "Hard-coded access token"
        Pattern = '(?i)access[_-]?token\s*[:=]\s*["''][^"'']{8,}["'']'
    }
)

$textExtensions = @(
    ".ps1", ".psm1", ".py", ".json", ".yaml", ".yml",
    ".xml", ".config", ".ini", ".env", ".md", ".txt",
    ".js", ".ts", ".cs", ".java", ".sh"
)

$trackedFiles = git ls-files

foreach ($file in $trackedFiles) {
    $normalizedFile = $file.Replace("\", "/")

    if ($excludedFiles -contains $normalizedFile) {
        continue
    }

    if (-not (Test-Path $file -PathType Leaf)) {
        continue
    }

    $extension = [System.IO.Path]::GetExtension($file).ToLower()

    if ($textExtensions -notcontains $extension) {
        continue
    }

    $content = Get-Content $file -Raw -ErrorAction SilentlyContinue

    if ([string]::IsNullOrWhiteSpace($content)) {
        continue
    }

    foreach ($rule in $secretRules) {
        if ($content -match $rule.Pattern) {
            throw "Possible $($rule.Name) found in tracked file: $file"
        }
    }
}

Write-Host "Secret scan passed."

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

& $python -m pytest `
    ".\tests" `
    ".\examples\shipment-validation\05-testing" `
    -q

if ($LASTEXITCODE -ne 0) {
    throw "Python tests failed."
}

Write-Host ""
Write-Host "Heartbeat local CI passed."
Write-Host "=== Heartbeat Local CI Completed ==="