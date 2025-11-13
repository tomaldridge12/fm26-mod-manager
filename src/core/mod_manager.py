import shutil
import zipfile
import rarfile
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class ModManager:
    """Manages mod installation, tracking, and conflict detection."""

    def __init__(self, mod_storage_dir: Path):
        """
        Initialize mod manager.

        Args:
            mod_storage_dir: Directory for storing mod files
        """
        self.mod_storage_dir = Path(mod_storage_dir)
        self.mod_storage_dir.mkdir(parents=True, exist_ok=True)
        self.mods: List[Dict] = []
        self._setup_rar_tool()

    def _setup_rar_tool(self):
        """Configure rarfile library to find unrar executable."""
        import platform
        import os

        system = platform.system()

        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\WinRAR\UnRAR.exe",
                r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'WinRAR', 'UnRAR.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'WinRAR', 'UnRAR.exe'),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    rarfile.UNRAR_TOOL = path
                    return

            rarfile.UNRAR_TOOL = "unrar"

        elif system == "Darwin":
            homebrew_path = "/opt/homebrew/bin/unrar"
            if os.path.exists(homebrew_path):
                rarfile.UNRAR_TOOL = homebrew_path
            else:
                rarfile.UNRAR_TOOL = "unrar"
        else:
            rarfile.UNRAR_TOOL = "unrar"

    def extract_mod(self, archive_path: str, mod_name: str, temp_dir: Path) -> Tuple[bool, Optional[List[Path]], Optional[str], Optional[str]]:
        """
        Extract mod archive and find bundle files.

        Args:
            archive_path: Path to mod archive file
            mod_name: Name for this mod
            temp_dir: Temporary extraction directory

        Returns:
            Tuple of (success, bundle_files_list, error_message, traceback_str)
        """
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)

            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            elif archive_path.endswith('.rar'):
                try:
                    with rarfile.RarFile(archive_path, 'r') as rar_ref:
                        rar_ref.extractall(temp_dir)
                except rarfile.RarCannotExec as e:
                    error_msg = (
                        "RAR extraction tool not found.\n\n"
                        "To extract RAR files, please install:\n\n"
                        "Windows: Download and install WinRAR from https://www.win-rar.com/\n"
                        "macOS: Run 'brew install unrar' in Terminal\n\n"
                        "Alternatively, extract the RAR file manually and create a ZIP archive instead."
                    )
                    return False, None, error_msg, traceback.format_exc()
            else:
                return False, None, "Only ZIP and RAR archives are supported.", None

            bundle_files = list(temp_dir.rglob("*.bundle"))

            if not bundle_files:
                return False, None, (
                    "No .bundle files found in the archive.\n\n"
                    "Please ensure the archive contains FM26 mod files."
                ), None

            return True, bundle_files, None, None

        except Exception as e:
            return False, None, f"Could not extract the archive:\n\n{str(e)}", traceback.format_exc()

    def install_mod(self, mod_name: str, bundle_files: List[Path]) -> Tuple[bool, Optional[str]]:
        """
        Copy mod files to permanent storage.

        Args:
            mod_name: Name of the mod
            bundle_files: List of extracted bundle file paths

        Returns:
            Tuple of (success, error_message)
        """
        try:
            mod_storage = self.mod_storage_dir / mod_name
            if mod_storage.exists():
                shutil.rmtree(mod_storage)
            mod_storage.mkdir(parents=True, exist_ok=True)

            for bundle_file in bundle_files:
                shutil.copy2(bundle_file, mod_storage / bundle_file.name)

            return True, None

        except Exception as e:
            return False, str(e)

    def create_mod_entry(self, mod_name: str, bundle_files: List[Path]) -> Dict:
        """
        Create mod metadata entry.

        Args:
            mod_name: Name of the mod
            bundle_files: List of bundle files

        Returns:
            Mod metadata dictionary
        """
        mod_storage = self.mod_storage_dir / mod_name

        # Auto-detect tags based on mod name and file types
        auto_tags = self._auto_detect_tags(mod_name, bundle_files)

        # Calculate total size of mod files
        total_size = self._calculate_mod_size(mod_storage, bundle_files)

        return {
            'name': mod_name,
            'enabled': False,
            'files': [f.name for f in bundle_files],
            'file_paths': {f.name: str(mod_storage / f.name) for f in bundle_files},
            'added_date': datetime.now().isoformat(),
            'tags': auto_tags,
            'load_order': 100,  # Default load order (100 is neutral)
            'size_bytes': total_size
        }

    def _calculate_mod_size(self, mod_storage: Path, bundle_files: List[Path]) -> int:
        """
        Calculate total size of mod files in bytes.

        Args:
            mod_storage: Mod storage directory
            bundle_files: List of bundle files

        Returns:
            Total size in bytes
        """
        total_size = 0
        for bundle_file in bundle_files:
            file_path = mod_storage / bundle_file.name
            if file_path.exists():
                total_size += file_path.stat().st_size
        return total_size

    def _auto_detect_tags(self, mod_name: str, bundle_files: List[Path]) -> List[str]:
        """
        Auto-detect tags based on mod name and files.

        Args:
            mod_name: Name of the mod
            bundle_files: List of bundle files

        Returns:
            List of detected tags
        """
        tags = []
        mod_name_lower = mod_name.lower()

        # Common tag patterns
        tag_patterns = {
            'Graphics': ['graphic', 'logo', 'kit', 'face', 'skin', 'stadium', 'background'],
            'Database': ['database', 'data', 'db', 'editor', 'league', 'nation', 'player'],
            'Gameplay': ['gameplay', 'balance', 'realism', 'difficulty', 'ai'],
            'Faces': ['face', 'facepack', 'facegen', 'portrait'],
            'Logos': ['logo', 'badge', 'emblem', 'crest'],
            'Kits': ['kit', 'uniform', 'jersey'],
            'Tactics': ['tactic', 'formation', 'strategy'],
            'Wonderkids': ['wonderkid', 'newgen', 'regen'],
            'Transfers': ['transfer', 'contract', 'wage'],
            'UI': ['ui', 'interface', 'skin', 'panel']
        }

        for tag, patterns in tag_patterns.items():
            if any(pattern in mod_name_lower for pattern in patterns):
                tags.append(tag)

        # Default tag if nothing detected
        if not tags:
            tags.append('Other')

        return tags

    def check_conflicts(self, file_names: List[str]) -> Dict[str, str]:
        """
        Check if files conflict with currently enabled mods.

        Args:
            file_names: List of bundle file names to check

        Returns:
            Dictionary mapping conflicting files to mod names
        """
        conflicts = {}
        for mod in self.mods:
            if mod['enabled']:
                for file_name in file_names:
                    if file_name in mod['files']:
                        conflicts[file_name] = mod['name']
        return conflicts

    def enable_mod(self, mod: Dict, data_path: Path) -> Tuple[bool, List[str], Optional[str]]:
        """
        Copy mod files to game directory.

        Args:
            mod: Mod metadata dictionary
            data_path: Path to game data folder

        Returns:
            Tuple of (success, copied_files_list, error_message)
        """
        copied_files = []

        try:
            for file_name, file_path in mod['file_paths'].items():
                if not Path(file_path).exists():
                    return False, copied_files, f"Mod file missing: {file_name}"

                dest = data_path / file_name
                shutil.copy2(file_path, dest)
                copied_files.append(file_name)

            return True, copied_files, None

        except Exception as e:
            return False, copied_files, str(e)

    def validate_mod_name(self, mod_name: str) -> Optional[str]:
        """
        Validate mod name for duplicates and empty strings.

        Args:
            mod_name: Proposed mod name

        Returns:
            Error message if invalid, None if valid
        """
        mod_name = mod_name.strip()

        if not mod_name:
            return "Mod name cannot be empty."

        if any(m['name'] == mod_name for m in self.mods):
            return f"A mod named '{mod_name}' already exists.\nPlease choose a different name."

        return None

    def get_mod_by_name(self, mod_name: str) -> Optional[Dict]:
        """Get mod metadata by name."""
        return next((m for m in self.mods if m['name'] == mod_name), None)

    def remove_mod_files(self, mod_name: str) -> None:
        """Delete mod files from storage."""
        mod_storage = self.mod_storage_dir / mod_name
        if mod_storage.exists():
            shutil.rmtree(mod_storage)

    def get_enabled_mods(self) -> List[Dict]:
        """Get list of currently enabled mods."""
        return [m for m in self.mods if m['enabled']]
