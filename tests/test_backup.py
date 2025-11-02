import pytest
from pathlib import Path
from src.core.backup import BackupManager


class TestBackupManager:
    """Test backup and restore operations for game files."""

    @pytest.fixture
    def setup_dirs(self, tmp_path):
        """Create temporary directory structure for testing."""
        backup_dir = tmp_path / "backups"
        data_path = tmp_path / "data"
        data_path.mkdir()

        backup_manager = BackupManager(backup_dir, str(data_path))

        return {
            'backup_manager': backup_manager,
            'backup_dir': backup_dir,
            'data_path': data_path,
            'original_backup_dir': backup_dir / "original"
        }

    def test_backup_manager_initialization(self, setup_dirs):
        """Backup manager should create necessary directories."""
        bm = setup_dirs['backup_manager']
        assert setup_dirs['original_backup_dir'].exists()
        assert setup_dirs['original_backup_dir'].is_dir()

    def test_backup_files_success(self, setup_dirs):
        """Successfully backup files that exist in data directory."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        test_files = ['file1.bundle', 'file2.bundle', 'file3.bundle']
        for file_name in test_files:
            (data_path / file_name).write_text(f"content of {file_name}")

        backed_up_count, failed = bm.backup_files(test_files)

        assert backed_up_count == 3
        assert len(failed) == 0
        for file_name in test_files:
            backup_file = setup_dirs['original_backup_dir'] / file_name
            assert backup_file.exists()
            assert backup_file.read_text() == f"content of {file_name}"

    def test_backup_files_skip_existing(self, setup_dirs):
        """Files already backed up should be skipped to preserve originals."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        file_name = 'test.bundle'
        (data_path / file_name).write_text("original content")

        count1, _ = bm.backup_files([file_name])
        assert count1 == 1

        (data_path / file_name).write_text("modified content")

        count2, _ = bm.backup_files([file_name])
        assert count2 == 0

        backup_file = setup_dirs['original_backup_dir'] / file_name
        assert backup_file.read_text() == "original content"

    def test_backup_files_skip_nonexistent(self, setup_dirs):
        """Nonexistent files should be skipped without error."""
        bm = setup_dirs['backup_manager']

        backed_up_count, failed = bm.backup_files(['nonexistent.bundle'])

        assert backed_up_count == 0
        assert len(failed) == 0

    def test_backup_files_partial_failure(self, setup_dirs):
        """Some files backing up should succeed even if others fail."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        (data_path / 'good.bundle').write_text("content")

        backed_up_count, failed = bm.backup_files(['good.bundle', 'missing.bundle'])

        assert backed_up_count == 1
        assert len(failed) == 0

    def test_restore_files_success(self, setup_dirs):
        """Successfully restore backed up files."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        test_files = ['file1.bundle', 'file2.bundle']
        for file_name in test_files:
            (data_path / file_name).write_text(f"original {file_name}")

        bm.backup_files(test_files)

        for file_name in test_files:
            (data_path / file_name).write_text(f"modified {file_name}")

        success, missing, failed = bm.restore_files(test_files)

        assert success is True
        assert len(missing) == 0
        assert len(failed) == 0
        for file_name in test_files:
            assert (data_path / file_name).read_text() == f"original {file_name}"

    def test_restore_files_missing_backup(self, setup_dirs):
        """Restoring files without backups should report missing files."""
        bm = setup_dirs['backup_manager']

        success, missing, failed = bm.restore_files(['missing.bundle'])

        assert success is False
        assert 'missing.bundle' in missing
        assert len(failed) == 0

    def test_restore_files_partial_missing(self, setup_dirs):
        """Restore should report which files are missing backups."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        (data_path / 'backed_up.bundle').write_text("original")
        bm.backup_files(['backed_up.bundle'])

        success, missing, failed = bm.restore_files(['backed_up.bundle', 'not_backed_up.bundle'])

        assert success is False
        assert 'not_backed_up.bundle' in missing
        assert 'backed_up.bundle' not in missing

    def test_restore_all_success(self, setup_dirs):
        """Restore all backed up files at once."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        test_files = ['file1.bundle', 'file2.bundle', 'file3.bundle']
        for file_name in test_files:
            (data_path / file_name).write_text(f"original {file_name}")

        bm.backup_files(test_files)

        for file_name in test_files:
            (data_path / file_name).write_text(f"modified {file_name}")

        restored_count, failed = bm.restore_all()

        assert restored_count == 3
        assert len(failed) == 0
        for file_name in test_files:
            assert (data_path / file_name).read_text() == f"original {file_name}"

    def test_get_backup_count(self, setup_dirs):
        """Get count of backed up files."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        assert bm.get_backup_count() == 0

        test_files = ['file1.bundle', 'file2.bundle']
        for file_name in test_files:
            (data_path / file_name).write_text("content")

        bm.backup_files(test_files)

        assert bm.get_backup_count() == 2

    def test_has_backups(self, setup_dirs):
        """Check if any backups exist."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        assert bm.has_backups() is False

        (data_path / 'test.bundle').write_text("content")
        bm.backup_files(['test.bundle'])

        assert bm.has_backups() is True

    @pytest.mark.parametrize("file_count", [1, 5, 10, 50])
    def test_backup_multiple_files(self, setup_dirs, file_count):
        """Test backing up various numbers of files."""
        data_path = setup_dirs['data_path']
        bm = setup_dirs['backup_manager']

        test_files = [f'file{i}.bundle' for i in range(file_count)]
        for file_name in test_files:
            (data_path / file_name).write_text(f"content {file_name}")

        backed_up_count, failed = bm.backup_files(test_files)

        assert backed_up_count == file_count
        assert len(failed) == 0
        assert bm.get_backup_count() == file_count
