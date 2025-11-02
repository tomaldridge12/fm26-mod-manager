import pytest
import json
from pathlib import Path
from src.core.config import ConfigManager


class TestConfigManagerWithProfiles:
    """Test configuration manager with profile support."""

    @pytest.fixture
    def config_manager(self, tmp_path):
        """Create config manager with temp file."""
        config_file = tmp_path / "config.json"
        return ConfigManager(config_file)

    @pytest.fixture
    def sample_mods(self):
        """Sample mod data."""
        return [
            {
                'name': 'Graphics Mod',
                'enabled': True,
                'files': ['ui.bundle'],
                'file_paths': {'ui.bundle': '/path/to/ui.bundle'},
                'added_date': '2024-01-15T10:30:00'
            },
            {
                'name': 'Tactics Mod',
                'enabled': False,
                'files': ['tactics.bundle'],
                'file_paths': {'tactics.bundle': '/path/to/tactics.bundle'},
                'added_date': '2024-01-16T14:20:00'
            }
        ]

    @pytest.fixture
    def sample_profiles(self, sample_mods):
        """Sample profile data."""
        return [
            {'name': 'Default', 'mods': sample_mods},
            {'name': 'Testing', 'mods': []},
            {'name': 'Vanilla', 'mods': [sample_mods[0]]}
        ]

    # Profile Save/Load Tests
    def test_save_and_load_single_profile(self, config_manager, sample_mods):
        """Should save and load single profile configuration."""
        fm_root = "/path/to/fm26"
        profiles = [{'name': 'Default', 'mods': sample_mods}]
        current_profile = 'Default'

        success = config_manager.save(fm_root, profiles, current_profile)
        assert success is True

        loaded_root, loaded_mods, loaded_profiles, loaded_current = config_manager.load()

        assert loaded_root == fm_root
        assert loaded_current == 'Default'
        assert len(loaded_profiles) == 1
        assert loaded_profiles[0]['name'] == 'Default'
        assert len(loaded_profiles[0]['mods']) == 2

    def test_save_and_load_multiple_profiles(self, config_manager, sample_profiles):
        """Should save and load multiple profiles."""
        fm_root = "/path/to/fm26"
        current_profile = 'Testing'

        config_manager.save(fm_root, sample_profiles, current_profile)

        _, _, loaded_profiles, loaded_current = config_manager.load()

        assert len(loaded_profiles) == 3
        assert loaded_current == 'Testing'
        assert loaded_profiles[0]['name'] == 'Default'
        assert loaded_profiles[1]['name'] == 'Testing'
        assert loaded_profiles[2]['name'] == 'Vanilla'

    def test_save_overwrites_profiles(self, config_manager, sample_profiles):
        """Saving should completely overwrite existing profiles."""
        config_manager.save("/path", sample_profiles, 'Default')

        new_profiles = [{'name': 'NewProfile', 'mods': []}]
        config_manager.save("/path", new_profiles, 'NewProfile')

        _, _, loaded_profiles, loaded_current = config_manager.load()

        assert len(loaded_profiles) == 1
        assert loaded_profiles[0]['name'] == 'NewProfile'
        assert loaded_current == 'NewProfile'

    # Backward Compatibility Tests
    def test_load_old_config_format_without_profiles(self, config_manager, sample_mods):
        """Should migrate old config format to profiles."""
        # Write old format config
        old_data = {
            'fm_root_path': '/path/to/fm26',
            'mods': sample_mods
        }
        config_manager.config_file.write_text(json.dumps(old_data))

        loaded_root, loaded_mods, loaded_profiles, loaded_current = config_manager.load()

        # Should create Default profile with old mods
        assert loaded_root == '/path/to/fm26'
        assert loaded_current == 'Default'
        assert len(loaded_profiles) == 1
        assert loaded_profiles[0]['name'] == 'Default'
        assert len(loaded_profiles[0]['mods']) == 2
        # Old format returns mods for backward compatibility
        assert len(loaded_mods) == 2
        assert loaded_mods[0]['name'] == 'Graphics Mod'

    def test_old_format_preserves_all_mod_data(self, config_manager, sample_mods):
        """Migrating old format should preserve all mod fields."""
        old_data = {
            'fm_root_path': '/path/to/fm26',
            'mods': sample_mods
        }
        config_manager.config_file.write_text(json.dumps(old_data))

        _, _, loaded_profiles, _ = config_manager.load()

        migrated_mods = loaded_profiles[0]['mods']
        assert migrated_mods[0]['name'] == sample_mods[0]['name']
        assert migrated_mods[0]['enabled'] == sample_mods[0]['enabled']
        assert migrated_mods[0]['files'] == sample_mods[0]['files']
        assert migrated_mods[0]['file_paths'] == sample_mods[0]['file_paths']
        assert migrated_mods[0]['added_date'] == sample_mods[0]['added_date']

    # Profile Data Integrity Tests
    def test_profile_mods_independence(self, config_manager, sample_mods):
        """Each profile should maintain independent mod lists."""
        profiles = [
            {'name': 'Profile1', 'mods': [sample_mods[0]]},
            {'name': 'Profile2', 'mods': sample_mods}
        ]

        config_manager.save("/path", profiles, 'Profile1')

        _, _, loaded_profiles, _ = config_manager.load()

        assert len(loaded_profiles[0]['mods']) == 1
        assert len(loaded_profiles[1]['mods']) == 2

    def test_profile_with_no_mods(self, config_manager):
        """Should handle profiles with empty mod lists."""
        profiles = [
            {'name': 'Empty', 'mods': []},
            {'name': 'AlsoEmpty', 'mods': []}
        ]

        config_manager.save("/path", profiles, 'Empty')

        _, _, loaded_profiles, _ = config_manager.load()

        assert len(loaded_profiles[0]['mods']) == 0
        assert len(loaded_profiles[1]['mods']) == 0

    # Current Profile Tests
    def test_save_and_load_current_profile(self, config_manager, sample_profiles):
        """Should preserve current profile selection."""
        config_manager.save("/path", sample_profiles, 'Vanilla')

        _, _, _, loaded_current = config_manager.load()

        assert loaded_current == 'Vanilla'

    def test_change_current_profile(self, config_manager, sample_profiles):
        """Should update current profile on save."""
        config_manager.save("/path", sample_profiles, 'Default')
        config_manager.save("/path", sample_profiles, 'Testing')

        _, _, _, loaded_current = config_manager.load()

        assert loaded_current == 'Testing'

    # JSON Format Tests
    def test_profile_config_format(self, config_manager, sample_profiles):
        """Saved config should have correct JSON structure."""
        config_manager.save("/path", sample_profiles, 'Default')

        with open(config_manager.config_file, 'r') as f:
            data = json.load(f)

        assert 'fm_root_path' in data
        assert 'profiles' in data
        assert 'current_profile' in data
        assert isinstance(data['profiles'], list)
        assert data['current_profile'] == 'Default'

    def test_profile_structure_in_json(self, config_manager, sample_mods):
        """Each profile should have correct structure in JSON."""
        profiles = [{'name': 'Test', 'mods': sample_mods}]
        config_manager.save("/path", profiles, 'Test')

        with open(config_manager.config_file, 'r') as f:
            data = json.load(f)

        profile = data['profiles'][0]
        assert 'name' in profile
        assert 'mods' in profile
        assert profile['name'] == 'Test'
        assert isinstance(profile['mods'], list)

    # Error Recovery Tests
    def test_load_corrupted_profile_data(self, config_manager):
        """Should return defaults for corrupted profile data."""
        config_manager.config_file.write_text("{ invalid json }")

        fm_root, mods, profiles, current = config_manager.load()

        assert fm_root is None
        assert mods == []
        assert len(profiles) == 1
        assert profiles[0]['name'] == 'Default'
        assert current == 'Default'

    def test_load_missing_profiles_key(self, config_manager):
        """Should handle config missing profiles key."""
        data = {'fm_root_path': '/path'}
        config_manager.config_file.write_text(json.dumps(data))

        _, _, loaded_profiles, loaded_current = config_manager.load()

        assert len(loaded_profiles) == 1
        assert loaded_profiles[0]['name'] == 'Default'
        assert loaded_current == 'Default'

    def test_load_missing_current_profile_key(self, config_manager):
        """Should default to 'Default' if current_profile missing."""
        data = {
            'fm_root_path': '/path',
            'profiles': [{'name': 'Test', 'mods': []}]
        }
        config_manager.config_file.write_text(json.dumps(data))

        _, _, _, loaded_current = config_manager.load()

        assert loaded_current == 'Default'

    # Edge Cases
    @pytest.mark.parametrize("profile_count", [0, 1, 5, 10])
    def test_various_profile_counts(self, config_manager, profile_count):
        """Should handle various numbers of profiles."""
        profiles = [
            {'name': f'Profile{i}', 'mods': []}
            for i in range(profile_count)
        ]

        if profile_count > 0:
            config_manager.save("/path", profiles, profiles[0]['name'])

            _, _, loaded_profiles, _ = config_manager.load()

            assert len(loaded_profiles) == profile_count

    def test_profile_with_special_characters(self, config_manager):
        """Should handle profile names with special characters."""
        profiles = [
            {'name': 'Test Profile!@#', 'mods': []},
            {'name': '测试配置', 'mods': []},
            {'name': 'Profile_123', 'mods': []}
        ]

        config_manager.save("/path", profiles, 'Test Profile!@#')

        _, _, loaded_profiles, loaded_current = config_manager.load()

        assert len(loaded_profiles) == 3
        assert loaded_current == 'Test Profile!@#'
        assert loaded_profiles[1]['name'] == '测试配置'

    def test_atomic_write_with_profiles(self, config_manager, sample_profiles):
        """Atomic write should work with profiles."""
        config_manager.save("/path", sample_profiles, 'Default')

        # Temp file should be cleaned up
        temp_file = config_manager.config_file.with_suffix('.tmp')
        assert not temp_file.exists()
        assert config_manager.config_file.exists()
