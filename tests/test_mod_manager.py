import pytest
import zipfile
from pathlib import Path
from datetime import datetime
from src.core.mod_manager import ModManager


class TestModManager:
    """Test mod extraction, installation, and conflict detection."""

    @pytest.fixture
    def mod_manager(self, tmp_path):
        mod_storage_dir = tmp_path / "mods"
        return ModManager(mod_storage_dir)

    @pytest.fixture
    def create_test_zip(self, tmp_path):
        """Create a test ZIP archive with bundle files."""
        def _create_zip(bundle_files):
            zip_path = tmp_path / "test_mod.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for bundle_name in bundle_files:
                    zf.writestr(bundle_name, f"content of {bundle_name}")
            return zip_path
        return _create_zip

    def test_mod_manager_initialization(self, mod_manager, tmp_path):
        """Mod manager should create storage directory."""
        assert mod_manager.mod_storage_dir.exists()
        assert mod_manager.mods == []

    def test_extract_mod_zip_success(self, mod_manager, create_test_zip, tmp_path):
        """Successfully extract ZIP archive with bundle files."""
        bundle_files = ['file1.bundle', 'file2.bundle']
        zip_path = create_test_zip(bundle_files)
        temp_dir = tmp_path / "temp"

        success, extracted_files, error, traceback = mod_manager.extract_mod(
            str(zip_path), "Test Mod", temp_dir
        )

        assert success is True
        assert error is None
        assert traceback is None
        assert len(extracted_files) == 2
        assert all(f.suffix == '.bundle' for f in extracted_files)

    def test_extract_mod_no_bundle_files(self, mod_manager, tmp_path):
        """ZIP without bundle files should fail with descriptive error."""
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("readme.txt", "This is not a bundle file")

        temp_dir = tmp_path / "temp"
        success, files, error, _ = mod_manager.extract_mod(
            str(zip_path), "Test Mod", temp_dir
        )

        assert success is False
        assert files is None
        assert "No .bundle files found" in error

    def test_extract_mod_unsupported_format(self, mod_manager, tmp_path):
        """Unsupported archive format should fail."""
        archive_path = tmp_path / "test.tar.gz"
        archive_path.touch()

        temp_dir = tmp_path / "temp"
        success, files, error, _ = mod_manager.extract_mod(
            str(archive_path), "Test Mod", temp_dir
        )

        assert success is False
        assert "Only ZIP and RAR archives are supported" in error

    def test_install_mod_success(self, mod_manager, tmp_path):
        """Successfully install mod files to storage."""
        bundle_files = [
            tmp_path / "file1.bundle",
            tmp_path / "file2.bundle"
        ]
        for f in bundle_files:
            f.write_text(f"content of {f.name}")

        success, error = mod_manager.install_mod("Test Mod", bundle_files)

        assert success is True
        assert error is None

        mod_storage = mod_manager.mod_storage_dir / "Test Mod"
        assert mod_storage.exists()
        assert (mod_storage / "file1.bundle").exists()
        assert (mod_storage / "file2.bundle").exists()

    def test_install_mod_overwrites_existing(self, mod_manager, tmp_path):
        """Installing mod with same name should overwrite existing."""
        bundle_file = tmp_path / "file.bundle"
        bundle_file.write_text("original content")

        mod_manager.install_mod("Test Mod", [bundle_file])

        bundle_file.write_text("new content")
        success, error = mod_manager.install_mod("Test Mod", [bundle_file])

        assert success is True
        mod_file = mod_manager.mod_storage_dir / "Test Mod" / "file.bundle"
        assert mod_file.read_text() == "new content"

    def test_create_mod_entry(self, mod_manager, tmp_path):
        """Create proper mod metadata entry."""
        bundle_files = [
            tmp_path / "file1.bundle",
            tmp_path / "file2.bundle"
        ]
        for f in bundle_files:
            f.write_text("content")

        mod_manager.install_mod("Test Mod", bundle_files)
        mod_entry = mod_manager.create_mod_entry("Test Mod", bundle_files)

        assert mod_entry['name'] == "Test Mod"
        assert mod_entry['enabled'] is False
        assert len(mod_entry['files']) == 2
        assert 'file1.bundle' in mod_entry['files']
        assert 'file2.bundle' in mod_entry['files']
        assert 'file_paths' in mod_entry
        assert 'added_date' in mod_entry

        date = datetime.fromisoformat(mod_entry['added_date'])
        assert isinstance(date, datetime)

    def test_validate_mod_name_valid(self, mod_manager):
        """Valid unique mod name should pass."""
        error = mod_manager.validate_mod_name("New Mod")
        assert error is None

    def test_validate_mod_name_empty(self, mod_manager):
        """Empty mod name should fail."""
        error = mod_manager.validate_mod_name("   ")
        assert error is not None
        assert "cannot be empty" in error

    def test_validate_mod_name_duplicate(self, mod_manager):
        """Duplicate mod name should fail."""
        mod_manager.mods = [{'name': 'Existing Mod'}]

        error = mod_manager.validate_mod_name("Existing Mod")
        assert error is not None
        assert "already exists" in error

    def test_validate_mod_name_trims_whitespace(self, mod_manager):
        """Mod name validation should trim whitespace."""
        error = mod_manager.validate_mod_name("  Valid Name  ")
        assert error is None

    def test_check_conflicts_no_conflicts(self, mod_manager):
        """No conflicts when no mods are enabled."""
        mod_manager.mods = [
            {'name': 'Mod 1', 'enabled': False, 'files': ['file1.bundle']},
            {'name': 'Mod 2', 'enabled': False, 'files': ['file2.bundle']}
        ]

        conflicts = mod_manager.check_conflicts(['file1.bundle', 'file2.bundle'])
        assert len(conflicts) == 0

    def test_check_conflicts_with_enabled_mod(self, mod_manager):
        """Detect conflicts with enabled mods."""
        mod_manager.mods = [
            {'name': 'Mod 1', 'enabled': True, 'files': ['file1.bundle', 'file2.bundle']},
            {'name': 'Mod 2', 'enabled': False, 'files': ['file3.bundle']}
        ]

        conflicts = mod_manager.check_conflicts(['file2.bundle', 'file4.bundle'])

        assert len(conflicts) == 1
        assert 'file2.bundle' in conflicts
        assert conflicts['file2.bundle'] == 'Mod 1'

    def test_check_conflicts_multiple_files(self, mod_manager):
        """Detect multiple conflicting files."""
        mod_manager.mods = [
            {'name': 'Mod A', 'enabled': True, 'files': ['file1.bundle']},
            {'name': 'Mod B', 'enabled': True, 'files': ['file2.bundle', 'file3.bundle']}
        ]

        conflicts = mod_manager.check_conflicts(['file1.bundle', 'file2.bundle'])

        assert len(conflicts) == 2
        assert conflicts['file1.bundle'] == 'Mod A'
        assert conflicts['file2.bundle'] == 'Mod B'

    def test_enable_mod_success(self, mod_manager, tmp_path):
        """Successfully enable mod by copying files to game directory."""
        bundle_files = [tmp_path / "src" / "file1.bundle"]
        bundle_files[0].parent.mkdir()
        bundle_files[0].write_text("mod content")

        mod_manager.install_mod("Test Mod", bundle_files)

        mod = {
            'name': 'Test Mod',
            'file_paths': {'file1.bundle': str(bundle_files[0])}
        }

        game_data_path = tmp_path / "game_data"
        game_data_path.mkdir()

        success, copied_files, error = mod_manager.enable_mod(mod, game_data_path)

        assert success is True
        assert error is None
        assert 'file1.bundle' in copied_files
        assert (game_data_path / "file1.bundle").exists()
        assert (game_data_path / "file1.bundle").read_text() == "mod content"

    def test_enable_mod_missing_file(self, mod_manager, tmp_path):
        """Enabling mod with missing file should fail."""
        mod = {
            'name': 'Test Mod',
            'file_paths': {'missing.bundle': '/nonexistent/path/missing.bundle'}
        }

        game_data_path = tmp_path / "game_data"
        game_data_path.mkdir()

        success, copied_files, error = mod_manager.enable_mod(mod, game_data_path)

        assert success is False
        assert error is not None
        assert "missing" in error.lower()

    def test_get_mod_by_name(self, mod_manager):
        """Get mod metadata by name."""
        mod_manager.mods = [
            {'name': 'Mod 1', 'enabled': True},
            {'name': 'Mod 2', 'enabled': False}
        ]

        mod = mod_manager.get_mod_by_name('Mod 2')
        assert mod is not None
        assert mod['name'] == 'Mod 2'
        assert mod['enabled'] is False

    def test_get_mod_by_name_not_found(self, mod_manager):
        """Getting nonexistent mod should return None."""
        mod_manager.mods = [{'name': 'Mod 1'}]

        mod = mod_manager.get_mod_by_name('Nonexistent')
        assert mod is None

    def test_remove_mod_files(self, mod_manager, tmp_path):
        """Remove mod files from storage."""
        bundle_file = tmp_path / "file.bundle"
        bundle_file.write_text("content")

        mod_manager.install_mod("Test Mod", [bundle_file])

        mod_storage = mod_manager.mod_storage_dir / "Test Mod"
        assert mod_storage.exists()

        mod_manager.remove_mod_files("Test Mod")
        assert not mod_storage.exists()

    def test_get_enabled_mods(self, mod_manager):
        """Get list of enabled mods only."""
        mod_manager.mods = [
            {'name': 'Mod 1', 'enabled': True},
            {'name': 'Mod 2', 'enabled': False},
            {'name': 'Mod 3', 'enabled': True},
        ]

        enabled_mods = mod_manager.get_enabled_mods()

        assert len(enabled_mods) == 2
        assert all(mod['enabled'] for mod in enabled_mods)
        assert enabled_mods[0]['name'] == 'Mod 1'
        assert enabled_mods[1]['name'] == 'Mod 3'

    @pytest.mark.parametrize("bundle_count", [1, 3, 5, 10])
    def test_extract_various_bundle_counts(self, mod_manager, create_test_zip, tmp_path, bundle_count):
        """Test extracting archives with various numbers of bundles."""
        bundle_files = [f'file{i}.bundle' for i in range(bundle_count)]
        zip_path = create_test_zip(bundle_files)
        temp_dir = tmp_path / "temp"

        success, extracted_files, _, _ = mod_manager.extract_mod(
            str(zip_path), "Test Mod", temp_dir
        )

        assert success is True
        assert len(extracted_files) == bundle_count
