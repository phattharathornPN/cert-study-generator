# Pull the generated pack off the 24/7 box, rebuild the reader site, publish it.
#
#   ./deploy-site.ps1                 CCNP v2 -> ccnp-encor-study
#   ./deploy-site.ps1 -Cert ccna      a different pack
#   ./deploy-site.ps1 -SkipPull       rebuild and publish what is already local
#
# The box owns the output; this machine only ever builds and publishes, so the
# pull is a full replace rather than a merge.
[CmdletBinding()]
param(
    [string]$Cert = "ccnp_v2",
    [string]$Project = "ccnp-encor-study",
    [string]$RemoteHost = "root@192.168.2.153",
    [switch]$SkipPull
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$venvPy = "$env:APPDATA\uv\tools\notebooklm-py\Scripts\python.exe"
$env:CERT = $Cert

# cert_config knows where this pack lives; don't second-guess it here.
$siteDir = & $venvPy -c "import cert_config; print(cert_config.SITE_DIR)"
$outDir = & $venvPy -c "import cert_config; print(cert_config.OUTPUT_DIR)"
$distDir = & $venvPy -c "import cert_config; print(cert_config.DIST_DIR)"

if (-not $SkipPull) {
    Write-Host "== pulling $outDir from $RemoteHost" -ForegroundColor Cyan
    if (Test-Path $outDir) { Remove-Item -Recurse -Force $outDir }
    # tar over ssh: rsync is not installed on this side.
    & cmd /c "ssh $RemoteHost `"cd cert-study-generator && tar -cz -f - $outDir`" | tar -xz -f -"
    if ($LASTEXITCODE -ne 0) { throw "pull failed" }
}

$slides = (Get-ChildItem "$outDir\*\slide.pdf" -ErrorAction SilentlyContinue).Count
$summaries = (Get-ChildItem "$outDir\*\summary_th.md" -ErrorAction SilentlyContinue).Count
Write-Host "== have $summaries summaries, $slides slides" -ForegroundColor Cyan

Write-Host "== building" -ForegroundColor Cyan
& $venvPy build_site.py
& $venvPy build_dist.py

# Wrangler needs Node >= 22, and the shell is normally parked on 18. Run the
# newer version straight out of its nvm install directory rather than calling
# `nvm use`: switching is global, does not affect this process's PATH anyway,
# and left the box on a different version than the one the user chose. The
# C:\nvm4w\nodejs shim is no good either -- nvm recreates that symlink on
# every switch, so a path through it goes stale mid-script.
$nodeDir = Get-ChildItem "$env:LOCALAPPDATA\nvm" -Directory -Filter "v2*" |
    Where-Object { [int](($_.Name -replace '^v') -split '\.')[0] -ge 22 } |
    Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $nodeDir) { throw "no Node >= 22 installed; wrangler needs one" }

Write-Host "== publishing to $Project (production) using $(Split-Path $nodeDir -Leaf)" -ForegroundColor Cyan
# npx.cmd is only a wrapper -- it launches whatever `node` PATH resolves to,
# which is still the old version. Put the chosen install first so the child
# process picks it up. This is scoped to this script's process; the shell the
# user comes back to is unchanged.
$env:Path = "$nodeDir;$env:Path"
# --branch main is not optional: the project's production branch is main
# while the repo sits on master, and without it the upload lands as a
# Preview deployment and the live site silently does not change.
& "$nodeDir\npx.cmd" wrangler pages deploy $distDir `
    --project-name $Project --branch main --commit-dirty=true
if ($LASTEXITCODE -ne 0) { throw "deploy failed" }

Write-Host "`nLive: https://$Project.pages.dev" -ForegroundColor Green
