param(
    [string]$TargetPath = $(if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $HOME ".agents\skills" })
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourcePath = Join-Path $ProjectRoot "skills"
New-Item -ItemType Directory -Force -Path $TargetPath | Out-Null
Get-ChildItem -Path $SourcePath -Directory | ForEach-Object {
    $Destination = Join-Path $TargetPath $_.Name
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Path (Join-Path $_.FullName "*") -Destination $Destination -Recurse -Force
    Write-Host "Installed skill: $($_.Name)"
}
Write-Host "Installed skills to: $TargetPath"
