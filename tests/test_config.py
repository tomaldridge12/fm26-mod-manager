import pytest
import json
from pathlib import Path
from src.core.config import ConfigManager


class TestConfigManager:
    """Test configuration persistence with atomic writes and corruption recovery."""

    @pytest.fixture
    def config_manager(self, tmp_path):
        config_file = tmp_path / "config.json"
        return ConfigManager(config_file)

    @pytest.fixture
    def sample_mods(self):
        return [
            {
                'name': 'Test Mod 1',
                'enabled': True,
                'files': ['file1.bundle', 'file2.bundle'],
                'file_paths': {'file1.bundle': '/path/to/file1.bundle'},
                'added_date': '2024-01-15T10:30:00'
            },
            {
                'name': 'Test Mod 2',
                'enabled': False,
                'files': ['file3.bundle'],
                'file_paths': {'file3.bundle': '/path/to/file3.bundle'},
                'added_date': '2024-01-16T14:20:00'
            }
        ]

    def test_config_manager_initialization(self, config_manager):
        """Config manager should create parent directories."""
        assert config_manager.config_file.parent.exists()

    def test_load_nonexistent_config(self, config_manager):
        """Loading nonexistent config should return default values."""
        fm_root, mods, profiles, current_profile = config_manager.load()

        assert fm_root is None
        assert mods == []
        assert len(profiles) == 1
        assert profiles[0]['name'] == 'Default'
        assert current_profile == 'Default'

    def test_save_and_load_config(self, config_manager, sample_mods):
        """Save and load configuration successfully."""
        fm_root = "C:/Program Files/Football Manager 26"
        profiles = [{'name': 'Default', 'mods': sample_mods}]
        current_profile = 'Default'

        success = config_manager.save(fm_root, profiles, current_profile)
        assert success is True

        loaded_root, loaded_mods, loaded_profiles, loaded_current = config_manager.load()
        assert loaded_root == fm_root
        assert loaded_current == 'Default'
        assert len(loaded_profiles) == 1
        assert len(loaded_profiles[0]['mods']) == 2
        assert loaded_profiles[0]['mods'][0]['name'] == 'Test Mod 1'
        assert loaded_profiles[0]['mods'][0]['enabled'] is True
        assert loaded_profiles[0]['mods'][1]['name'] == 'Test Mod 2'
        assert loaded_profiles[0]['mods'][1]['enabled'] is False

    def test_save_overwrites_existing_config(self, config_manager, sample_mods):
        """Saving should overwrite existing configuration."""
        profiles1 = [{'name': 'Default', 'mods': [sample_mods[0]]}]
        config_manager.save("Path 1", profiles1, 'Default')

        profiles2 = [{'name': 'Default', 'mods': [sample_mods[1]]}]
        config_manager.save("Path 2", profiles2, 'Default')

        loaded_root, loaded_mods, loaded_profiles, _ = config_manager.load()
        assert loaded_root == "Path 2"
        assert len(loaded_profiles[0]['mods']) == 1
        assert loaded_profiles[0]['mods'][0]['name'] == 'Test Mod 2'

    def test_save_empty_mods(self, config_manager):
        """Saving with empty mods list should work."""
        fm_root = "/some/path"
        profiles = [{'name': 'Default', 'mods': []}]

        success = config_manager.save(fm_root, profiles, 'Default')
        assert success is True

        loaded_root, loaded_mods, loaded_profiles, _ = config_manager.load()
        assert loaded_root == fm_root
        assert loaded_profiles[0]['mods'] == []

    def test_save_none_fm_root(self, config_manager, sample_mods):
        """Saving with None fm_root should work."""
        profiles = [{'name': 'Default', 'mods': sample_mods}]
        success = config_manager.save(None, profiles, 'Default')
        assert success is True

        loaded_root, loaded_mods, loaded_profiles, _ = config_manager.load()
        assert loaded_root is None
        assert len(loaded_profiles[0]['mods']) == 2

    def test_load_corrupted_config(self, config_manager):
        """Loading corrupted JSON should return defaults."""
        config_manager.config_file.write_text("{ invalid json }")

        fm_root, mods, profiles, current_profile = config_manager.load()

        assert fm_root is None
        assert mods == []
        assert len(profiles) == 1
        assert profiles[0]['name'] == 'Default'

    def test_load_malformed_config(self, config_manager):
        """Loading malformed but valid JSON should return defaults."""
        config_manager.config_file.write_text('{"unexpected_key": "value"}')

        fm_root, mods, profiles, current_profile = config_manager.load()

        assert fm_root is None
        assert mods == []
        assert len(profiles) == 1

    def test_atomic_write_creates_temp_file(self, config_manager, sample_mods):
        """Atomic write should use temp file then rename."""
        fm_root = "/test/path"
        profiles = [{'name': 'Default', 'mods': sample_mods}]

        success = config_manager.save(fm_root, profiles, 'Default')
        assert success is True

        temp_file = config_manager.config_file.with_suffix('.tmp')
        assert not temp_file.exists()

        assert config_manager.config_file.exists()

    def test_config_file_format(self, config_manager, sample_mods):
        """Saved config should be properly formatted JSON."""
        fm_root = "/test/path"
        profiles = [{'name': 'Default', 'mods': sample_mods}]
        config_manager.save(fm_root, profiles, 'Default')

        with open(config_manager.config_file, 'r') as f:
            data = json.load(f)

        assert 'fm_root_path' in data
        assert 'profiles' in data
        assert 'current_profile' in data
        assert data['fm_root_path'] == fm_root
        assert isinstance(data['profiles'], list)
        assert len(data['profiles'][0]['mods']) == 2

    def test_save_preserves_mod_data_structure(self, config_manager, sample_mods):
        """All mod data fields should be preserved."""
        profiles = [{'name': 'Default', 'mods': sample_mods}]
        config_manager.save("/path", profiles, 'Default')

        _, loaded_mods, loaded_profiles, _ = config_manager.load()

        original = sample_mods[0]
        loaded = loaded_profiles[0]['mods'][0]

        assert loaded['name'] == original['name']
        assert loaded['enabled'] == original['enabled']
        assert loaded['files'] == original['files']
        assert loaded['file_paths'] == original['file_paths']
        assert loaded['added_date'] == original['added_date']

    @pytest.mark.parametrize("mod_count", [0, 1, 5, 10, 50])
    def test_save_load_various_mod_counts(self, config_manager, mod_count):
        """Test saving and loading various numbers of mods."""
        mods = [
            {
                'name': f'Mod {i}',
                'enabled': i % 2 == 0,
                'files': [f'file{i}.bundle'],
                'file_paths': {},
                'added_date': '2024-01-01T00:00:00'
            }
            for i in range(mod_count)
        ]

        profiles = [{'name': 'Default', 'mods': mods}]
        success = config_manager.save("/path", profiles, 'Default')
        assert success is True

        _, loaded_mods, loaded_profiles, _ = config_manager.load()
        assert len(loaded_profiles[0]['mods']) == mod_count

    def test_config_json_is_indented(self, config_manager, sample_mods):
        """Config JSON should be formatted with indentation for readability."""
        profiles = [{'name': 'Default', 'mods': sample_mods}]
        config_manager.save("/path", profiles, 'Default')

        content = config_manager.config_file.read_text()

        assert '\n' in content
        assert '  ' in content

    def test_load_empty_mods_array(self, config_manager):
        """Config with empty mods array should load correctly (old format)."""
        data = {'fm_root_path': '/test/path', 'mods': []}
        config_manager.config_file.write_text(json.dumps(data))

        fm_root, mods, profiles, current_profile = config_manager.load()

        assert fm_root == '/test/path'
        assert mods == []
        assert len(profiles) == 1
        assert profiles[0]['mods'] == []

    def test_load_missing_mods_key(self, config_manager):
        """Config without mods or profiles key should default to empty array."""
        data = {'fm_root_path': '/test/path'}
        config_manager.config_file.write_text(json.dumps(data))

        fm_root, mods, profiles, current_profile = config_manager.load()

        assert fm_root == '/test/path'
        assert mods == []
        assert len(profiles) == 1
        assert profiles[0]['mods'] == []
