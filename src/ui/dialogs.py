import tkinter as tk
from tkinter import scrolledtext
from .styles import COLORS


class ModernDialog:
    """Base class for modern styled dialogs."""

    def __init__(self, parent, title: str, width: int = 500):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=COLORS['bg_primary'])
        self.dialog.resizable(False, False)

        self.dialog.overrideredirect(False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.minsize(width, 100)

    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")


class InputDialog(ModernDialog):
    """Modern input dialog for text entry."""

    def __init__(self, parent, title: str, prompt: str, initial_value: str = ""):
        super().__init__(parent, title, width=520)

        container = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        title_label = tk.Label(
            container,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))

        prompt_label = tk.Label(
            container,
            text=prompt,
            font=('Segoe UI', 10),
            fg=COLORS['fg_secondary'],
            bg=COLORS['bg_primary'],
            justify=tk.LEFT
        )
        prompt_label.pack(anchor=tk.W, pady=(0, 12))

        input_frame = tk.Frame(container, bg=COLORS['bg_primary'])
        input_frame.pack(fill=tk.X, pady=(0, 20))

        self.entry = tk.Entry(
            input_frame,
            font=('Segoe UI', 11),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            insertbackground=COLORS['accent'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=2,
            highlightcolor=COLORS['accent'],
            highlightbackground=COLORS['border']
        )
        self.entry.pack(fill=tk.X, ipady=10, padx=2)
        self.entry.insert(0, initial_value)
        self.entry.select_range(0, tk.END)
        self.entry.focus()

        self.entry.bind('<Return>', lambda e: self._on_ok())
        self.entry.bind('<Escape>', lambda e: self._on_cancel())

        button_frame = tk.Frame(container, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            bg=COLORS['bg_elevated'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10,
            borderwidth=0
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        ok_btn = tk.Button(
            button_frame,
            text="OK",
            command=self._on_ok,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10,
            borderwidth=0,
            activebackground=COLORS['accent_emphasis']
        )
        ok_btn.pack(side=tk.RIGHT)

        cancel_btn.bind('<Enter>', lambda e: cancel_btn.config(bg=COLORS['border']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.config(bg=COLORS['bg_elevated']))

        self._center_on_parent(parent)

    def _on_ok(self):
        self.result = self.entry.get()
        self.dialog.destroy()

    def _on_cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Display dialog and return result."""
        self.dialog.wait_window()
        return self.result


class ConfirmDialog(ModernDialog):
    """Modern confirmation dialog."""

    def __init__(self, parent, title: str, message: str, confirm_text: str = "Confirm", cancel_text: str = "Cancel"):
        super().__init__(parent, title, width=500)

        container = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        header = tk.Frame(container, bg=COLORS['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))

        icon = tk.Label(
            header,
            text="?",
            font=('Segoe UI', 28, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary'],
            width=2
        )
        icon.pack(side=tk.LEFT, padx=(0, 15))

        title_label = tk.Label(
            header,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        message_label = tk.Label(
            container,
            text=message,
            font=('Segoe UI', 10),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary'],
            justify=tk.LEFT,
            wraplength=430
        )
        message_label.pack(anchor=tk.W, pady=(0, 20))

        button_frame = tk.Frame(container, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(
            button_frame,
            text=cancel_text,
            command=self._on_cancel,
            bg=COLORS['bg_elevated'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        confirm_btn = tk.Button(
            button_frame,
            text=confirm_text,
            command=self._on_confirm,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10,
            activebackground=COLORS['accent_emphasis']
        )
        confirm_btn.pack(side=tk.RIGHT)

        cancel_btn.bind('<Enter>', lambda e: cancel_btn.config(bg=COLORS['border']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.config(bg=COLORS['bg_elevated']))

        self.dialog.bind('<Escape>', lambda e: self._on_cancel())

        self._center_on_parent(parent)

    def _on_confirm(self):
        self.result = True
        self.dialog.destroy()

    def _on_cancel(self):
        self.result = False
        self.dialog.destroy()

    def show(self):
        """Display dialog and return result."""
        self.dialog.wait_window()
        return self.result


class MessageDialog(ModernDialog):
    """Modern message dialog for info/success/warning."""

    def __init__(self, parent, title: str, message: str, message_type: str = "info"):
        super().__init__(parent, title, width=480)

        icons = {
            'info': ('ℹ', COLORS['info']),
            'success': ('✓', COLORS['success']),
            'warning': ('⚠', COLORS['warning']),
            'error': ('✕', COLORS['error'])
        }
        icon_text, icon_color = icons.get(message_type, icons['info'])

        container = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        header = tk.Frame(container, bg=COLORS['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))

        icon = tk.Label(
            header,
            text=icon_text,
            font=('Segoe UI', 28, 'bold'),
            fg=icon_color,
            bg=COLORS['bg_primary'],
            width=2
        )
        icon.pack(side=tk.LEFT, padx=(0, 15))

        title_label = tk.Label(
            header,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        message_label = tk.Label(
            container,
            text=message,
            font=('Segoe UI', 10),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary'],
            justify=tk.LEFT,
            wraplength=410
        )
        message_label.pack(anchor=tk.W, pady=(0, 20))

        ok_btn = tk.Button(
            container,
            text="OK",
            command=self.dialog.destroy,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=10,
            activebackground=COLORS['accent_emphasis']
        )
        ok_btn.pack(anchor=tk.E)

        self.dialog.bind('<Return>', lambda e: self.dialog.destroy())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())

        self._center_on_parent(parent)

    def show(self):
        """Display dialog."""
        self.dialog.wait_window()


class ErrorDialog(ModernDialog):
    """Modern error dialog with expandable traceback details."""

    def __init__(self, parent, title: str, message: str, details: str = None):
        """
        Create error dialog with optional expandable details.

        Args:
            parent: Parent window
            title: Dialog title
            message: User-friendly error message
            details: Technical details/traceback (optional)
        """
        super().__init__(parent, title, width=550)

        container = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        header = tk.Frame(container, bg=COLORS['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))

        icon = tk.Label(
            header,
            text="✕",
            font=('Segoe UI', 28, 'bold'),
            fg=COLORS['error'],
            bg=COLORS['bg_primary'],
            width=2
        )
        icon.pack(side=tk.LEFT, padx=(0, 15))

        title_label = tk.Label(
            header,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        message_label = tk.Label(
            container,
            text=message,
            font=('Segoe UI', 10),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary'],
            justify=tk.LEFT,
            wraplength=480
        )
        message_label.pack(anchor=tk.W, pady=(0, 15))

        if details:
            self.details_frame = None
            self.details_visible = False
            self.details_text = details

            self.toggle_btn = tk.Button(
                container,
                text="▶  Show Technical Details",
                command=self._toggle_details,
                bg=COLORS['bg_elevated'],
                fg=COLORS['fg_primary'],
                font=('Segoe UI', 9),
                relief=tk.FLAT,
                cursor='hand2',
                padx=12,
                pady=8,
                anchor=tk.W
            )
            self.toggle_btn.pack(fill=tk.X, pady=(0, 15))

            self.toggle_btn.bind('<Enter>', lambda e: self.toggle_btn.config(bg=COLORS['border']))
            self.toggle_btn.bind('<Leave>', lambda e: self.toggle_btn.config(bg=COLORS['bg_elevated']))

        ok_btn = tk.Button(
            container,
            text="OK",
            command=self.dialog.destroy,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=10,
            activebackground=COLORS['accent_emphasis']
        )
        ok_btn.pack(anchor=tk.E)

        self.dialog.bind('<Return>', lambda e: self.dialog.destroy())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())

        self._center_on_parent(parent)

    def _toggle_details(self):
        """Toggle visibility of technical details."""
        if self.details_visible:
            if self.details_frame:
                self.details_frame.destroy()
                self.details_frame = None
            self.toggle_btn.config(text="▶  Show Technical Details")
            self.details_visible = False
        else:
            self.details_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
            self.details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

            details_label = tk.Label(
                self.details_frame,
                text="Technical Details:",
                font=('Segoe UI', 9, 'bold'),
                fg=COLORS['fg_primary'],
                bg=COLORS['bg_primary'],
                anchor=tk.W
            )
            details_label.pack(fill=tk.X, pady=(0, 5))

            details_text = scrolledtext.ScrolledText(
                self.details_frame,
                height=10,
                width=60,
                font=('Consolas', 8),
                bg=COLORS['bg_secondary'],
                fg=COLORS['fg_primary'],
                relief=tk.FLAT,
                wrap=tk.WORD
            )
            details_text.pack(fill=tk.BOTH, expand=True)
            details_text.insert('1.0', self.details_text)
            details_text.config(state=tk.DISABLED)

            copy_btn = tk.Button(
                self.details_frame,
                text="Copy to Clipboard",
                command=lambda: self._copy_to_clipboard(details_text),
                bg=COLORS['bg_secondary'],
                fg=COLORS['fg_primary'],
                font=('Segoe UI', 8),
                relief=tk.FLAT,
                cursor='hand2',
                padx=10,
                pady=3
            )
            copy_btn.pack(anchor=tk.E, pady=(5, 0))

            self.toggle_btn.config(text="▼  Hide Technical Details")
            self.details_visible = True

            self.dialog.update_idletasks()

    def _copy_to_clipboard(self, text_widget):
        """Copy details to clipboard."""
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(text_widget.get('1.0', tk.END))
        self.dialog.update()

    def show(self):
        """Display the dialog modally."""
        self.dialog.wait_window()


def show_error(parent, title: str, message: str, details: str = None):
    """Show error dialog with optional technical details."""
    dialog = ErrorDialog(parent, title, message, details)
    dialog.show()


def show_info(parent, title: str, message: str):
    """Show info message dialog."""
    dialog = MessageDialog(parent, title, message, 'info')
    dialog.show()


def show_success(parent, title: str, message: str):
    """Show success message dialog."""
    dialog = MessageDialog(parent, title, message, 'success')
    dialog.show()


def show_warning(parent, title: str, message: str):
    """Show warning message dialog."""
    dialog = MessageDialog(parent, title, message, 'warning')
    dialog.show()


def ask_string(parent, title: str, prompt: str, initial_value: str = "") -> str:
    """Show input dialog and return entered text."""
    dialog = InputDialog(parent, title, prompt, initial_value)
    return dialog.show()


def ask_yes_no(parent, title: str, message: str) -> bool:
    """Show confirmation dialog and return True/False."""
    dialog = ConfirmDialog(parent, title, message)
    return dialog.show()


class ProfileDialog(ModernDialog):
    """Dialog for managing profiles."""

    def __init__(self, parent, profiles: list, current_profile: str):
        super().__init__(parent, "Manage Profiles", width=600)

        self.profiles = profiles.copy()
        self.current_profile = current_profile
        self.selected_profile = current_profile

        container = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        title_label = tk.Label(
            container,
            text="Manage Profiles",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary']
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))

        # Profile list frame
        list_frame = tk.Frame(container, bg=COLORS['bg_secondary'], highlightthickness=1,
                             highlightbackground=COLORS['border'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Listbox for profiles
        self.profile_listbox = tk.Listbox(
            list_frame,
            font=('Segoe UI', 11),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            selectbackground=COLORS['accent'],
            selectforeground='#ffffff',
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            activestyle='none'
        )
        self.profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, command=self.profile_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.config(yscrollcommand=scrollbar.set)

        self._refresh_list()

        # Button frame for profile actions
        action_frame = tk.Frame(container, bg=COLORS['bg_primary'])
        action_frame.pack(fill=tk.X, pady=(0, 15))

        new_btn = tk.Button(
            action_frame,
            text="+ New Profile",
            command=self._new_profile,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        new_btn.pack(side=tk.LEFT, padx=(0, 8))

        rename_btn = tk.Button(
            action_frame,
            text="Rename",
            command=self._rename_profile,
            bg=COLORS['bg_elevated'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        rename_btn.pack(side=tk.LEFT, padx=(0, 8))

        delete_btn = tk.Button(
            action_frame,
            text="Delete",
            command=self._delete_profile,
            bg=COLORS['error'],
            fg='#ffffff',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        delete_btn.pack(side=tk.LEFT)

        # Export/Import buttons
        import_btn = tk.Button(
            action_frame,
            text="Import",
            command=self._import_profile,
            bg=COLORS['info'],
            fg='#ffffff',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        import_btn.pack(side=tk.RIGHT)

        export_btn = tk.Button(
            action_frame,
            text="Export",
            command=self._export_profile,
            bg=COLORS['info'],
            fg='#ffffff',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        )
        export_btn.pack(side=tk.RIGHT, padx=(0, 8))

        # Bottom buttons
        button_frame = tk.Frame(container, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            bg=COLORS['bg_elevated'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        switch_btn = tk.Button(
            button_frame,
            text="Switch Profile",
            command=self._on_switch,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10,
            activebackground=COLORS['accent_emphasis']
        )
        switch_btn.pack(side=tk.RIGHT)

        self.dialog.bind('<Escape>', lambda e: self._on_cancel())

        self._center_on_parent(parent)

    def _refresh_list(self):
        """Refresh the profile list display."""
        self.profile_listbox.delete(0, tk.END)
        for idx, profile in enumerate(self.profiles):
            name = profile['name']
            if name == self.current_profile:
                name += " (current)"
            self.profile_listbox.insert(tk.END, name)
            if profile['name'] == self.selected_profile:
                self.profile_listbox.selection_set(idx)

    def _new_profile(self):
        """Create a new profile."""
        name = ask_string(self.dialog, "New Profile", "Enter a name for the new profile:", "")
        if not name:
            return

        name = name.strip()
        if not name:
            return

        if any(p['name'] == name for p in self.profiles):
            show_error(self.dialog, "Profile Exists", f"A profile named '{name}' already exists.")
            return

        self.profiles.append({'name': name, 'mods': []})
        self.selected_profile = name
        self._refresh_list()

    def _rename_profile(self):
        """Rename the selected profile."""
        selection = self.profile_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        old_name = self.profiles[idx]['name']

        new_name = ask_string(self.dialog, "Rename Profile", f"Enter new name for '{old_name}':", old_name)
        if not new_name or new_name == old_name:
            return

        new_name = new_name.strip()
        if not new_name:
            return

        if any(p['name'] == new_name for p in self.profiles):
            show_error(self.dialog, "Profile Exists", f"A profile named '{new_name}' already exists.")
            return

        self.profiles[idx]['name'] = new_name
        if self.current_profile == old_name:
            self.current_profile = new_name
        if self.selected_profile == old_name:
            self.selected_profile = new_name
        self._refresh_list()

    def _delete_profile(self):
        """Delete the selected profile."""
        selection = self.profile_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        profile_name = self.profiles[idx]['name']

        if profile_name == self.current_profile:
            show_error(self.dialog, "Cannot Delete", "Cannot delete the currently active profile.")
            return

        if not ask_yes_no(self.dialog, "Confirm Delete",
                         f"Are you sure you want to delete profile '{profile_name}'?\n\nAll mods in this profile will be removed."):
            return

        self.profiles.pop(idx)
        if self.selected_profile == profile_name:
            self.selected_profile = self.current_profile
        self._refresh_list()

    def _on_switch(self):
        """Switch to selected profile."""
        selection = self.profile_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        self.selected_profile = self.profiles[idx]['name']
        self.result = {
            'profiles': self.profiles,
            'selected_profile': self.selected_profile
        }
        self.dialog.destroy()

    def _export_profile(self):
        """Export selected profile to JSON file."""
        selection = self.profile_listbox.curselection()
        if not selection:
            show_warning(self.dialog, "No Selection", "Please select a profile to export.")
            return

        idx = selection[0]
        profile = self.profiles[idx]

        from tkinter import filedialog
        import json
        from pathlib import Path
        from datetime import datetime

        filename = f"{profile['name']}.fm26profile"
        file_path = filedialog.asksaveasfilename(
            parent=self.dialog,
            title="Export Profile",
            defaultextension=".fm26profile",
            initialfile=filename,
            filetypes=[("FM26 Profile", "*.fm26profile"), ("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            export_data = {
                'profile_name': profile['name'],
                'mod_count': len(profile['mods']),
                'mods': profile['mods'],
                'exported_date': datetime.now().isoformat(),
                'fm26_mod_manager_version': '1.0'
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            show_info(self.dialog, "Export Successful",
                     f"Profile '{profile['name']}' exported successfully!\n\n"
                     f"File: {Path(file_path).name}\n"
                     f"Mods: {len(profile['mods'])}")

        except Exception as e:
            show_error(self.dialog, "Export Failed", f"Failed to export profile:\n\n{str(e)}")

    def _import_profile(self):
        """Import profile from JSON file."""
        from tkinter import filedialog
        import json

        file_path = filedialog.askopenfilename(
            parent=self.dialog,
            title="Import Profile",
            filetypes=[("FM26 Profile", "*.fm26profile"), ("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)

            profile_name = import_data.get('profile_name', 'Imported Profile')
            mods = import_data.get('mods', [])

            # Check if profile name already exists
            original_name = profile_name
            counter = 1
            while any(p['name'] == profile_name for p in self.profiles):
                profile_name = f"{original_name} ({counter})"
                counter += 1

            # Create new profile with imported data
            self.profiles.append({
                'name': profile_name,
                'mods': mods
            })

            self.selected_profile = profile_name
            self._refresh_list()

            show_info(self.dialog, "Import Successful",
                     f"Profile imported successfully!\n\n"
                     f"Name: {profile_name}\n"
                     f"Mods: {len(mods)}\n\n"
                     f"Note: The mod files themselves are not imported.\n"
                     f"You'll need to install the mods separately.")

        except Exception as e:
            show_error(self.dialog, "Import Failed", f"Failed to import profile:\n\n{str(e)}")

    def _on_cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Display dialog and return result."""
        self.dialog.wait_window()
        return self.result


def show_profile_dialog(parent, profiles: list, current_profile: str):
    """Show profile management dialog."""
    dialog = ProfileDialog(parent, profiles, current_profile)
    return dialog.show()


class TagManagementDialog:
    """Dialog for managing mod tags."""

    def __init__(self, parent, mod_name: str, current_tags: list):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Manage Tags - {mod_name}")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg=COLORS['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.mod_name = mod_name
        self.current_tags = list(current_tags) if current_tags else []
        self.result = None

        # Available tag categories
        self.available_tags = [
            'Graphics', 'Database', 'Gameplay', 'Faces', 'Logos',
            'Kits', 'Tactics', 'Wonderkids', 'Transfers', 'UI',
            'Realism', 'Championship', 'Lower Leagues', 'International',
            'Competition', 'Stadium', 'Other'
        ]

        self._create_ui()

    def _create_ui(self):
        """Create dialog UI."""
        # Header
        header = tk.Label(
            self.dialog,
            text=f"Manage Tags for '{self.mod_name}'",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 12, 'bold')
        )
        header.pack(pady=20, padx=20, anchor=tk.W)

        # Main content frame
        content = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Selected tags section
        selected_label = tk.Label(
            content,
            text="Selected Tags:",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 10, 'bold')
        )
        selected_label.pack(anchor=tk.W, pady=(0, 5))

        selected_frame = tk.Frame(
            content,
            bg=COLORS['bg_secondary'],
            highlightthickness=1,
            highlightbackground=COLORS['border']
        )
        selected_frame.pack(fill=tk.X, pady=(0, 15))

        self.selected_tags_frame = tk.Frame(selected_frame, bg=COLORS['bg_secondary'])
        self.selected_tags_frame.pack(fill=tk.X, padx=10, pady=10)

        # Available tags section
        available_label = tk.Label(
            content,
            text="Available Tags (click to add):",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 10, 'bold')
        )
        available_label.pack(anchor=tk.W, pady=(0, 5))

        available_frame = tk.Frame(
            content,
            bg=COLORS['bg_secondary'],
            highlightthickness=1,
            highlightbackground=COLORS['border']
        )
        available_frame.pack(fill=tk.BOTH, expand=True)

        self.available_tags_frame = tk.Frame(available_frame, bg=COLORS['bg_secondary'])
        self.available_tags_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        button_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ActionButton(button_frame, "Save", self._on_save, style='primary').pack(side=tk.RIGHT)
        ActionButton(button_frame, "Cancel", self._on_cancel, style='secondary').pack(side=tk.RIGHT, padx=(0, 10))

        self._refresh_tags()

    def _refresh_tags(self):
        """Refresh tag display."""
        # Clear frames
        for widget in self.selected_tags_frame.winfo_children():
            widget.destroy()
        for widget in self.available_tags_frame.winfo_children():
            widget.destroy()

        # Show selected tags as removable pills
        if self.current_tags:
            for tag in self.current_tags:
                self._create_tag_pill(self.selected_tags_frame, tag, removable=True)
        else:
            no_tags_label = tk.Label(
                self.selected_tags_frame,
                text="No tags selected",
                bg=COLORS['bg_secondary'],
                fg=COLORS['fg_secondary'],
                font=('Segoe UI', 9, 'italic')
            )
            no_tags_label.pack()

        # Show available tags as clickable buttons
        row_frame = None
        for i, tag in enumerate(self.available_tags):
            if tag in self.current_tags:
                continue

            if i % 4 == 0:
                row_frame = tk.Frame(self.available_tags_frame, bg=COLORS['bg_secondary'])
                row_frame.pack(fill=tk.X, pady=2)

            tag_btn = tk.Button(
                row_frame,
                text=f"+ {tag}",
                command=lambda t=tag: self._add_tag(t),
                bg=COLORS['bg_elevated'],
                fg=COLORS['accent'],
                font=('Segoe UI', 9),
                relief=tk.FLAT,
                cursor='hand2',
                padx=10,
                pady=5
            )
            tag_btn.pack(side=tk.LEFT, padx=2)
            tag_btn.bind('<Enter>', lambda e, b=tag_btn: b.config(bg=COLORS['accent_emphasis'], fg='#ffffff'))
            tag_btn.bind('<Leave>', lambda e, b=tag_btn: b.config(bg=COLORS['bg_elevated'], fg=COLORS['accent']))

    def _create_tag_pill(self, parent, tag: str, removable: bool = False):
        """Create a tag pill widget."""
        pill = tk.Frame(
            parent,
            bg=COLORS['accent'],
            highlightthickness=1,
            highlightbackground=COLORS['accent_emphasis']
        )
        pill.pack(side=tk.LEFT, padx=2, pady=2)

        label = tk.Label(
            pill,
            text=tag,
            bg=COLORS['accent'],
            fg='#ffffff',
            font=('Segoe UI', 9)
        )
        label.pack(side=tk.LEFT, padx=(8, 4), pady=4)

        if removable:
            remove_btn = tk.Label(
                pill,
                text="×",
                bg=COLORS['accent'],
                fg='#ffffff',
                font=('Segoe UI', 11, 'bold'),
                cursor='hand2'
            )
            remove_btn.pack(side=tk.LEFT, padx=(0, 6), pady=4)
            remove_btn.bind('<Button-1>', lambda e, t=tag: self._remove_tag(t))
            remove_btn.bind('<Enter>', lambda e: remove_btn.config(fg=COLORS['error']))
            remove_btn.bind('<Leave>', lambda e: remove_btn.config(fg='#ffffff'))

    def _add_tag(self, tag: str):
        """Add a tag to the mod."""
        if tag not in self.current_tags:
            self.current_tags.append(tag)
            self._refresh_tags()

    def _remove_tag(self, tag: str):
        """Remove a tag from the mod."""
        if tag in self.current_tags:
            self.current_tags.remove(tag)
            self._refresh_tags()

    def _on_save(self):
        """Save and close."""
        self.result = self.current_tags
        self.dialog.destroy()

    def _on_cancel(self):
        """Cancel and close."""
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Display dialog and return result."""
        self.dialog.wait_window()
        return self.result


def show_tag_dialog(parent, mod_name: str, current_tags: list):
    """Show tag management dialog."""
    dialog = TagManagementDialog(parent, mod_name, current_tags)
    return dialog.show()
