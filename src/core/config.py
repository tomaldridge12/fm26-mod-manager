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

    def load(self) -> tuple[Optional[str], List[Dict]]:
        """
        Load configuration from disk with error recovery.

        Returns:
            Tuple of (fm_root_path, mods_list)
        """
        if not self.config_file.exists():
            return None, []

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                fm_root_path = data.get('fm_root_path')
                mods = data.get('mods', [])
                return fm_root_path, mods

        except (json.JSONDecodeError, Exception):
            return None, []

    def save(self, fm_root_path: Optional[str], mods: List[Dict]) -> bool:
        """
        Save configuration with atomic write.

        Uses temp file + rename for atomic operation to prevent corruption.

        Args:
            fm_root_path: Path to FM26 root folder
            mods: List of mod metadata dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'fm_root_path': fm_root_path,
                'mods': mods
            }

            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            if temp_file.exists():
                shutil.move(str(temp_file), str(self.config_file))

            return True

        except Exception:
            return False
