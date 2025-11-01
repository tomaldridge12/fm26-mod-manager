"""
UI styling and theme configuration.
"""

from tkinter import ttk


def apply_dark_theme(style: ttk.Style):
    """Apply modern dark theme to application."""
    style.theme_use('clam')

    # Base styles
    style.configure('TFrame', background='#1a1a2e')
    style.configure('TLabel', background='#1a1a2e', foreground='#e0e0e0', font=('Segoe UI', 10))
    style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#00d4ff')
    style.configure('TButton', font=('Segoe UI', 10), padding=10)
    style.map('TButton', background=[('active', '#00d4ff')])

    # Treeview (mod list)
    style.configure('Treeview',
                    background='#2a2a3e',
                    foreground='#e0e0e0',
                    fieldbackground='#2a2a3e',
                    borderwidth=0,
                    font=('Segoe UI', 10))
    style.configure('Treeview.Heading',
                    background='#1a1a2e',
                    foreground='#00d4ff',
                    font=('Segoe UI', 10, 'bold'))
    style.map('Treeview',
              background=[('selected', '#00d4ff')],
              foreground=[('selected', '#1a1a2e')])


# Color scheme constants
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#2a2a3e',
    'fg_primary': '#e0e0e0',
    'accent': '#00d4ff',
    'success': '#00ff88',
    'warning': '#ffaa00',
    'error': '#ff6b6b',
    'info': '#00d4ff',
}
