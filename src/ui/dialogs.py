"""
Custom dialog windows with enhanced error reporting.
"""

import tkinter as tk
from tkinter import scrolledtext
from .styles import COLORS


class ErrorDialog:
    """Error dialog with expandable traceback details."""

    def __init__(self, parent, title: str, message: str, details: str = None):
        """
        Create error dialog with optional expandable details.

        Args:
            parent: Parent window
            title: Dialog title
            message: User-friendly error message
            details: Technical details/traceback (optional)
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=COLORS['bg_primary'])
        self.dialog.resizable(False, False)

        # Center on parent
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Main message
        message_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Error icon and message
        icon_label = tk.Label(
            message_frame,
            text="⚠",
            font=('Segoe UI', 32),
            fg=COLORS['error'],
            bg=COLORS['bg_primary']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))

        text_label = tk.Label(
            message_frame,
            text=message,
            font=('Segoe UI', 10),
            fg=COLORS['fg_primary'],
            bg=COLORS['bg_primary'],
            justify=tk.LEFT,
            wraplength=400
        )
        text_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Details section (expandable)
        if details:
            self.details_frame = None
            self.details_visible = False

            # Show/Hide details button
            self.toggle_btn = tk.Button(
                self.dialog,
                text="▶ Show Technical Details",
                command=self._toggle_details,
                bg=COLORS['bg_secondary'],
                fg=COLORS['fg_primary'],
                font=('Segoe UI', 9),
                relief=tk.FLAT,
                cursor='hand2',
                padx=10,
                pady=5
            )
            self.toggle_btn.pack(fill=tk.X, padx=20, pady=(0, 10))

            # Details text (initially hidden)
            self.details_text = details

        # OK button
        button_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ok_btn = tk.Button(
            button_frame,
            text="OK",
            command=self.dialog.destroy,
            bg=COLORS['accent'],
            fg=COLORS['bg_primary'],
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=8
        )
        ok_btn.pack(side=tk.RIGHT)

        # Size and position
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _toggle_details(self):
        """Toggle visibility of technical details."""
        if self.details_visible:
            # Hide details
            if self.details_frame:
                self.details_frame.destroy()
                self.details_frame = None
            self.toggle_btn.config(text="▶ Show Technical Details")
            self.details_visible = False
        else:
            # Show details
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

            # Scrolled text widget for details
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

            # Copy button
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

            self.toggle_btn.config(text="▼ Hide Technical Details")
            self.details_visible = True

            # Reposition dialog
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
    """
    Show error dialog with optional technical details.

    Args:
        parent: Parent window
        title: Dialog title
        message: User-friendly error message
        details: Technical details/traceback (optional)
    """
    dialog = ErrorDialog(parent, title, message, details)
    dialog.show()
