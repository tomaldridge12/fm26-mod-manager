# FM26 Mod Manager

![CI Status](https://github.com/tomaldridge12/fm26/actions/workflows/ci.yml/badge.svg)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE.md)

A professional mod manager for Football Manager 2026, built with Python and tkinter.

## Features

- **Simple Installation Path Selection** - Just select your "Football Manager 26" folder
- **Easy Mod Management** - Enable, disable, and remove mods with one click

## For Users

### Installation

#### Option 1: Download Pre-built Executable (Recommended)
1. Download the latest release for your OS:
   - **Windows**: `FM26ModManager.exe`
   - **macOS**: `FM26 Mod Manager.app`
2. Double-click to run (no Python installation required)

#### Option 2: Run from Source
Requires Python 3.10+ and uv:
```bash
git clone <repository-url>
cd fm26
uv sync
uv run python src/main.py
```

### Usage

1. **First Launch**: Browse to select your "Football Manager 26" installation folder
   - Windows: Usually `C:/Program Files (x86)/Steam/steamapps/common/Football Manager 26`
   - macOS: Usually `~/Library/Application Support/Steam/steamapps/common/Football Manager 26`

2. **Add Mods**: Click "+ Add Mod" and select a .zip or .rar archive containing .bundle files

3. **Enable Mods**: Select a mod and click "Enable"
   - Original files are automatically backed up before modification
   - Conflicts are detected and reported

4. **Disable Mods**: Select an enabled mod and click "Disable"
   - Original files are restored automatically

5. **Restore All**: Click "↺ Restore All" to disable all mods and restore vanilla game files

### Important Notes

- **Backups are automatic** - Original files are backed up only when mods modify them
- **Safe to use** - All operations can be undone by disabling mods or using "Restore All"

## For Developers

### Project Structure

```
src/
├── main.py              # Entry point with exception handling
├── app.py               # Main application orchestrator
├── core/
│   ├── paths.py         # Path management & validation
│   ├── backup.py        # Selective backup/restore operations
│   ├── mod_manager.py   # Mod installation & conflict detection
│   └── config.py        # Configuration persistence
└── ui/
    ├── styles.py        # Theme and colors
    └── components.py    # Reusable UI widgets
```

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd fm26

# Install dependencies (including dev tools)
uv sync

# Run in development mode
uv run python src/main.py

# Run tests
uv run pytest

# Run tests with verbose output
uv run pytest -v
```

### Building Executables

See [BUILD.md](BUILD.md) for detailed build instructions.

**Quick build:**
- Windows: `build_windows.bat`
- macOS: `./build_macos.sh`


### Testing

The project includes comprehensive unit tests for all core functionality:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_backup.py

# Run with coverage report
uv run pytest --cov=src --cov-report=html
```


See [tests/README.md](tests/README.md) for detailed test documentation.

## License

Apache 2.0, see `LICENSE.md` for more details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (especially error cases)
5. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Include your OS, FM26 version, and error messages (if any)
