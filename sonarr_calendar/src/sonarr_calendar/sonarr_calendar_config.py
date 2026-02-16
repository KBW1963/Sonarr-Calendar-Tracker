#!/usr/bin/env python3
"""
Sonarr Calendar Tracker Pro - Configuration Setup Tool
Creates and saves configuration settings to a hidden file
Now with refresh interval in hours and platform detection

Version History:
===============
v1.0.0 (2024-01-01) - Initial release
  - Basic configuration GUI
  - Sonarr connection settings
  - Date range configuration
  - File path configuration
  - Refresh interval in hours

v1.1.0 (2024-01-10) - Platform detection and path improvements
  - Added platform detection (Windows/Linux/macOS)
  - Platform-specific default paths
  - Cross-platform directory handling
  - Added window centering

v1.2.0 (2024-01-12) - Connection testing
  - Added requests library integration
  - Sonarr connection testing
  - API key visibility toggle
  - Connection status display

v1.3.0 (2024-01-14) - UI improvements
  - Added emoji icons for better UX
  - Improved error messages
  - Configuration validation
  - Configuration summary dialog
  - Status bar with feedback

v2.1.0 (2024-01-15) - Mouse cut/copy/paste functionality
  - Added right-click context menu for all input fields
  - Custom EntryWithMenu, SpinboxWithMenu, ComboboxWithMenu classes
  - Cross-platform clipboard support (Windows/Linux/macOS)
  - Keyboard shortcuts: Ctrl+X/C/V/A (Cmd+X/C/V/A on macOS)
  - Right-click menu with Cut, Copy, Paste, Select All options
  - API key field now supports paste operations
  - All input fields fully clipboard-enabled

Current Version: v2.1.0
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

# Also check for requests (optional but recommended) - Added in v1.2.0
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / '.sonarr_calendar_config.json'
EXECUTION_DIR = Path.cwd()  # Get the directory where script was executed from

# v2.1.0: Right-click context menu class for all input widgets
class RightClickMenu:
    """Right-click context menu for Entry widgets - Added in v2.1.0"""
    def __init__(self, widget):
        self.widget = widget
        self.menu = tk.Menu(widget, tearoff=0)
        self.menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        self.menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.menu.add_separator()
        self.menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # Bind right-click to show menu (cross-platform)
        widget.bind("<Button-3>", self.show_menu)  # Linux/Windows right-click
        widget.bind("<Button-2>", self.show_menu)  # macOS right-click (Button-2)
        
        # Bind keyboard shortcuts for consistency
        widget.bind("<Control-x>", lambda e: self.cut())
        widget.bind("<Control-c>", lambda e: self.copy())
        widget.bind("<Control-v>", lambda e: self.paste())
        widget.bind("<Control-a>", lambda e: self.select_all())
        
        # For macOS Command key
        widget.bind("<Command-x>", lambda e: self.cut())
        widget.bind("<Command-c>", lambda e: self.copy())
        widget.bind("<Command-v>", lambda e: self.paste())
        widget.bind("<Command-a>", lambda e: self.select_all())
    
    def show_menu(self, event):
        """Show the right-click menu"""
        try:
            self.widget.focus_set()
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def cut(self):
        """Cut selected text"""
        try:
            self.widget.event_generate("<<Cut>>")
        except:
            pass
    
    def copy(self):
        """Copy selected text"""
        try:
            self.widget.event_generate("<<Copy>>")
        except:
            pass
    
    def paste(self):
        """Paste text from clipboard"""
        try:
            self.widget.event_generate("<<Paste>>")
        except:
            pass
    
    def select_all(self):
        """Select all text"""
        try:
            self.widget.select_range(0, tk.END)
            self.widget.icursor(tk.END)
        except:
            pass

# v2.1.0: Custom widget classes with right-click menu support
class SpinboxWithMenu(ttk.Spinbox):
    """Spinbox with right-click menu support - Added in v2.1.0"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        RightClickMenu(self)

class ComboboxWithMenu(ttk.Combobox):
    """Combobox with right-click menu support - Added in v2.1.0"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        RightClickMenu(self)

class EntryWithMenu(ttk.Entry):
    """Entry with right-click menu support - Added in v2.1.0"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        RightClickMenu(self)

class SonarrConfigApp:
    """Main application class for Sonarr Calendar Configuration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sonarr Calendar Pro - Configuration Setup")
        self.root.geometry("800x880")
        self.root.resizable(False, False)
        
        # v1.1.0: Platform detection
        self.system = platform.system()
        
        # v1.1.0: Set window icon if available
        self.set_window_icon()
        
        # v1.1.0: Center the window
        self.center_window()
        
        # v1.2.0: Check for requests library
        if not REQUESTS_AVAILABLE:
            self.show_requests_warning()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Sonarr Calendar Pro - Configuration", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # ==================== Sonarr Configuration Section ====================
        self.create_section_header(main_frame, "Sonarr Connection Settings", 1)
        
        # Sonarr URL
        ttk.Label(main_frame, text="Sonarr URL:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sonarr_url = EntryWithMenu(main_frame, width=50, font=('Arial', 10))
        self.sonarr_url.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(main_frame, text="e.g., http://192.168.1.100:8989", 
                 font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Sonarr API Key with visibility toggle
        ttk.Label(main_frame, text="API Key:", font=('Arial', 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        api_frame = ttk.Frame(main_frame)
        api_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.sonarr_api_key = EntryWithMenu(api_frame, width=45, font=('Arial', 10), show="•")
        self.sonarr_api_key.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # v1.2.0: API key visibility toggle
        self.show_key = tk.BooleanVar(value=False)
        self.toggle_btn = ttk.Button(api_frame, text="👁️", width=3, command=self.toggle_api_key_visibility)
        self.toggle_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Find this in Sonarr > Settings > General", 
                 font=('Arial', 8), foreground='gray').grid(row=5, column=1, sticky=tk.W, padx=(10, 0))
        
        # v1.2.0: Test Connection Button
        self.test_btn = ttk.Button(main_frame, text="Test Connection", command=self.test_connection)
        self.test_btn.grid(row=6, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        self.connection_status = ttk.Label(main_frame, text="", font=('Arial', 9))
        self.connection_status.grid(row=6, column=2, sticky=tk.W, pady=10)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ==================== Date Range Configuration Section ====================
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
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=11, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ==================== File Paths Configuration Section ====================
        self.create_section_header(main_frame, "File & Directory Settings", 12)
        
        # Show execution directory info
        ttk.Label(main_frame, text=f"Execution directory: {EXECUTION_DIR}", 
                 font=('Arial', 8), foreground='blue').grid(row=13, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Output HTML File
        ttk.Label(main_frame, text="HTML Output File:", font=('Arial', 10)).grid(row=14, column=0, sticky=tk.W, pady=5)
        self.output_html = EntryWithMenu(main_frame, width=45, font=('Arial', 10))
        self.output_html.grid(row=14, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_file(self.output_html, "HTML Files", "*.html")).grid(row=14, column=3, padx=(5, 0))
        
        # Output JSON File (Optional)
        ttk.Label(main_frame, text="JSON Output File (Optional):", font=('Arial', 10)).grid(row=15, column=0, sticky=tk.W, pady=5)
        self.output_json = EntryWithMenu(main_frame, width=45, font=('Arial', 10))
        self.output_json.grid(row=15, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_file(self.output_json, "JSON Files", "*.json")).grid(row=15, column=3, padx=(5, 0))
        
        # Image Cache Directory
        ttk.Label(main_frame, text="Image Cache Directory:", font=('Arial', 10)).grid(row=16, column=0, sticky=tk.W, pady=5)
        self.image_cache = EntryWithMenu(main_frame, width=45, font=('Arial', 10))
        self.image_cache.grid(row=16, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.image_cache)).grid(row=16, column=3, padx=(5, 0))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=17, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ==================== Refresh Configuration Section ====================
        self.create_section_header(main_frame, "Refresh Settings", 18)
        
        # Refresh Interval in hours
        ttk.Label(main_frame, text="Auto-Refresh Interval:", font=('Arial', 10)).grid(row=19, column=0, sticky=tk.W, pady=5)
        self.refresh_interval = ComboboxWithMenu(main_frame, values=[1, 2, 3, 4, 6, 8, 12, 24, 48, 72, 168], width=8, font=('Arial', 10))
        self.refresh_interval.grid(row=19, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.refresh_interval.set(6)
        ttk.Label(main_frame, text="hours (1-168 hours / 7 days)", font=('Arial', 8), foreground='gray').grid(row=19, column=2, sticky=tk.W)
        
        # Info text with emoji
        ttk.Label(main_frame, text="⏰ The script will automatically refresh the calendar at this interval", 
                 font=('Arial', 10), foreground='#666666').grid(row=20, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=21, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        
        # ==================== Action Buttons ====================
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=22, column=0, columnspan=4, pady=10)
        
        self.save_btn = ttk.Button(button_frame, text="💾 Save Configuration", command=self.save_configuration, width=25)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(button_frame, text="📂 Load Configuration", command=self.load_configuration, width=25)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.default_btn = ttk.Button(button_frame, text="🔄 Reset to Defaults", command=self.reset_defaults, width=25)
        self.default_btn.pack(side=tk.LEFT, padx=5)
              
        self.exit_btn = ttk.Button(button_frame, text="🚪 Exit", command=self.root.quit, width=20)
        self.exit_btn.pack()
        
        # ==================== Footer with Version Info ====================
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=23, column=0, columnspan=4, pady=(5, 0))
        
        version_label = ttk.Label(footer_frame, 
                                 text="Version 2.1.0 | Released: 2024-01-15 | Right-click for cut/copy/paste",
                                 font=('Arial', 8), foreground='gray')
        version_label.pack()
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to configure...")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Load existing configuration if available
        self.load_configuration()
    
    # v1.2.0: Requests warning method
    def show_requests_warning(self):
        """Show warning if requests library is not installed - Added in v1.2.0"""
        # Create a warning label at the top
        warning_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        warning_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(5, 0))
        
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️ requests library not installed - Connection test disabled",
                                 foreground='orange',
                                 font=('Arial', 9, 'bold'))
        warning_label.pack(padx=10, pady=5)
    
    # v1.2.0: API key visibility toggle
    def toggle_api_key_visibility(self):
        """Toggle the visibility of the API key - Added in v1.2.0"""
        if self.show_key.get():
            self.sonarr_api_key.config(show="•")
            self.toggle_btn.config(text="👁️")
            self.show_key.set(False)
        else:
            self.sonarr_api_key.config(show="")
            self.toggle_btn.config(text="🔒")
            self.show_key.set(True)
    
    # v1.1.0: Window icon method
    def set_window_icon(self):
        """Set window icon in a cross-platform way - Added in v1.1.0"""
        try:
            system = platform.system()
            
            if system == "Windows":
                if Path('icon.ico').exists():
                    self.root.iconbitmap(default='icon.ico')
            elif system == "Darwin":  # macOS
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
    
    # v1.1.0: Center window method
    def center_window(self):
        """Center the window on the screen - Added in v1.1.0"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    # v1.0.0: Section header creator
    def create_section_header(self, parent, text, row):
        """Create a section header with underline - Added in v1.0.0"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 5))
        
        label = ttk.Label(frame, text=text, font=('Arial', 11, 'bold'))
        label.pack(anchor=tk.W)
        
        separator = ttk.Separator(frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(2, 0))
    
    # v1.0.0: File browser (v1.1.0: updated for cross-platform)
    def browse_file(self, entry, file_type, extension):
        """Browse for a file - cross-platform compatible - Added in v1.0.0, updated v1.1.0"""
        system = platform.system()
        
        if system == "Windows":
            defaultextension = extension
        else:
            defaultextension = ''
            
        filename = filedialog.asksaveasfilename(
            defaultextension=defaultextension,
            filetypes=[(file_type, extension), ("All Files", "*.*")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    # v1.0.0: Directory browser (v1.1.0: updated for cross-platform)
    def browse_directory(self, entry):
        """Browse for a directory - cross-platform compatible - Added in v1.0.0, updated v1.1.0"""
        initial_dir = entry.get() or str(EXECUTION_DIR)
        directory = filedialog.askdirectory(initialdir=initial_dir)
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)
    
    # v1.2.0: Connection testing
    def test_connection(self):
        """Test connection to Sonarr - Added in v1.2.0"""
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("Missing Dependency", 
                "The 'requests' library is required for connection testing.\n\n"
                "Please install it with:\n"
                "  pip3 install requests")
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
                data = response.json()
                version = data.get('version', 'Unknown')
                self.connection_status.config(text=f"✅ Connected! Sonarr v{version}", foreground='green')
            else:
                self.connection_status.config(text=f"❌ Connection failed (Status: {response.status_code})", foreground='red')
        except requests.exceptions.ConnectionError:
            self.connection_status.config(text="❌ Cannot connect to Sonarr", foreground='red')
        except Exception as e:
            self.connection_status.config(text=f"❌ Error: {str(e)[:30]}...", foreground='red')
    
    # v1.3.0: Configuration validation
    def validate_config(self):
        """Validate configuration values - Added in v1.3.0"""
        errors = []
        
        # Validate Sonarr URL
        url = self.sonarr_url.get().strip()
        if not url:
            errors.append("Sonarr URL is required")
        elif not url.startswith(('http://', 'https://')):
            errors.append("Sonarr URL must start with http:// or https://")
        
        # Validate API Key
        if not self.sonarr_api_key.get().strip():
            errors.append("Sonarr API Key is required")
        
        # Validate days past
        try:
            days_past = int(self.days_past.get())
            if days_past < 0 or days_past > 365:
                errors.append("Days Past must be between 0 and 365")
        except ValueError:
            errors.append("Days Past must be a valid number")
        
        # Validate days future
        try:
            days_future = int(self.days_future.get())
            if days_future < 1 or days_future > 365:
                errors.append("Days Future must be between 1 and 365")
        except ValueError:
            errors.append("Days Future must be a valid number")
        
        # Validate file paths
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
        
        # Validate cache directory
        cache_dir = self.image_cache.get().strip()
        if cache_dir:
            cache_path = Path(cache_dir)
            if not cache_path.exists():
                try:
                    cache_path.mkdir(parents=True, exist_ok=True)
                except:
                    errors.append(f"Cannot create cache directory: {cache_dir}")
        
        # Validate refresh interval
        try:
            refresh_hours = int(self.refresh_interval.get())
            if refresh_hours < 1 or refresh_hours > 168:
                errors.append("Refresh Interval must be between 1 and 168 hours")
        except ValueError:
            errors.append("Refresh Interval must be a valid number")
        
        return errors
    
    # v1.0.0: Save configuration (v1.3.0: added validation and summary)
    def save_configuration(self):
        """Save configuration to hidden file - Added in v1.0.0, updated v1.3.0"""
        # Validate configuration
        errors = self.validate_config()
        if errors:
            error_msg = "Please fix the following errors:\n\n• " + "\n• ".join(errors)
            messagebox.showerror("Validation Error", error_msg)
            return
        
        # Prepare configuration data
        config = {
            'sonarr_url': self.sonarr_url.get().strip(),
            'sonarr_api_key': self.sonarr_api_key.get().strip(),
            'days_past': int(self.days_past.get()),
            'days_future': int(self.days_future.get()),
            'output_html_file': self.output_html.get().strip(),
            'output_json_file': self.output_json.get().strip() or None,
            'image_cache_dir': self.image_cache.get().strip() or str(EXECUTION_DIR / "sonarr_images"),
            'refresh_interval_hours': int(self.refresh_interval.get())
        }
        
        try:
            # Save to hidden file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            
            # Display summary
            self.show_config_summary(config)
            
            self.status_var.set(f"✅ Configuration saved successfully to {CONFIG_FILE.name}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration:\n{str(e)}")
            self.status_var.set("❌ Failed to save configuration")
    
    # v1.3.0: Configuration summary
    def show_config_summary(self, config):
        """Display a summary of saved configuration - Added in v1.3.0"""
        # Mask the API key for display
        api_key = config['sonarr_api_key']
        masked_key = '•' * 32 + (api_key[-4:] if len(api_key) > 4 else '')
        
        summary = f"""✅ Configuration Saved Successfully! (v2.1.0)

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REFRESH SETTINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Interval:     {config['refresh_interval_hours']} hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The configuration has been saved to:
{CONFIG_FILE}

You can now run the main Sonarr Calendar script:
  python3 sonarr_calendar.py"""
        
        messagebox.showinfo("Configuration Saved", summary)
    
    # v1.0.0: Load configuration
    def load_configuration(self):
        """Load configuration from hidden file - Added in v1.0.0"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                # Populate fields
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
                
                # Load refresh interval in hours
                refresh_hours = config.get('refresh_interval_hours', 6)
                self.refresh_interval.set(refresh_hours)
                
                self.status_var.set(f"📂 Configuration loaded from {CONFIG_FILE.name}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration:\n{str(e)}")
                self.reset_defaults()
        else:
            self.status_var.set("ℹ️ No existing configuration found. Using defaults.")
            self.reset_defaults()
    
    # v1.0.0: Reset to defaults (updated to use execution directory)
    def reset_defaults(self):
        """Reset to default values - Added in v1.0.0"""
        self.sonarr_url.delete(0, tk.END)
        self.sonarr_url.insert(0, "http://localhost:8989")
        
        self.sonarr_api_key.delete(0, tk.END)
        
        self.days_past.delete(0, tk.END)
        self.days_past.insert(0, 7)
        
        self.days_future.set(30)
        
        # Set default paths based on execution directory
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
        
        self.status_var.set("🔄 Reset to default values")

def main():
    """Main function to run the configuration GUI"""
    root = tk.Tk()
    app = SonarrConfigApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Check Python version
    if sys.version_info[0] < 3:
        print("This script requires Python 3")
        sys.exit(1)
    
    main()