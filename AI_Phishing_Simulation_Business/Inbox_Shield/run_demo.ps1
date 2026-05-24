param(
    [string]$SampleFolder = "samples"
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot

Write-Host ""
Write-Host "NorthStar Inbox Shield Demo" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

if (-not $env:XAI_API_KEY) {
    Write-Error "XAI_API_KEY is not set in this PowerShell session."
}

Write-Host "1. Running batch analysis against '$SampleFolder'..." -ForegroundColor Yellow
python run_against_folder.py $SampleFolder

Write-Host ""
Write-Host "2. Checking labelled expectations..." -ForegroundColor Yellow
python check_eval.py

Write-Host ""
Write-Host "3. CSV summary:" -ForegroundColor Yellow
Get-Content "outputs\inbox_shield_results.csv" -Raw

Write-Host ""
Write-Host "Demo complete." -ForegroundColor Green
