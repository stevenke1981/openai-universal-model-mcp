$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv was not found on PATH. Install uv first: https://docs.astral.sh/uv/"
}

uv sync --extra dev
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Add OPENAI_API_KEY before starting the MCP server."
}
New-Item -ItemType Directory -Force -Path "artifacts" | Out-Null
Write-Host "Installation complete. Edit .env, then run .\scripts\test.ps1 and .\scripts\run.ps1."
