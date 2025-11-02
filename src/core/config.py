import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional


class ConfigManager:
    """Manages persistent configuration with atomic writes."""

    def __init__(self, config_file: Path):
        """
        Initialize config manager.

        Args:
            config_file: Path to config JSON file
        """
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> tuple[Optional[str], List[Dict], List[Dict], str]:
        """
        Load configuration from disk with error recovery.

        Returns:
            Tuple of (fm_root_path, mods_list, profiles_list, current_profile)
        """
        if not self.config_file.exists():
            return None, [], [{'name': 'Default', 'mods': []}], 'Default'

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                fm_root_path = data.get('fm_root_path')

                # Handle old config format (pre-profiles)
                if 'profiles' not in data:
                    mods = data.get('mods', [])
                    profiles = [{'name': 'Default', 'mods': mods}]
                    current_profile = 'Default'
                else:
                    profiles = data.get('profiles', [{'name': 'Default', 'mods': []}])
                    current_profile = data.get('current_profile', 'Default')
                    mods = []  # Mods are now stored in profiles

                return fm_root_path, mods, profiles, current_profile

        except (json.JSONDecodeError, Exception):
            return None, [], [{'name': 'Default', 'mods': []}], 'Default'

    def save(self, fm_root_path: Optional[str], profiles: List[Dict], current_profile: str) -> bool:
        """
        Save configuration with atomic write.

        Uses temp file + rename for atomic operation to prevent corruption.

        Args:
            fm_root_path: Path to FM26 root folder
            profiles: List of profile dictionaries
            current_profile: Name of the currently active profile

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'fm_root_path': fm_root_path,
                'profiles': profiles,
                'current_profile': current_profile
            }

            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            if temp_file.exists():
                shutil.move(str(temp_file), str(self.config_file))

            return True

        except Exception:
            return False
