import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.core.paths import PathManager


class TestPathManager:
    """Test path detection, validation, and OS-specific handling."""

    @pytest.fixture
    def path_manager(self):
        return PathManager()

    @pytest.mark.parametrize("system,expected_path", [
        ("Windows", "fm_Data/StreamingAssets/aa/StandaloneWindows64"),
        ("Darwin", "fm.app/Contents/Resources/Data/StreamingAssets/aa/StandaloneOSX"),
    ])
    def test_get_data_path_os_specific(self, path_manager, system, expected_path, tmp_path):
        """Verify correct data path construction for different operating systems."""
        fm_root = tmp_path / "Football Manager 26"
        fm_root.mkdir()

        data_path = fm_root / Path(expected_path)
        data_path.mkdir(parents=True, exist_ok=True)

        with patch.object(path_manager, 'system', system):
            result = path_manager.get_data_path(str(fm_root))
            assert result is not None
            assert Path(result).exists()
            assert expected_path.replace('/', '\\') in result or expected_path in result

    def test_get_data_path_unsupported_os(self, path_manager):
        """Unsupported OS should return None."""
        with patch.object(path_manager, 'system', 'Linux'):
            result = path_manager.get_data_path("/some/path")
            assert result is None

    def test_get_data_path_none_input(self, path_manager):
        """None input should return None."""
        assert path_manager.get_data_path(None) is None

    def test_validate_installation_valid(self, path_manager, tmp_path):
        """Valid FM26 installation structure should pass validation."""
        fm_root = tmp_path / "Football Manager 26"
        fm_root.mkdir()

        if path_manager.system == "Windows":
            data_path = fm_root / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
        else:
            data_path = fm_root / "fm.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "aa" / "StandaloneOSX"

        data_path.mkdir(parents=True, exist_ok=True)

        assert path_manager.validate_installation(str(fm_root)) is True

    def test_validate_installation_missing_data_folder(self, path_manager, tmp_path):
        """Missing data folder should fail validation."""
        fm_root = tmp_path / "Football Manager 26"
        fm_root.mkdir()

        assert path_manager.validate_installation(str(fm_root)) is False

    def test_validate_installation_none_input(self, path_manager):
        """None input should fail validation."""
        assert path_manager.validate_installation(None) is False

    def test_validate_installation_nonexistent_path(self, path_manager):
        """Nonexistent path should fail validation."""
        assert path_manager.validate_installation("/nonexistent/path") is False

    def test_validate_folder_selection_correct_folder(self, path_manager, tmp_path):
        """Selecting correct FM26 folder should succeed."""
        fm_root = tmp_path / "Football Manager 26"
        fm_root.mkdir()

        if path_manager.system == "Windows":
            data_path = fm_root / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
        else:
            data_path = fm_root / "fm.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "aa" / "StandaloneOSX"

        data_path.mkdir(parents=True, exist_ok=True)

        is_valid, corrected_path, error = path_manager.validate_folder_selection(str(fm_root))
        assert is_valid is True
        assert corrected_path == str(fm_root)
        assert error is None

    def test_validate_folder_selection_parent_folder(self, path_manager, tmp_path):
        """Selecting parent folder should auto-correct to FM26 subfolder."""
        parent = tmp_path / "steamapps" / "common"
        parent.mkdir(parents=True)

        fm_root = parent / "Football Manager 26"
        fm_root.mkdir()

        if path_manager.system == "Windows":
            data_path = fm_root / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
        else:
            data_path = fm_root / "fm.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "aa" / "StandaloneOSX"

        data_path.mkdir(parents=True, exist_ok=True)

        is_valid, corrected_path, error = path_manager.validate_folder_selection(str(parent))
        assert is_valid is True
        assert corrected_path == str(fm_root)
        assert error is None

    def test_validate_folder_selection_wrong_folder(self, path_manager, tmp_path):
        """Selecting wrong folder should return error message."""
        wrong_folder = tmp_path / "SomeOtherGame"
        wrong_folder.mkdir()

        is_valid, corrected_path, error = path_manager.validate_folder_selection(str(wrong_folder))
        assert is_valid is False
        assert corrected_path is None
        assert "Football Manager 26" in error

    def test_validate_folder_selection_invalid_structure(self, path_manager, tmp_path):
        """FM26 folder without valid structure should return error."""
        fm_root = tmp_path / "Football Manager 26"
        fm_root.mkdir()

        is_valid, corrected_path, error = path_manager.validate_folder_selection(str(fm_root))
        assert is_valid is False
        assert corrected_path is None
        assert "valid FM26 installation" in error
