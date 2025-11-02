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
