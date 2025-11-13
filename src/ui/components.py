import tkinter as tk
from tkinter import ttk, scrolledtext
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

        # Track checked items
        self.checked_items = set()

        self.tree = ttk.Treeview(
            self.frame,
            columns=('Select', 'Status', 'Name', 'Date', 'Files'),
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='extended',
            height=8
        )

        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('Select', text='☐', anchor=tk.CENTER)
        self.tree.heading('Status', text='STATUS', anchor=tk.W)
        self.tree.heading('Name', text='MOD NAME', anchor=tk.W)
        self.tree.heading('Date', text='DATE ADDED', anchor=tk.W)
        self.tree.heading('Files', text='MODIFIED FILES', anchor=tk.W)

        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('Select', width=30, stretch=False, anchor=tk.CENTER)
        self.tree.column('Status', width=90, stretch=False)
        self.tree.column('Name', width=220)
        self.tree.column('Date', width=130, stretch=False)
        self.tree.column('Files', width=260)

        # Bind click on Select column to toggle checkbox
        self.tree.bind('<Button-1>', self._on_click)

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
        self.checked_items.clear()

    def add_mod(self, mod_data: dict):
        """Add mod to the tree."""
        checkbox = "☐"  # Unchecked by default
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
        self.tree.insert('', tk.END, values=(checkbox, status, mod_data['name'], formatted_date, files), tags=(tag,))

    def _on_click(self, event):
        """Handle click events for checkbox toggling."""
        region = self.tree.identify_region(event.x, event.y)
        if region == 'heading':
            column = self.tree.identify_column(event.x)
            if column == '#1':  # Select column
                self._toggle_all()
        elif region == 'cell':
            column = self.tree.identify_column(event.x)
            if column == '#1':  # Select column
                item = self.tree.identify_row(event.y)
                if item:
                    self._toggle_item(item)

    def _toggle_item(self, item):
        """Toggle checkbox for an item."""
        if item in self.checked_items:
            self.checked_items.remove(item)
            values = list(self.tree.item(item, 'values'))
            values[0] = "☐"
            self.tree.item(item, values=values)
        else:
            self.checked_items.add(item)
            values = list(self.tree.item(item, 'values'))
            values[0] = "☑"
            self.tree.item(item, values=values)

    def _toggle_all(self):
        """Toggle all checkboxes."""
        all_items = self.tree.get_children()
        if len(self.checked_items) == len(all_items):
            # Uncheck all
            for item in all_items:
                if item in self.checked_items:
                    self.checked_items.remove(item)
                    values = list(self.tree.item(item, 'values'))
                    values[0] = "☐"
                    self.tree.item(item, values=values)
            self.tree.heading('Select', text='☐')
        else:
            # Check all
            for item in all_items:
                if item not in self.checked_items:
                    self.checked_items.add(item)
                    values = list(self.tree.item(item, 'values'))
                    values[0] = "☑"
                    self.tree.item(item, values=values)
            self.tree.heading('Select', text='☑')

    def get_selection(self):
        """Get currently selected item (for single selection)."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return item['values'][2] if item['values'] else None  # Index 2 is Name now

    def get_checked_items(self):
        """Get list of checked mod names."""
        checked_names = []
        for item in self.checked_items:
            values = self.tree.item(item, 'values')
            if values:
                checked_names.append(values[2])  # Index 2 is Name
        return checked_names


class ExpandableLogViewer:
    """Expandable log viewer that sits under the status bar."""

    def __init__(self, parent: tk.Widget):
        """
        Create expandable log viewer.

        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.expanded = False
        self.log_buffer = []  # Store all logs with their levels

        # Main container
        self.container = tk.Frame(
            parent,
            bg=COLORS['bg_tertiary'],
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            highlightcolor=COLORS['border']
        )

        # Toggle button bar
        self.toggle_bar = tk.Frame(
            self.container,
            bg=COLORS['bg_tertiary'],
            height=36
        )
        self.toggle_bar.pack(fill=tk.X)
        self.toggle_bar.pack_propagate(False)

        # Toggle button
        self.toggle_btn = tk.Button(
            self.toggle_bar,
            text="▼  Show Logs",
            command=self._toggle,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8,
            anchor=tk.W,
            borderwidth=0
        )
        self.toggle_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.toggle_btn.bind('<Enter>', lambda e: self.toggle_btn.config(bg=COLORS['bg_elevated']))
        self.toggle_btn.bind('<Leave>', lambda e: self.toggle_btn.config(bg=COLORS['bg_tertiary']))

        # Clear logs button
        self.clear_btn = tk.Button(
            self.toggle_bar,
            text="Clear Logs",
            command=self._clear_logs,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8,
            borderwidth=0
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=(0, 15))

        self.clear_btn.bind('<Enter>', lambda e: self.clear_btn.config(bg=COLORS['bg_elevated'], fg=COLORS['error']))
        self.clear_btn.bind('<Leave>', lambda e: self.clear_btn.config(bg=COLORS['bg_tertiary'], fg=COLORS['fg_secondary']))

        # Log content frame (initially hidden)
        self.log_frame = None
        self.log_text = None
        self.clear_callback = None

    def pack(self, **kwargs):
        """Pack the container."""
        self.container.pack(**kwargs)

    def set_clear_callback(self, callback: Callable):
        """Set callback for clearing logs."""
        self.clear_callback = callback

    def _toggle(self):
        """Toggle log viewer expansion."""
        if self.expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self):
        """Expand the log viewer."""
        self.expanded = True
        self.toggle_btn.config(text="▲  Hide Logs")

        # Create log frame
        self.log_frame = tk.Frame(
            self.container,
            bg=COLORS['bg_primary']
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Scrolled text widget
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=12,
            font=('Consolas', 9),
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            insertbackground=COLORS['accent'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED,
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            highlightcolor=COLORS['accent']
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        # Configure tags for different log levels
        self.log_text.tag_configure('info', foreground=COLORS['info'])
        self.log_text.tag_configure('success', foreground=COLORS['success'])
        self.log_text.tag_configure('warning', foreground=COLORS['warning'])
        self.log_text.tag_configure('error', foreground=COLORS['error'])
        self.log_text.tag_configure('debug', foreground=COLORS['fg_secondary'])

        # Populate from buffer
        self.log_text.config(state=tk.NORMAL)
        for message, level in self.log_buffer:
            self.log_text.insert(tk.END, message, level)
        self.log_text.see(tk.END)  # Scroll to bottom
        self.log_text.config(state=tk.DISABLED)

    def _collapse(self):
        """Collapse the log viewer."""
        self.expanded = False
        self.toggle_btn.config(text="▼  Show Logs")

        if self.log_frame:
            self.log_frame.destroy()
            self.log_frame = None
            self.log_text = None

    def _clear_logs(self):
        """Clear the log display and call callback."""
        # Clear buffer
        self.log_buffer.clear()

        # Clear visible logs if expanded
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            self.log_text.config(state=tk.DISABLED)

        if self.clear_callback:
            self.clear_callback()

    def append_log(self, message: str, level: str = 'info'):
        """
        Append a log message.

        Args:
            message: Log message
            level: Log level (info, success, warning, error, debug)
        """
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}\n"

        # Always add to buffer
        self.log_buffer.append((formatted_message, level))

        # Update visible widget if expanded
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, formatted_message, level)
            self.log_text.see(tk.END)  # Auto-scroll to bottom
            self.log_text.config(state=tk.DISABLED)

    def load_logs(self, log_contents: str):
        """
        Load existing log contents.

        Args:
            log_contents: Full log file contents
        """
        if not self.log_text:
            return

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', log_contents)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


class ModDetailsPanel:
    """Side panel showing detailed information about selected mod."""

    def __init__(self, parent: tk.Widget):
        """
        Create mod details panel.

        Args:
            parent: Parent widget
        """
        self.container = tk.Frame(
            parent,
            bg=COLORS['bg_secondary'],
            highlightthickness=1,
            highlightbackground=COLORS['border'],
            width=300
        )
        self.container.pack_propagate(False)

        # Header
        header = tk.Frame(self.container, bg=COLORS['bg_tertiary'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Mod Details",
            bg=COLORS['bg_tertiary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        title.pack(side=tk.LEFT, padx=15, pady=10)

        # Scrollable content
        canvas = tk.Canvas(
            self.container,
            bg=COLORS['bg_secondary'],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            self.container,
            command=canvas.yview,
            bg=COLORS['bg_secondary'],
            troughcolor=COLORS['bg_secondary'],
            activebackground=COLORS['accent']
        )
        self.content = tk.Frame(canvas, bg=COLORS['bg_secondary'])

        self.content.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.content, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._show_placeholder()

    def pack(self, **kwargs):
        """Pack the container."""
        self.container.pack(**kwargs)

    def _show_placeholder(self):
        """Show placeholder when no mod is selected."""
        self._clear_content()

        placeholder = tk.Label(
            self.content,
            text="Select a mod to view details",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 10, 'italic')
        )
        placeholder.pack(padx=20, pady=40)

    def _clear_content(self):
        """Clear all content."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_mod_details(self, mod: dict):
        """
        Display mod details.

        Args:
            mod: Mod data dictionary
        """
        self._clear_content()

        # Mod name
        name_label = tk.Label(
            self.content,
            text=mod['name'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 12, 'bold'),
            wraplength=260,
            justify=tk.LEFT
        )
        name_label.pack(padx=15, pady=(15, 10), anchor=tk.W)

        # Status
        status_text = "✓ Enabled" if mod['enabled'] else "○ Disabled"
        status_color = COLORS['success'] if mod['enabled'] else COLORS['fg_secondary']
        status_label = tk.Label(
            self.content,
            text=status_text,
            bg=COLORS['bg_secondary'],
            fg=status_color,
            font=('Segoe UI', 10, 'bold')
        )
        status_label.pack(padx=15, pady=(0, 15), anchor=tk.W)

        # Separator
        self._add_separator()

        # Date added
        from datetime import datetime
        date_str = mod.get('added_date', '')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str)
                formatted_date = date_obj.strftime('%B %d, %Y at %I:%M %p')
            except (ValueError, AttributeError):
                formatted_date = 'Unknown'
        else:
            formatted_date = 'Unknown'

        self._add_detail_item("Added", formatted_date)

        # File count
        file_count = len(mod.get('files', []))
        self._add_detail_item("Files", str(file_count))

        # Size
        size_bytes = mod.get('size_bytes', 0)
        if size_bytes > 0:
            size_str = self._format_size(size_bytes)
            self._add_detail_item("Size", size_str)

        # Load order
        load_order = mod.get('load_order', 100)
        self._add_detail_item("Load Order", str(load_order))

        # Tags
        tags = mod.get('tags', [])
        if tags:
            self._add_separator()
            tags_header = tk.Label(
                self.content,
                text="Tags",
                bg=COLORS['bg_secondary'],
                fg=COLORS['fg_secondary'],
                font=('Segoe UI', 9, 'bold')
            )
            tags_header.pack(padx=15, pady=(10, 5), anchor=tk.W)

            tags_frame = tk.Frame(self.content, bg=COLORS['bg_secondary'])
            tags_frame.pack(padx=15, pady=(0, 10), anchor=tk.W)

            for tag in tags:
                tag_pill = tk.Frame(
                    tags_frame,
                    bg=COLORS['accent'],
                    highlightthickness=1,
                    highlightbackground=COLORS['accent_emphasis']
                )
                tag_pill.pack(side=tk.LEFT, padx=(0, 5), pady=2)

                tag_label = tk.Label(
                    tag_pill,
                    text=tag,
                    bg=COLORS['accent'],
                    fg='#ffffff',
                    font=('Segoe UI', 8)
                )
                tag_label.pack(padx=6, pady=3)

        # Files list
        self._add_separator()
        files_header = tk.Label(
            self.content,
            text="Modified Files",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        files_header.pack(padx=15, pady=(10, 5), anchor=tk.W)

        files_frame = tk.Frame(
            self.content,
            bg=COLORS['bg_tertiary'],
            highlightthickness=1,
            highlightbackground=COLORS['border']
        )
        files_frame.pack(padx=15, pady=(0, 15), fill=tk.X)

        for file in mod.get('files', []):
            file_label = tk.Label(
                files_frame,
                text=f"• {file}",
                bg=COLORS['bg_tertiary'],
                fg=COLORS['fg_primary'],
                font=('Consolas', 8),
                anchor=tk.W,
                wraplength=250,
                justify=tk.LEFT
            )
            file_label.pack(padx=10, pady=3, anchor=tk.W)

    def _format_size(self, size_bytes: int) -> str:
        """
        Format size in bytes to human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                if unit == 'B':
                    return f"{size_bytes} {unit}"
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _add_separator(self):
        """Add a visual separator."""
        separator = tk.Frame(
            self.content,
            bg=COLORS['border'],
            height=1
        )
        separator.pack(fill=tk.X, padx=15, pady=10)

    def _add_detail_item(self, label: str, value: str):
        """
        Add a detail item row.

        Args:
            label: Item label
            value: Item value
        """
        frame = tk.Frame(self.content, bg=COLORS['bg_secondary'])
        frame.pack(padx=15, pady=3, fill=tk.X)

        label_widget = tk.Label(
            frame,
            text=f"{label}:",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 9, 'bold')
        )
        label_widget.pack(side=tk.LEFT)

        value_widget = tk.Label(
            frame,
            text=value,
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 9)
        )
        value_widget.pack(side=tk.LEFT, padx=(5, 0))
