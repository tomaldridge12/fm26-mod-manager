"""
Backup and restore operations for game files.

Implements space-efficient selective backup strategy that only backs up
files actually being modified by mods.
"""

import shutil
from pathlib import Path
from typing import List, Tuple, Optional


class BackupManager:
    """Manages selective backup and restore of original game files."""

    def __init__(self, backup_dir: Path, data_path: str):
        """
        Initialize backup manager.

        Args:
            backup_dir: Directory for storing backups
            data_path: Path to game data folder containing .bundle files
        """
        self.backup_dir = Path(backup_dir)
        self.data_path = Path(data_path)
        self.original_backup_dir = self.backup_dir / "original"
        self.original_backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_files(self, file_names: List[str]) -> Tuple[int, List[str]]:
        """
        Backup specific files before modification (space-efficient selective backup).

        Only backs up files that don't already have backups, avoiding duplicates
        and saving space.

        Args:
            file_names: List of bundle file names to backup

        Returns:
            Tuple of (backed_up_count, failed_files_list)
        """
        backed_up = 0
        failed_files = []

        for file_name in file_names:
            source = self.data_path / file_name
            dest = self.original_backup_dir / file_name

            # Skip if already backed up (preserve first backup)
            if dest.exists():
                continue

            # Skip if source doesn't exist (mod might add new files)
            if not source.exists():
                continue

            try:
                shutil.copy2(source, dest)
                backed_up += 1
            except Exception as e:
                failed_files.append(f"{file_name} ({str(e)})")

        return backed_up, failed_files

    def restore_files(self, file_names: List[str]) -> Tuple[bool, List[str], List[str]]:
        """
        Restore specific files from backup.

        Args:
            file_names: List of bundle file names to restore

        Returns:
            Tuple of (success, missing_backups, failed_restores)
        """
        missing_backups = []
        failed_restores = []

        for file_name in file_names:
            backup_file = self.original_backup_dir / file_name

            if not backup_file.exists():
                missing_backups.append(file_name)
                continue

            try:
                dest = self.data_path / file_name
                shutil.copy2(backup_file, dest)
            except Exception as e:
                failed_restores.append(f"{file_name} ({str(e)})")

        success = len(missing_backups) == 0 and len(failed_restores) == 0
        return success, missing_backups, failed_restores

    def restore_all(self) -> Tuple[int, List[str]]:
        """
        Restore all backed up files.

        Returns:
            Tuple of (restored_count, failed_files_list)
        """
        restored = 0
        failed_files = []

        for backup_file in self.original_backup_dir.glob("*.bundle"):
            try:
                dest = self.data_path / backup_file.name
                shutil.copy2(backup_file, dest)
                restored += 1
            except Exception as e:
                failed_files.append(f"{backup_file.name} ({str(e)})")

        return restored, failed_files

    def get_backup_count(self) -> int:
        """Get count of backed up files."""
        return len(list(self.original_backup_dir.glob("*.bundle")))

    def has_backups(self) -> bool:
        """Check if any backups exist."""
        return self.original_backup_dir.exists() and self.get_backup_count() > 0
