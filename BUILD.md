# Building FM26 Mod Manager

This document explains how to build standalone executables for Windows and macOS.

## Prerequisites

- **uv** package manager (https://github.com/astral-sh/uv)
- Python 3.10+ (managed by uv)
- Git (optional, for version control)

## Quick Build

### Windows

```bash
# Run the build script
build_windows.bat
```

The executable will be created at: `dist/FM26ModManager.exe`

### macOS

```bash
# Make script executable (first time only)
chmod +x build_macos.sh

# Run the build script
./build_macos.sh
```

The application bundle will be created at: `dist/FM26 Mod Manager.app`

## Manual Build Process

If you prefer to build manually:

```bash
# 1. Install dependencies
uv sync --dev

# 2. Build with PyInstaller
uv run pyinstaller fm26.spec --clean --noconfirm

# 3. Find output in dist/ folder
```

## Build Output

### Windows
- **File**: `FM26ModManager.exe` (~8-10 MB)
- **Type**: Single executable file
- **Distribution**: Simply share the .exe file

### macOS
- **File**: `FM26 Mod Manager.app`
- **Type**: Application bundle
- **Distribution**:
  - Zip the .app bundle, or
  - Create a DMG image (requires additional tools)

## Distribution Notes

### Windows
1. The .exe is a standalone file that includes Python and all dependencies
2. Users do NOT need Python installed
3. Windows may show a SmartScreen warning on first run (expected for unsigned apps)
4. To avoid warnings, the executable would need to be code-signed (requires certificate)

### macOS
1. The .app bundle includes everything needed to run
2. Users do NOT need Python installed
3. macOS may block the app as it's not notarized
4. Users can right-click → Open to bypass Gatekeeper on first run
5. For distribution, consider:
   - Code signing with Apple Developer certificate
   - Notarization through Apple

## Troubleshooting

### Build fails with "module not found"
- Run `uv sync --dev` to ensure all dependencies are installed
- Check that you're running from the project root directory

### Executable won't run
- **Windows**: Try running from command line to see error messages
- **macOS**: Check Console.app for error logs
- Ensure the build was done on the same OS as the target platform

### Large executable size
- This is normal - the executable includes Python runtime and all dependencies
- Size can be reduced by using PyInstaller's `--onedir` mode instead of `--onefile`

## Advanced: Creating Installers

### Windows Installer (Optional)
Use tools like:
- **Inno Setup** (free, recommended)
- **NSIS** (free)
- **WiX Toolset** (free, more complex)

### macOS DMG (Optional)
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "FM26 Mod Manager" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "FM26-Mod-Manager.dmg" \
  "dist/FM26 Mod Manager.app"
```

## Version Management

To update the version:
1. Edit `fm26.spec` - update `CFBundleShortVersionString` and `CFBundleVersion`
2. Rebuild with the build script

## Clean Build

To ensure a completely fresh build:

```bash
# Remove build artifacts
rm -rf build/ dist/

# Rebuild
# Windows: build_windows.bat
# macOS: ./build_macos.sh
```

## CI/CD Integration

For automated builds, use the manual build process:

```yaml
# Example GitHub Actions workflow
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Build
  run: |
    uv sync --dev
    uv run pyinstaller fm26.spec --clean --noconfirm

- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    name: fm26-${{ runner.os }}
    path: dist/
```
