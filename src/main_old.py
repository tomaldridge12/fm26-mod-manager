import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import shutil
import os
import zipfile
import rarfile
import platform
from pathlib import Path
from datetime import datetime
import hashlib
import traceback

class FM26ModManager:
    def __init__(self, root):
        self.root = root
        self.root.title("FM26 Mod Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')

        # Detect platform
        self.system = platform.system()

        # Initialize paths
        self.fm_root_path = None
        self.data_path = None

        # Try to auto-detect game installation
        self.fm_root_path = self.detect_game_installation()
        if self.fm_root_path:
            self.data_path = self.get_data_path(self.fm_root_path)

        # Setup config and backup directories
        self.setup_storage_paths()

        self.mods = []
        self.load_config()

        # Update paths after loading config in case user had a custom path
        if self.fm_root_path:
            self.data_path = self.get_data_path(self.fm_root_path)

        self.create_ui()
        self.refresh_mod_list()

        # Show warning if no valid installation found
        if not self.fm_root_path or not self.validate_installation(self.fm_root_path):
            self.show_status("No valid FM26 installation detected. Please browse to your installation folder.", "warning")
        
    def detect_game_installation(self):
        """Detect the FM26 root folder based on OS"""
        if self.system == "Windows":
            # Common Steam library locations
            possible_roots = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/Football Manager 26"),
                Path("D:/SteamLibrary/steamapps/common/Football Manager 26"),
                Path("E:/SteamLibrary/steamapps/common/Football Manager 26"),
            ]
        elif self.system == "Darwin":  # macOS
            possible_roots = [
                Path.home() / "Library/Application Support/Steam/steamapps/common/Football Manager 26"
            ]
        else:
            return None

        for root in possible_roots:
            if root.exists() and self.validate_installation(root):
                return str(root)
        return None

    def validate_installation(self, fm_root):
        """Validate that the folder contains a valid FM26 installation"""
        if not fm_root:
            return False

        try:
            root_path = Path(fm_root)
            if not root_path.exists():
                return False

            # Check for expected structure based on OS
            data_path = self.get_data_path(fm_root)
            if not data_path:
                return False

            data_path_obj = Path(data_path)
            return data_path_obj.exists() and data_path_obj.is_dir()

        except Exception:
            return False

    def get_data_path(self, fm_root):
        """Get the data path (StandalonePlatform folder) from FM26 root"""
        if not fm_root:
            return None

        try:
            root_path = Path(fm_root)

            if self.system == "Windows":
                data_path = root_path / "fm_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
            elif self.system == "Darwin":  # macOS
                data_path = root_path / "fm.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "aa" / "StandaloneOSX"
            else:
                return None

            if data_path.exists():
                return str(data_path)
            return None

        except Exception:
            return None

    def setup_storage_paths(self):
        """Setup config and backup directory paths"""
        try:
            if self.fm_root_path:
                base_path = Path(self.fm_root_path) / ".fm26_mod_manager"
            else:
                base_path = Path.home() / ".fm26_mod_manager"

            base_path.mkdir(exist_ok=True)
            self.config_file = base_path / "config.json"
            self.backup_dir = base_path / "backups"
            self.backup_dir.mkdir(exist_ok=True)

        except Exception as e:
            # Fallback to home directory
            base_path = Path.home() / ".fm26_mod_manager"
            base_path.mkdir(exist_ok=True)
            self.config_file = base_path / "config.json"
            self.backup_dir = base_path / "backups"
            self.backup_dir.mkdir(exist_ok=True)
    
    
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

        ttk.Label(path_frame, text="Installation:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))

        self.path_var = tk.StringVar(value=self.fm_root_path or "")
        path_entry = tk.Entry(path_frame, textvariable=self.path_var, font=('Segoe UI', 9),
                            bg='#2a2a3e', fg='#e0e0e0', insertbackground='#00d4ff',
                            relief=tk.FLAT, bd=0, state='readonly')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)

        browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_game_path,
                              bg='#00d4ff', fg='#1a1a2e', font=('Segoe UI', 9, 'bold'),
                              relief=tk.FLAT, cursor='hand2', padx=15, pady=5)
        browse_btn.pack(side=tk.LEFT)

        # Status bar
        self.status_frame = tk.Frame(self.root, bg='#2a2a3e', height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(self.status_frame, text="Ready",
                                     bg='#2a2a3e', fg='#e0e0e0',
                                     font=('Segoe UI', 9), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(self.root, style='TFrame')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_btn = tk.Button(button_frame, text="+ Add Mod", command=self.add_mod,
                           bg='#00d4ff', fg='#1a1a2e', font=('Segoe UI', 10, 'bold'),
                           relief=tk.FLAT, cursor='hand2', padx=20, pady=10)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        restore_btn = tk.Button(button_frame, text="↺ Restore All", command=self.restore_original,
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
        
    def show_status(self, message, status_type="info"):
        """Show status message in status bar"""
        if not hasattr(self, 'status_label'):
            return

        colors = {
            "info": "#00d4ff",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff6b6b"
        }

        self.status_label.config(text=message, fg=colors.get(status_type, "#e0e0e0"))
        self.root.update_idletasks()

    def browse_game_path(self):
        """Browse for Football Manager 26 installation folder"""
        initial_dir = self.fm_root_path if self.fm_root_path else None

        path = filedialog.askdirectory(
            title="Select Football Manager 26 folder",
            initialdir=initial_dir
        )

        if not path:
            return

        try:
            path_obj = Path(path)

            # Check if this is or contains the FM26 folder
            if "Football Manager 26" not in path_obj.parts:
                # Check if user selected a parent folder
                fm26_folder = path_obj / "Football Manager 26"
                if fm26_folder.exists():
                    path = str(fm26_folder)
                else:
                    self.show_status("Please select the 'Football Manager 26' folder", "error")
                    messagebox.showerror(
                        "Invalid Selection",
                        "Please select the 'Football Manager 26' folder.\n\n"
                        "This folder is typically located at:\n"
                        "Steam/steamapps/common/Football Manager 26"
                    )
                    return

            # Validate the installation
            if not self.validate_installation(path):
                self.show_status("Invalid FM26 installation detected", "error")
                messagebox.showerror(
                    "Invalid Installation",
                    "The selected folder does not contain a valid FM26 installation.\n\n"
                    "Please ensure you've selected the correct 'Football Manager 26' folder."
                )
                return

            # Update paths
            self.fm_root_path = path
            self.data_path = self.get_data_path(path)

            if not self.data_path:
                self.show_status("Could not locate game data files", "error")
                messagebox.showerror(
                    "Data Files Not Found",
                    "Could not locate the game data files.\n\n"
                    "Please ensure FM26 is properly installed."
                )
                return

            # Update UI
            self.path_var.set(path)

            # Update storage paths
            self.setup_storage_paths()

            # Save config
            self.save_config()

            self.show_status(f"Installation path updated successfully", "success")

        except Exception as e:
            self.show_status("Error updating installation path", "error")
            messagebox.showerror(
                "Error",
                f"An error occurred while updating the installation path:\n\n{str(e)}"
            )
    
    def add_mod(self):
        """Add a new mod from archive or folder"""
        if not self.validate_paths():
            return

        filetypes = [
            ("Archive files", "*.zip *.rar *.7z"),
            ("ZIP files", "*.zip"),
            ("RAR files", "*.rar"),
            ("All files", "*.*")
        ]

        file_path = filedialog.askopenfilename(title="Select Mod Archive", filetypes=filetypes)
        if not file_path:
            return

        # Validate file exists
        if not Path(file_path).exists():
            self.show_status("Selected file does not exist", "error")
            messagebox.showerror("File Not Found", "The selected file could not be found.")
            return

        # Ask for mod name
        mod_name = simpledialog.askstring(
            "Mod Name",
            "Enter a name for this mod:",
            initialvalue=Path(file_path).stem
        )

        if not mod_name:
            return

        # Validate mod name
        mod_name = mod_name.strip()
        if not mod_name:
            self.show_status("Mod name cannot be empty", "error")
            messagebox.showerror("Invalid Name", "Mod name cannot be empty.")
            return

        # Check for duplicate names
        if any(m['name'] == mod_name for m in self.mods):
            self.show_status("Mod name already exists", "error")
            messagebox.showerror(
                "Duplicate Name",
                f"A mod named '{mod_name}' already exists.\nPlease choose a different name."
            )
            return

        temp_dir = None
        try:
            self.show_status(f"Extracting '{mod_name}'...", "info")

            temp_dir = self.backup_dir / "temp_extract"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)

            # Extract archive
            try:
                if file_path.endswith('.zip'):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif file_path.endswith('.rar'):
                    with rarfile.RarFile(file_path, 'r') as rar_ref:
                        rar_ref.extractall(temp_dir)
                else:
                    self.show_status("Unsupported archive format", "error")
                    messagebox.showerror(
                        "Unsupported Format",
                        "Only ZIP and RAR archives are supported."
                    )
                    return
            except Exception as e:
                self.show_status("Failed to extract archive", "error")
                messagebox.showerror(
                    "Extraction Failed",
                    f"Could not extract the archive:\n\n{str(e)}"
                )
                return

            # Find all .bundle files
            bundle_files = list(temp_dir.rglob("*.bundle"))

            if not bundle_files:
                self.show_status("No bundle files found in archive", "warning")
                messagebox.showwarning(
                    "No Files Found",
                    "No .bundle files found in the archive.\n\n"
                    "Please ensure the archive contains FM26 mod files."
                )
                return

            # Check for conflicts
            conflicts = self.check_conflicts([f.name for f in bundle_files])
            if conflicts:
                conflict_msg = "The following files conflict with enabled mods:\n\n"
                for file, mod in conflicts.items():
                    conflict_msg += f"  • {file} (used by '{mod}')\n"
                conflict_msg += "\nThe mod will be added but you'll need to disable conflicting mods to enable it."
                messagebox.showwarning("Conflicts Detected", conflict_msg)

            self.show_status(f"Installing '{mod_name}'...", "info")

            # Create mod entry
            mod_data = {
                'name': mod_name,
                'enabled': False,
                'files': [f.name for f in bundle_files],
                'file_paths': {},
                'added_date': datetime.now().isoformat()
            }

            # Copy files to permanent storage
            mod_storage = self.backup_dir / "mods" / mod_name
            if mod_storage.exists():
                shutil.rmtree(mod_storage)
            mod_storage.mkdir(parents=True, exist_ok=True)

            for bundle_file in bundle_files:
                shutil.copy2(bundle_file, mod_storage / bundle_file.name)

            # Update file paths to permanent storage
            mod_data['file_paths'] = {f.name: str(mod_storage / f.name) for f in bundle_files}

            self.mods.append(mod_data)
            self.save_config()
            self.refresh_mod_list()

            self.show_status(f"Mod '{mod_name}' added successfully", "success")
            messagebox.showinfo(
                "Success",
                f"Mod '{mod_name}' added successfully!\n\n"
                f"Files: {len(bundle_files)}\n"
                f"Status: Disabled"
            )

        except Exception as e:
            self.show_status("Failed to add mod", "error")
            messagebox.showerror(
                "Error",
                f"An error occurred while adding the mod:\n\n{str(e)}\n\n"
                f"Please try again or check the archive file."
            )

        finally:
            # Clean up temp directory
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

    def validate_paths(self):
        """Validate that necessary paths are set and valid"""
        if not self.fm_root_path or not self.data_path:
            self.show_status("No FM26 installation configured", "error")
            messagebox.showerror(
                "Installation Required",
                "Please select your Football Manager 26 installation folder first.\n\n"
                "Use the 'Browse' button to locate your FM26 installation."
            )
            return False

        if not Path(self.data_path).exists():
            self.show_status("FM26 data path not found", "error")
            messagebox.showerror(
                "Installation Error",
                "The FM26 data files could not be found.\n\n"
                "Please ensure FM26 is properly installed and select the correct folder."
            )
            return False

        return True
    
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
        if not self.validate_paths():
            return

        selection = self.mod_tree.selection()
        if not selection:
            self.show_status("No mod selected", "warning")
            messagebox.showwarning("No Selection", "Please select a mod to enable.")
            return

        try:
            item = self.mod_tree.item(selection[0])
            mod_name = item['values'][1]

            mod = next((m for m in self.mods if m['name'] == mod_name), None)
            if not mod:
                self.show_status("Mod not found", "error")
                messagebox.showerror("Error", "Selected mod could not be found.")
                return

            if mod['enabled']:
                self.show_status("Mod is already enabled", "info")
                messagebox.showinfo("Already Enabled", "This mod is already enabled.")
                return

            # Check conflicts
            conflicts = self.check_conflicts(mod['files'])
            if conflicts:
                self.show_status("Cannot enable due to conflicts", "error")
                conflict_list = "\n".join([f"  • {file} (used by '{mod_name}')" for file, mod_name in conflicts.items()])
                messagebox.showerror(
                    "Conflicts Detected",
                    f"Cannot enable mod due to file conflicts:\n\n{conflict_list}\n\n"
                    "Please disable the conflicting mods first."
                )
                return

            self.show_status(f"Enabling '{mod_name}'...", "info")

            # Backup originals if not already backed up
            if not self.backup_original(mod['files']):
                return

            # Validate mod files exist
            missing_files = []
            for file_name, file_path in mod['file_paths'].items():
                if not Path(file_path).exists():
                    missing_files.append(file_name)

            if missing_files:
                self.show_status("Mod files are missing", "error")
                messagebox.showerror(
                    "Missing Files",
                    f"The following mod files are missing:\n\n" +
                    "\n".join([f"  • {f}" for f in missing_files]) +
                    "\n\nThe mod may have been corrupted or deleted."
                )
                return

            # Copy mod files to game directory
            game_path = Path(self.data_path)
            copied_files = []

            try:
                for file_name, file_path in mod['file_paths'].items():
                    dest = game_path / file_name
                    shutil.copy2(file_path, dest)
                    copied_files.append(file_name)

                mod['enabled'] = True
                self.save_config()
                self.refresh_mod_list()
                self.show_status(f"Mod '{mod_name}' enabled successfully", "success")
                messagebox.showinfo("Success", f"Mod '{mod_name}' has been enabled successfully!")

            except Exception as e:
                # Rollback copied files
                self.show_status("Failed to enable mod, rolling back", "error")
                for file_name in copied_files:
                    try:
                        self.restore_files([file_name])
                    except Exception:
                        pass

                messagebox.showerror(
                    "Enable Failed",
                    f"Failed to enable mod:\n\n{str(e)}\n\n"
                    "Any partial changes have been rolled back."
                )

        except Exception as e:
            self.show_status("Unexpected error", "error")
            messagebox.showerror(
                "Error",
                f"An unexpected error occurred:\n\n{str(e)}"
            )
    
    def disable_mod(self):
        """Disable selected mod"""
        if not self.validate_paths():
            return

        selection = self.mod_tree.selection()
        if not selection:
            self.show_status("No mod selected", "warning")
            messagebox.showwarning("No Selection", "Please select a mod to disable.")
            return

        try:
            item = self.mod_tree.item(selection[0])
            mod_name = item['values'][1]

            mod = next((m for m in self.mods if m['name'] == mod_name), None)
            if not mod:
                self.show_status("Mod not found", "error")
                messagebox.showerror("Error", "Selected mod could not be found.")
                return

            if not mod['enabled']:
                self.show_status("Mod is not enabled", "info")
                messagebox.showinfo("Not Enabled", "This mod is not currently enabled.")
                return

            self.show_status(f"Disabling '{mod_name}'...", "info")

            # Restore original files
            if not self.restore_files(mod['files']):
                self.show_status("Failed to restore original files", "error")
                return

            mod['enabled'] = False
            self.save_config()
            self.refresh_mod_list()
            self.show_status(f"Mod '{mod_name}' disabled successfully", "success")
            messagebox.showinfo("Success", f"Mod '{mod_name}' has been disabled successfully!")

        except Exception as e:
            self.show_status("Failed to disable mod", "error")
            messagebox.showerror(
                "Error",
                f"Failed to disable mod:\n\n{str(e)}"
            )
    
    def remove_mod(self):
        """Remove selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            self.show_status("No mod selected", "warning")
            messagebox.showwarning("No Selection", "Please select a mod to remove.")
            return

        try:
            item = self.mod_tree.item(selection[0])
            mod_name = item['values'][1]

            mod = next((m for m in self.mods if m['name'] == mod_name), None)
            if not mod:
                self.show_status("Mod not found", "error")
                messagebox.showerror("Error", "Selected mod could not be found.")
                return

            # Confirm removal
            if not messagebox.askyesno(
                "Confirm Removal",
                f"Are you sure you want to remove '{mod_name}'?\n\n"
                f"This will permanently delete the mod files."
            ):
                return

            self.show_status(f"Removing '{mod_name}'...", "info")

            # Disable if enabled
            if mod['enabled']:
                try:
                    self.restore_files(mod['files'])
                except Exception as e:
                    self.show_status("Warning: Could not restore original files", "warning")

            # Remove mod files
            mod_storage = self.backup_dir / "mods" / mod_name
            if mod_storage.exists():
                try:
                    shutil.rmtree(mod_storage)
                except Exception as e:
                    self.show_status("Warning: Could not delete mod files", "warning")

            self.mods.remove(mod)
            self.save_config()
            self.refresh_mod_list()
            self.show_status(f"Mod '{mod_name}' removed successfully", "success")
            messagebox.showinfo("Success", f"Mod '{mod_name}' has been removed successfully!")

        except Exception as e:
            self.show_status("Failed to remove mod", "error")
            messagebox.showerror(
                "Error",
                f"Failed to remove mod:\n\n{str(e)}"
            )
    
    def backup_original(self, specific_files):
        """
        Backup only specific original game files before they're modified.
        This saves space by only backing up files that will be overwritten.
        Returns True on success, False on failure.
        """
        if not self.validate_paths():
            return False

        try:
            game_path = Path(self.data_path)
            original_backup = self.backup_dir / "original"
            original_backup.mkdir(exist_ok=True)

            backed_up = 0
            skipped = 0
            failed_files = []

            for file_name in specific_files:
                source = game_path / file_name
                dest = original_backup / file_name

                # Skip if already backed up
                if dest.exists():
                    skipped += 1
                    continue

                # Skip if source doesn't exist (might be a new file from mod)
                if not source.exists():
                    continue

                try:
                    shutil.copy2(source, dest)
                    backed_up += 1
                except Exception as e:
                    failed_files.append(f"{file_name} ({str(e)})")

            # Only show errors if backup actually failed
            if failed_files:
                self.show_status("Some files could not be backed up", "warning")
                messagebox.showerror(
                    "Backup Warning",
                    f"Failed to backup some files:\n\n" +
                    "\n".join([f"  • {f}" for f in failed_files]) +
                    "\n\nYou may want to manually backup these files before enabling this mod."
                )
                return False

            # Silent success - backups happen automatically
            if backed_up > 0:
                self.show_status(f"Backed up {backed_up} file(s) before modification", "info")

            return True

        except Exception as e:
            self.show_status("Backup failed", "error")
            messagebox.showerror(
                "Backup Failed",
                f"Failed to backup original files:\n\n{str(e)}\n\n"
                "Cannot enable mod without backing up original files first."
            )
            return False
    
    def restore_original(self):
        """Restore all backed up original files and disable all mods"""
        if not self.validate_paths():
            return

        original_backup = self.backup_dir / "original"
        if not original_backup.exists() or not list(original_backup.glob("*.bundle")):
            self.show_status("No backups found", "warning")
            messagebox.showinfo(
                "No Backups Found",
                "No backed up files found.\n\n"
                "Original files are only backed up when mods modify them.\n"
                "If no mods have been enabled yet, there's nothing to restore."
            )
            return

        backup_count = len(list(original_backup.glob("*.bundle")))
        enabled_mods = [m for m in self.mods if m['enabled']]

        if not messagebox.askyesno(
            "Confirm Restore",
            f"Restore {backup_count} backed up file(s) to their original state?\n\n"
            f"This will disable {len(enabled_mods)} enabled mod(s) and restore\n"
            f"all modified files to their vanilla versions."
        ):
            return

        try:
            self.show_status("Restoring original files...", "info")

            game_path = Path(self.data_path)
            restored = 0
            failed_files = []

            for backup_file in original_backup.glob("*.bundle"):
                try:
                    dest = game_path / backup_file.name
                    shutil.copy2(backup_file, dest)
                    restored += 1
                except Exception as e:
                    failed_files.append(f"{backup_file.name} ({str(e)})")

            # Disable all mods
            for mod in self.mods:
                mod['enabled'] = False

            self.save_config()
            self.refresh_mod_list()

            if failed_files:
                self.show_status("Restore completed with errors", "warning")
                messagebox.showwarning(
                    "Restore Completed with Errors",
                    f"Restored {restored} of {backup_count} files.\n\n"
                    f"Failed to restore:\n" + "\n".join([f"  • {f}" for f in failed_files])
                )
            else:
                self.show_status(f"Restored {restored} original files", "success")
                messagebox.showinfo(
                    "Success",
                    f"Successfully restored {restored} original file(s)!\n\n"
                    f"All mods have been disabled."
                )

        except Exception as e:
            self.show_status("Restore failed", "error")
            messagebox.showerror(
                "Restore Failed",
                f"Failed to restore files:\n\n{str(e)}"
            )
    
    def restore_files(self, file_names):
        """Restore specific files from backup. Returns True on success, False on failure."""
        try:
            original_backup = self.backup_dir / "original"
            game_path = Path(self.data_path)

            if not original_backup.exists():
                messagebox.showerror(
                    "No Backup",
                    "Original backup folder not found.\n\n"
                    "Cannot restore files without a backup."
                )
                return False

            missing_backups = []
            failed_restores = []

            for file_name in file_names:
                backup_file = original_backup / file_name

                if not backup_file.exists():
                    missing_backups.append(file_name)
                    continue

                try:
                    dest = game_path / file_name
                    shutil.copy2(backup_file, dest)
                except Exception as e:
                    failed_restores.append(f"{file_name} ({str(e)})")

            if missing_backups or failed_restores:
                error_msg = ""
                if missing_backups:
                    error_msg += "Missing backup files:\n" + "\n".join([f"  • {f}" for f in missing_backups])
                if failed_restores:
                    if error_msg:
                        error_msg += "\n\n"
                    error_msg += "Failed to restore:\n" + "\n".join([f"  • {f}" for f in failed_restores])

                messagebox.showerror("Restore Failed", error_msg)
                return False

            return True

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to restore files:\n\n{str(e)}"
            )
            return False
    
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
        try:
            # Try to load from FM26 root first, then fallback to home directory
            config_to_load = self.config_file

            # If FM root path exists, prefer config there
            if self.fm_root_path and Path(self.fm_root_path).exists():
                fm_root_config = Path(self.fm_root_path) / ".fm26_mod_manager" / "config.json"
                if fm_root_config.exists():
                    config_to_load = fm_root_config

            # Fallback to home directory config if FM root config doesn't exist
            if not config_to_load.exists():
                home_config = Path.home() / ".fm26_mod_manager" / "config.json"
                if home_config.exists():
                    config_to_load = home_config

            if config_to_load.exists():
                try:
                    with open(config_to_load, 'r') as f:
                        data = json.load(f)
                        loaded_fm_root = data.get('fm_root_path', self.fm_root_path)
                        if loaded_fm_root and self.validate_installation(loaded_fm_root):
                            self.fm_root_path = loaded_fm_root
                        self.mods = data.get('mods', [])
                except json.JSONDecodeError:
                    # Config file corrupted, start fresh
                    self.mods = []

        except Exception:
            # Silent failure for config load - just use defaults
            self.mods = []

    def save_config(self):
        """Save configuration to file"""
        try:
            data = {
                'fm_root_path': self.fm_root_path,
                'mods': self.mods
            }

            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first, then rename (atomic operation)
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            # Replace old config with new one
            if temp_file.exists():
                shutil.move(str(temp_file), str(self.config_file))

        except Exception as e:
            # Show error but don't crash
            if hasattr(self, 'show_status'):
                self.show_status("Warning: Failed to save configuration", "warning")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to prevent crashes"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    messagebox.showerror(
        "Unexpected Error",
        f"An unexpected error occurred:\n\n{exc_value}\n\n"
        f"The application will continue running, but you may want to restart it.\n\n"
        f"If this problem persists, please report it to the developer."
    )

if __name__ == "__main__":
    try:
        import sys
        # Set global exception handler
        sys.excepthook = handle_exception

        root = tk.Tk()

        # Handle window close event
        def on_closing():
            if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        app = FM26ModManager(root)
        root.mainloop()

    except Exception as e:
        messagebox.showerror(
            "Fatal Error",
            f"A fatal error occurred during startup:\n\n{str(e)}\n\n"
            f"The application cannot continue."
        )
        sys.exit(1)