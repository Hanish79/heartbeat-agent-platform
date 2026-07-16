param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "document",
        "risk",
        "decision",
        "architecture",
        "requirement",
        "pipeline",
        "fix"
    )]
    [string]$ChangeType,

    [Parameter(Mandatory = $true)]
    [string]$Description
)

$ErrorActionPreference = "Stop"

$cleanDescription = $Description `
    -replace '[^a-zA-Z0-9\s-]', '' `
    -replace '\s+', '-' `
    -replace '-+', '-'

$cleanDescription = $cleanDescription.ToLower().Trim("-")

$branchName = "feature/$ChangeType-$cleanDescription"

$currentBranch = git branch --show-current

if ($currentBranch -ne "main") {
    throw "You must start from main. Current branch: $currentBranch"
}

git pull origin main

if ($LASTEXITCODE -ne 0) {
    throw "Unable to update main from origin."
}

git checkout -b $branchName

if ($LASTEXITCODE -ne 0) {
    throw "Unable to create branch: $branchName"
}

Write-Host "Created branch: $branchName"