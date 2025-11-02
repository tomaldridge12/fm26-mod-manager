import sys
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from core.paths import PathManager
from core.backup import BackupManager
from core.mod_manager import ModManager
from core.config import ConfigManager
from ui.styles import apply_dark_theme, COLORS
from ui.components import StatusBar, ActionButton, ModTreeView
from ui.dialogs import show_error, show_info, show_success, show_warning, ask_string, ask_yes_no


class FM26ModManagerApp:
    """Main application coordinating all mod management operations."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FM26 Mod Manager")
        self.root.geometry("1000x900")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.minsize(900, 650)

        self.path_manager = PathManager()
        self.fm_root_path = None
        self.data_path = None

        self.fm_root_path = self.path_manager.detect_installation()
        if self.fm_root_path:
            self.data_path = self.path_manager.get_data_path(self.fm_root_path)

        self._setup_storage()

        self.config_manager = ConfigManager(self.config_file)
        self.mod_manager = ModManager(self.backup_dir / "mods")
        if self.data_path:
            self.backup_manager = BackupManager(self.backup_dir, self.data_path)
        else:
            self.backup_manager = None

        self._load_config()

        self._create_ui()
        self._refresh_mod_list()

        if not self.fm_root_path or not self.path_manager.validate_installation(self.fm_root_path):
            self.status_bar.show("No valid FM26 installation detected. Please browse to your installation folder.", "warning")

    def _setup_storage(self):
        """Initialize config and backup directory paths."""
        try:
            if self.fm_root_path:
                base_path = Path(self.fm_root_path) / ".fm26_mod_manager"
            else:
                base_path = Path.home() / ".fm26_mod_manager"

            base_path.mkdir(exist_ok=True)
            self.config_file = base_path / "config.json"
            self.backup_dir = base_path / "backups"
            self.backup_dir.mkdir(exist_ok=True)

        except Exception:
            base_path = Path.home() / ".fm26_mod_manager"
            base_path.mkdir(exist_ok=True)
            self.config_file = base_path / "config.json"
            self.backup_dir = base_path / "backups"
            self.backup_dir.mkdir(exist_ok=True)

    def _load_config(self):
        """Load configuration and update paths if needed."""
        fm_root, mods = self.config_manager.load()

        if fm_root and self.path_manager.validate_installation(fm_root):
            self.fm_root_path = fm_root
            self.data_path = self.path_manager.get_data_path(fm_root)
            if self.data_path:
                self.backup_manager = BackupManager(self.backup_dir, self.data_path)

        self.mod_manager.mods = mods

    def _save_config(self):
        """Persist configuration to disk."""
        success = self.config_manager.save(self.fm_root_path, self.mod_manager.mods)
        if not success and hasattr(self, 'status_bar'):
            self.status_bar.show("Warning: Failed to save configuration", "warning")

    def _create_ui(self):
        """Build the modern user interface."""
        style = ttk.Style()
        apply_dark_theme(style)

        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=30, pady=(25, 15))

        title_label = ttk.Label(header_frame, text="FM26 Mod Manager", style='Title.TLabel')
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(
            header_frame,
            text="Manage your Football Manager 2026 modifications",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))

        separator = tk.Frame(self.root, bg=COLORS['border'], height=1)
        separator.pack(fill=tk.X, padx=30, pady=(10, 20))

        self._create_path_section()

        self._create_action_buttons()
        self._create_mod_list()
        self._create_mod_controls()

        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _create_path_section(self):
        """Create modern installation path card."""
        card = tk.Frame(
            self.root,
            bg=COLORS['bg_secondary'],
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            highlightcolor=COLORS['border']
        )
        card.pack(fill=tk.X, padx=30, pady=(0, 20))

        content = tk.Frame(card, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.X, padx=15, pady=15)

        label = tk.Label(
            content,
            text="Installation Path",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        label.pack(anchor=tk.W, pady=(0, 8))

        path_row = tk.Frame(content, bg=COLORS['bg_secondary'])
        path_row.pack(fill=tk.X)

        self.path_var = tk.StringVar(value=self.fm_root_path or "Not set")
        path_entry = tk.Entry(
            path_row,
            textvariable=self.path_var,
            font=('Segoe UI', 10),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_primary'],
            insertbackground=COLORS['accent'],
            relief=tk.FLAT,
            bd=0,
            state='readonly',
            readonlybackground=COLORS['bg_tertiary']
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        ActionButton(
            path_row,
            "Browse",
            self._browse_installation,
            style='primary',
            icon="📁"
        ).pack(side=tk.LEFT)

    def _create_action_buttons(self):
        """Create modern action buttons."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        ActionButton(
            button_frame,
            "Add Mod",
            self._add_mod,
            style='primary',
            icon="+"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ActionButton(
            button_frame,
            "Restore All",
            self._restore_all,
            style='secondary',
            icon="↺"
        ).pack(side=tk.LEFT)

    def _create_mod_list(self):
        """Create modern mod list display."""
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 15))

        header = tk.Label(
            list_frame,
            text="Installed Mods",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        header.pack(anchor=tk.W, pady=(0, 10))

        self.mod_tree = ModTreeView(list_frame)
        self.mod_tree.pack(fill=tk.BOTH, expand=True)

    def _create_mod_controls(self):
        """Create modern mod control buttons."""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=30, pady=(0, 15))

        ActionButton(
            control_frame,
            "Enable",
            self._enable_mod,
            style='success',
            icon="✓"
        ).pack(side=tk.LEFT, padx=(0, 8))

        ActionButton(
            control_frame,
            "Disable",
            self._disable_mod,
            style='secondary',
            icon="○"
        ).pack(side=tk.LEFT, padx=(0, 8))

        ActionButton(
            control_frame,
            "Remove",
            self._remove_mod,
            style='danger',
            icon="×"
        ).pack(side=tk.LEFT)

    def _validate_paths(self) -> bool:
        """Ensure installation paths are valid before operations."""
        if not self.fm_root_path or not self.data_path:
            self.status_bar.show("No FM26 installation configured", "error")
            show_error(self.root, 
                "Installation Required",
                "Please select your Football Manager 26 installation folder first.\n\n"
                "Use the 'Browse' button to locate your FM26 installation."
            )
            return False

        if not Path(self.data_path).exists():
            self.status_bar.show("FM26 data path not found", "error")
            show_error(self.root, 
                "Installation Error",
                "The FM26 data files could not be found.\n\n"
                "Please ensure FM26 is properly installed and select the correct folder."
            )
            return False

        return True

    def _browse_installation(self):
        """Handle installation folder selection."""
        initial_dir = self.fm_root_path if self.fm_root_path else None

        path = filedialog.askdirectory(
            title="Select Football Manager 26 folder",
            initialdir=initial_dir
        )

        if not path:
            return

        try:
            is_valid, corrected_path, error_msg = self.path_manager.validate_folder_selection(path)

            if not is_valid:
                self.status_bar.show("Invalid installation selected", "error")
                show_error(self.root, "Invalid Selection", error_msg)
                return

            self.fm_root_path = corrected_path
            self.data_path = self.path_manager.get_data_path(corrected_path)

            self.backup_manager = BackupManager(self.backup_dir, self.data_path)
            self._setup_storage()

            self.path_var.set(corrected_path)
            self._save_config()

            self.status_bar.show("Installation path updated successfully", "success")

        except Exception as e:
            self.status_bar.show("Error updating installation path", "error")
            show_error(self.root, 
                "Error",
                f"An error occurred while updating the installation path:\n\n{str(e)}"
            )

    def _add_mod(self):
        """Handle mod addition workflow."""
        if not self._validate_paths():
            return

        filetypes = [
            ("Archive files", "*.zip *.rar *.7z"),
            ("ZIP files", "*.zip"),
            ("RAR files", "*.rar"),
            ("All files", "*.*")
        ]

        file_path = filedialog.askopenfilename(title="Select Mod Archive", filetypes=filetypes)
        if not file_path or not Path(file_path).exists():
            return

        mod_name = ask_string(self.root, "Mod Name", "Enter a name for this mod:", Path(file_path).stem
        )

        if not mod_name:
            return

        error = self.mod_manager.validate_mod_name(mod_name)
        if error:
            self.status_bar.show("Invalid mod name", "error")
            show_error(self.root, "Invalid Name", error)
            return

        temp_dir = self.backup_dir / "temp_extract"
        try:
            self.status_bar.show(f"Extracting '{mod_name}'...", "info")

            success, bundle_files, error_msg, traceback_str = self.mod_manager.extract_mod(file_path, mod_name, temp_dir)
            if not success:
                self.status_bar.show("Extraction failed", "error")
                show_error(self.root, "Extraction Failed", error_msg, traceback_str)
                return

            conflicts = self.mod_manager.check_conflicts([f.name for f in bundle_files])
            if conflicts:
                conflict_msg = "The following files conflict with enabled mods:\n\n"
                for file, mod in conflicts.items():
                    conflict_msg += f"  • {file} (used by '{mod}')\n"
                conflict_msg += "\nThe mod will be added but you'll need to disable conflicting mods to enable it."
                show_warning(self.root, "Conflicts Detected", conflict_msg)

            self.status_bar.show(f"Installing '{mod_name}'...", "info")

            success, error_msg = self.mod_manager.install_mod(mod_name, bundle_files)
            if not success:
                self.status_bar.show("Installation failed", "error")
                show_error(self.root, "Installation Failed", f"Failed to install mod:\n\n{error_msg}")
                return

            mod_data = self.mod_manager.create_mod_entry(mod_name, bundle_files)
            self.mod_manager.mods.append(mod_data)
            self._save_config()
            self._refresh_mod_list()

            self.status_bar.show(f"Mod '{mod_name}' added successfully", "success")
            show_info(self.root, 
                "Success",
                f"Mod '{mod_name}' added successfully!\n\n"
                f"Files: {len(bundle_files)}\n"
                f"Status: Disabled"
            )

        except Exception as e:
            self.status_bar.show("Failed to add mod", "error")
            show_error(self.root, 
                "Error",
                f"An error occurred while adding the mod:\n\n{str(e)}"
            )

        finally:
            if temp_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

    def _enable_mod(self):
        """Handle mod enabling workflow."""
        if not self._validate_paths():
            return

        mod_name = self.mod_tree.get_selection()
        if not mod_name:
            self.status_bar.show("No mod selected", "warning")
            show_warning(self.root, "No Selection", "Please select a mod to enable.")
            return

        try:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                self.status_bar.show("Mod not found", "error")
                show_error(self.root, "Error", "Selected mod could not be found.")
                return

            if mod['enabled']:
                self.status_bar.show("Mod is already enabled", "info")
                show_info(self.root, "Already Enabled", "This mod is already enabled.")
                return

            conflicts = self.mod_manager.check_conflicts(mod['files'])
            if conflicts:
                self.status_bar.show("Cannot enable due to conflicts", "error")
                conflict_list = "\n".join([f"  • {file} (used by '{mod_name}')" for file, mod_name in conflicts.items()])
                show_error(self.root, 
                    "Conflicts Detected",
                    f"Cannot enable mod due to file conflicts:\n\n{conflict_list}\n\n"
                    "Please disable the conflicting mods first."
                )
                return

            self.status_bar.show(f"Enabling '{mod_name}'...", "info")

            backed_up, failed = self.backup_manager.backup_files(mod['files'])
            if failed:
                self.status_bar.show("Backup failed", "error")
                show_error(self.root, 
                    "Backup Failed",
                    f"Failed to backup some files:\n\n" +
                    "\n".join([f"  • {f}" for f in failed])
                )
                return

            if backed_up > 0:
                self.status_bar.show(f"Backed up {backed_up} file(s) before modification", "info")

            success, copied_files, error_msg = self.mod_manager.enable_mod(mod, Path(self.data_path))

            if not success:
                self.status_bar.show("Failed to enable mod, rolling back", "error")
                if copied_files:
                    self.backup_manager.restore_files(copied_files)

                show_error(self.root, 
                    "Enable Failed",
                    f"Failed to enable mod:\n\n{error_msg}\n\n"
                    "Any partial changes have been rolled back."
                )
                return

            mod['enabled'] = True
            self._save_config()
            self._refresh_mod_list()
            self.status_bar.show(f"Mod '{mod_name}' enabled successfully", "success")
            show_info(self.root, "Success", f"Mod '{mod_name}' has been enabled successfully!")

        except Exception as e:
            self.status_bar.show("Unexpected error", "error")
            show_error(self.root, "Error", f"An unexpected error occurred:\n\n{str(e)}")

    def _disable_mod(self):
        """Handle mod disabling workflow."""
        if not self._validate_paths():
            return

        mod_name = self.mod_tree.get_selection()
        if not mod_name:
            self.status_bar.show("No mod selected", "warning")
            show_warning(self.root, "No Selection", "Please select a mod to disable.")
            return

        try:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                self.status_bar.show("Mod not found", "error")
                show_error(self.root, "Error", "Selected mod could not be found.")
                return

            if not mod['enabled']:
                self.status_bar.show("Mod is not enabled", "info")
                show_info(self.root, "Not Enabled", "This mod is not currently enabled.")
                return

            self.status_bar.show(f"Disabling '{mod_name}'...", "info")

            success, missing, failed = self.backup_manager.restore_files(mod['files'])
            if not success:
                error_msg = ""
                if missing:
                    error_msg += "Missing backup files:\n" + "\n".join([f"  • {f}" for f in missing])
                if failed:
                    if error_msg:
                        error_msg += "\n\n"
                    error_msg += "Failed to restore:\n" + "\n".join([f"  • {f}" for f in failed])

                self.status_bar.show("Failed to restore original files", "error")
                show_error(self.root, "Restore Failed", error_msg)
                return

            mod['enabled'] = False
            self._save_config()
            self._refresh_mod_list()
            self.status_bar.show(f"Mod '{mod_name}' disabled successfully", "success")
            show_info(self.root, "Success", f"Mod '{mod_name}' has been disabled successfully!")

        except Exception as e:
            self.status_bar.show("Failed to disable mod", "error")
            show_error(self.root, "Error", f"Failed to disable mod:\n\n{str(e)}")

    def _remove_mod(self):
        """Handle mod removal workflow."""
        mod_name = self.mod_tree.get_selection()
        if not mod_name:
            self.status_bar.show("No mod selected", "warning")
            show_warning(self.root, "No Selection", "Please select a mod to remove.")
            return

        try:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                return

            if not ask_yes_no(self.root, 
                "Confirm Removal",
                f"Are you sure you want to remove '{mod_name}'?\n\n"
                f"This will permanently delete the mod files."
            ):
                return

            self.status_bar.show(f"Removing '{mod_name}'...", "info")

            if mod['enabled'] and self.backup_manager:
                self.backup_manager.restore_files(mod['files'])

            self.mod_manager.remove_mod_files(mod_name)
            self.mod_manager.mods.remove(mod)
            self._save_config()
            self._refresh_mod_list()

            self.status_bar.show(f"Mod '{mod_name}' removed successfully", "success")
            show_info(self.root, "Success", f"Mod '{mod_name}' has been removed successfully!")

        except Exception as e:
            self.status_bar.show("Failed to remove mod", "error")
            show_error(self.root, "Error", f"Failed to remove mod:\n\n{str(e)}")

    def _restore_all(self):
        """Handle restore all workflow."""
        if not self._validate_paths() or not self.backup_manager:
            return

        if not self.backup_manager.has_backups():
            self.status_bar.show("No backups found", "warning")
            show_info(self.root, 
                "No Backups Found",
                "No backed up files found.\n\n"
                "Original files are only backed up when mods modify them.\n"
                "If no mods have been enabled yet, there's nothing to restore."
            )
            return

        backup_count = self.backup_manager.get_backup_count()
        enabled_mods = self.mod_manager.get_enabled_mods()

        if not ask_yes_no(self.root, 
            "Confirm Restore",
            f"Restore {backup_count} backed up file(s) to their original state?\n\n"
            f"This will disable {len(enabled_mods)} enabled mod(s) and restore\n"
            f"all modified files to their vanilla versions."
        ):
            return

        try:
            self.status_bar.show("Restoring original files...", "info")

            restored, failed = self.backup_manager.restore_all()

            for mod in self.mod_manager.mods:
                mod['enabled'] = False

            self._save_config()
            self._refresh_mod_list()

            if failed:
                self.status_bar.show("Restore completed with errors", "warning")
                show_warning(self.root, 
                    "Restore Completed with Errors",
                    f"Restored {restored} of {backup_count} files.\n\n"
                    f"Failed to restore:\n" + "\n".join([f"  • {f}" for f in failed])
                )
            else:
                self.status_bar.show(f"Restored {restored} original files", "success")
                show_info(self.root, 
                    "Success",
                    f"Successfully restored {restored} original file(s)!\n\n"
                    f"All mods have been disabled."
                )

        except Exception as e:
            self.status_bar.show("Restore failed", "error")
            show_error(self.root, "Restore Failed", f"Failed to restore files:\n\n{str(e)}")

    def _refresh_mod_list(self):
        """Update mod list display."""
        self.mod_tree.clear()
        for mod in self.mod_manager.mods:
            self.mod_tree.add_mod(mod)
