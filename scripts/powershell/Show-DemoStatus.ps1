$ErrorActionPreference = "Stop"

$root = "C:\Heartbeat"
Set-Location $root

Write-Host ""
Write-Host "=== Heartbeat Demo Status ==="
Write-Host ""

$approvalFiles = @{
    Requirements = ".\approvals\requirements.json"
    Architecture = ".\approvals\architecture.json"
    Deployment   = ".\approvals\deployment.json"
}

foreach ($name in $approvalFiles.Keys) {
    $approval = Get-Content $approvalFiles[$name] -Raw | ConvertFrom-Json

    Write-Host "$name approval:"
    Write-Host "  Status:      $($approval.status)"
    Write-Host "  Approved by: $($approval.approved_by)"
    Write-Host "  Approved at: $($approval.approved_at)"
    Write-Host ""
}

$tests = Test-Path `
    ".\examples\shipment-validation\06-evidence\test-results.md"

$traceability = Test-Path `
    ".\examples\shipment-validation\06-evidence\traceability.csv"

$release = Test-Path `
    ".\examples\shipment-validation\07-release\release-manifest.md"

Write-Host "Evidence:"
Write-Host "  Test evidence:   $tests"
Write-Host "  Traceability:    $traceability"
Write-Host "  Release manifest: $release"
Write-Host ""

Write-Host "Git:"
Write-Host "  Branch: $(git branch --show-current)"
Write-Host "  Commit: $(git rev-parse --short HEAD)"
Write-Host ""

git status --short

Write-Host ""
Write-Host "=== End Status ==="