"""
UI styling and theme configuration - Modern sleek design.
"""

from tkinter import ttk


def apply_dark_theme(style: ttk.Style):
    """Apply modern sleek dark theme with subtle gradients and depth."""
    style.theme_use('clam')

    # Base styles with modern spacing
    style.configure('TFrame', background='#0d1117')
    style.configure('TLabel',
                    background='#0d1117',
                    foreground='#c9d1d9',
                    font=('Segoe UI', 10))
    style.configure('Title.TLabel',
                    font=('Segoe UI', 24, 'bold'),
                    foreground='#58a6ff',
                    background='#0d1117')
    style.configure('Subtitle.TLabel',
                    font=('Segoe UI', 9),
                    foreground='#8b949e',
                    background='#0d1117')

    # Modern treeview with better contrast
    style.configure('Treeview',
                    background='#161b22',
                    foreground='#c9d1d9',
                    fieldbackground='#161b22',
                    borderwidth=0,
                    font=('Segoe UI', 10),
                    rowheight=32)
    style.configure('Treeview.Heading',
                    background='#21262d',
                    foreground='#58a6ff',
                    font=('Segoe UI', 10, 'bold'),
                    borderwidth=0,
                    relief='flat')
    style.map('Treeview',
              background=[('selected', '#1f6feb')],
              foreground=[('selected', '#ffffff')])
    style.map('Treeview.Heading',
              background=[('active', '#30363d')])


# Modern color palette inspired by GitHub Dark theme
COLORS = {
    'bg_primary': '#0d1117',      # Deep dark background
    'bg_secondary': '#161b22',    # Slightly lighter panels
    'bg_tertiary': '#21262d',     # Card backgrounds
    'bg_elevated': '#30363d',     # Hover states

    'fg_primary': '#c9d1d9',      # Primary text
    'fg_secondary': '#8b949e',    # Secondary text
    'fg_muted': '#484f58',        # Muted text

    'accent': '#58a6ff',          # Primary blue
    'accent_emphasis': '#1f6feb', # Darker blue for contrast

    'success': '#3fb950',         # Green
    'success_emphasis': '#238636',

    'warning': '#d29922',         # Orange/yellow
    'warning_emphasis': '#9e6a03',

    'error': '#f85149',           # Red
    'error_emphasis': '#da3633',

    'info': '#58a6ff',

    'border': '#30363d',          # Subtle borders
    'shadow': '#010409',          # Shadows for depth
}
