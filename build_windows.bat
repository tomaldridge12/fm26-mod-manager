@echo off
REM Build script for Windows executable

echo ========================================
echo FM26 Mod Manager - Windows Build
echo ========================================
echo.

REM Check if uv is available
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: uv not found. Please install uv first.
    exit /b 1
)

echo [1/3] Installing dependencies...
uv sync --dev
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo [2/3] Building executable with PyInstaller...
uv run pyinstaller fm26.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo Error: Build failed
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo Executable location: dist\FM26ModManager.exe
echo.
echo You can now distribute the executable to users.
echo Users do NOT need Python installed to run it.
echo.

pause
