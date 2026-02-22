#!/usr/bin/env python3
"""
Sonarr Calendar Tracker Pro - Configuration Setup Tool
Creates and saves configuration settings to a hidden file
Now with refresh interval in hours and platform detection

Version History (Semantic Versioning):
======================================
v2.2.4 (2026-02-22) - Improved summary dialog layout
  - ScrollableMessageBox now has a larger default window (700x500)
  - Close button is always visible at the bottom, text area expands
  - No need to resize window to see the button

v2.2.3 (2026-02-22) - Save config to home directory & summary improvements
  - Configuration now saved in user's home folder (~/.sonarr_calendar_config/)
  - Loads from home folder first, falls back to script directory (migration support)
  - Summary dialog button renamed to "Close" for clarity
  - All version dates updated to 2026

v2.2.2 (2026-02-21) - Fixed right‑click paste and config location display
  - Right‑click menu now correctly pastes clipboard content
  - Displays the full path of the loaded configuration file
  - Improved scrollable summary dialog

v2.2.1 (2026-02-20) - Minor fixes
  - (Previous fixes)

v2.2.0 (2026-02-19) - Added enable_image_cache option & double‑paste fix
  - Added checkbox to enable/disable image caching
  - Fixed double‑paste in input fields

... (older versions)

Current Version: v2.2.4
"""

# Check for tkinter first
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError as e:
    print("\n" + "="*60)
    print("ERROR: tkinter is not installed on your system.")
    print("="*60)
    print("\nPlease install tkinter using your package manager:\n")
    
    import platform
    system = platform.system()
    
    if system == "Linux":
        print("  Debian/Ubuntu:")
        print("    sudo apt update")
        print("    sudo apt install python3-tk")
        print("\n  Fedora/RHEL/CentOS:")
        print("    sudo dnf install python3-tkinter")
        print("\n  Arch Linux:")
        print("    sudo pacman -S tk")
        print("\n  openSUSE:")
        print("    sudo zypper install python3-tk")
    elif system == "Darwin":  # macOS
        print("  Using Homebrew:")
        print("    brew install python-tk")
        print("\n  Or if using python.org installer, reinstall with tkinter option")
    elif system == "Windows":
        print("  Reinstall Python and make sure to check:")
        print("  'tcl/tk and IDLE' during installation")
    
    print("\n" + "="*60)
    print("After installing tkinter, run this script again.")
    print("="*60 + "\n")
    sys.exit(1)

import json
import os
import sys
import platform
from pathlib import Path

# Also check for requests (optional but recommended)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ============================================================================
# CONFIGURATION (v2.2.3 – home directory)
# ============================================================================
HOME_CONFIG_DIR = Path.home() / '.sonarr_calendar_config'
HOME_CONFIG_FILE = HOME_CONFIG_DIR / '.sonarr_calendar_config.json'
OLD_CONFIG_DIR = Path(__file__).parent
OLD_CONFIG_FILE = OLD_CONFIG_DIR / '.sonarr_calendar_config.json'
EXECUTION_DIR = Path.cwd()  # Get the directory where script was executed from

# Determine which config file to use (prefer home, fallback to old)
def get_config_path():
    if HOME_CONFIG_FILE.exists():
        return HOME_CONFIG_FILE
    elif OLD_CONFIG_FILE.exists():
        return OLD_CONFIG_FILE
    return HOME_CONFIG_FILE  # default (will create at home)

CONFIG_FILE = get_config_path()
CONFIG_DIR = CONFIG_FILE.parent

# ============================================================================
# CUSTOM DIALOG FOR CONFIGURATION SUMMARY (v2.2.4 – improved layout)
# ============================================================================
class ScrollableMessageBox:
    """A scrollable message box with always‑visible Close button."""
    def __init__(self, parent, title, text, width=80, height=25):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.transient(parent)
        self.top.grab_set()

        # Larger default size, but resizable
        self.top.geometry("700x500")
        self.top.minsize(500, 300)

        # Main frame
        main_frame = ttk.Frame(self.top, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbars – expands
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, width=width, height=height,
                               font=("Courier", 10))
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)  # read-only

        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Close button – always visible at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        btn = ttk.Button(button_frame, text="Close", command=self.top.destroy)
        btn.pack()

        self.top.update_idletasks()
        self.center_window()

    def center_window(self):
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'{width}x{height}+{x}+{y}')

# ============================================================================
# RIGHT-CLICK MENU CLASS (v2.1.0, fixed v2.2.2)
# ============================================================================
class RightClickMenu:
    """Right-click context menu for Entry widgets."""
    def __init__(self, widget):
        self.widget = widget
        self.menu = tk.Menu(widget, tearoff=0)
        self.menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        self.menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.menu.add_separator()
        self.menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        widget.bind("<Button-3>", self.show_menu)  # Linux/Windows right-click
        widget.bind("<Button-2>", self.show_menu)  # macOS right-click (Button-2)
        
        widget.bind("<Control-x>", lambda e: [self.cut(), "break"][0])
        widget.bind("<Control-c>", lambda e: [self.copy(), "break"][0])
        widget.bind("<Control-v>", lambda e: [self.paste(), "break"][0])
        widget.bind("<Control-a>", lambda e: [self.select_all(), "break"][0])
        
        widget.bind("<Command-x>", lambda e: [self.cut(), "break"][0])
        widget.bind("<Command-c>", lambda e: [self.copy(), "break"][0])
        widget.bind("<Command-v>", lambda e: [self.paste(), "break"][0])
        widget.bind("<Command-a>", lambda e: [self.select_all(), "break"][0])
    
    def show_menu(self, event):
        try:
            self.widget.focus_set()
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def cut(self):
        try:
            self.widget.event_generate("<<Cut>>")
        except:
            pass
    
    def copy(self):
        try:
            self.widget.event_generate("<<Copy>>")
        except:
            pass
    
    def paste(self):
        try:
            self.widget.event_generate("<<Paste>>")
        except:
            pass
    
    def select_all(self):
        try:
            self.widget.select_range(0, tk.END)
            self.widget.icursor(tk.END)
        except:
            pass

class SpinboxWithMenu(ttk.Spinbox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        RightClickMenu(self)

class ComboboxWithMenu(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        RightClickMenu(self)

class EntryWithMenu(ttk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        RightClickMenu(self)

class SonarrConfigApp:
    """Main application class for Sonarr Calendar Configuration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sonarr Calendar Pro - Configuration Setup")
        self.root.geometry("800x1000")
        self.root.resizable(False, False)
        
        self.system = platform.system()
        self.set_window_icon()
        self.center_window()
        
        if not REQUESTS_AVAILABLE:
            self.show_requests_warning()
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Sonarr Calendar Pro - Configuration", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # ========== Sonarr Connection ==========
        self.create_section_header(main_frame, "Sonarr Connection Settings", 1)
        
        # Sonarr URL
        ttk.Label(main_frame, text="Sonarr URL:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sonarr_url = EntryWithMenu(main_frame, width=50, font=('Arial', 10))
        self.sonarr_url.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(main_frame, text="e.g., http://192.168.1.100:8989", 
                 font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # API Key with visibility toggle
        ttk.Label(main_frame, text="API Key:", font=('Arial', 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        api_frame = ttk.Frame(main_frame)
        api_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.sonarr_api_key = EntryWithMenu(api_frame, width=45, font=('Arial', 10), show="•")
        self.sonarr_api_key.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.show_key = tk.BooleanVar(value=False)
        self.toggle_btn = ttk.Button(api_frame, text="👁️", width=3, command=self.toggle_api_key_visibility)
        self.toggle_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Find this in Sonarr > Settings > General", 
                 font=('Arial', 8), foreground='gray').grid(row=5, column=1, sticky=tk.W, padx=(10, 0))
        
        # Test Connection
        self.test_btn = ttk.Button(main_frame, text="Test Connection", command=self.test_connection)
        self.test_btn.grid(row=6, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        self.connection_status = ttk.Label(main_frame, text="", font=('Arial', 9))
        self.connection_status.grid(row=6, column=2, sticky=tk.W, pady=10)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ========== Date Range ==========
        self.create_section_header(main_frame, "Date Range Settings", 8)
        
        # Days Past
        ttk.Label(main_frame, text="Days to Look Back:", font=('Arial', 10)).grid(row=9, column=0, sticky=tk.W, pady=5)
        self.days_past = SpinboxWithMenu(main_frame, from_=0, to=90, width=10, font=('Arial', 10))
        self.days_past.grid(row=9, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.days_past.set(7)
        ttk.Label(main_frame, text="(0-90 days)", font=('Arial', 8), foreground='gray').grid(row=9, column=2, sticky=tk.W)
        
        # Days Future
        ttk.Label(main_frame, text="Days to Look Forward:", font=('Arial', 10)).grid(row=10, column=0, sticky=tk.W, pady=5)
        self.days_future = ComboboxWithMenu(main_frame, values=[7, 14, 30, 60, 90, 180, 365], width=8, font=('Arial', 10))
        self.days_future.grid(row=10, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.days_future.set(30)
        ttk.Label(main_frame, text="(7-365 days)", font=('Arial', 8), foreground='gray').grid(row=10, column=2, sticky=tk.W)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=11, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ========== File Paths ==========
        self.create_section_header(main_frame, "File & Directory Settings", 12)
        
        ttk.Label(main_frame, text=f"Execution directory: {EXECUTION_DIR}", 
                 font=('Arial', 8), foreground='blue').grid(row=13, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # HTML Output
        ttk.Label(main_frame, text="HTML Output File:", font=('Arial', 10)).grid(row=14, column=0, sticky=tk.W, pady=5)
        self.output_html = EntryWithMenu(main_frame, width=45, font=('Arial', 10))
        self.output_html.grid(row=14, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_file(self.output_html, "HTML Files", "*.html")).grid(row=14, column=3, padx=(5, 0))
        
        # JSON Output (optional)
        ttk.Label(main_frame, text="JSON Output File (Optional):", font=('Arial', 10)).grid(row=15, column=0, sticky=tk.W, pady=5)
        self.output_json = EntryWithMenu(main_frame, width=45, font=('Arial', 10))
        self.output_json.grid(row=15, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_file(self.output_json, "JSON Files", "*.json")).grid(row=15, column=3, padx=(5, 0))
        
        # Image Cache Directory
        ttk.Label(main_frame, text="Image Cache Directory:", font=('Arial', 10)).grid(row=16, column=0, sticky=tk.W, pady=5)
        self.image_cache = EntryWithMenu(main_frame, width=45, font=('Arial', 10))
        self.image_cache.grid(row=16, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.image_cache)).grid(row=16, column=3, padx=(5, 0))
        
        # Enable Image Cache checkbox
        self.enable_cache_var = tk.BooleanVar(value=True)
        self.enable_cache_check = ttk.Checkbutton(main_frame, text="Enable image caching (recommended)", 
                                                  variable=self.enable_cache_var)
        self.enable_cache_check.grid(row=17, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=18, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ========== Refresh Settings ==========
        self.create_section_header(main_frame, "Refresh Settings", 19)
        
        ttk.Label(main_frame, text="Auto-Refresh Interval:", font=('Arial', 10)).grid(row=20, column=0, sticky=tk.W, pady=5)
        self.refresh_interval = ComboboxWithMenu(main_frame, values=[1, 2, 3, 4, 6, 8, 12, 24, 48, 72, 168], width=8, font=('Arial', 10))
        self.refresh_interval.grid(row=20, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.refresh_interval.set(6)
        ttk.Label(main_frame, text="hours (1-168 hours / 7 days)", font=('Arial', 8), foreground='gray').grid(row=20, column=2, sticky=tk.W)
        
        ttk.Label(main_frame, text="⏰ The script will automatically refresh the calendar at this interval", 
                 font=('Arial', 10), foreground='#666666').grid(row=21, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=22, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ========== Action Buttons ==========
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=23, column=0, columnspan=4, pady=10)
        
        self.save_btn = ttk.Button(button_frame, text="💾 Save Configuration", command=self.save_configuration, width=25)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(button_frame, text="📂 Load Configuration", command=self.load_configuration, width=25)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.default_btn = ttk.Button(button_frame, text="🔄 Reset to Defaults", command=self.reset_defaults, width=25)
        self.default_btn.pack(side=tk.LEFT, padx=5)
        
        self.exit_btn = ttk.Button(button_frame, text="🚪 Exit", command=self.root.quit, width=20)
        self.exit_btn.pack()
        
        # Footer with version
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=24, column=0, columnspan=4, pady=(5, 0))
        version_label = ttk.Label(footer_frame, text="Version 2.2.4", font=('Arial', 8), foreground='gray')
        version_label.pack()
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to configure...")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Load existing config if available
        self.load_configuration()
    
    # ---------- Helper methods ----------
    def show_requests_warning(self):
        warning_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        warning_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(5, 0))
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️ requests library not installed - Connection test disabled",
                                 foreground='orange', font=('Arial', 9, 'bold'))
        warning_label.pack(padx=10, pady=5)
    
    def toggle_api_key_visibility(self):
        if self.show_key.get():
            self.sonarr_api_key.config(show="•")
            self.toggle_btn.config(text="👁️")
            self.show_key.set(False)
        else:
            self.sonarr_api_key.config(show="")
            self.toggle_btn.config(text="🔒")
            self.show_key.set(True)
    
    def set_window_icon(self):
        try:
            system = platform.system()
            if system == "Windows":
                if Path('icon.ico').exists():
                    self.root.iconbitmap(default='icon.ico')
            elif system == "Darwin":
                if Path('icon.icns').exists():
                    pass
                elif Path('icon.png').exists():
                    icon = tk.PhotoImage(file='icon.png')
                    self.root.iconphoto(True, icon)
            elif system == "Linux":
                if Path('icon.png').exists():
                    icon = tk.PhotoImage(file='icon.png')
                    self.root.iconphoto(True, icon)
                elif Path('icon.xbm').exists():
                    self.root.iconbitmap('@icon.xbm')
        except:
            pass
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_section_header(self, parent, text, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 5))
        label = ttk.Label(frame, text=text, font=('Arial', 11, 'bold'))
        label.pack(anchor=tk.W)
        separator = ttk.Separator(frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(2, 0))
    
    def browse_file(self, entry, file_type, extension):
        filename = filedialog.asksaveasfilename(
            defaultextension=extension if platform.system() == "Windows" else '',
            filetypes=[(file_type, extension), ("All Files", "*.*")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def browse_directory(self, entry):
        initial_dir = entry.get() or str(EXECUTION_DIR)
        directory = filedialog.askdirectory(initialdir=initial_dir)
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)
    
    def test_connection(self):
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("Missing Dependency", 
                "The 'requests' library is required for connection testing.\n\n"
                "Please install it with:\n  pip3 install requests")
            return
        
        url = self.sonarr_url.get().strip()
        api_key = self.sonarr_api_key.get().strip()
        if not url or not api_key:
            self.connection_status.config(text="❌ URL and API Key required", foreground='red')
            return
        
        self.connection_status.config(text="⏳ Testing connection...", foreground='blue')
        self.root.update()
        
        try:
            headers = {"X-Api-Key": api_key}
            response = requests.get(f"{url}/api/v3/system/status", headers=headers, timeout=10)
            if response.status_code == 200:
                version = response.json().get('version', 'Unknown')
                self.connection_status.config(text=f"✅ Connected! Sonarr v{version}", foreground='green')
            else:
                self.connection_status.config(text=f"❌ Connection failed (Status: {response.status_code})", foreground='red')
        except requests.exceptions.ConnectionError:
            self.connection_status.config(text="❌ Cannot connect to Sonarr", foreground='red')
        except Exception as e:
            self.connection_status.config(text=f"❌ Error: {str(e)[:30]}...", foreground='red')
    
    def validate_config(self):
        errors = []
        url = self.sonarr_url.get().strip()
        if not url:
            errors.append("Sonarr URL is required")
        elif not url.startswith(('http://', 'https://')):
            errors.append("Sonarr URL must start with http:// or https://")
        if not self.sonarr_api_key.get().strip():
            errors.append("Sonarr API Key is required")
        try:
            dp = int(self.days_past.get())
            if dp < 0 or dp > 365:
                errors.append("Days Past must be between 0 and 365")
        except ValueError:
            errors.append("Days Past must be a valid number")
        try:
            df = int(self.days_future.get())
            if df < 1 or df > 365:
                errors.append("Days Future must be between 1 and 365")
        except ValueError:
            errors.append("Days Future must be a valid number")
        html_path = self.output_html.get().strip()
        if not html_path:
            errors.append("HTML Output File path is required")
        else:
            html_dir = Path(html_path).parent
            if str(html_dir) and not html_dir.exists():
                try:
                    html_dir.mkdir(parents=True, exist_ok=True)
                except:
                    errors.append(f"Cannot create directory for HTML file: {html_dir}")
        cache_dir = self.image_cache.get().strip()
        if self.enable_cache_var.get() and cache_dir:
            cache_path = Path(cache_dir)
            if not cache_path.exists():
                try:
                    cache_path.mkdir(parents=True, exist_ok=True)
                except:
                    errors.append(f"Cannot create cache directory: {cache_dir}")
        try:
            rh = int(self.refresh_interval.get())
            if rh < 1 or rh > 168:
                errors.append("Refresh Interval must be between 1 and 168 hours")
        except ValueError:
            errors.append("Refresh Interval must be a valid number")
        return errors
    
    def save_configuration(self):
        errors = self.validate_config()
        if errors:
            error_msg = "Please fix the following errors:\n\n• " + "\n• ".join(errors)
            messagebox.showerror("Validation Error", error_msg)
            return
        
        config = {
            'sonarr_url': self.sonarr_url.get().strip(),
            'sonarr_api_key': self.sonarr_api_key.get().strip(),
            'days_past': int(self.days_past.get()),
            'days_future': int(self.days_future.get()),
            'output_html_file': self.output_html.get().strip(),
            'output_json_file': self.output_json.get().strip() or None,
            'image_cache_dir': self.image_cache.get().strip() or str(EXECUTION_DIR / "sonarr_images"),
            'refresh_interval_hours': int(self.refresh_interval.get()),
            'enable_image_cache': self.enable_cache_var.get()
        }
        
        try:
            # Ensure the home config directory exists
            HOME_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(HOME_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            self.show_config_summary(config)
            self.status_var.set(f"✅ Configuration saved successfully to {HOME_CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration:\n{str(e)}")
            self.status_var.set("❌ Failed to save configuration")
    
    def show_config_summary(self, config):
        # Mask API key
        api_key = config['sonarr_api_key']
        masked_key = '•' * 32 + (api_key[-4:] if len(api_key) > 4 else '')
        cache_enabled = "Enabled" if config['enable_image_cache'] else "Disabled"
        
        summary = f"""✅ Configuration Saved Successfully! (v2.2.4)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SONARR SETTINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL:          {config['sonarr_url']}
API Key:      {masked_key}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATE RANGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Look Back:    {config['days_past']} days
Look Forward: {config['days_future']} days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE PATHS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTML Output:  {config['output_html_file']}
JSON Output:  {config['output_json_file'] or 'Not enabled'}
Cache Dir:    {config['image_cache_dir']}
Image Cache:  {cache_enabled}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REFRESH SETTINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Interval:     {config['refresh_interval_hours']} hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The configuration has been saved to:
{HOME_CONFIG_FILE}

You can now run the main Sonarr Calendar script:
  python3 sonarr_calendar.py"""
        
        ScrollableMessageBox(self.root, "Configuration Saved", summary, width=80, height=25)
    
    def load_configuration(self):
        # Try home directory first
        if HOME_CONFIG_FILE.exists():
            try:
                with open(HOME_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self._apply_config(config)
                self.status_var.set(f"📂 Configuration loaded from {HOME_CONFIG_FILE}")
                messagebox.showinfo("Configuration Loaded", 
                                   f"Configuration loaded successfully from:\n{HOME_CONFIG_FILE}")
                return
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load from home:\n{str(e)}")
        
        # Fallback to old location
        if OLD_CONFIG_FILE.exists():
            try:
                with open(OLD_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self._apply_config(config)
                self.status_var.set(f"📂 Configuration loaded from {OLD_CONFIG_FILE}")
                messagebox.showinfo("Configuration Loaded (Legacy)", 
                                   f"Configuration loaded from old location:\n{OLD_CONFIG_FILE}\n\nIt will be migrated to home on next save.")
                return
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load old config:\n{str(e)}")
        
        self.status_var.set("ℹ️ No existing configuration found. Using defaults.")
        self.reset_defaults()
    
    def _apply_config(self, config):
        self.sonarr_url.delete(0, tk.END)
        self.sonarr_url.insert(0, config.get('sonarr_url', ''))
        self.sonarr_api_key.delete(0, tk.END)
        self.sonarr_api_key.insert(0, config.get('sonarr_api_key', ''))
        self.days_past.delete(0, tk.END)
        self.days_past.insert(0, config.get('days_past', 7))
        self.days_future.set(config.get('days_future', 30))
        self.output_html.delete(0, tk.END)
        self.output_html.insert(0, config.get('output_html_file', ''))
        self.output_json.delete(0, tk.END)
        self.output_json.insert(0, config.get('output_json_file', ''))
        self.image_cache.delete(0, tk.END)
        self.image_cache.insert(0, config.get('image_cache_dir', ''))
        self.refresh_interval.set(config.get('refresh_interval_hours', 6))
        self.enable_cache_var.set(config.get('enable_image_cache', True))
    
    def reset_defaults(self):
        self.sonarr_url.delete(0, tk.END)
        self.sonarr_url.insert(0, "http://localhost:8989")
        self.sonarr_api_key.delete(0, tk.END)
        self.days_past.delete(0, tk.END)
        self.days_past.insert(0, 7)
        self.days_future.set(30)
        default_html = EXECUTION_DIR / "sonarr_calendar.html"
        default_json = EXECUTION_DIR / "sonarr_calendar_data.json"
        default_cache = EXECUTION_DIR / "sonarr_images"
        self.output_html.delete(0, tk.END)
        self.output_html.insert(0, str(default_html))
        self.output_json.delete(0, tk.END)
        self.output_json.insert(0, str(default_json))
        self.image_cache.delete(0, tk.END)
        self.image_cache.insert(0, str(default_cache))
        self.refresh_interval.set(6)
        self.enable_cache_var.set(True)
        self.status_var.set("🔄 Reset to default values")

def main():
    root = tk.Tk()
    app = SonarrConfigApp(root)
    root.mainloop()

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("This script requires Python 3")
        sys.exit(1)
    main()