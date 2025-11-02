import tkinter as tk
from tkinter import ttk
from typing import Callable
from .styles import COLORS


class StatusBar:
    """Modern status bar with icon and subtle animations."""

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(
            parent,
            bg=COLORS['bg_tertiary'],
            height=36,
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            highlightcolor=COLORS['border']
        )

        self.icon_label = tk.Label(
            self.frame,
            text="●",
            bg=COLORS['bg_tertiary'],
            fg=COLORS['success'],
            font=('Segoe UI', 12),
            anchor=tk.W
        )
        self.icon_label.pack(side=tk.LEFT, padx=(15, 5))

        self.label = tk.Label(
            self.frame,
            text="Ready",
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 9),
            anchor=tk.W
        )
        self.label.pack(side=tk.LEFT, padx=(0, 15))

    def pack(self, **kwargs):
        """Pack the status bar frame."""
        self.frame.pack(**kwargs)

    def show(self, message: str, status_type: str = "info"):
        """Update status message with icon and color coding."""
        icon_colors = {
            'info': COLORS['info'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'error': COLORS['error']
        }

        color = COLORS.get(status_type, COLORS['fg_primary'])
        icon_color = icon_colors.get(status_type, COLORS['info'])

        self.icon_label.config(fg=icon_color)
        self.label.config(text=message, fg=color)
        self.frame.update_idletasks()


class ActionButton:
    """Modern button with hover effects and rounded appearance."""

    def __init__(self, parent: tk.Widget, text: str, command: Callable,
                 style: str = 'secondary', icon: str = None):
        """
        Create modern action button.

        Args:
            parent: Parent widget
            text: Button text
            command: Click handler
            style: 'primary', 'secondary', 'success', 'danger'
            icon: Optional emoji/icon before text
        """
        styles = {
            'primary': {
                'bg': COLORS['accent'],
                'fg': '#ffffff',
                'hover_bg': COLORS['accent_emphasis']
            },
            'secondary': {
                'bg': COLORS['bg_elevated'],
                'fg': COLORS['fg_primary'],
                'hover_bg': COLORS['border']
            },
            'success': {
                'bg': COLORS['success_emphasis'],
                'fg': '#ffffff',
                'hover_bg': COLORS['success']
            },
            'danger': {
                'bg': COLORS['error_emphasis'],
                'fg': '#ffffff',
                'hover_bg': COLORS['error']
            }
        }

        config = styles.get(style, styles['secondary'])
        button_text = f"{icon}  {text}" if icon else text

        self.button = tk.Button(
            parent,
            text=button_text,
            command=command,
            bg=config['bg'],
            fg=config['fg'],
            font=('Segoe UI', 10, 'bold' if style == 'primary' else 'normal'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            borderwidth=0,
            activebackground=config['hover_bg'],
            activeforeground=config['fg']
        )

        self.normal_bg = config['bg']
        self.hover_bg = config['hover_bg']
        self.fg_color = config['fg']

        self.button.bind('<Enter>', self._on_enter)
        self.button.bind('<Leave>', self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter."""
        self.button.config(bg=self.hover_bg)

    def _on_leave(self, event):
        """Handle mouse leave."""
        self.button.config(bg=self.normal_bg)

    def pack(self, **kwargs):
        """Pack the button."""
        self.button.pack(**kwargs)


class ModTreeView:
    """Modern mod list with card-like appearance."""

    def __init__(self, parent: tk.Widget):
        self.container = tk.Frame(
            parent,
            bg=COLORS['border'],
            highlightthickness=0
        )

        self.frame = tk.Frame(
            self.container,
            bg=COLORS['bg_secondary']
        )
        self.frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        scrollbar = tk.Scrollbar(
            self.frame,
            bg=COLORS['bg_secondary'],
            troughcolor=COLORS['bg_secondary'],
            activebackground=COLORS['accent'],
            highlightthickness=0,
            borderwidth=0
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            self.frame,
            columns=('Status', 'Name', 'Date', 'Files'),
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=12
        )

        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('Status', text='STATUS', anchor=tk.W)
        self.tree.heading('Name', text='MOD NAME', anchor=tk.W)
        self.tree.heading('Date', text='DATE ADDED', anchor=tk.W)
        self.tree.heading('Files', text='MODIFIED FILES', anchor=tk.W)

        self.tree.column('#0', width=20, stretch=False)
        self.tree.column('Status', width=100, stretch=False)
        self.tree.column('Name', width=240)
        self.tree.column('Date', width=140, stretch=False)
        self.tree.column('Files', width=280)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.tree.tag_configure('enabled', foreground=COLORS['success'])
        self.tree.tag_configure('disabled', foreground=COLORS['fg_secondary'])

    def pack(self, **kwargs):
        """Pack the container."""
        self.container.pack(**kwargs)

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

        from datetime import datetime
        date_str = mod_data.get('added_date', '')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str)
                formatted_date = date_obj.strftime('%b %d, %Y')
            except (ValueError, AttributeError):
                formatted_date = 'Unknown'
        else:
            formatted_date = 'Unknown'

        tag = 'enabled' if mod_data['enabled'] else 'disabled'
        self.tree.insert('', tk.END, values=(status, mod_data['name'], formatted_date, files), tags=(tag,))

    def get_selection(self):
        """Get currently selected item."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return item['values'][1] if item['values'] else None
