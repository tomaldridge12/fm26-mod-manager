import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import shutil
import os
import zipfile
import rarfile
import platform
from pathlib import Path
from datetime import datetime
import hashlib

class FM26ModManager:
    def __init__(self, root):
        self.root = root
        self.root.title("FM26 Mod Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Detect platform and set default game path
        self.system = platform.system()
        self.game_path = self.detect_game_path()
        
        # Config file for storing settings and mod data
        self.config_file = Path.home() / ".fm26_mod_manager" / "config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Backup directory
        self.backup_dir = Path.home() / ".fm26_mod_manager" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.mods = []
        self.load_config()
        
        self.create_ui()
        self.refresh_mod_list()
        
    def detect_game_path(self):
        """Detect the game installation path based on OS"""
        if self.system == "Windows":
            # Common Steam library locations
            possible_paths = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64"),
                Path("D:/SteamLibrary/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64"),
                Path("E:/SteamLibrary/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64"),
            ]
        elif self.system == "Darwin":  # macOS
            possible_paths = [
                Path.home() / "Library/Application Support/Steam/steamapps/common/Football Manager 26/fm.app/Contents/Resources/Data/StreamingAssets/aa/StandaloneOSX"
            ]
        else:
            possible_paths = []
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        return ""
    
    def create_ui(self):
        """Create the modern UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabel', background='#1a1a2e', foreground='#e0e0e0', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#00d4ff')
        style.configure('TButton', font=('Segoe UI', 10), padding=10)
        style.map('TButton', background=[('active', '#00d4ff')])
        
        # Header
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(header_frame, text="⚽ FM26 Mod Manager", style='Title.TLabel')
        title_label.pack()
        
        # Game path section
        path_frame = ttk.Frame(self.root, style='TFrame')
        path_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        ttk.Label(path_frame, text="Game Path:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.path_var = tk.StringVar(value=self.game_path)
        path_entry = tk.Entry(path_frame, textvariable=self.path_var, font=('Segoe UI', 9), 
                            bg='#2a2a3e', fg='#e0e0e0', insertbackground='#00d4ff', 
                            relief=tk.FLAT, bd=0)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
        
        browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_game_path,
                              bg='#00d4ff', fg='#1a1a2e', font=('Segoe UI', 9, 'bold'),
                              relief=tk.FLAT, cursor='hand2', padx=15, pady=5)
        browse_btn.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(self.root, style='TFrame')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_btn = tk.Button(button_frame, text="+ Add Mod", command=self.add_mod,
                           bg='#00d4ff', fg='#1a1a2e', font=('Segoe UI', 10, 'bold'),
                           relief=tk.FLAT, cursor='hand2', padx=20, pady=10)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        backup_btn = tk.Button(button_frame, text="💾 Backup Original", command=self.backup_original,
                              bg='#4a4a5e', fg='#e0e0e0', font=('Segoe UI', 10),
                              relief=tk.FLAT, cursor='hand2', padx=20, pady=10)
        backup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        restore_btn = tk.Button(button_frame, text="↺ Restore Original", command=self.restore_original,
                               bg='#4a4a5e', fg='#e0e0e0', font=('Segoe UI', 10),
                               relief=tk.FLAT, cursor='hand2', padx=20, pady=10)
        restore_btn.pack(side=tk.LEFT)
        
        # Mod list
        list_frame = ttk.Frame(self.root, style='TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(list_frame, text="Installed Mods:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        # Treeview for mods
        tree_frame = tk.Frame(list_frame, bg='#2a2a3e')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(tree_frame, bg='#2a2a3e')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.mod_tree = ttk.Treeview(tree_frame, columns=('Status', 'Name', 'Files'),
                                     show='tree headings', yscrollcommand=scrollbar.set,
                                     selectmode='browse', height=15)
        
        style.configure('Treeview', background='#2a2a3e', foreground='#e0e0e0',
                       fieldbackground='#2a2a3e', borderwidth=0, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', background='#1a1a2e', foreground='#00d4ff',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#00d4ff')], 
                 foreground=[('selected', '#1a1a2e')])
        
        self.mod_tree.heading('#0', text='', anchor=tk.W)
        self.mod_tree.heading('Status', text='Status', anchor=tk.W)
        self.mod_tree.heading('Name', text='Mod Name', anchor=tk.W)
        self.mod_tree.heading('Files', text='Modified Files', anchor=tk.W)
        
        self.mod_tree.column('#0', width=50, stretch=False)
        self.mod_tree.column('Status', width=100, stretch=False)
        self.mod_tree.column('Name', width=300)
        self.mod_tree.column('Files', width=350)
        
        self.mod_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.mod_tree.yview)
        
        # Mod action buttons
        mod_button_frame = ttk.Frame(self.root, style='TFrame')
        mod_button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        enable_btn = tk.Button(mod_button_frame, text="Enable", command=self.enable_mod,
                              bg='#00ff88', fg='#1a1a2e', font=('Segoe UI', 9, 'bold'),
                              relief=tk.FLAT, cursor='hand2', padx=15, pady=8)
        enable_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        disable_btn = tk.Button(mod_button_frame, text="Disable", command=self.disable_mod,
                               bg='#ff6b6b', fg='#1a1a2e', font=('Segoe UI', 9, 'bold'),
                               relief=tk.FLAT, cursor='hand2', padx=15, pady=8)
        disable_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_btn = tk.Button(mod_button_frame, text="Remove", command=self.remove_mod,
                              bg='#4a4a5e', fg='#e0e0e0', font=('Segoe UI', 9),
                              relief=tk.FLAT, cursor='hand2', padx=15, pady=8)
        remove_btn.pack(side=tk.LEFT)
        
    def browse_game_path(self):
        """Browse for game installation directory"""
        path = filedialog.askdirectory(title="Select FM26 StreamingAssets/aa folder")
        if path:
            self.path_var.set(path)
            self.game_path = path
            self.save_config()
    
    def add_mod(self):
        """Add a new mod from archive or folder"""
        filetypes = [
            ("Archive files", "*.zip *.rar *.7z"),
            ("ZIP files", "*.zip"),
            ("RAR files", "*.rar"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="Select Mod Archive", filetypes=filetypes)
        if not file_path:
            return
        
        # Ask for mod name
        mod_name = tk.simpledialog.askstring("Mod Name", "Enter a name for this mod:",
                                             initialvalue=Path(file_path).stem)
        if not mod_name:
            return
        
        # Extract and analyze mod
        try:
            temp_dir = self.backup_dir / "temp_extract"
            temp_dir.mkdir(exist_ok=True)
            
            # Extract archive
            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            elif file_path.endswith('.rar'):
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    rar_ref.extractall(temp_dir)
            
            # Find all .bundle files
            bundle_files = list(temp_dir.rglob("*.bundle"))
            
            if not bundle_files:
                messagebox.showwarning("No Files Found", "No .bundle files found in the archive.")
                shutil.rmtree(temp_dir)
                return
            
            # Check for conflicts
            conflicts = self.check_conflicts([f.name for f in bundle_files])
            if conflicts:
                conflict_msg = "The following files conflict with existing mods:\n\n"
                for file, mod in conflicts.items():
                    conflict_msg += f"• {file} (used by '{mod}')\n"
                conflict_msg += "\nYou will need to disable conflicting mods to use this one."
                messagebox.showwarning("Conflicts Detected", conflict_msg)
            
            # Create mod entry
            mod_data = {
                'name': mod_name,
                'enabled': False,
                'files': [f.name for f in bundle_files],
                'file_paths': {f.name: str(f) for f in bundle_files},
                'added_date': datetime.now().isoformat()
            }
            
            # Copy files to permanent storage
            mod_storage = self.backup_dir / "mods" / mod_name
            mod_storage.mkdir(parents=True, exist_ok=True)
            
            for bundle_file in bundle_files:
                shutil.copy2(bundle_file, mod_storage / bundle_file.name)
            
            # Update file paths to permanent storage
            mod_data['file_paths'] = {f.name: str(mod_storage / f.name) for f in bundle_files}
            
            self.mods.append(mod_data)
            self.save_config()
            self.refresh_mod_list()
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            messagebox.showinfo("Success", f"Mod '{mod_name}' added successfully!\n\n"
                                          f"Files: {len(bundle_files)}\n"
                                          f"Status: Disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add mod: {str(e)}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def check_conflicts(self, files):
        """Check if files conflict with existing enabled mods"""
        conflicts = {}
        for mod in self.mods:
            if mod['enabled']:
                for file in files:
                    if file in mod['files']:
                        conflicts[file] = mod['name']
        return conflicts
    
    def enable_mod(self):
        """Enable selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to enable.")
            return
        
        item = self.mod_tree.item(selection[0])
        mod_name = item['values'][1]
        
        mod = next((m for m in self.mods if m['name'] == mod_name), None)
        if not mod:
            return
        
        if mod['enabled']:
            messagebox.showinfo("Already Enabled", "This mod is already enabled.")
            return
        
        # Check conflicts
        conflicts = self.check_conflicts(mod['files'])
        if conflicts:
            messagebox.showerror("Conflicts", "Cannot enable mod due to file conflicts.\n"
                                             "Disable conflicting mods first.")
            return
        
        # Backup originals if not already backed up
        self.backup_original(mod['files'])
        
        # Copy mod files to game directory
        try:
            game_path = Path(self.path_var.get())
            if not game_path.exists():
                messagebox.showerror("Error", "Game path does not exist!")
                return
            
            for file_name, file_path in mod['file_paths'].items():
                dest = game_path / file_name
                shutil.copy2(file_path, dest)
            
            mod['enabled'] = True
            self.save_config()
            self.refresh_mod_list()
            messagebox.showinfo("Success", f"Mod '{mod_name}' enabled successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable mod: {str(e)}")
    
    def disable_mod(self):
        """Disable selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to disable.")
            return
        
        item = self.mod_tree.item(selection[0])
        mod_name = item['values'][1]
        
        mod = next((m for m in self.mods if m['name'] == mod_name), None)
        if not mod or not mod['enabled']:
            messagebox.showinfo("Not Enabled", "This mod is not currently enabled.")
            return
        
        # Restore original files
        try:
            self.restore_files(mod['files'])
            mod['enabled'] = False
            self.save_config()
            self.refresh_mod_list()
            messagebox.showinfo("Success", f"Mod '{mod_name}' disabled successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable mod: {str(e)}")
    
    def remove_mod(self):
        """Remove selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to remove.")
            return
        
        item = self.mod_tree.item(selection[0])
        mod_name = item['values'][1]
        
        if not messagebox.askyesno("Confirm", f"Remove mod '{mod_name}'?"):
            return
        
        mod = next((m for m in self.mods if m['name'] == mod_name), None)
        if not mod:
            return
        
        # Disable if enabled
        if mod['enabled']:
            self.restore_files(mod['files'])
        
        # Remove mod files
        mod_storage = self.backup_dir / "mods" / mod_name
        if mod_storage.exists():
            shutil.rmtree(mod_storage)
        
        self.mods.remove(mod)
        self.save_config()
        self.refresh_mod_list()
        messagebox.showinfo("Success", f"Mod '{mod_name}' removed successfully!")
    
    def backup_original(self, specific_files=None):
        """Backup original game files"""
        game_path = Path(self.path_var.get())
        if not game_path.exists():
            messagebox.showerror("Error", "Game path does not exist!")
            return
        
        original_backup = self.backup_dir / "original"
        original_backup.mkdir(exist_ok=True)
        
        try:
            if specific_files:
                files_to_backup = specific_files
            else:
                files_to_backup = [f.name for f in game_path.glob("*.bundle")]
            
            backed_up = 0
            for file_name in files_to_backup:
                source = game_path / file_name
                dest = original_backup / file_name
                
                if source.exists() and not dest.exists():
                    shutil.copy2(source, dest)
                    backed_up += 1
            
            if not specific_files:
                messagebox.showinfo("Success", f"Backed up {backed_up} original files!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup files: {str(e)}")
    
    def restore_original(self):
        """Restore all original files"""
        if not messagebox.askyesno("Confirm", "Restore all original files?\n"
                                             "This will disable all mods."):
            return
        
        original_backup = self.backup_dir / "original"
        if not original_backup.exists():
            messagebox.showwarning("No Backup", "No original backup found!")
            return
        
        try:
            game_path = Path(self.path_var.get())
            for backup_file in original_backup.glob("*.bundle"):
                dest = game_path / backup_file.name
                shutil.copy2(backup_file, dest)
            
            # Disable all mods
            for mod in self.mods:
                mod['enabled'] = False
            
            self.save_config()
            self.refresh_mod_list()
            messagebox.showinfo("Success", "All original files restored!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore files: {str(e)}")
    
    def restore_files(self, file_names):
        """Restore specific files from backup"""
        original_backup = self.backup_dir / "original"
        game_path = Path(self.path_var.get())
        
        for file_name in file_names:
            backup_file = original_backup / file_name
            if backup_file.exists():
                dest = game_path / file_name
                shutil.copy2(backup_file, dest)
    
    def refresh_mod_list(self):
        """Refresh the mod list display"""
        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)
        
        for mod in self.mods:
            status = "✓ Enabled" if mod['enabled'] else "○ Disabled"
            status_color = '#00ff88' if mod['enabled'] else '#ff6b6b'
            files = ', '.join(mod['files'][:3])
            if len(mod['files']) > 3:
                files += f" (+{len(mod['files'])-3} more)"
            
            self.mod_tree.insert('', tk.END, values=(status, mod['name'], files),
                                tags=('enabled' if mod['enabled'] else 'disabled',))
        
        self.mod_tree.tag_configure('enabled', foreground='#00ff88')
        self.mod_tree.tag_configure('disabled', foreground='#ff6b6b')
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.game_path = data.get('game_path', self.game_path)
                self.mods = data.get('mods', [])
    
    def save_config(self):
        """Save configuration to file"""
        data = {
            'game_path': self.path_var.get(),
            'mods': self.mods
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, indent=2, fp=f)

if __name__ == "__main__":
    # Note: This requires the rarfile package: pip install rarfile
    # Also requires the unrar utility to be installed on the system
    root = tk.Tk()
    app = FM26ModManager(root)
    root.mainloop()