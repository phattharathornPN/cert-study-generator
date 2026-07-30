# PowerShell shim for the `ccnp` bash CLI.
#
# PowerShell can't execute a shebang script directly -- running `./ccnp`
# just opens it in whatever app is associated with extensionless files.
# This forwards to Git Bash so `./ccnp.ps1 slides-fast` behaves exactly
# like `./ccnp slides-fast` does on Linux.
#
# Usage (from D:\CCNP-Study):
#   ./ccnp.ps1 status
#   ./ccnp.ps1 slides-fast
#   ./ccnp.ps1 slides-fast 4 account2

$ErrorActionPreference = "Stop"

# Prefer Git Bash. Avoid C:\Windows\System32\bash.exe -- that's the WSL
# launcher, which runs inside the Linux filesystem and won't see the same
# Python/venv setup this repo uses on Windows.
$candidates = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
)

$bash = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $bash) {
    Write-Error "Git Bash not found. Install Git for Windows, or run the CLI from a Git Bash prompt: ./ccnp $($args -join ' ')"
    exit 1
}

$script = Join-Path $PSScriptRoot "ccnp"
& $bash $script @args
exit $LASTEXITCODE
