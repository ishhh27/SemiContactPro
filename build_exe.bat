@echo off
REM ============================================================
REM  SemiContact Pro — Windows EXE Builder
REM  Run this script from the project root directory.
REM ============================================================

echo.
echo  ============================================================
echo   SemiContact Pro — Build Script
echo  ============================================================
echo.

REM Install / upgrade dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  ERROR: pip install failed. Check your Python environment.
    pause & exit /b 1
)

REM Clean previous build artefacts
echo [2/3] Cleaning previous build...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist

REM Run PyInstaller
echo [3/3] Building EXE with PyInstaller...
pyinstaller SemiContactPro.spec --noconfirm
if errorlevel 1 (
    echo  ERROR: PyInstaller build failed.
    pause & exit /b 1
)

echo.
echo  ============================================================
echo   Build complete!
echo   EXE location:  dist\SemiContactPro.exe
echo  ============================================================
echo.
pause
