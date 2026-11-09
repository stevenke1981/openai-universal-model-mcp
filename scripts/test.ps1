$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
uv run pytest
uv run ruff check .
uv run python -m compileall src
