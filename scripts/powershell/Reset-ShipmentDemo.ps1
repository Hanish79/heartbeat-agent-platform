$ErrorActionPreference = "Stop"

$projectRoot = "C:\Heartbeat"
Set-Location $projectRoot

Write-Host "Resetting Shipment Validation demo..."

$approvalFiles = @(
    ".\approvals\requirements.json",
    ".\approvals\architecture.json",
    ".\approvals\deployment.json"
)

foreach ($approvalFile in $approvalFiles) {
    if (-not (Test-Path $approvalFile)) {
        throw "Missing approval file: $approvalFile"
    }

    $approval = Get-Content $approvalFile -Raw | ConvertFrom-Json
    $approval.status = "pending"
    $approval.approved_at = ""
    $approval.comments = ""

    $approval |
        ConvertTo-Json -Depth 10 |
        Set-Content $approvalFile -Encoding UTF8
}

$generatedPaths = @(
    ".\examples\shipment-validation\02-requirements\requirements.md",
    ".\examples\shipment-validation\03-architecture\architecture.md",
    ".\examples\shipment-validation\04-development",
    ".\examples\shipment-validation\05-testing",
    ".\examples\shipment-validation\06-evidence",
    ".\examples\shipment-validation\07-release"
)

foreach ($path in $generatedPaths) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
        Write-Host "Removed: $path"
    }
}

$folders = @(
    ".\examples\shipment-validation\02-requirements",
    ".\examples\shipment-validation\03-architecture",
    ".\examples\shipment-validation\04-development",
    ".\examples\shipment-validation\05-testing",
    ".\examples\shipment-validation\06-evidence",
    ".\examples\shipment-validation\07-release"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}

Write-Host "Shipment Validation demo reset completed."