import pytest
from src.core.profile_manager import ProfileManager


class TestProfileManager:
    """Test profile management functionality."""

    @pytest.fixture
    def profile_manager(self):
        """Create a fresh ProfileManager instance."""
        return ProfileManager()

    @pytest.fixture
    def sample_mods(self):
        """Sample mod data for testing."""
        return [
            {
                'name': 'Graphics Mod',
                'enabled': True,
                'files': ['ui.bundle', 'graphics.bundle'],
                'file_paths': {
                    'ui.bundle': '/storage/Graphics Mod/ui.bundle',
                    'graphics.bundle': '/storage/Graphics Mod/graphics.bundle'
                },
                'added_date': '2024-01-15T10:30:00'
            },
            {
                'name': 'Tactics Mod',
                'enabled': False,
                'files': ['tactics.bundle'],
                'file_paths': {'tactics.bundle': '/storage/Tactics Mod/tactics.bundle'},
                'added_date': '2024-01-16T14:20:00'
            }
        ]

    # Profile Creation Tests
    def test_create_profile_success(self, profile_manager):
        """Should successfully create a new profile."""
        result = profile_manager.create_profile("Gaming")

        assert result is True
        assert len(profile_manager.profiles) == 1
        assert profile_manager.profiles[0]['name'] == "Gaming"
        assert profile_manager.profiles[0]['mods'] == []

    def test_create_duplicate_profile_fails(self, profile_manager):
        """Should fail when creating duplicate profile name."""
        profile_manager.create_profile("Gaming")
        result = profile_manager.create_profile("Gaming")

        assert result is False
        assert len(profile_manager.profiles) == 1

    def test_create_multiple_profiles(self, profile_manager):
        """Should create multiple profiles successfully."""
        profile_manager.create_profile("Default")
        profile_manager.create_profile("Testing")
        profile_manager.create_profile("Vanilla")

        assert len(profile_manager.profiles) == 3
        assert profile_manager.get_profile_names() == ["Default", "Testing", "Vanilla"]

    # Profile Deletion Tests
    def test_delete_profile_success(self, profile_manager):
        """Should successfully delete a non-current profile."""
        profile_manager.create_profile("Default")
        profile_manager.create_profile("ToDelete")
        profile_manager.current_profile = "Default"

        result = profile_manager.delete_profile("ToDelete")

        assert result is True
        assert len(profile_manager.profiles) == 1
        assert profile_manager.get_profile("ToDelete") is None

    def test_delete_current_profile_fails(self, profile_manager):
        """Should not allow deleting the currently active profile."""
        profile_manager.create_profile("Active")
        profile_manager.current_profile = "Active"

        result = profile_manager.delete_profile("Active")

        assert result is False
        assert len(profile_manager.profiles) == 1

    def test_delete_nonexistent_profile_fails(self, profile_manager):
        """Should fail when deleting non-existent profile."""
        result = profile_manager.delete_profile("DoesNotExist")

        assert result is False

    # Profile Switching Tests
    def test_switch_profile_success(self, profile_manager):
        """Should successfully switch to existing profile."""
        profile_manager.create_profile("Profile1")
        profile_manager.create_profile("Profile2")
        profile_manager.current_profile = "Profile1"

        result = profile_manager.switch_profile("Profile2")

        assert result is True
        assert profile_manager.current_profile == "Profile2"

    def test_switch_to_nonexistent_profile_fails(self, profile_manager):
        """Should fail when switching to non-existent profile."""
        profile_manager.create_profile("Profile1")
        profile_manager.current_profile = "Profile1"

        result = profile_manager.switch_profile("DoesNotExist")

        assert result is False
        assert profile_manager.current_profile == "Profile1"

    # Profile Renaming Tests
    def test_rename_profile_success(self, profile_manager):
        """Should successfully rename a profile."""
        profile_manager.create_profile("OldName")

        result = profile_manager.rename_profile("OldName", "NewName")

        assert result is True
        assert profile_manager.get_profile("OldName") is None
        assert profile_manager.get_profile("NewName") is not None

    def test_rename_current_profile_updates_current(self, profile_manager):
        """Should update current_profile when renaming active profile."""
        profile_manager.create_profile("OldName")
        profile_manager.current_profile = "OldName"

        result = profile_manager.rename_profile("OldName", "NewName")

        assert result is True
        assert profile_manager.current_profile == "NewName"

    def test_rename_to_existing_name_fails(self, profile_manager):
        """Should fail when renaming to an existing profile name."""
        profile_manager.create_profile("Profile1")
        profile_manager.create_profile("Profile2")

        result = profile_manager.rename_profile("Profile1", "Profile2")

        assert result is False
        assert profile_manager.get_profile("Profile1") is not None

    def test_rename_nonexistent_profile_fails(self, profile_manager):
        """Should fail when renaming non-existent profile."""
        result = profile_manager.rename_profile("DoesNotExist", "NewName")

        assert result is False

    # Mod Management Tests
    def test_get_current_profile_mods(self, profile_manager, sample_mods):
        """Should return mods for current profile."""
        profile_manager.create_profile("Default")
        profile_manager.current_profile = "Default"
        profile_manager.profiles[0]['mods'] = sample_mods

        mods = profile_manager.get_current_profile_mods()

        assert len(mods) == 2
        assert mods[0]['name'] == 'Graphics Mod'

    def test_get_current_profile_mods_when_not_found(self, profile_manager):
        """Should return empty list if current profile doesn't exist."""
        profile_manager.current_profile = "NonExistent"

        mods = profile_manager.get_current_profile_mods()

        assert mods == []

    def test_set_current_profile_mods(self, profile_manager, sample_mods):
        """Should update mods for current profile."""
        profile_manager.create_profile("Default")
        profile_manager.current_profile = "Default"

        profile_manager.set_current_profile_mods(sample_mods)

        assert len(profile_manager.profiles[0]['mods']) == 2
        assert profile_manager.profiles[0]['mods'][0]['name'] == 'Graphics Mod'

    def test_set_current_profile_mods_when_not_found(self, profile_manager, sample_mods):
        """Should not crash when setting mods for non-existent profile."""
        profile_manager.current_profile = "NonExistent"

        # Should not raise exception
        profile_manager.set_current_profile_mods(sample_mods)

    # Profile Isolation Tests
    def test_profiles_have_independent_mods(self, profile_manager, sample_mods):
        """Each profile should maintain its own independent mod list."""
        profile_manager.create_profile("Profile1")
        profile_manager.create_profile("Profile2")

        profile_manager.current_profile = "Profile1"
        profile_manager.set_current_profile_mods(sample_mods)

        profile_manager.current_profile = "Profile2"
        profile_manager.set_current_profile_mods([sample_mods[0]])  # Only one mod

        # Check Profile1 still has both mods
        profile1_mods = profile_manager.get_profile("Profile1")['mods']
        assert len(profile1_mods) == 2

        # Check Profile2 has only one mod
        profile2_mods = profile_manager.get_profile("Profile2")['mods']
        assert len(profile2_mods) == 1

    def test_switching_profiles_doesnt_lose_data(self, profile_manager, sample_mods):
        """Switching between profiles should preserve each profile's mods."""
        profile_manager.create_profile("Profile1")
        profile_manager.create_profile("Profile2")

        # Set up Profile1
        profile_manager.current_profile = "Profile1"
        profile_manager.set_current_profile_mods(sample_mods)

        # Switch to Profile2 and set different mods
        profile_manager.switch_profile("Profile2")
        profile_manager.set_current_profile_mods([])

        # Switch back to Profile1
        profile_manager.switch_profile("Profile1")
        mods = profile_manager.get_current_profile_mods()

        assert len(mods) == 2
        assert mods[0]['name'] == 'Graphics Mod'

    # Edge Cases
    def test_get_profile_names_empty(self, profile_manager):
        """Should return empty list when no profiles exist."""
        assert profile_manager.get_profile_names() == []

    def test_get_profile_returns_none_for_nonexistent(self, profile_manager):
        """Should return None for non-existent profile."""
        assert profile_manager.get_profile("DoesNotExist") is None

    @pytest.mark.parametrize("profile_name", [
        "Default",
        "My Gaming Profile",
        "Profile_123",
        "测试配置",  # Unicode
        "Profile!@#",
    ])
    def test_create_profile_with_various_names(self, profile_manager, profile_name):
        """Should handle various profile name formats."""
        result = profile_manager.create_profile(profile_name)

        assert result is True
        assert profile_manager.get_profile(profile_name) is not None
