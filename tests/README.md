# FM26 Mod Manager - Test Suite

Comprehensive unit tests for critical functionality in the FM26 Mod Manager.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_backup.py

# Run specific test
uv run pytest tests/test_backup.py::TestBackupManager::test_backup_files_success
```

## Test Coverage

### PathManager Tests (12 tests)
Tests OS-specific path handling, installation validation, and folder selection:
- **OS-Specific Paths**: Verifies correct data path construction for Windows and macOS
- **Installation Validation**: Tests detection of valid FM26 installation structure
- **Folder Selection**: Tests auto-correction when user selects parent folder or wrong folder
- **Error Handling**: Validates error messages for invalid selections

### BackupManager Tests (15 tests)
Tests space-efficient backup and restore operations:
- **Selective Backup**: Backs up only files being modified (not entire game directory)
- **Preserve Originals**: Skips files already backed up to preserve first backup
- **Restore Operations**: Individual file restore and restore all functionality
- **Edge Cases**: Missing files, partial failures, nonexistent backups
- **Parametrized Tests**: 1, 5, 10, 50 files to test scalability

### ConfigManager Tests (19 tests)
Tests configuration persistence with atomic writes:
- **Atomic Writes**: Uses temp file + rename to prevent corruption
- **Corruption Recovery**: Handles malformed/corrupted JSON gracefully
- **Data Integrity**: All mod metadata fields preserved across save/load
- **Edge Cases**: Empty mods, None values, missing keys
- **Parametrized Tests**: 0, 1, 5, 10, 50 mods to test scalability

### ModManager Tests (24 tests)
Tests mod extraction, installation, and conflict detection:
- **Archive Extraction**: ZIP support with bundle file detection
- **Installation**: Copy mod files to storage with overwrite capability
- **Validation**: Mod name validation (empty, duplicate, whitespace)
- **Conflict Detection**: Detects files already used by enabled mods
- **File Operations**: Enable/disable mods, remove files, get enabled mods
- **Parametrized Tests**: Various bundle counts (1, 3, 5, 10)

## Test Organization

Each test class focuses on a specific core component:
- `test_paths.py` - `PathManager` class
- `test_backup.py` - `BackupManager` class
- `test_config.py` - `ConfigManager` class
- `test_mod_manager.py` - `ModManager` class

## Key Testing Strategies

1. **Fixtures**: Use pytest fixtures for setup/teardown (temporary directories, test data)
2. **Parametrization**: Use `@pytest.mark.parametrize` to test multiple scenarios efficiently
3. **Isolation**: Each test uses `tmp_path` to avoid side effects
4. **Edge Cases**: Test boundary conditions, error paths, and invalid inputs
5. **Real Behavior**: Tests use actual file I/O operations, not mocks (except OS detection)

## What We Don't Test

- **UI Components**: Tkinter widgets are not unit tested (requires integration/E2E tests)
- **User Interactions**: Button clicks, dialog flows (better suited for E2E tests)
- **RAR Extraction**: Requires external UnRAR tool (tested manually)
- **Cross-Platform**: Tests run on current OS only (CI would test all platforms)

## Test Statistics

- **Total Tests**: 70
- **Test Files**: 4
- **Parametrized Variations**: 14
- **Execution Time**: ~0.6-1.0 seconds
- **Pass Rate**: 100%
