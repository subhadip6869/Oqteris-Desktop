# Windows Installer Build Script for Oqteris
# Runs Nuitka compilation and compiles Inno Setup installer

$ErrorActionPreference = "Stop"

Write-Host "==> Compiling Oqteris standalone executable with Nuitka..." -ForegroundColor Cyan
python scripts/build_nuitka.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Nuitka compilation failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "==> Building Inno Setup Windows installer (.exe)..." -ForegroundColor Cyan
$isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $isccPath)) {
    $cmd = Get-Command "iscc" -ErrorAction SilentlyContinue
    if ($cmd) {
        $isccPath = $cmd.Source
    } else {
        Write-Error "Inno Setup compiler (ISCC.exe) not found!"
        exit 1
    }
}

& $isccPath packaging/windows/setup.iss
if ($LASTEXITCODE -ne 0) {
    Write-Error "Inno Setup compiler failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

$setupExe = "dist/Oqteris-1.0.0-Windows-x64-Setup.exe"
if (-not (Test-Path $setupExe)) {
    Write-Error "Expected installer not found at $setupExe"
    exit 1
}

Write-Host "==> Windows installer built successfully: $setupExe" -ForegroundColor Green
