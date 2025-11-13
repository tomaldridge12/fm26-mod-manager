import sys
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from core.paths import PathManager
from core.backup import BackupManager
from core.mod_manager import ModManager
from core.config import ConfigManager
from core.profile_manager import ProfileManager
from core.logger import AppLogger
from core.update_detector import UpdateDetector
from ui.styles import apply_dark_theme, COLORS
from ui.components import StatusBar, ActionButton, ModTreeView, ExpandableLogViewer, ModDetailsPanel
from ui.dialogs import show_error, show_info, show_success, show_warning, ask_string, ask_yes_no, show_profile_dialog, show_tag_dialog, show_game_update_dialog


class FM26ModManagerApp:
    """Main application coordinating all mod management operations."""

    def __init__(self, root: tk.Tk, dnd_available: bool = False):
        self.root = root
        self.dnd_available = dnd_available
        self.root.title("FM26 Mod Manager")
        self.root.geometry("1000x750")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.minsize(900, 600)

        # Search and filter state
        self.search_var = tk.StringVar()
        self.filter_status_var = tk.StringVar(value="All")
        self.filter_tag_var = tk.StringVar(value="All Tags")

        # Configure Combobox dropdown popup colors
        self.root.option_add('*TCombobox*Listbox.background', COLORS['bg_tertiary'])
        self.root.option_add('*TCombobox*Listbox.foreground', COLORS['fg_primary'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLORS['accent_emphasis'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))

        self.path_manager = PathManager()
        self.fm_root_path = None
        self.data_path = None

        self.fm_root_path = self.path_manager.detect_installation()
        if self.fm_root_path:
            self.data_path = self.path_manager.get_data_path(self.fm_root_path)

        self._setup_storage()

        # Initialize logger
        log_file = self.backup_dir / "fm26_mod_manager.log"
        self.logger = AppLogger(log_file)
        self.logger.info("FM26 Mod Manager started")

        self.config_manager = ConfigManager(self.config_file)
        self.mod_manager = ModManager(self.backup_dir / "mods")
        self.profile_manager = ProfileManager()
        if self.data_path:
            self.backup_manager = BackupManager(self.backup_dir, self.data_path)
            self.update_detector = UpdateDetector(self.data_path)
        else:
            self.backup_manager = None
            self.update_detector = None

        self._load_config()

        self._create_ui()
        self._refresh_mod_list()
        self._setup_drag_drop()
        self._setup_keyboard_shortcuts()

        if not self.fm_root_path or not self.path_manager.validate_installation(self.fm_root_path):
            self.status_bar.show("No valid FM26 installation detected. Please browse to your installation folder.", "warning")
        else:
            # Check for game updates after UI is ready
            self.root.after(500, self._check_for_game_update)

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
        fm_root, mods, profiles, current_profile = self.config_manager.load()

        if fm_root and self.path_manager.validate_installation(fm_root):
            self.fm_root_path = fm_root
            self.data_path = self.path_manager.get_data_path(fm_root)
            if self.data_path:
                self.backup_manager = BackupManager(self.backup_dir, self.data_path)

        # Load profiles
        self.profile_manager.profiles = profiles
        self.profile_manager.current_profile = current_profile

        # Load mods for current profile
        current = self.profile_manager.get_profile(current_profile)
        if current:
            self.mod_manager.mods = current['mods']
        else:
            self.mod_manager.mods = mods

    def _save_config(self):
        """Persist configuration to disk."""
        # Update current profile's mods
        self.profile_manager.set_current_profile_mods(self.mod_manager.mods)

        success = self.config_manager.save(
            self.fm_root_path,
            self.profile_manager.profiles,
            self.profile_manager.current_profile
        )
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
        self._create_profile_section()
        self._create_search_filter_section()

        self._create_action_buttons()

        # Pack bottom elements first (status bar, then logs, then mod controls)
        # This ensures they stay at the bottom
        self.log_viewer = ExpandableLogViewer(self.root)
        self.log_viewer.pack(fill=tk.X, side=tk.BOTTOM)
        self.log_viewer.set_clear_callback(self.logger.clear_logs)

        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)


        # Mod list fills remaining space
        self._create_mod_list()

        # Set up logger callbacks
        self.logger.set_ui_callback(self._on_log_message)
        self.logger.set_status_callback(self.status_bar.show)

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

    def _create_profile_section(self):
        """Create profile selector section."""
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
            text="Profile",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        label.pack(anchor=tk.W, pady=(0, 8))

        profile_row = tk.Frame(content, bg=COLORS['bg_secondary'])
        profile_row.pack(fill=tk.X)

        self.profile_var = tk.StringVar(value=self.profile_manager.current_profile)

        # Create combobox for profile selection
        self.profile_combo = ttk.Combobox(
            profile_row,
            textvariable=self.profile_var,
            values=self.profile_manager.get_profile_names(),
            state='readonly',
            font=('Segoe UI', 11),
            width=30
        )
        self.profile_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.profile_combo.bind('<<ComboboxSelected>>', self._on_profile_changed)

        ActionButton(
            profile_row,
            "Manage Profiles",
            self._manage_profiles,
            style='primary',
            icon="⚙"
        ).pack(side=tk.LEFT)

    def _create_search_filter_section(self):
        """Create search and filter controls."""
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

        # Search box
        search_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        search_frame.pack(fill=tk.X, pady=(0, 10))

        search_label = tk.Label(
            search_frame,
            text="🔍",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 12)
        )
        search_label.pack(side=tk.LEFT, padx=(0, 8))

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_primary'],
            insertbackground=COLORS['accent'],
            relief=tk.FLAT,
            bd=0
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        search_entry.insert(0, "Search mods...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search mods..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search mods...") if not search_entry.get() else None)
        self.search_var.trace_add('write', lambda *args: self._refresh_mod_list())

        # Filter row
        filter_row = tk.Frame(content, bg=COLORS['bg_secondary'])
        filter_row.pack(fill=tk.X)

        # Status filter
        status_label = tk.Label(
            filter_row,
            text="Status:",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        status_label.pack(side=tk.LEFT, padx=(0, 8))

        status_filter = ttk.Combobox(
            filter_row,
            textvariable=self.filter_status_var,
            values=["All", "Enabled", "Disabled"],
            state='readonly',
            font=('Segoe UI', 9),
            width=12
        )
        status_filter.pack(side=tk.LEFT, padx=(0, 15))
        status_filter.bind('<<ComboboxSelected>>', lambda e: self._refresh_mod_list())

        # Tag filter
        tag_label = tk.Label(
            filter_row,
            text="Category:",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        tag_label.pack(side=tk.LEFT, padx=(0, 8))

        self.tag_filter = ttk.Combobox(
            filter_row,
            textvariable=self.filter_tag_var,
            values=["All Tags"],
            state='readonly',
            font=('Segoe UI', 9),
            width=18
        )
        self.tag_filter.pack(side=tk.LEFT, padx=(0, 15))
        self.tag_filter.bind('<<ComboboxSelected>>', lambda e: self._refresh_mod_list())

        # Sort by load order toggle
        self.sort_by_load_order_var = tk.BooleanVar(value=False)
        sort_check = ttk.Checkbutton(
            filter_row,
            text="Sort by Load Order",
            variable=self.sort_by_load_order_var,
            command=self._refresh_mod_list
        )
        sort_check.pack(side=tk.RIGHT, padx=(15, 0))

        # Clear filters button
        ActionButton(
            filter_row,
            "Clear Filters",
            self._clear_filters,
            style='secondary',
            icon="×"
        ).pack(side=tk.RIGHT)

    def _clear_filters(self):
        """Clear all search and filter criteria."""
        self.search_var.set("")
        self.filter_status_var.set("All")
        self.filter_tag_var.set("All Tags")
        self._refresh_mod_list()

    def _create_action_buttons(self):
        """Create modern action buttons."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        # Left-aligned buttons
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
        ).pack(side=tk.LEFT, padx=(0, 10))

        ActionButton(
            button_frame,
            "Launch Game",
            self._launch_game,
            style='success',
            icon="▶"
        ).pack(side=tk.LEFT)

        # Right-aligned mod control buttons
        ActionButton(
            button_frame,
            "Remove",
            self._remove_mod,
            style='danger',
            icon="×"
        ).pack(side=tk.RIGHT)

        # Bulk operations section (left of mod controls)
        bulk_label = tk.Label(
            button_frame,
            text="Bulk:",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        bulk_label.pack(side=tk.RIGHT, padx=(20, 8))

        ActionButton(
            button_frame,
            "Enable Selected",
            self._bulk_enable,
            style='success',
            icon="✓"
        ).pack(side=tk.RIGHT, padx=(0, 8))

        ActionButton(
            button_frame,
            "Disable Selected",
            self._bulk_disable,
            style='secondary',
            icon="○"
        ).pack(side=tk.RIGHT, padx=(0, 8))

        ActionButton(
            button_frame,
            "Remove Selected",
            self._bulk_remove,
            style='danger',
            icon="×"
        ).pack(side=tk.RIGHT, padx=(0, 8))

        ActionButton(
            button_frame,
            "Tags",
            self._manage_tags,
            style='secondary',
            icon="🏷"
        ).pack(side=tk.RIGHT, padx=(0, 8))

        ActionButton(
            button_frame,
            "Disable",
            self._disable_mod,
            style='secondary',
            icon="○"
        ).pack(side=tk.RIGHT, padx=(0, 8))

        ActionButton(
            button_frame,
            "Enable",
            self._enable_mod,
            style='success',
            icon="✓"
        ).pack(side=tk.RIGHT, padx=(0, 8))

    def _create_mod_list(self):
        """Create modern mod list display with details panel."""
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

        # Create PanedWindow for resizable split view
        paned = tk.PanedWindow(
            list_frame,
            orient=tk.HORIZONTAL,
            bg=COLORS['bg_primary'],
            sashwidth=4,
            sashrelief=tk.FLAT,
            bd=0
        )
        paned.pack(fill=tk.BOTH, expand=True)

        # Mod list on the left
        mod_list_container = tk.Frame(paned, bg=COLORS['bg_primary'])
        self.mod_tree = ModTreeView(mod_list_container)
        self.mod_tree.pack(fill=tk.BOTH, expand=True)

        # Bind selection event to update details panel
        self.mod_tree.tree.bind('<<TreeviewSelect>>', self._on_mod_selected)

        paned.add(mod_list_container, minsize=400)

        # Details panel on the right
        self.details_panel = ModDetailsPanel(paned)
        paned.add(self.details_panel.container, minsize=250)

    def _on_mod_selected(self, event=None):
        """Handle mod selection to update details panel."""
        mod_name = self.mod_tree.get_selection()
        if mod_name:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if mod:
                self.details_panel.show_mod_details(mod)
        else:
            self.details_panel._show_placeholder()

    def _setup_drag_drop(self):
        """Setup drag and drop for mod archives."""
        if not self.dnd_available:
            self.logger.debug("Drag-and-drop not available (tkinterdnd2 not installed)")
            return

        try:
            # Register the window to accept drops
            self.root.drop_target_register('DND_Files')
            self.root.dnd_bind('<<Drop>>', self._on_drop)
            self.root.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.root.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            self.logger.info("Drag-and-drop enabled for mod archives")
        except Exception as e:
            self.logger.warning(f"Failed to setup drag-and-drop: {str(e)}")

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # Ctrl+F: Focus search
        self.root.bind('<Control-f>', lambda e: self._focus_search())

        # Ctrl+E: Enable selected mod
        self.root.bind('<Control-e>', lambda e: self._enable_mod())

        # Ctrl+D: Disable selected mod
        self.root.bind('<Control-d>', lambda e: self._disable_mod())

        # Ctrl+T: Manage tags for selected mod
        self.root.bind('<Control-t>', lambda e: self._manage_tags())

        # Delete: Remove selected mod
        self.root.bind('<Delete>', lambda e: self._remove_mod())

        # Ctrl+R: Restore all
        self.root.bind('<Control-r>', lambda e: self._restore_all())

        # Ctrl+L: Launch game
        self.root.bind('<Control-l>', lambda e: self._launch_game())

        # Ctrl+N: New profile
        self.root.bind('<Control-n>', lambda e: self._manage_profiles())

        # Ctrl+A: Add mod
        self.root.bind('<Control-a>', lambda e: self._add_mod())

        # Ctrl+P: Manage profiles
        self.root.bind('<Control-p>', lambda e: self._manage_profiles())

        self.logger.info("Keyboard shortcuts enabled")

    def _focus_search(self):
        """Focus the search entry field."""
        # Find the search entry widget and focus it
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                self._find_and_focus_search(widget)
                break

    def _find_and_focus_search(self, widget):
        """Recursively find and focus search entry."""
        for child in widget.winfo_children():
            if isinstance(child, tk.Entry) and str(child.cget('textvariable')) == str(self.search_var):
                child.focus_set()
                if child.get() == "Search mods...":
                    child.delete(0, tk.END)
                return True
            elif isinstance(child, (tk.Frame, ttk.Frame)):
                if self._find_and_focus_search(child):
                    return True
        return False

    def _on_drag_enter(self, event):
        """Handle drag enter event."""
        # Visual feedback that we can accept the drop
        self.root.configure(bg=COLORS['accent_emphasis'])
        return event.action

    def _on_drag_leave(self, event):
        """Handle drag leave event."""
        # Restore normal background
        self.root.configure(bg=COLORS['bg_primary'])
        return event.action

    def _on_drop(self, event):
        """Handle file drop event."""
        # Restore normal background
        self.root.configure(bg=COLORS['bg_primary'])

        # Get dropped files
        files = event.data

        # Handle different formats (Windows vs Unix)
        if isinstance(files, str):
            # Windows: space-separated paths, possibly with braces
            if files.startswith('{'):
                # Multiple files with braces: {file1} {file2}
                import re
                file_list = re.findall(r'\{([^}]+)\}', files)
            else:
                # Single file or space-separated
                file_list = [files.strip()]
        else:
            file_list = list(files)

        # Filter for zip/rar files
        valid_files = []
        for file_path in file_list:
            file_path = file_path.strip()
            if file_path.lower().endswith(('.zip', '.rar')):
                valid_files.append(file_path)

        if not valid_files:
            self.logger.warning("No valid mod archives in dropped files")
            show_warning(self.root, "Invalid Files",
                "Please drop ZIP or RAR mod archive files.")
            return event.action

        # Process each valid file
        for file_path in valid_files:
            self._add_mod_from_file(file_path)

        return event.action

    def _validate_paths(self) -> bool:
        """Ensure installation paths are valid before operations."""
        if not self.fm_root_path or not self.data_path:
            self.logger.error("No FM26 installation configured")
            show_error(self.root,
                "Installation Required",
                "Please select your Football Manager 26 installation folder first.\n\n"
                "Use the 'Browse' button to locate your FM26 installation."
            )
            return False

        if not Path(self.data_path).exists():
            self.logger.error("FM26 data path not found")
            show_error(self.root,
                "Installation Error",
                "The FM26 data files could not be found.\n\n"
                "Please ensure FM26 is properly installed and select the correct folder."
            )
            return False

        return True

    def _browse_installation(self):
        """Handle installation folder selection."""
        self.logger.debug("Opening installation folder browser")
        initial_dir = self.fm_root_path if self.fm_root_path else None

        path = filedialog.askdirectory(
            title="Select Football Manager 26 folder",
            initialdir=initial_dir
        )

        if not path:
            self.logger.debug("Installation folder selection cancelled")
            return

        try:
            self.logger.info(f"Validating installation path: {path}")
            is_valid, corrected_path, error_msg = self.path_manager.validate_folder_selection(path)

            if not is_valid:
                self.logger.error(f"Invalid installation path: {error_msg}")
                show_error(self.root, "Invalid Selection", error_msg)
                return

            self.fm_root_path = corrected_path
            self.data_path = self.path_manager.get_data_path(corrected_path)

            self.backup_manager = BackupManager(self.backup_dir, self.data_path)
            self._setup_storage()

            self.path_var.set(corrected_path)
            self._save_config()

            self.logger.success(f"Installation path updated: {corrected_path}")

        except Exception as e:
            self.logger.error(f"Error updating installation path: {str(e)}")
            show_error(self.root,
                "Error",
                f"An error occurred while updating the installation path:\n\n{str(e)}"
            )

    def _on_profile_changed(self, event=None):
        """Handle profile selection change from combobox."""
        new_profile = self.profile_var.get()
        old_profile = self.profile_manager.current_profile

        if old_profile == new_profile:
            return

        self.logger.info(f"Switching profile from '{old_profile}' to '{new_profile}'")

        # Save current profile's mods before switching
        self.profile_manager.set_current_profile_mods(self.mod_manager.mods)

        # Disable all enabled mods in current profile
        if self._validate_paths() and self.backup_manager:
            enabled_mods = [m for m in self.mod_manager.mods if m['enabled']]
            if enabled_mods:
                # Restore all files for currently enabled mods
                all_files = []
                for mod in enabled_mods:
                    all_files.extend(mod['files'])

                if all_files:
                    self.backup_manager.restore_files(all_files)

        # Switch to new profile
        self.profile_manager.current_profile = new_profile

        # Load new profile's mods
        current = self.profile_manager.get_profile(new_profile)
        if current:
            self.mod_manager.mods = current['mods']
        else:
            self.mod_manager.mods = []

        # Enable all mods that should be enabled in new profile
        if self._validate_paths() and self.backup_manager:
            enabled_mods = [m for m in self.mod_manager.mods if m['enabled']]
            for mod in enabled_mods:
                # Backup and enable each mod
                self.backup_manager.backup_files(mod['files'])
                self.mod_manager.enable_mod(mod, Path(self.data_path))

        # Update UI
        self._refresh_mod_list()
        self._save_config()

        self.logger.success(f"Successfully switched to profile '{new_profile}'")

    def _manage_profiles(self):
        """Handle profile management dialog."""
        self.logger.debug("Opening profile management dialog")
        result = show_profile_dialog(
            self.root,
            self.profile_manager.profiles,
            self.profile_manager.current_profile
        )

        if not result:
            self.logger.debug("Profile management cancelled")
            return

        # Check if profile was switched
        old_profile = self.profile_manager.current_profile
        new_profile = result['selected_profile']

        if old_profile != new_profile:
            self.logger.info(f"Switching profile from '{old_profile}' to '{new_profile}'")
            # Save current profile's mods before switching
            self.profile_manager.set_current_profile_mods(self.mod_manager.mods)

            # Disable all enabled mods in current profile
            if self._validate_paths() and self.backup_manager:
                enabled_mods = [m for m in self.mod_manager.mods if m['enabled']]
                if enabled_mods:
                    # Restore all files for currently enabled mods
                    all_files = []
                    for mod in enabled_mods:
                        all_files.extend(mod['files'])

                    if all_files:
                        self.backup_manager.restore_files(all_files)

            # Switch to new profile
            self.profile_manager.profiles = result['profiles']
            self.profile_manager.current_profile = new_profile

            # Load new profile's mods
            current = self.profile_manager.get_profile(new_profile)
            if current:
                self.mod_manager.mods = current['mods']
            else:
                self.mod_manager.mods = []

            # Enable all mods that should be enabled in new profile
            if self._validate_paths() and self.backup_manager:
                enabled_mods = [m for m in self.mod_manager.mods if m['enabled']]
                for mod in enabled_mods:
                    # Backup and enable each mod
                    self.backup_manager.backup_files(mod['files'])
                    self.mod_manager.enable_mod(mod, Path(self.data_path))

            # Update UI
            self.profile_var.set(new_profile)
            self.profile_combo['values'] = self.profile_manager.get_profile_names()
            self._refresh_mod_list()
            self._save_config()

            self.logger.success(f"Successfully switched to profile '{new_profile}'")
        else:
            # Just update profiles list (renames, deletions, etc.)
            self.logger.debug("Profile list updated (no switch)")
            self.profile_manager.profiles = result['profiles']
            self.profile_combo['values'] = self.profile_manager.get_profile_names()
            self._save_config()

    def _launch_game(self):
        """Launch Football Manager 26."""
        self.logger.info("Attempting to launch FM26")
        if not self.fm_root_path:
            self.logger.error("Cannot launch game: No FM26 installation configured")
            show_error(self.root,
                "Installation Required",
                "Please select your Football Manager 26 installation folder first.\n\n"
                "Use the 'Browse' button to locate your FM26 installation."
            )
            return

        exe_path = self.path_manager.get_executable_path(self.fm_root_path)
        if not exe_path:
            self.logger.error("Cannot launch game: Executable not found")
            show_error(self.root,
                "Executable Not Found",
                "Could not find the FM26 executable.\n\n"
                "Please ensure FM26 is properly installed."
            )
            return

        try:
            import subprocess
            import platform

            system = platform.system()

            if system == "Windows":
                # On Windows, use shell=False and pass the path directly
                self.logger.info(f"Launching game (Windows): {exe_path}")
                subprocess.Popen([exe_path], cwd=str(Path(self.fm_root_path)))
            elif system == "Darwin":
                # On macOS, use 'open' command to launch the .app bundle
                self.logger.info(f"Launching game (macOS): {exe_path}")
                subprocess.Popen(['open', exe_path])
            else:
                self.logger.error(f"Unsupported platform: {system}")
                show_error(self.root,
                    "Unsupported Platform",
                    "Game launching is only supported on Windows and macOS."
                )
                return

            self.logger.success("Game launched successfully")

        except Exception as e:
            self.logger.error(f"Failed to launch game: {str(e)}")
            show_error(self.root,
                "Launch Failed",
                f"An error occurred while launching the game:\n\n{str(e)}"
            )

    def _add_mod(self):
        """Handle mod addition workflow via file browser."""
        if not self._validate_paths():
            return

        filetypes = [
            ("Archive files", "*.zip *.rar *.7z"),
            ("ZIP files", "*.zip"),
            ("RAR files", "*.rar"),
            ("All files", "*.*")
        ]

        self.logger.debug("Opening mod archive file browser")
        file_path = filedialog.askopenfilename(title="Select Mod Archive", filetypes=filetypes)
        if not file_path or not Path(file_path).exists():
            self.logger.debug("Mod archive selection cancelled")
            return

        self._add_mod_from_file(file_path)

    def _add_mod_from_file(self, file_path: str):
        """
        Add a mod from a file path (used by both file browser and drag-drop).

        Args:
            file_path: Path to the mod archive file
        """
        if not self._validate_paths():
            return

        # Validate file exists and is a supported format
        if not Path(file_path).exists():
            self.logger.error(f"File not found: {file_path}")
            show_error(self.root, "File Not Found", f"The file does not exist:\n\n{file_path}")
            return

        if not file_path.lower().endswith(('.zip', '.rar')):
            self.logger.error(f"Unsupported file format: {file_path}")
            show_error(self.root, "Unsupported Format",
                "Only ZIP and RAR archives are supported.\n\n"
                "Please provide a .zip or .rar file.")
            return

        # Ask for mod name
        mod_name = ask_string(self.root, "Mod Name", "Enter a name for this mod:", Path(file_path).stem
        )

        if not mod_name:
            self.logger.debug("Mod name input cancelled")
            return

        error = self.mod_manager.validate_mod_name(mod_name)
        if error:
            self.logger.warning(f"Invalid mod name: {mod_name}")
            show_error(self.root, "Invalid Name", error)
            return

        self.logger.info(f"Adding mod '{mod_name}' from {file_path}")

        temp_dir = self.backup_dir / "temp_extract"
        try:
            self.logger.info(f"Extracting '{mod_name}'...")

            success, bundle_files, error_msg, traceback_str = self.mod_manager.extract_mod(file_path, mod_name, temp_dir)
            if not success:
                self.logger.error(f"Extraction failed: {error_msg}")
                show_error(self.root, "Extraction Failed", error_msg, traceback_str)
                return

            conflicts = self.mod_manager.check_conflicts([f.name for f in bundle_files])
            if conflicts:
                self.logger.warning(f"Mod '{mod_name}' has conflicts with existing mods")
                conflict_msg = "The following files conflict with enabled mods:\n\n"
                for file, mod in conflicts.items():
                    conflict_msg += f"  • {file} (used by '{mod}')\n"
                conflict_msg += "\nThe mod will be added but you'll need to disable conflicting mods to enable it."
                show_warning(self.root, "Conflicts Detected", conflict_msg)

            self.logger.info(f"Installing '{mod_name}'...")

            success, error_msg = self.mod_manager.install_mod(mod_name, bundle_files)
            if not success:
                self.logger.error(f"Installation failed: {error_msg}")
                show_error(self.root, "Installation Failed", f"Failed to install mod:\n\n{error_msg}")
                return

            mod_data = self.mod_manager.create_mod_entry(mod_name, bundle_files)
            self.mod_manager.mods.append(mod_data)
            self._save_config()
            self._refresh_mod_list()

            self.logger.success(f"Mod '{mod_name}' added successfully with {len(bundle_files)} file(s)")
            show_info(self.root,
                "Success",
                f"Mod '{mod_name}' added successfully!\n\n"
                f"Files: {len(bundle_files)}\n"
                f"Status: Disabled"
            )

        except Exception as e:
            self.logger.error(f"Failed to add mod: {str(e)}")
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
            self.logger.warning("No mod selected for enabling")
            show_warning(self.root, "No Selection", "Please select a mod to enable.")
            return

        try:
            self.logger.info(f"Attempting to enable mod '{mod_name}'")
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                self.logger.error(f"Mod '{mod_name}' not found")
                show_error(self.root, "Error", "Selected mod could not be found.")
                return

            if mod['enabled']:
                self.logger.warning(f"Mod '{mod_name}' is already enabled")
                show_info(self.root, "Already Enabled", "This mod is already enabled.")
                return

            conflicts = self.mod_manager.check_conflicts(mod['files'])
            if conflicts:
                self.logger.error(f"Cannot enable '{mod_name}' due to conflicts")
                conflict_list = "\n".join([f"  • {file} (used by '{mod_name}')" for file, mod_name in conflicts.items()])
                show_error(self.root,
                    "Conflicts Detected",
                    f"Cannot enable mod due to file conflicts:\n\n{conflict_list}\n\n"
                    "Please disable the conflicting mods first."
                )
                return

            self.logger.info(f"Enabling '{mod_name}'...")

            backed_up, failed = self.backup_manager.backup_files(mod['files'])
            if failed:
                self.logger.error(f"Backup failed for {len(failed)} file(s)")
                show_error(self.root,
                    "Backup Failed",
                    f"Failed to backup some files:\n\n" +
                    "\n".join([f"  • {f}" for f in failed])
                )
                return

            if backed_up > 0:
                self.logger.info(f"Backed up {backed_up} file(s) before modification")

            success, copied_files, error_msg = self.mod_manager.enable_mod(mod, Path(self.data_path))

            if not success:
                self.logger.error(f"Failed to enable mod, rolling back: {error_msg}")
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
            self.logger.success(f"Mod '{mod_name}' enabled successfully")
            show_info(self.root, "Success", f"Mod '{mod_name}' has been enabled successfully!")

        except Exception as e:
            self.logger.error(f"Unexpected error while enabling mod: {str(e)}")
            show_error(self.root, "Error", f"An unexpected error occurred:\n\n{str(e)}")

    def _disable_mod(self):
        """Handle mod disabling workflow."""
        if not self._validate_paths():
            return

        mod_name = self.mod_tree.get_selection()
        if not mod_name:
            self.logger.warning("No mod selected for disabling")
            show_warning(self.root, "No Selection", "Please select a mod to disable.")
            return

        try:
            self.logger.info(f"Attempting to disable mod '{mod_name}'")
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                self.logger.error(f"Mod '{mod_name}' not found")
                show_error(self.root, "Error", "Selected mod could not be found.")
                return

            if not mod['enabled']:
                self.logger.warning(f"Mod '{mod_name}' is not enabled")
                show_info(self.root, "Not Enabled", "This mod is not currently enabled.")
                return

            self.logger.info(f"Disabling '{mod_name}'...")

            success, missing, failed = self.backup_manager.restore_files(mod['files'])
            if not success:
                error_msg = ""
                if missing:
                    error_msg += "Missing backup files:\n" + "\n".join([f"  • {f}" for f in missing])
                if failed:
                    if error_msg:
                        error_msg += "\n\n"
                    error_msg += "Failed to restore:\n" + "\n".join([f"  • {f}" for f in failed])

                self.logger.error(f"Failed to restore original files for '{mod_name}'")
                show_error(self.root, "Restore Failed", error_msg)
                return

            mod['enabled'] = False
            self._save_config()
            self._refresh_mod_list()
            self.logger.success(f"Mod '{mod_name}' disabled successfully")
            show_info(self.root, "Success", f"Mod '{mod_name}' has been disabled successfully!")

        except Exception as e:
            self.logger.error(f"Failed to disable mod: {str(e)}")
            show_error(self.root, "Error", f"Failed to disable mod:\n\n{str(e)}")

    def _manage_tags(self):
        """Handle tag management workflow."""
        mod_name = self.mod_tree.get_selection()
        if not mod_name:
            self.logger.warning("No mod selected for tag management")
            show_warning(self.root, "No Selection", "Please select a mod to manage tags.")
            return

        try:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                return

            current_tags = mod.get('tags', [])
            new_tags = show_tag_dialog(self.root, mod_name, current_tags)

            if new_tags is not None:  # None means cancelled
                mod['tags'] = new_tags
                self._save_config()
                self._refresh_mod_list()
                self.logger.info(f"Updated tags for '{mod_name}': {', '.join(new_tags)}")
                show_info(self.root, "Success", f"Tags updated for '{mod_name}'!")

        except Exception as e:
            self.logger.error(f"Failed to manage tags: {str(e)}")
            show_error(self.root, "Error", f"Failed to manage tags:\n\n{str(e)}")

    def _remove_mod(self):
        """Handle mod removal workflow."""
        mod_name = self.mod_tree.get_selection()
        if not mod_name:
            self.logger.warning("No mod selected for removal")
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
                self.logger.debug(f"Mod removal cancelled for '{mod_name}'")
                return

            self.logger.info(f"Removing '{mod_name}'...")

            if mod['enabled'] and self.backup_manager:
                self.backup_manager.restore_files(mod['files'])

            self.mod_manager.remove_mod_files(mod_name)
            self.mod_manager.mods.remove(mod)
            self._save_config()
            self._refresh_mod_list()

            self.logger.success(f"Mod '{mod_name}' removed successfully")
            show_info(self.root, "Success", f"Mod '{mod_name}' has been removed successfully!")

        except Exception as e:
            self.logger.error(f"Failed to remove mod: {str(e)}")
            show_error(self.root, "Error", f"Failed to remove mod:\n\n{str(e)}")

    def _restore_all(self):
        """Handle restore all workflow."""
        if not self._validate_paths() or not self.backup_manager:
            return

        if not self.backup_manager.has_backups():
            self.logger.warning("No backups found to restore")
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
            self.logger.debug("Restore all cancelled")
            return

        try:
            self.logger.info("Restoring original files...")

            restored, failed = self.backup_manager.restore_all()

            for mod in self.mod_manager.mods:
                mod['enabled'] = False

            self._save_config()
            self._refresh_mod_list()

            if failed:
                self.logger.warning(f"Restore completed with {len(failed)} errors")
                show_warning(self.root,
                    "Restore Completed with Errors",
                    f"Restored {restored} of {backup_count} files.\n\n"
                    f"Failed to restore:\n" + "\n".join([f"  • {f}" for f in failed])
                )
            else:
                self.logger.success(f"Restored {restored} original file(s)")
                show_info(self.root,
                    "Success",
                    f"Successfully restored {restored} original file(s)!\n\n"
                    f"All mods have been disabled."
                )

        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            show_error(self.root, "Restore Failed", f"Failed to restore files:\n\n{str(e)}")

    def _on_log_message(self, message: str, level: str):
        """
        Handle log messages for UI display.

        Args:
            message: Log message
            level: Log level (debug, info, warning, error)
        """
        self.log_viewer.append_log(message, level)

    def _refresh_mod_list(self):
        """Update mod list display with search and filter applied."""
        self.mod_tree.clear()

        # Get filter criteria
        search_text = self.search_var.get().lower()
        if search_text == "search mods...":
            search_text = ""

        status_filter = self.filter_status_var.get()
        tag_filter = self.filter_tag_var.get()

        # Sort mods by load order if requested
        mods_to_display = list(self.mod_manager.mods)
        if self.sort_by_load_order_var.get():
            mods_to_display.sort(key=lambda m: m.get('load_order', 100))

        # Filter mods
        for mod in mods_to_display:
            # Apply search filter
            if search_text and search_text not in mod['name'].lower():
                continue

            # Apply status filter
            if status_filter == "Enabled" and not mod['enabled']:
                continue
            if status_filter == "Disabled" and mod['enabled']:
                continue

            # Apply tag filter
            if tag_filter != "All Tags":
                mod_tags = mod.get('tags', [])
                if tag_filter not in mod_tags:
                    continue

            # Add mod to tree
            self.mod_tree.add_mod(mod)

        # Update tag filter dropdown with all available tags
        self._update_tag_filter_dropdown()

    def _update_tag_filter_dropdown(self):
        """Update tag filter dropdown with all unique tags from mods."""
        all_tags = set()
        for mod in self.mod_manager.mods:
            tags = mod.get('tags', [])
            all_tags.update(tags)

        tag_values = ["All Tags"] + sorted(all_tags)
        self.tag_filter['values'] = tag_values

        # Reset to "All Tags" if current selection is no longer valid
        if self.filter_tag_var.get() not in tag_values:
            self.filter_tag_var.set("All Tags")

    def _bulk_enable(self):
        """Enable all checked mods."""
        if not self._validate_paths():
            return

        checked_names = self.mod_tree.get_checked_items()
        if not checked_names:
            self.logger.warning("No mods selected for bulk enable")
            show_warning(self.root, "No Selection", "Please check mods to enable using the checkboxes.")
            return

        enabled_count = 0
        failed_count = 0

        for mod_name in checked_names:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod or mod['enabled']:
                continue

            # Check conflicts
            conflicts = self.mod_manager.check_conflicts(mod['files'])
            if conflicts:
                self.logger.warning(f"Skipping '{mod_name}' due to conflicts")
                failed_count += 1
                continue

            # Enable mod
            backed_up, failed = self.backup_manager.backup_files(mod['files'])
            if not failed:
                success, copied_files, error_msg = self.mod_manager.enable_mod(mod, Path(self.data_path))
                if success:
                    mod['enabled'] = True
                    enabled_count += 1
                else:
                    failed_count += 1

        self._save_config()
        self._refresh_mod_list()

        if failed_count > 0:
            self.logger.warning(f"Bulk enable: {enabled_count} enabled, {failed_count} failed")
            show_warning(self.root, "Partial Success",
                        f"Enabled {enabled_count} mod(s).\n{failed_count} failed due to conflicts or errors.")
        else:
            self.logger.success(f"Bulk enabled {enabled_count} mod(s)")
            show_info(self.root, "Success", f"Successfully enabled {enabled_count} mod(s)!")

    def _bulk_disable(self):
        """Disable all checked mods."""
        if not self._validate_paths():
            return

        checked_names = self.mod_tree.get_checked_items()
        if not checked_names:
            self.logger.warning("No mods selected for bulk disable")
            show_warning(self.root, "No Selection", "Please check mods to disable using the checkboxes.")
            return

        disabled_count = 0

        for mod_name in checked_names:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod or not mod['enabled']:
                continue

            success, missing, failed = self.backup_manager.restore_files(mod['files'])
            if success:
                mod['enabled'] = False
                disabled_count += 1

        self._save_config()
        self._refresh_mod_list()

        self.logger.success(f"Bulk disabled {disabled_count} mod(s)")
        show_info(self.root, "Success", f"Successfully disabled {disabled_count} mod(s)!")

    def _bulk_remove(self):
        """Remove all checked mods."""
        checked_names = self.mod_tree.get_checked_items()
        if not checked_names:
            self.logger.warning("No mods selected for bulk remove")
            show_warning(self.root, "No Selection", "Please check mods to remove using the checkboxes.")
            return

        if not ask_yes_no(self.root,
            "Confirm Bulk Removal",
            f"Are you sure you want to remove {len(checked_names)} mod(s)?\n\n"
            f"This will permanently delete the mod files."
        ):
            self.logger.debug("Bulk removal cancelled")
            return

        removed_count = 0

        for mod_name in checked_names:
            mod = self.mod_manager.get_mod_by_name(mod_name)
            if not mod:
                continue

            if mod['enabled'] and self.backup_manager:
                self.backup_manager.restore_files(mod['files'])

            self.mod_manager.remove_mod_files(mod_name)
            self.mod_manager.mods.remove(mod)
            removed_count += 1

        self._save_config()
        self._refresh_mod_list()

        self.logger.success(f"Bulk removed {removed_count} mod(s)")
        show_info(self.root, "Success", f"Successfully removed {removed_count} mod(s)!")

    def _check_for_game_update(self):
        """Check if the game has been updated and handle recovery."""
        if not self.update_detector or not self.backup_manager:
            return

        try:
            update_detected, message = self.update_detector.detect_update(self.backup_dir)

            if update_detected:
                self.logger.warning(f"Game update detected: {message}")

                # Get list of enabled mods before recovery
                enabled_mods = [mod['name'] for mod in self.mod_manager.mods if mod['enabled']]

                # Show update dialog
                result = show_game_update_dialog(
                    self.root,
                    enabled_mods,
                    len(self.mod_manager.mods)
                )

                if result == 'recover':
                    self._handle_game_update_recovery(enabled_mods)
                else:
                    self.logger.info("Game update recovery cancelled by user")
            else:
                self.logger.debug(f"Update check: {message}")

        except Exception as e:
            self.logger.error(f"Error checking for game update: {str(e)}")

    def _handle_game_update_recovery(self, previously_enabled_mods: list):
        """
        Handle recovery from a game update.

        Args:
            previously_enabled_mods: List of mod names that were enabled before the update
        """
        try:
            self.logger.info("Starting game update recovery process")

            # Step 1: Clear all old backups (they're from the old game version)
            self.logger.info("Clearing old backup files...")
            import shutil
            backup_files_dir = self.backup_dir / "files"
            if backup_files_dir.exists():
                shutil.rmtree(backup_files_dir)
                backup_files_dir.mkdir(exist_ok=True)
                self.logger.info("Old backups cleared")

            # Step 2: Clear the fingerprint so it's recalculated
            self.update_detector.clear_fingerprint(self.backup_dir)

            # Step 3: Disable all mods in the manager
            for mod in self.mod_manager.mods:
                mod['enabled'] = False

            # Step 4: Store new fingerprint
            new_fingerprint = self.update_detector.calculate_game_fingerprint()
            if new_fingerprint:
                self.update_detector.store_fingerprint(self.backup_dir, new_fingerprint)
                self.logger.info("New game fingerprint stored")

            # Step 5: Save config and refresh UI
            self._save_config()
            self._refresh_mod_list()

            # Step 6: Inform user
            recovery_message = (
                f"Game update recovery complete!\n\n"
                f"• Old backups cleared\n"
                f"• All mods marked as disabled\n"
                f"• {len(self.mod_manager.mods)} mod(s) ready to re-enable\n\n"
            )

            if previously_enabled_mods:
                recovery_message += (
                    f"Previously enabled mods ({len(previously_enabled_mods)}):\n" +
                    "\n".join([f"  • {mod}" for mod in previously_enabled_mods[:10]])
                )
                if len(previously_enabled_mods) > 10:
                    recovery_message += f"\n  ... and {len(previously_enabled_mods) - 10} more"

                recovery_message += "\n\nYou can now re-enable these mods using the bulk enable feature."

            self.logger.success("Game update recovery completed successfully")
            show_info(self.root, "Recovery Complete", recovery_message)

        except Exception as e:
            self.logger.error(f"Recovery failed: {str(e)}")
            show_error(self.root, "Recovery Failed",
                      f"An error occurred during recovery:\n\n{str(e)}\n\n"
                      f"Please check the logs for details.")
