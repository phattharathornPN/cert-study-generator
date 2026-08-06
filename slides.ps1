# Run the original sequential slide generator (slides_only.py) on this machine.
#
#   ./slides.ps1                          one topic at a time, default account
#   ./slides.ps1 -Profile account2        a different account
#   ./slides.ps1 -StartId 05_01           resume from a topic
#   ./slides.ps1 -UseChecklist            bespoke per-topic checklists
#   ./slides.ps1 -Cert ccna               a different pack
#
# Why this and not slides_parallel.py: the sequential runner paces itself
# (20s between topics) and refreshes auth every 13 minutes on its own, which
# is what let it run for hours unattended -- 49 decks on 2026-07-29. The
# parallel runner has neither, and three days of tuning its concurrency
# produced fewer decks, not more.
#
# Ctrl+C stops it; finished topics are skipped on the next run.
#
# Only one machine may run against a notebook at a time. The 24/7 box is
# currently stopped and disabled, so this has the notebook to itself. To hand
# the job back:
#
#     ssh root@192.168.2.153 'systemctl enable --now cert-handover.timer cert-slides@ccnp_v2'
[CmdletBinding()]
param(
    [string]$Profile = "",
    [string]$StartId = "",
    [string]$EndId = "",
    [switch]$UseChecklist,
    [string]$Cert = "ccnp_v2"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$venvPy = "$env:APPDATA\uv\tools\notebooklm-py\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Error "notebooklm python not found at $venvPy"
    exit 1
}

# run.py resolves its notebook id at import time, so .env has to be in the
# environment before python starts.
$env:CERT = $Cert
Get-Content .env | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
    $k, $v = $_ -split '=', 2
    Set-Item "env:$($k.Trim())" $v.Trim()
}

$cmd = @("slides_only.py")
if ($Profile)      { $cmd += @("--profile", $Profile) }
if ($StartId)      { $cmd += @("--start-id", $StartId) }
if ($EndId)        { $cmd += @("--end-id", $EndId) }
if ($UseChecklist) { $cmd += "--use-checklist" }

Write-Host "CERT=$Cert  ->  $($cmd -join ' ')`n" -ForegroundColor Cyan
& $venvPy @cmd
