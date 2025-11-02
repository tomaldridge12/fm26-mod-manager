"""Profile management for mod configurations."""
from typing import List, Dict, Optional


class ProfileManager:
    """Manages multiple mod configuration profiles."""

    def __init__(self):
        """Initialize profile manager."""
        self.profiles: List[Dict] = []
        self.current_profile: str = "Default"

    def create_profile(self, name: str) -> bool:
        """
        Create a new profile.

        Args:
            name: Name for the new profile

        Returns:
            True if created successfully, False if already exists
        """
        if any(p['name'] == name for p in self.profiles):
            return False

        self.profiles.append({
            'name': name,
            'mods': []  # Each profile has its own mod list with enabled states
        })
        return True

    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.

        Args:
            name: Name of profile to delete

        Returns:
            True if deleted successfully, False if not found or is current profile
        """
        if name == self.current_profile:
            return False

        profile = self.get_profile(name)
        if not profile:
            return False

        self.profiles.remove(profile)
        return True

    def get_profile(self, name: str) -> Optional[Dict]:
        """Get profile by name."""
        return next((p for p in self.profiles if p['name'] == name), None)

    def get_profile_names(self) -> List[str]:
        """Get list of all profile names."""
        return [p['name'] for p in self.profiles]

    def switch_profile(self, name: str) -> bool:
        """
        Switch to a different profile.

        Args:
            name: Name of profile to switch to

        Returns:
            True if switched successfully, False if profile not found
        """
        if not self.get_profile(name):
            return False

        self.current_profile = name
        return True

    def get_current_profile_mods(self) -> List[Dict]:
        """Get mods for the current profile."""
        profile = self.get_profile(self.current_profile)
        if not profile:
            return []
        return profile['mods']

    def set_current_profile_mods(self, mods: List[Dict]) -> None:
        """Set mods for the current profile."""
        profile = self.get_profile(self.current_profile)
        if profile:
            profile['mods'] = mods

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """
        Rename a profile.

        Args:
            old_name: Current name of profile
            new_name: New name for profile

        Returns:
            True if renamed successfully, False otherwise
        """
        if any(p['name'] == new_name for p in self.profiles):
            return False

        profile = self.get_profile(old_name)
        if not profile:
            return False

        profile['name'] = new_name
        if self.current_profile == old_name:
            self.current_profile = new_name

        return True
