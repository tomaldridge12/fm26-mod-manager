import platform
from pathlib import Path
from typing import Optional, Tuple


class PathManager:
    """Manages FM26 installation paths across different operating systems."""

    def __init__(self):
        self.system = platform.system()

    def detect_installation(self) -> Optional[str]:
        """
        Auto-detect FM26 installation in common Steam library locations.

        Returns:
            Path to FM26 root folder, or None if not found
        """
        if self.system == "Windows":
            possible_roots = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/Football Manager 26"),
                Path("D:/SteamLibrary/steamapps/common/Football Manager 26"),
                Path("E:/SteamLibrary/steamapps/common/Football Manager 26"),
            ]
        elif self.system == "Darwin":  # macOS
            possible_roots = [
                Path.home() / "Library/Application Support/Steam/steamapps/common/Football Manager 26"
            ]
        else:
            return None

        for root in possible_roots:
            if root.exists() and self.validate_installation(root):
                return str(root)
        return None

    def validate_installation(self, fm_root: Optional[str]) -> bool:
        """
        Verify folder contains valid FM26 installation structure.

        Args:
            fm_root: Path to supposed FM26 root folder

        Returns:
            True if valid installation, False otherwise
        """
        if not fm_root:
            return False

        try:
            root_path = Path(fm_root)
            if not root_path.exists():
                return False

            data_path = self.get_data_path(fm_root)
            if not data_path:
                return False

            return Path(data_path).exists() and Path(data_path).is_dir()

        except Exception:
            return False

    def get_data_path(self, fm_root: Optional[str]) -> Optional[str]:
        """
        Construct OS-specific path to game data folder.

        Args:
            fm_root: Path to FM26 root folder

        Returns:
            Path to StandalonePlatform folder containing .bundle files
        """
        if not fm_root:
            return None

        try:
            root_path = Path(fm_root)

            if self.system == "Windows":
                data_path = root_path / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
            elif self.system == "Darwin":
                data_path = root_path / "fm.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "aa" / "StandaloneOSX"
            else:
                return None

            return str(data_path) if data_path.exists() else None

        except Exception:
            return None

    def validate_folder_selection(self, selected_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate and correct user-selected folder path.

        Handles cases where user selects parent folder or incorrect path.

        Args:
            selected_path: User-selected folder path

        Returns:
            Tuple of (is_valid, corrected_path, error_message)
        """
        try:
            path_obj = Path(selected_path)

            if "Football Manager 26" not in path_obj.parts:
                fm26_folder = path_obj / "Football Manager 26"
                if fm26_folder.exists():
                    selected_path = str(fm26_folder)
                else:
                    return False, None, (
                        "Please select the 'Football Manager 26' folder.\n\n"
                        "This folder is typically located at:\n"
                        "Steam/steamapps/common/Football Manager 26"
                    )

            if not self.validate_installation(selected_path):
                return False, None, (
                    "The selected folder does not contain a valid FM26 installation.\n\n"
                    "Please ensure you've selected the correct 'Football Manager 26' folder."
                )

            data_path = self.get_data_path(selected_path)
            if not data_path:
                return False, None, (
                    "Could not locate the game data files.\n\n"
                    "Please ensure FM26 is properly installed."
                )

            return True, selected_path, None

        except Exception as e:
            return False, None, f"An error occurred while validating the path:\n\n{str(e)}"
