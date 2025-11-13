"""Game update detection and recovery management."""

import hashlib
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime


class UpdateDetector:
    """Detects game updates and manages recovery."""

    def __init__(self, data_path: Path):
        """
        Initialize update detector.

        Args:
            data_path: Path to game data directory
        """
        self.data_path = Path(data_path)
        self.game_fingerprint_file = ".game_fingerprint"

    def calculate_game_fingerprint(self) -> Optional[str]:
        """
        Calculate a fingerprint of the game installation.

        Uses key game files to detect if the game has been updated.
        Returns a hash that changes when the game is patched.

        Returns:
            Fingerprint string or None if unable to calculate
        """
        try:
            # Key files that would change during an update
            key_files = []

            # Look for common FM data files
            patterns = ['*.dbc', '*.lnc', '*.ltc']
            for pattern in patterns:
                key_files.extend(list(self.data_path.glob(pattern))[:5])  # Sample 5 of each type

            if not key_files:
                return None

            # Create fingerprint from file sizes and modification times
            fingerprint_data = []
            for file_path in sorted(key_files):
                if file_path.exists():
                    stat = file_path.stat()
                    fingerprint_data.append(f"{file_path.name}:{stat.st_size}:{stat.st_mtime}")

            if not fingerprint_data:
                return None

            # Hash the collected data
            fingerprint_str = "|".join(fingerprint_data)
            return hashlib.sha256(fingerprint_str.encode()).hexdigest()

        except Exception:
            return None

    def get_stored_fingerprint(self, backup_dir: Path) -> Optional[Dict]:
        """
        Get the stored game fingerprint from backup directory.

        Args:
            backup_dir: Backup directory path

        Returns:
            Dictionary with fingerprint data or None
        """
        fingerprint_file = backup_dir / self.game_fingerprint_file
        if not fingerprint_file.exists():
            return None

        try:
            import json
            with open(fingerprint_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def store_fingerprint(self, backup_dir: Path, fingerprint: str) -> bool:
        """
        Store the current game fingerprint.

        Args:
            backup_dir: Backup directory path
            fingerprint: Fingerprint to store

        Returns:
            True if successful
        """
        fingerprint_file = backup_dir / self.game_fingerprint_file
        try:
            import json
            data = {
                'fingerprint': fingerprint,
                'timestamp': datetime.now().isoformat(),
                'data_path': str(self.data_path)
            }
            with open(fingerprint_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def detect_update(self, backup_dir: Path) -> Tuple[bool, Optional[str]]:
        """
        Detect if the game has been updated.

        Args:
            backup_dir: Backup directory path

        Returns:
            Tuple of (update_detected, message)
        """
        current_fingerprint = self.calculate_game_fingerprint()
        if not current_fingerprint:
            return False, "Unable to calculate game fingerprint"

        stored_data = self.get_stored_fingerprint(backup_dir)

        # First time - store fingerprint
        if not stored_data:
            self.store_fingerprint(backup_dir, current_fingerprint)
            return False, "Game fingerprint initialized"

        stored_fingerprint = stored_data.get('fingerprint')
        if stored_fingerprint != current_fingerprint:
            timestamp = stored_data.get('timestamp', 'unknown')
            return True, f"Game update detected (last known state: {timestamp})"

        return False, "No update detected"

    def clear_fingerprint(self, backup_dir: Path) -> bool:
        """
        Clear the stored fingerprint.

        Args:
            backup_dir: Backup directory path

        Returns:
            True if successful
        """
        fingerprint_file = backup_dir / self.game_fingerprint_file
        try:
            if fingerprint_file.exists():
                fingerprint_file.unlink()
            return True
        except Exception:
            return False
