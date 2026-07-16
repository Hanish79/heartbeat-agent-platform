param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [string]$DestinationPath = "C:\Heartbeat\documents\01-raw-source-documents"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SourcePath)) {
    throw "Source path does not exist: $SourcePath"
}

New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null

$allowedExtensions = @(
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".txt", ".md", ".csv", ".json", ".xml"
)

$files = Get-ChildItem -Path $SourcePath -File -Recurse |
    Where-Object {
        $allowedExtensions -contains $_.Extension.ToLower()
    }

foreach ($file in $files) {
    $target = Join-Path $DestinationPath $file.Name

    if (Test-Path $target) {
        $sourceHash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
        $targetHash = (Get-FileHash $target -Algorithm SHA256).Hash

        if ($sourceHash -eq $targetHash) {
            Write-Host "Skipped unchanged file: $($file.Name)"
            continue
        }

        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $target = Join-Path $DestinationPath "$baseName-$timestamp$($file.Extension)"
    }

    Copy-Item $file.FullName $target
    Write-Host "Imported: $($file.FullName) -> $target"
}