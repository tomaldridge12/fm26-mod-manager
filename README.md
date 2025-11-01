# FM26 Mod Manager

A professional mod manager for Football Manager 2026, built with Python and tkinter.

## Features

- **Simple Installation Path Selection** - Just select your "Football Manager 26" folder
- **Automatic OS Detection** - Works on both Windows and macOS
- **Space-Efficient Backups** - Only backs up files being modified (not 3GB of everything)
- **Conflict Detection** - Warns you if mods modify the same files
- **Professional UI** - Modern dark theme with status feedback
- **Robust Error Handling** - Never crashes, all errors shown in UI
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
uv sync --dev

# Run in development mode
uv run python src/main.py
```

### Building Executables

See [BUILD.md](BUILD.md) for detailed build instructions.

**Quick build:**
- Windows: `build_windows.bat`
- macOS: `./build_macos.sh`

### Code Style

- **Modular design** - Each module has a single responsibility
- **Type hints** - Used throughout for better IDE support
- **Docstrings** - All public functions documented
- **Error handling** - All operations wrapped in try-catch with UI feedback
- **No crashes** - Global exception handler ensures graceful failures

### Adding New Features

1. Identify the appropriate module (core vs UI)
2. Add functionality to the relevant class
3. Update UI components if needed
4. Test error cases thoroughly
5. Update this README

## Architecture

### Core Principles

- **Separation of Concerns**: Business logic separated from UI
- **Error Recovery**: All operations handle failures gracefully
- **User Feedback**: Status bar shows real-time operation progress
- **Data Safety**: Atomic config writes prevent corruption
- **Space Efficiency**: Selective backups save disk space

### Key Components

- **PathManager**: OS-specific path handling and validation
- **BackupManager**: Smart backup system that only saves modified files
- **ModManager**: Handles mod extraction, installation, and conflicts
- **ConfigManager**: Atomic configuration saves with corruption recovery
- **UI Components**: Reusable widgets with consistent styling

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
