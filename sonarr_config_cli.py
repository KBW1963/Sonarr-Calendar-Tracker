#!/usr/bin/env python3
"""
Sonarr Calendar Tracker Pro - CLI Configuration Tool
For Linux/Windows/macOS systems - Creates and saves configuration settings

Version History:
===============
v1.0.0 (2026-02-06) - Initial release
v1.1.0 (2026-02-07) - Platform detection and path improvements
v1.2.0 (2026-02-08) - Connection testing
v1.3.0 (2026-02-09) - UI improvements
v2.1.0 (2026-02-10) - Mouse cut/copy/paste functionality (CLI uses terminal defaults)
v2.2.0 (2026-02-11) - File checking and security improvements
v2.3.0 (2026-02-12) - API key input masking and default refresh
v2.4.0 (2026-02-13) - Enhanced connection error handling and API key masking
v2.5.0 (2026-02-14) - Fixed API key masking and graceful interrupt handling
v2.6.0 (2026-02-15) - Real-time API key masking with visual feedback
v3.0.0 (2026-02-16) - Pre-execution OS validation and dependency checking
v3.1.0 (2026-02-18) - Added image cache enable/disable option
v3.1.1 (2026-02-18) - Fixed file permission issues (save in home dir)
v3.1.2 (2026-02-18) - Fixed NameError in connection test
v3.1.3 (2026-02-21) - Improved paste support and config location display
v3.1.4 (2026-02-23) - Replaced custom raw input with getpass for reliability
v3.1.5 (2026-02-24) - Added input sanitization to remove terminal escape sequences
  - Prevents path corruption when users accidentally use arrow keys during input
  - Applies only to non‑password fields (file paths, URLs, etc.)
  - Uses regex to strip ASCII control characters

Current Version: v3.1.5
"""

import json
import os
import sys
import platform
import getpass
import signal
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import argparse

# ============================================================================
# COLOR CLASS
# ============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# PRE-EXECUTION VALIDATION
# ============================================================================

class PreFlightChecker:
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.issues = []
        self.warnings = []
        self.init_terminal_colors()
    
    def init_terminal_colors(self):
        if self.system == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                Colors.HEADER = Colors.BLUE = Colors.GREEN = Colors.YELLOW = Colors.RED = Colors.ENDC = Colors.BOLD = Colors.UNDERLINE = ''
    
    def print_header(self):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 Sonarr Calendar Pro - Pre-Flight Check v3.1.5{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, text): print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    def print_error(self, text):   print(f"{Colors.RED}❌ {text}{Colors.ENDC}")
    def print_warning(self, text): print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")
    def print_info(self, text):    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")
    
    def check_python_version(self) -> bool:
        if self.python_version.major < 3 or (self.python_version.major == 3 and self.python_version.minor < 6):
            self.issues.append(f"Python 3.6+ required (detected: {self.python_version.major}.{self.python_version.minor})")
            return False
        self.print_success(f"Python version: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        return True
    
    def check_os_compatibility(self) -> bool:
        supported_os = ['Windows', 'Linux', 'Darwin']
        if self.system not in supported_os:
            self.issues.append(f"Unsupported OS: {self.system}")
            return False
        os_name = "macOS" if self.system == "Darwin" else self.system
        self.print_success(f"Operating System: {os_name}")
        return True
    
    def check_terminal_capabilities(self) -> bool:
        if not sys.stdout.isatty():
            self.warnings.append("Not running in an interactive terminal")
            return False
        self.print_success("Terminal: Interactive mode detected")
        return True
    
    def check_required_modules(self) -> bool:
        optional_modules = ['requests']
        for module in optional_modules:
            try:
                __import__(module)
                self.print_success(f"Module: {module} - available (optional)")
            except ImportError:
                self.warnings.append(f"Optional module '{module}' is not installed")
        return True
    
    def check_terminal_size(self) -> bool:
        try:
            columns, rows = os.get_terminal_size()
            if columns < 60:
                self.warnings.append(f"Terminal width ({columns}) is small. Recommended: 80+ columns")
            else:
                self.print_success(f"Terminal size: {columns}x{rows}")
            return True
        except:
            self.warnings.append("Could not determine terminal size")
            return False
    
    def get_installation_instructions(self) -> Dict[str, List[str]]:
        return {
            'Windows': [
                "1. Install Python 3.6+ from https://www.python.org/downloads/",
                "2. Make sure to check 'Add Python to PATH' during installation",
                "3. Open Command Prompt or PowerShell and run:",
                "   pip install requests",
                "4. For best terminal experience, use Windows Terminal or PowerShell 7+"
            ],
            'Linux': [
                "1. Install Python 3.6+ and pip:",
                "   # Debian/Ubuntu: sudo apt update && sudo apt install python3 python3-pip",
                "   # Fedora: sudo dnf install python3 python3-pip",
                "   # Arch: sudo pacman -S python python-pip",
                "2. Install required packages: pip3 install requests",
                "3. For raw terminal input: sudo apt install python3-tty (Debian/Ubuntu)"
            ],
            'Darwin': [
                "1. Install Python 3.6+ using Homebrew: brew install python3",
                "2. Or download from https://www.python.org/downloads/",
                "3. Install required packages: pip3 install requests"
            ]
        }
    
    def show_installation_instructions(self):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}📋 Installation Instructions for {self.system}{Colors.ENDC}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.ENDC}")
        instructions = self.get_installation_instructions()
        system_key = self.system if self.system in instructions else 'Linux'
        for line in instructions[system_key]:
            print(f"  {line}")
        print(f"\n{Colors.YELLOW}Once requirements are installed, re-run: {Colors.BOLD}{sys.executable} {sys.argv[0]}{Colors.ENDC}\n")
    
    def run_validation(self) -> bool:
        self.print_header()
        checks = [
            ("Python Version", self.check_python_version()),
            ("OS Compatibility", self.check_os_compatibility()),
            ("Terminal Capabilities", self.check_terminal_capabilities()),
            ("Required Modules", self.check_required_modules()),
            ("Terminal Size", self.check_terminal_size())
        ]
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
        if self.issues:
            print(f"\n{Colors.RED}❌ Validation Failed - {len(self.issues)} issue(s):{Colors.ENDC}")
            for issue in self.issues:
                print(f"  {Colors.RED}• {issue}{Colors.ENDC}")
            if self.warnings:
                print(f"\n{Colors.YELLOW}⚠️  {len(self.warnings)} warning(s):{Colors.ENDC}")
                for warning in self.warnings:
                    print(f"  {Colors.YELLOW}• {warning}{Colors.ENDC}")
            self.show_installation_instructions()
            return False
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  {len(self.warnings)} warning(s) found:{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}• {warning}{Colors.ENDC}")
            print(f"\n{Colors.GREEN}✅ Basic validation passed with warnings{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}✅ All validation checks passed!{Colors.ENDC}")
        return True

# ============================================================================
# MAIN SCRIPT
# ============================================================================

# Check Python version
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    print("\n" + "="*60)
    print("❌ Python 3.6 or higher is required")
    print("="*60)
    print(f"Detected: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("\nPlease install Python 3.6+ from:")
    print("  https://www.python.org/downloads/")
    sys.exit(1)

validator = PreFlightChecker()
if not validator.run_validation():
    sys.exit(1)

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG_DIR = Path.home() / '.sonarr_calendar_config'
CONFIG_FILE = CONFIG_DIR / '.sonarr_calendar_config.json'
EXECUTION_DIR = Path.cwd()

def signal_handler(sig, frame):
    print(f"\n\n{Colors.YELLOW}⚠️  Configuration interrupted by user{Colors.ENDC}")
    print(f"{Colors.BLUE}ℹ️  Exiting gracefully. No changes were saved.{Colors.ENDC}\n")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ============================================================================
# SONARRCLICONFIG CLASS
# ============================================================================

class SonarrCLIConfig:
    def __init__(self):
        self.system = platform.system()
        self.config: Dict[str, Any] = {}
        self.use_existing_as_defaults = False
        try:
            import requests
            self.requests_available = True
            self.requests = requests
        except ImportError:
            self.requests_available = False
            self.requests = None
        self.check_existing_config()
    
    def check_existing_config(self):
        if CONFIG_FILE.exists():
            self.print_header("EXISTING CONFIGURATION FOUND")
            print(f"Found existing configuration file: {CONFIG_FILE}")
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
                print(f"\n{Colors.BOLD}Existing settings preview:{Colors.ENDC}")
                if 'sonarr_url' in self.config:
                    print(f"  • Sonarr URL: {self.config['sonarr_url']}")
                if 'sonarr_api_key' in self.config:
                    key = self.config['sonarr_api_key']
                    masked = '•' * (len(key) - 6) + key[-6:] if len(key) > 6 else '•' * len(key)
                    print(f"  • API Key: {masked}")
                if 'days_past' in self.config:
                    print(f"  • Days Past: {self.config['days_past']}")
                if 'days_future' in self.config:
                    print(f"  • Days Future: {self.config['days_future']}")
                if 'output_html_file' in self.config:
                    print(f"  • HTML Output: {self.config['output_html_file']}")
                if 'enable_image_cache' in self.config:
                    status = "Enabled" if self.config['enable_image_cache'] else "Disabled"
                    print(f"  • Image Cache: {status}")
                
                self.use_existing_as_defaults = self.get_yes_no(
                    "\nUse these values as defaults during configuration?", default=True
                )
                if self.use_existing_as_defaults:
                    self.print_success("Will use existing values as defaults")
                else:
                    self.print_info("Starting with fresh defaults")
                    self.config = {}
            except Exception as e:
                self.print_error(f"Failed to load existing configuration: {e}")
                self.print_info("Starting with fresh defaults")
                self.config = {}
        else:
            self.print_info("No existing configuration found. Using defaults.")
    
    def print_header(self, text): print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    def print_success(self, text): print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    def print_error(self, text):   print(f"{Colors.RED}❌ {text}{Colors.ENDC}")
    def print_warning(self, text): print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")
    def print_info(self, text):    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")
    def print_bullet(self, text):  print(f"  • {text}")
    
    # ==========================================================================
    # NEW: Input sanitization helper (v3.1.5)
    # ==========================================================================
    def _sanitize_input(self, value: str) -> str:
        """
        Remove control characters (including terminal escape sequences) from input.
        Preserves printable characters and newlines (though newlines are unlikely in paths).
        """
        # Remove ASCII control characters (0x00-0x08, 0x0b, 0x0c, 0x0e-0x1f, 0x7f-0x9f)
        # This also removes ESC (0x1b) and other unwanted codes.
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)

    # ==========================================================================
    # MODIFIED get_input – now sanitizes non‑password input (v3.1.5)
    # ==========================================================================
    def get_input(self, prompt: str, default: str = "", password: bool = False, mask_default: bool = False, field_name: str = "") -> str:
        """
        Get user input with optional default value.
        For password fields, uses getpass (no echo). After input, shows 40 asterisks as confirmation.
        For non‑password fields, input is sanitized to remove control characters.
        """
        display_default = default
        if mask_default and default and len(default) > 6:
            # Show only last 6 characters for API keys
            display_default = '•' * (len(default) - 6) + default[-6:]
        
        if default:
            if mask_default:
                full_prompt = f"{prompt} [{display_default}]: "
            else:
                full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        if password:
            # Use getpass for secure input (no echo)
            print(f"{Colors.BLUE}⏎ Type or paste your API key (input will be hidden){Colors.ENDC}")
            value = getpass.getpass(full_prompt)
            if value:
                # Visual confirmation: show 40 asterisks
                print(f"{Colors.GREEN}✓ API key received ({len(value)} characters): {'•' * 40}{Colors.ENDC}")
                return value.strip()
            else:
                return default if default else ""
        else:
            value = input(full_prompt)
            if value.strip():
                # Sanitize the input to remove any control characters
                clean_value = self._sanitize_input(value.strip())
                return clean_value
            else:
                return default
    
    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        default_str = "Y/n" if default else "y/N"
        try:
            resp = input(f"{prompt} [{default_str}]: ").strip().lower()
            return default if not resp else resp.startswith('y')
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Prompt cancelled{Colors.ENDC}")
            raise
    
    def validate_url(self, url: str) -> bool:
        return url.startswith(('http://', 'https://'))
    
    def test_connection(self, url: str, api_key: str) -> bool:
        """Test connection to Sonarr."""
        if not self.requests_available:
            self.print_warning("requests library not installed. Cannot test connection.")
            self.print_info("Install with: pip install requests")
            return False
        
        self.print_info("Testing connection to Sonarr...")
        
        try:
            headers = {"X-Api-Key": api_key}
            response = self.requests.get(f"{url}/api/v3/system/status", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'Unknown')
                self.print_success(f"Connected! Sonarr v{version}")
                return True
            else:
                self.print_error(f"Connection failed (Status: {response.status_code})")
                return False
        except self.requests.exceptions.ConnectionError:
            self.print_error("❌ Cannot connect to Sonarr - Check URL and network")
            return False
        except self.requests.exceptions.Timeout:
            self.print_error("❌ Connection timeout - Sonarr is not responding")
            return False
        except Exception as e:
            self.print_error(f"❌ Connection error: {str(e)}")
            return False
    
    def handle_connection_failure(self):
        self.print_warning("\nConnection test failed!")
        print("\nWhat would you like to do?")
        print("  1. Retry with different settings")
        print("  2. Restart configuration from beginning")
        print("  3. Continue anyway (not recommended)")
        while True:
            try:
                choice = input("\nEnter choice [1-3]: ").strip()
                if choice == "1": return "retry"
                if choice == "2": return "restart"
                if choice == "3": return "continue"
                self.print_error("Please enter 1, 2, or 3")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Choice cancelled{Colors.ENDC}")
                raise
    
    def configure_sonarr(self):
        self.print_header("SONARR CONNECTION SETTINGS")
        max_attempts = 3
        attempt = 1
        while attempt <= max_attempts:
            default_url = self.config.get('sonarr_url', 'http://localhost:8989')
            while True:
                try:
                    url = self.get_input("Sonarr URL", default_url)
                    if self.validate_url(url):
                        self.config['sonarr_url'] = url
                        break
                    else:
                        self.print_error("URL must start with http:// or https://")
                except KeyboardInterrupt:
                    raise
            default_key = self.config.get('sonarr_api_key', '')
            self.print_info("Find your API key in Sonarr > Settings > General")
            while True:
                try:
                    api_key = self.get_input("API Key", default_key, password=True, mask_default=True)
                    if api_key:
                        self.config['sonarr_api_key'] = api_key
                        break
                    else:
                        self.print_error("API Key is required")
                except KeyboardInterrupt:
                    raise
            if self.get_yes_no("\nTest connection to Sonarr?", True):
                success = self.test_connection(self.config['sonarr_url'], self.config['sonarr_api_key'])
                if not success:
                    action = self.handle_connection_failure()
                    if action == "retry":
                        attempt += 1
                        if attempt <= max_attempts:
                            self.print_info(f"Retry attempt {attempt} of {max_attempts}")
                            continue
                        else:
                            self.print_error("Max retry attempts reached.")
                            if not self.get_yes_no("Continue anyway?", False):
                                sys.exit(0)
                            break
                    elif action == "restart":
                        self.print_info("Restarting configuration...")
                        self.config = {}
                        return self.configure_sonarr()
                    else:  # continue
                        self.print_warning("Continuing despite failure.")
                        break
                else:
                    break
            else:
                break
    
    def configure_date_range(self):
        self.print_header("DATE RANGE SETTINGS")
        default_past = str(self.config.get('days_past', 7))
        while True:
            try:
                days_past = int(self.get_input("Days to look back (0-90)", default_past))
                if 0 <= days_past <= 90:
                    self.config['days_past'] = days_past
                    break
                self.print_error("Days must be between 0 and 90")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                raise
        default_future = str(self.config.get('days_future', 30))
        future_options = [7, 14, 30, 60, 90, 180, 365]
        print("\nDays to look forward:")
        for i, d in enumerate(future_options, 1):
            marker = " (default)" if d == int(default_future) else ""
            print(f"  {i}. {d} days{marker}")
        while True:
            try:
                choice = input(f"\nSelect option [1-{len(future_options)}]: ").strip()
                if not choice:
                    days_future = int(default_future)
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(future_options):
                        days_future = future_options[idx]
                    else:
                        self.print_error(f"Please enter a number between 1 and {len(future_options)}")
                        continue
                if 1 <= days_future <= 365:
                    self.config['days_future'] = days_future
                    break
                self.print_error("Days must be between 1 and 365")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                raise
    
    def configure_file_paths(self):
        self.print_header("FILE & DIRECTORY SETTINGS")
        self.print_info(f"Files will default to execution directory: {EXECUTION_DIR}")
        default_html = self.config.get('output_html_file', str(EXECUTION_DIR / "sonarr_calendar.html"))
        try:
            html_path = self.get_input("HTML output file path", default_html)
            self.config['output_html_file'] = html_path
        except KeyboardInterrupt:
            raise
        default_json = self.config.get('output_json_file', str(EXECUTION_DIR / "sonarr_calendar_data.json"))
        try:
            json_path = self.get_input("JSON output file (optional, press Enter to skip)", default_json)
            self.config['output_json_file'] = json_path if json_path else None
        except KeyboardInterrupt:
            raise
        default_cache = self.config.get('image_cache_dir', str(EXECUTION_DIR / "sonarr_images"))
        try:
            cache_dir = self.get_input("Image cache directory", default_cache)
            self.config['image_cache_dir'] = cache_dir
        except KeyboardInterrupt:
            raise
        default_cache_enabled = self.config.get('enable_image_cache', True)
        enable_cache = self.get_yes_no("Enable image caching? (recommended)", default=default_cache_enabled)
        self.config['enable_image_cache'] = enable_cache
        for path in [os.path.dirname(html_path), cache_dir]:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
                self.print_success(f"Created directory: {path}")
    
    def configure_refresh(self):
        self.print_header("REFRESH SETTINGS")
        default_interval = str(self.config.get('refresh_interval_hours', 6))
        interval_options = [1, 2, 3, 4, 6, 8, 12, 24, 48, 72, 168]
        print("Auto-refresh interval options:")
        for i, h in enumerate(interval_options, 1):
            if h == 24: display = "1 day"
            elif h == 168: display = "7 days"
            else: display = f"{h} hours"
            marker = " (default)" if h == int(default_interval) else ""
            print(f"  {i}. {display}{marker}")
        while True:
            try:
                choice = input(f"\nSelect option [1-{len(interval_options)}]: ").strip()
                if not choice:
                    refresh_hours = int(default_interval)
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(interval_options):
                        refresh_hours = interval_options[idx]
                    else:
                        self.print_error(f"Please enter a number between 1 and {len(interval_options)}")
                        continue
                if 1 <= refresh_hours <= 168:
                    self.config['refresh_interval_hours'] = refresh_hours
                    break
                self.print_error("Interval must be between 1 and 168 hours")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                raise
        if refresh_hours == 24: interval_display = "1 day"
        elif refresh_hours == 168: interval_display = "7 days"
        elif refresh_hours == 1: interval_display = "1 hour"
        else: interval_display = f"{refresh_hours} hours"
        self.print_info(f"Calendar will auto-refresh every {interval_display}")
    
    def show_config_summary(self):
        self.print_header("CONFIGURATION SUMMARY")
        print(f"{Colors.BOLD}Sonarr Settings:{Colors.ENDC}")
        self.print_bullet(f"URL: {self.config['sonarr_url']}")
        key = self.config['sonarr_api_key']
        masked = '•' * (len(key) - 6) + key[-6:] if len(key) > 6 else '•' * len(key)
        self.print_bullet(f"API Key: {masked}")
        print(f"\n{Colors.BOLD}Date Range:{Colors.ENDC}")
        self.print_bullet(f"Look back: {self.config['days_past']} days")
        self.print_bullet(f"Look forward: {self.config['days_future']} days")
        print(f"\n{Colors.BOLD}File Paths:{Colors.ENDC}")
        self.print_bullet(f"HTML: {self.config['output_html_file']}")
        self.print_bullet(f"JSON: {self.config['output_json_file'] or 'Not enabled'}")
        self.print_bullet(f"Cache: {self.config['image_cache_dir']}")
        cache_status = "Enabled" if self.config.get('enable_image_cache', True) else "Disabled"
        self.print_bullet(f"Image Cache: {cache_status}")
        refresh_hours = self.config['refresh_interval_hours']
        if refresh_hours == 24: interval = "1 day"
        elif refresh_hours == 168: interval = "7 days"
        elif refresh_hours == 1: interval = "1 hour"
        else: interval = f"{refresh_hours} hours"
        print(f"\n{Colors.BOLD}Refresh Settings:{Colors.ENDC}")
        self.print_bullet(f"Interval: {interval} ({refresh_hours} hours)")
        print(f"\n{Colors.BOLD}Execution Info:{Colors.ENDC}")
        self.print_bullet(f"Platform: {self.system}")
        self.print_bullet(f"Execution Directory: {EXECUTION_DIR}")
        self.print_bullet(f"Config File: {CONFIG_FILE}")
        print(f"\n{Colors.BOLD}Version:{Colors.ENDC}")
        self.print_bullet(f"v3.1.5 (2026-02-24) - Input sanitization added")
    
    def save_configuration(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.print_success(f"Configuration saved to {CONFIG_FILE}")
            return True
        except Exception as e:
            self.print_error(f"Failed to save configuration: {e}")
            return False
    
    def run_configuration_wizard(self):
        self.print_header("SONARR CALENDAR PRO - CLI CONFIGURATION v3.1.5")
        print("Welcome to the Sonarr Calendar configuration tool!")
        print(f"Platform: {self.system}")
        print(f"Execution Directory: {EXECUTION_DIR}")
        print("This wizard will help you set up your calendar preferences.\n")
        print("💡 Tip: Use Ctrl+Shift+C/V or right-click to copy/paste in most terminals")
        print("🔒 API keys are masked (input hidden) for security")
        print("   • No asterisks appear while typing, but input is secure")
        print("   • 40 asterisks shown as confirmation after input")
        print("   • Input sanitization now prevents stray characters from arrow keys")
        print("   • Press Ctrl+C at any time to exit gracefully\n")
        try:
            self.configure_sonarr()
            self.configure_date_range()
            self.configure_file_paths()
            self.configure_refresh()
            self.show_config_summary()
            if self.get_yes_no("\nSave this configuration?", True):
                if self.save_configuration():
                    print(f"\n{Colors.GREEN}Configuration complete!{Colors.ENDC}")
                    print(f"You can now run the main Sonarr Calendar script:")
                    print(f"  {Colors.BOLD}sonarr_calendar.py{Colors.ENDC}  # (Windows: python sonarr_calendar.py, Linux/macOS: python3)")
            else:
                print(f"\n{Colors.YELLOW}Configuration cancelled.{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠️  Configuration interrupted{Colors.ENDC}")
            print(f"{Colors.BLUE}ℹ️  Exiting gracefully. No changes were saved.{Colors.ENDC}\n")
            sys.exit(0)
    
    def quick_configure(self, args):
        self.print_header("QUICK CONFIGURATION v3.1.5")
        if args.url: self.config['sonarr_url'] = args.url
        if args.api_key: self.config['sonarr_api_key'] = args.api_key
        if args.days_past: self.config['days_past'] = args.days_past
        if args.days_future: self.config['days_future'] = args.days_future
        if args.html_file: self.config['output_html_file'] = args.html_file
        if args.json_file: self.config['output_json_file'] = args.json_file
        if args.cache_dir: self.config['image_cache_dir'] = args.cache_dir
        if args.refresh_interval: self.config['refresh_interval_hours'] = args.refresh_interval
        if args.enable_image_cache is not None:
            self.config['enable_image_cache'] = args.enable_image_cache
        else:
            self.config['enable_image_cache'] = self.config.get('enable_image_cache', True)
        # Set defaults for any missing fields
        self.config.setdefault('sonarr_url', 'http://localhost:8989')
        self.config.setdefault('sonarr_api_key', '')
        self.config.setdefault('days_past', 7)
        self.config.setdefault('days_future', 30)
        self.config.setdefault('output_html_file', str(EXECUTION_DIR / "sonarr_calendar.html"))
        self.config.setdefault('output_json_file', None)
        self.config.setdefault('image_cache_dir', str(EXECUTION_DIR / "sonarr_images"))
        self.config.setdefault('refresh_interval_hours', 6)
        self.config.setdefault('enable_image_cache', True)
        self.show_config_summary()
        if self.save_configuration():
            print(f"\n{Colors.GREEN}Quick configuration complete!{Colors.ENDC}")
    
    def show_config(self):
        if not self.config:
            self.print_warning("No configuration found.")
            return
        self.show_config_summary()
        print(f"\nConfig file: {CONFIG_FILE}")
    
    def reset_config(self):
        if self.get_yes_no("Are you sure you want to reset all configuration?", False):
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
                self.print_success("Configuration reset to defaults")
                self.config = {}
            else:
                self.print_warning("No configuration file found")

def main():
    parser = argparse.ArgumentParser(
        description="Sonarr Calendar Pro - CLI Configuration Tool v3.1.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run interactive wizard
  %(prog)s --show             # Show current configuration
  %(prog)s --reset            # Reset configuration
  %(prog)s --quick --url http://localhost:8989 --api-key YOUR_KEY  # Quick config
        """
    )
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--reset', action='store_true', help='Reset configuration to defaults')
    parser.add_argument('--quick', action='store_true', help='Quick configuration mode')
    parser.add_argument('--url', help='Sonarr URL')
    parser.add_argument('--api-key', help='Sonarr API key')
    parser.add_argument('--days-past', type=int, help='Days to look back')
    parser.add_argument('--days-future', type=int, help='Days to look forward')
    parser.add_argument('--html-file', help='HTML output file path')
    parser.add_argument('--json-file', help='JSON output file path')
    parser.add_argument('--cache-dir', help='Image cache directory')
    parser.add_argument('--refresh-interval', type=int, help='Refresh interval in hours')
    parser.add_argument('--enable-image-cache', type=lambda x: x.lower() == 'true', nargs='?', const=True,
                        help='Enable image caching (true/false)')
    args = parser.parse_args()
    if args.quick and not (args.url and args.api_key):
        print("Error: Quick mode requires --url and --api-key")
        print("Example: python3 sonarr_config_cli.py --quick --url http://localhost:8989 --api-key YOUR_KEY")
        sys.exit(1)
    try:
        configurator = SonarrCLIConfig()
        if args.show:
            configurator.show_config()
        elif args.reset:
            configurator.reset_config()
        elif args.quick:
            configurator.quick_configure(args)
        else:
            configurator.run_configuration_wizard()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Configuration interrupted by user{Colors.ENDC}")
        print(f"{Colors.BLUE}ℹ️  Exiting gracefully. No changes were saved.{Colors.ENDC}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()