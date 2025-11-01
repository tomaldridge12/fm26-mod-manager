#!/bin/bash
# Build script for macOS application bundle

set -e  # Exit on error

echo "========================================"
echo "FM26 Mod Manager - macOS Build"
echo "========================================"
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Please install uv first."
    exit 1
fi

echo "[1/3] Installing dependencies..."
uv sync --dev

echo ""
echo "[2/3] Building application bundle with PyInstaller..."
uv run pyinstaller fm26.spec --clean --noconfirm

echo ""
echo "[3/3] Build complete!"
echo ""
echo "Application bundle location: dist/FM26 Mod Manager.app"
echo ""
echo "You can now:"
echo "  1. Test the app: open 'dist/FM26 Mod Manager.app'"
echo "  2. Copy to Applications: cp -r 'dist/FM26 Mod Manager.app' /Applications/"
echo "  3. Create DMG for distribution (requires additional tools)"
echo ""
echo "Users do NOT need Python installed to run the application."
echo ""
