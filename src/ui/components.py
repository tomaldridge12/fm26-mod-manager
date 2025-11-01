"""
Reusable UI components and widgets.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable
from .styles import COLORS


class StatusBar:
    """Status bar for displaying operation feedback."""

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=COLORS['bg_secondary'], height=30)
        self.label = tk.Label(
            self.frame,
            text="Ready",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 9),
            anchor=tk.W
        )
        self.label.pack(side=tk.LEFT, padx=10, pady=5)

    def pack(self, **kwargs):
        """Pack the status bar frame."""
        self.frame.pack(**kwargs)

    def show(self, message: str, status_type: str = "info"):
        """Update status message with color coding."""
        color = COLORS.get(status_type, COLORS['fg_primary'])
        self.label.config(text=message, fg=color)
        self.frame.update_idletasks()


class ActionButton:
    """Styled action button with consistent appearance."""

    def __init__(self, parent: tk.Widget, text: str, command: Callable,
                 bg_color: str = None, fg_color: str = None, bold: bool = False):
        font_style = ('Segoe UI', 10, 'bold') if bold else ('Segoe UI', 10)
        bg = bg_color or COLORS['bg_secondary']
        fg = fg_color or COLORS['fg_primary']

        self.button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            font=font_style,
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )

    def pack(self, **kwargs):
        """Pack the button."""
        self.button.pack(**kwargs)


class ModTreeView:
    """Custom treeview for displaying mod list."""

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=COLORS['bg_secondary'])

        # Scrollbar
        scrollbar = tk.Scrollbar(self.frame, bg=COLORS['bg_secondary'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=('Status', 'Name', 'Files'),
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=15
        )

        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('Status', text='Status', anchor=tk.W)
        self.tree.heading('Name', text='Mod Name', anchor=tk.W)
        self.tree.heading('Files', text='Modified Files', anchor=tk.W)

        self.tree.column('#0', width=50, stretch=False)
        self.tree.column('Status', width=100, stretch=False)
        self.tree.column('Name', width=300)
        self.tree.column('Files', width=350)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Tags for styling
        self.tree.tag_configure('enabled', foreground=COLORS['success'])
        self.tree.tag_configure('disabled', foreground=COLORS['error'])

    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)

    def clear(self):
        """Remove all items."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_mod(self, mod_data: dict):
        """Add mod to the tree."""
        status = "✓ Enabled" if mod_data['enabled'] else "○ Disabled"
        files = ', '.join(mod_data['files'][:3])
        if len(mod_data['files']) > 3:
            files += f" (+{len(mod_data['files'])-3} more)"

        tag = 'enabled' if mod_data['enabled'] else 'disabled'
        self.tree.insert('', tk.END, values=(status, mod_data['name'], files), tags=(tag,))

    def get_selection(self):
        """Get currently selected item."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return item['values'][1] if item['values'] else None
