#!/usr/bin/env python3
"""
Sonarr Calendar Tracker Pro - CLI Configuration Tool
For Linux/Windows/macOS systems - Creates and saves configuration settings

Version History:
===============
v1.0.0 (2024-01-01) - Initial release
  - Basic configuration wizard
  - Sonarr connection settings
  - Date range configuration
  - File path configuration
  - Refresh interval in hours

v1.1.0 (2024-01-10) - Platform detection and path improvements
  - Added multi-platform support (Windows, Linux, macOS)
  - Platform-specific path handling
  - Added window centering for GUI (not applicable to CLI)
  - Cross-platform directory operations

v1.2.0 (2024-01-12) - Connection testing
  - Added requests library integration
  - Sonarr connection testing
  - API key masking in display
  - Connection status feedback

v1.3.0 (2024-01-14) - UI improvements
  - Added emoji icons for better UX
  - Improved error messages
  - Configuration validation
  - Configuration summary display
  - Status messages with color coding

v2.1.0 (2024-01-15) - Mouse cut/copy/paste functionality (CLI uses terminal defaults)
  - Terminal native copy/paste support (Ctrl+Shift+C/V)
  - Right-click paste in most terminals
  - Cross-platform clipboard compatibility
  - All input fields support terminal paste operations

v2.2.0 (2024-01-16) - File checking and security improvements
  - Added config file existence check at startup
  - Option to use existing values as defaults during configuration
  - API key masking in prompts - displays only last 6 characters
  - Improved platform-specific execution instructions
  - Better handling of existing configuration values

v2.3.0 (2024-01-17) - API key input masking and default refresh
  - API key input now masked with asterisks during typing
  - Visual feedback when pasting API keys
  - Refresh interval default set to 6 hours
  - Enhanced security for sensitive input

v2.4.0 (2024-01-18) - Enhanced connection error handling and API key masking
  - Connection failure now prompts user to restart configuration
  - API key input shows 40 asterisks when pasted (visual feedback)
  - All characters masked during typing for maximum security
  - Improved error messages with clear next steps
  - Option to retry or restart configuration on connection failure

v2.5.0 (2024-01-19) - Fixed API key masking and graceful interrupt handling
  - Fixed API key input to show 40 asterisks when pasted
  - Auto-submit after paste with visual confirmation
  - Added graceful handling of Ctrl+C interrupts
  - Clean exit with user-friendly message
  - Proper signal handling for all platforms

v2.6.0 (2024-01-20) - Real-time API key masking with visual feedback
  - Custom input function shows asterisks while typing/pasting
  - Visual confirmation shows 40 asterisks after input
  - Backspace and delete keys work normally
  - Cross-platform compatibility for all terminal types

v3.0.0 (2024-01-21) - Pre-execution OS validation and dependency checking
  - Added comprehensive OS validation before script execution
  - Platform-specific dependency checking
  - Clear installation instructions for each OS
  - Graceful exit with re-run instructions
  - Python version validation
  - Terminal capability checking

Current Version: v3.0.0
"""

import json
import os
import sys
import platform
import getpass
import signal
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import argparse

# ============================================================================
# COLOR CLASS (Defined early for use in validation)
# ============================================================================

class Colors:
    """ANSI color codes for terminal output - works on all platforms"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# PRE-EXECUTION VALIDATION (v3.0.0)
# ============================================================================

class PreFlightChecker:
    """Pre-execution validation and dependency checking - Added in v3.0.0"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.issues = []
        self.warnings = []
        
        # Initialize terminal colors based on platform
        self.init_terminal_colors()
    
    def init_terminal_colors(self):
        """Initialize terminal colors based on platform"""
        if self.system == "Windows":
            # Windows 10+ supports ANSI colors in some terminals
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # Disable colors if not supported
                Colors.HEADER = ''
                Colors.BLUE = ''
                Colors.GREEN = ''
                Colors.YELLOW = ''
                Colors.RED = ''
                Colors.ENDC = ''
                Colors.BOLD = ''
                Colors.UNDERLINE = ''
    
    def print_header(self):
        """Print validation header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 Sonarr Calendar Pro - Pre-Flight Check v3.0.0{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}❌ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")
    
    def check_python_version(self) -> bool:
        """Check Python version (requires 3.6+)"""
        if self.python_version.major < 3 or (self.python_version.major == 3 and self.python_version.minor < 6):
            self.issues.append(
                f"Python 3.6 or higher required (detected: {self.python_version.major}.{self.python_version.minor})"
            )
            return False
        self.print_success(f"Python version: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        return True
    
    def check_os_compatibility(self) -> bool:
        """Check if OS is supported"""
        supported_os = ['Windows', 'Linux', 'Darwin']  # Darwin is macOS
        if self.system not in supported_os:
            self.issues.append(f"Unsupported operating system: {self.system}")
            return False
        os_name = "macOS" if self.system == "Darwin" else self.system
        self.print_success(f"Operating System: {os_name}")
        return True
    
    def check_terminal_capabilities(self) -> bool:
        """Check terminal capabilities for ANSI colors and raw input"""
        # Check if stdout is a terminal
        if not sys.stdout.isatty():
            self.warnings.append("Not running in an interactive terminal")
            return False
        
        self.print_success("Terminal: Interactive mode detected")
        return True
    
    def check_required_modules(self) -> bool:
        """Check if required Python modules are available"""
        required_modules = []
        optional_modules = ['requests']
        
        # Check required modules
        for module in required_modules:
            try:
                __import__(module)
                self.print_success(f"Module: {module} - available")
            except ImportError:
                self.issues.append(f"Required module '{module}' is not installed")
        
        # Check optional modules
        for module in optional_modules:
            try:
                __import__(module)
                self.print_success(f"Module: {module} - available (optional)")
            except ImportError:
                self.warnings.append(f"Optional module '{module}' is not installed")
        
        return len(self.issues) == 0
    
    def check_terminal_size(self) -> bool:
        """Check if terminal is large enough"""
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
        """Get platform-specific installation instructions"""
        instructions = {
            'Windows': [
                "1. Install Python 3.6+ from https://www.python.org/downloads/",
                "2. Make sure to check 'Add Python to PATH' during installation",
                "3. Open Command Prompt or PowerShell and run:",
                "   pip install requests",
                "4. For best terminal experience, use Windows Terminal or PowerShell 7+"
            ],
            'Linux': [
                "1. Install Python 3.6+ and pip:",
                "   # Debian/Ubuntu:",
                "   sudo apt update",
                "   sudo apt install python3 python3-pip",
                "   # Fedora/RHEL/CentOS:",
                "   sudo dnf install python3 python3-pip",
                "   # Arch Linux:",
                "   sudo pacman -S python python-pip",
                "2. Install required packages:",
                "   pip3 install requests",
                "3. For raw terminal input (used for API key masking):",
                "   # This is usually included with Python, but if missing:",
                "   sudo apt install python3-tty  # Debian/Ubuntu"
            ],
            'Darwin': [  # macOS
                "1. Install Python 3.6+ using Homebrew:",
                "   brew install python3",
                "2. Or download from https://www.python.org/downloads/",
                "3. Install required packages:",
                "   pip3 install requests",
                "4. For best terminal experience, use iTerm2 or Terminal.app"
            ]
        }
        return instructions
    
    def show_installation_instructions(self):
        """Display platform-specific installation instructions"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}📋 Installation Instructions for {self.system}{Colors.ENDC}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.ENDC}")
        
        instructions = self.get_installation_instructions()
        system_key = self.system if self.system in instructions else 'Linux'  # Default to Linux for unknown
        
        for line in instructions[system_key]:
            print(f"  {line}")
        
        print(f"\n{Colors.YELLOW}Once requirements have been installed, re-run the configuration script:{Colors.ENDC}")
        print(f"  {Colors.BOLD}{sys.executable} {sys.argv[0]}{Colors.ENDC}\n")
    
    def run_validation(self) -> bool:
        """Run all validation checks"""
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
            print(f"\n{Colors.RED}❌ Validation Failed - {len(self.issues)} issue(s) found:{Colors.ENDC}")
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


# Check Python version first (minimum requirement)
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    print("\n" + "="*60)
    print("❌ Python 3.6 or higher is required")
    print("="*60)
    print(f"Detected: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("\nPlease install Python 3.6+ from:")
    print("  https://www.python.org/downloads/")
    print("\nOnce installed, re-run this script.")
    print("="*60 + "\n")
    sys.exit(1)

# Run pre-flight validation
validator = PreFlightChecker()
if not validator.run_validation():
    sys.exit(1)

# ============================================================================
# MAIN SCRIPT (continues after validation)
# ============================================================================

# Try to import requests (optional) - Added in v1.2.0
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

# v2.5.0: Signal handler for graceful interrupt
def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n\n{Colors.YELLOW}⚠️  Configuration interrupted by user{Colors.ENDC}")
    print(f"{Colors.BLUE}ℹ️  Exiting gracefully. No changes were saved.{Colors.ENDC}\n")
    sys.exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# v2.6.0: Custom masked input function that shows asterisks in real-time
def masked_input(prompt: str) -> str:
    """
    Custom input function that masks input with asterisks in real-time.
    Works on Unix-like systems (Linux, macOS) and Windows.
    """
    print(prompt, end='', flush=True)
    
    # Store the input
    value = []
    
    # Check if we're on Windows
    if platform.system() == "Windows":
        # Windows doesn't support termios, use getpass with a workaround
        # But we want real-time feedback, so we'll use msvcrt
        try:
            import msvcrt
            while True:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    if char in (b'\r', b'\n'):  # Enter key
                        print()
                        break
                    elif char in (b'\x08', b'\x7f'):  # Backspace
                        if value:
                            value.pop()
                            # Move cursor back, overwrite with space, move back again
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    else:
                        try:
                            # Try to decode the character
                            decoded_char = char.decode('utf-8')
                            value.append(decoded_char)
                            # Show asterisk
                            sys.stdout.write('*')
                            sys.stdout.flush()
                        except:
                            # Ignore non-UTF8 characters
                            pass
        except ImportError:
            # Fallback to getpass if msvcrt is not available
            return getpass.getpass("")
    else:
        # Unix-like system (Linux, macOS)
        import termios
        import tty
        import select
        
        old_settings = None
        try:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            
            while True:
                # Read one character
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    
                    if char in ('\r', '\n'):  # Enter key
                        print()
                        break
                    elif char in ('\x7f', '\x08'):  # Backspace
                        if value:
                            value.pop()
                            # Move cursor back, overwrite with space, move back again
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    elif char == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    else:
                        value.append(char)
                        # Show asterisk
                        sys.stdout.write('*')
                        sys.stdout.flush()
        finally:
            # Restore terminal settings
            if old_settings and fd:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    return ''.join(value)

class SonarrCLIConfig:
    """CLI-based configuration tool for Sonarr Calendar"""
    
    def __init__(self):
        self.system = platform.system()
        self.config: Dict[str, Any] = {}
        self.use_existing_as_defaults = False
        self.check_existing_config()
    
    # v2.2.0: Check for existing config and ask to use as defaults
    def check_existing_config(self):
        """Check if configuration file exists and ask to use as defaults"""
        if CONFIG_FILE.exists():
            self.print_header("EXISTING CONFIGURATION FOUND")
            print(f"Found existing configuration file: {CONFIG_FILE}")
            
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
                
                # Show masked preview of existing config
                print(f"\n{Colors.BOLD}Existing settings preview:{Colors.ENDC}")
                if 'sonarr_url' in self.config:
                    print(f"  • Sonarr URL: {self.config['sonarr_url']}")
                if 'sonarr_api_key' in self.config:
                    api_key = self.config['sonarr_api_key']
                    masked = '•' * (len(api_key) - 6) + api_key[-6:] if len(api_key) > 6 else '•' * len(api_key)
                    print(f"  • API Key: {masked}")
                if 'days_past' in self.config:
                    print(f"  • Days Past: {self.config['days_past']}")
                if 'days_future' in self.config:
                    print(f"  • Days Future: {self.config['days_future']}")
                if 'output_html_file' in self.config:
                    print(f"  • HTML Output: {self.config['output_html_file']}")
                
                # Ask user if they want to use these as defaults
                self.use_existing_as_defaults = self.get_yes_no(
                    "\nUse these values as defaults during configuration?", 
                    default=True
                )
                
                if self.use_existing_as_defaults:
                    self.print_success("Will use existing values as defaults")
                else:
                    self.print_info("Starting with fresh defaults")
                    self.config = {}  # Clear config to use program defaults
                    
            except Exception as e:
                self.print_error(f"Failed to load existing configuration: {e}")
                self.print_info("Starting with fresh defaults")
                self.config = {}
        else:
            self.print_info("No existing configuration found. Using defaults.")
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, text: str):
        """Print success message - v1.3.0: Added emoji"""
        print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        """Print error message - v1.3.0: Added emoji"""
        print(f"{Colors.RED}❌ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        """Print warning message - v1.3.0: Added emoji"""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        """Print info message - v1.3.0: Added emoji"""
        print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")
    
    def print_bullet(self, text: str):
        """Print bullet point"""
        print(f"  • {text}")
    
    # v2.2.0: Enhanced get_input with masked API key support
    # v2.3.0: Added visual feedback for API key input
    # v2.4.0: Enhanced API key masking with asterisks display
    # v2.5.0: Fixed API key input to show asterisks when pasted
    # v2.6.0: Real-time masking with custom input function
    def get_input(self, prompt: str, default: str = "", password: bool = False, mask_default: bool = False, field_name: str = "") -> str:
        """Get user input with optional default value
           v2.1.0: Terminal native copy/paste supported (Ctrl+Shift+C/V, right-click)
           v2.2.0: Added masked default display for sensitive values
           v2.3.0: Added visual feedback for API key input
           v2.4.0: Enhanced API key masking - shows 40 asterisks when pasted
           v2.5.0: Fixed API key input to actually show asterisks and auto-submit
           v2.6.0: Real-time masking with custom input function
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
            # For API keys, use custom masked input that shows asterisks in real-time
            print(f"{Colors.BLUE}⏎ Type or paste your API key (asterisks will appear as you type){Colors.ENDC}")
            
            try:
                # Use custom masked input function
                value = masked_input(full_prompt)
                
                if value:
                    # v2.6.0: Show 40 asterisks as visual confirmation
                    print(f"{Colors.GREEN}✓ API key received ({len(value)} characters): {'•' * 40}{Colors.ENDC}")
                    return value.strip()
                else:
                    # If empty and we have a default, use it
                    if default:
                        print(f"{Colors.BLUE}ℹ️ Using existing API key{Colors.ENDC}")
                        return default
                    else:
                        return ""
            except KeyboardInterrupt:
                # Handle Ctrl+C during input
                print(f"\n{Colors.YELLOW}⚠️  Input cancelled{Colors.ENDC}")
                raise
        else:
            value = input(full_prompt)
            return value.strip() if value.strip() else default
    
    def get_choice(self, prompt: str, choices: list, default: Optional[str] = None) -> str:
        """Get user choice from a list of options"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        if default:
            default_prompt = f" (default: {default})"
        else:
            default_prompt = ""
        
        while True:
            try:
                selection = input(f"Enter choice number{default_prompt}: ").strip()
                if not selection and default:
                    return default
                
                idx = int(selection) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
                else:
                    self.print_error(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Choice cancelled{Colors.ENDC}")
                raise
    
    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no answer from user"""
        default_str = "Y/n" if default else "y/N"
        try:
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            
            if not response:
                return default
            return response.startswith('y')
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Prompt cancelled{Colors.ENDC}")
            raise
    
    def load_existing_config(self):
        """Load existing configuration if available - v2.2.0: Now integrated into check_existing_config"""
        pass  # Functionality moved to check_existing_config
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        return url.startswith(('http://', 'https://'))
    
    # v1.2.0: Connection testing
    # v2.4.0: Enhanced error handling with restart option
    def test_connection(self, url: str, api_key: str) -> bool:
        """Test connection to Sonarr - Added in v1.2.0, enhanced v2.4.0"""
        if not REQUESTS_AVAILABLE:
            self.print_warning("requests library not installed. Cannot test connection.")
            self.print_info("Install with: pip3 install requests")
            return False
        
        self.print_info("Testing connection to Sonarr...")
        
        try:
            headers = {"X-Api-Key": api_key}
            response = requests.get(f"{url}/api/v3/system/status", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'Unknown')
                self.print_success(f"Connected! Sonarr v{version}")
                return True
            else:
                self.print_error(f"Connection failed (Status: {response.status_code})")
                self.print_error("Please check your URL and API key")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("❌ Cannot connect to Sonarr - Check URL and network")
            self.print_error("   • Verify Sonarr is running")
            self.print_error("   • Check if the URL is correct")
            self.print_error("   • Ensure no firewall is blocking the connection")
            return False
        except requests.exceptions.Timeout:
            self.print_error("❌ Connection timeout - Sonarr is not responding")
            self.print_error("   • Check if Sonarr is running")
            self.print_error("   • Verify network connectivity")
            return False
        except Exception as e:
            self.print_error(f"❌ Connection error: {str(e)}")
            return False
    
    # v2.4.0: Handle connection failure with restart option
    def handle_connection_failure(self):
        """Handle connection test failure - Added in v2.4.0"""
        self.print_warning("\nConnection test failed!")
        print("\nWhat would you like to do?")
        print("  1. Retry with different settings")
        print("  2. Restart configuration from beginning")
        print("  3. Continue anyway (not recommended)")
        
        while True:
            try:
                choice = input("\nEnter choice [1-3]: ").strip()
                if choice == "1":
                    return "retry"
                elif choice == "2":
                    return "restart"
                elif choice == "3":
                    return "continue"
                else:
                    self.print_error("Please enter 1, 2, or 3")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Choice cancelled{Colors.ENDC}")
                raise
    
    # v1.0.0: Sonarr configuration (v2.2.0: Updated to use masked defaults, v2.3.0: Added visual feedback, v2.4.0: Enhanced error handling, v2.5.0: Fixed API key masking, v2.6.0: Real-time masking)
    def configure_sonarr(self):
        """Configure Sonarr connection settings"""
        self.print_header("SONARR CONNECTION SETTINGS")
        
        max_attempts = 3
        attempt = 1
        
        while attempt <= max_attempts:
            # Sonarr URL
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
            
            # Sonarr API Key - with masked default and visual feedback
            default_key = self.config.get('sonarr_api_key', '')
            self.print_info("Find your API key in Sonarr > Settings > General")
            
            while True:
                try:
                    api_key = self.get_input("API Key", default_key, password=True, mask_default=True, field_name="API Key")
                    if api_key:
                        self.config['sonarr_api_key'] = api_key
                        break
                    else:
                        self.print_error("API Key is required")
                except KeyboardInterrupt:
                    raise
            
            # Test connection - v1.2.0
            if self.get_yes_no("\nTest connection to Sonarr?", True):
                connection_success = self.test_connection(self.config['sonarr_url'], self.config['sonarr_api_key'])
                
                if not connection_success:
                    # v2.4.0: Handle connection failure
                    try:
                        action = self.handle_connection_failure()
                    except KeyboardInterrupt:
                        raise
                    
                    if action == "retry":
                        attempt += 1
                        if attempt <= max_attempts:
                            self.print_info(f"Retry attempt {attempt} of {max_attempts}")
                            continue
                        else:
                            self.print_error(f"Maximum retry attempts ({max_attempts}) reached.")
                            try:
                                if not self.get_yes_no("Continue with configuration anyway?", False):
                                    self.print_info("Exiting configuration. Please try again later.")
                                    sys.exit(0)
                                break
                            except KeyboardInterrupt:
                                raise
                    elif action == "restart":
                        self.print_info("Restarting configuration from beginning...")
                        self.config = {}  # Clear config
                        return self.configure_sonarr()  # Restart
                    else:  # continue
                        self.print_warning("Continuing with configuration despite connection failure.")
                        break
                else:
                    # Connection successful
                    break
            else:
                # User chose not to test
                break
        
        # If we've exhausted attempts but user chose to continue
        pass
    
    # v1.0.0: Date range configuration (v2.2.0: Updated to use existing config)
    def configure_date_range(self):
        """Configure date range settings"""
        self.print_header("DATE RANGE SETTINGS")
        
        # Days past
        default_past = str(self.config.get('days_past', 7))
        while True:
            try:
                days_past = int(self.get_input("Days to look back (0-90)", default_past))
                if 0 <= days_past <= 90:
                    self.config['days_past'] = days_past
                    break
                else:
                    self.print_error("Days must be between 0 and 90")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                raise
        
        # Days future
        default_future = str(self.config.get('days_future', 30))
        future_options = [7, 14, 30, 60, 90, 180, 365]
        
        print("\nDays to look forward:")
        for i, days in enumerate(future_options, 1):
            marker = " (default)" if days == int(default_future) else ""
            print(f"  {i}. {days} days{marker}")
        
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
                else:
                    self.print_error("Days must be between 1 and 365")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                raise
    
    # v1.0.0: File paths configuration (v1.1.0: updated for cross-platform, v2.2.0: uses existing config)
    def configure_file_paths(self):
        """Configure file and directory paths - using execution directory"""
        self.print_header("FILE & DIRECTORY SETTINGS")
        
        # Show execution directory
        self.print_info(f"Files will default to execution directory: {EXECUTION_DIR}")
        
        # HTML Output file
        default_html = self.config.get('output_html_file', 
                                      str(EXECUTION_DIR / "sonarr_calendar.html"))
        try:
            html_path = self.get_input("HTML output file path", default_html)
            self.config['output_html_file'] = html_path
        except KeyboardInterrupt:
            raise
        
        # JSON Output file (optional)
        default_json = self.config.get('output_json_file', 
                                      str(EXECUTION_DIR / "sonarr_calendar_data.json"))
        try:
            json_path = self.get_input("JSON output file (optional, press Enter to skip)", default_json)
            self.config['output_json_file'] = json_path if json_path else None
        except KeyboardInterrupt:
            raise
        
        # Image cache directory
        default_cache = self.config.get('image_cache_dir', 
                                       str(EXECUTION_DIR / "sonarr_images"))
        try:
            cache_dir = self.get_input("Image cache directory", default_cache)
            self.config['image_cache_dir'] = cache_dir
        except KeyboardInterrupt:
            raise
        
        # Create directories if they don't exist
        for path in [os.path.dirname(html_path), cache_dir]:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
                self.print_success(f"Created directory: {path}")
    
    # v1.0.0: Refresh configuration (v2.2.0: uses existing config, v2.3.0: Default to 6 hours)
    def configure_refresh(self):
        """Configure refresh settings - v2.3.0: Default set to 6 hours"""
        self.print_header("REFRESH SETTINGS")
        
        # Refresh interval in hours - Default to 6 hours (v2.3.0)
        default_interval = str(self.config.get('refresh_interval_hours', 6))
        interval_options = [1, 2, 3, 4, 6, 8, 12, 24, 48, 72, 168]
        
        print("Auto-refresh interval options:")
        for i, hours in enumerate(interval_options, 1):
            if hours == 24:
                display = "1 day"
            elif hours == 168:
                display = "7 days"
            else:
                display = f"{hours} hours"
            
            marker = " (default)" if hours == int(default_interval) else ""
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
                else:
                    self.print_error("Interval must be between 1 and 168 hours")
            except ValueError:
                self.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                raise
        
        # Display human-readable interval
        if refresh_hours == 24:
            interval_display = "1 day"
        elif refresh_hours == 168:
            interval_display = "7 days"
        elif refresh_hours == 1:
            interval_display = "1 hour"
        else:
            interval_display = f"{refresh_hours} hours"
        
        self.print_info(f"Calendar will auto-refresh every {interval_display}")
    
    # v1.3.0: Configuration summary (v2.2.0: Updated with version info, v2.4.0: Updated version, v2.5.0: Updated version, v2.6.0: Updated version, v3.0.0: Updated version)
    def show_config_summary(self):
        """Display configuration summary - v1.3.0: Enhanced with better formatting"""
        self.print_header("CONFIGURATION SUMMARY")
        
        # Sonarr Settings
        print(f"{Colors.BOLD}Sonarr Settings:{Colors.ENDC}")
        self.print_bullet(f"URL: {self.config['sonarr_url']}")
        api_key = self.config['sonarr_api_key']
        masked_key = '•' * (len(api_key) - 6) + api_key[-6:] if len(api_key) > 6 else '•' * len(api_key)
        self.print_bullet(f"API Key: {masked_key}")
        
        # Date Range
        print(f"\n{Colors.BOLD}Date Range:{Colors.ENDC}")
        self.print_bullet(f"Look back: {self.config['days_past']} days")
        self.print_bullet(f"Look forward: {self.config['days_future']} days")
        
        # File Paths
        print(f"\n{Colors.BOLD}File Paths:{Colors.ENDC}")
        self.print_bullet(f"HTML: {self.config['output_html_file']}")
        self.print_bullet(f"JSON: {self.config['output_json_file'] or 'Not enabled'}")
        self.print_bullet(f"Cache: {self.config['image_cache_dir']}")
        
        # Refresh Settings
        refresh_hours = self.config['refresh_interval_hours']
        if refresh_hours == 24:
            interval = "1 day"
        elif refresh_hours == 168:
            interval = "7 days"
        elif refresh_hours == 1:
            interval = "1 hour"
        else:
            interval = f"{refresh_hours} hours"
        
        print(f"\n{Colors.BOLD}Refresh Settings:{Colors.ENDC}")
        self.print_bullet(f"Interval: {interval} ({refresh_hours} hours)")
        
        # Execution Info
        print(f"\n{Colors.BOLD}Execution Info:{Colors.ENDC}")
        self.print_bullet(f"Platform: {self.system}")
        self.print_bullet(f"Execution Directory: {EXECUTION_DIR}")
        self.print_bullet(f"Config File: {CONFIG_FILE}")
        
        # Version info
        print(f"\n{Colors.BOLD}Version:{Colors.ENDC}")
        self.print_bullet(f"v3.0.0 (2024-01-21) - Pre-execution OS validation")
    
    # v1.0.0: Save configuration
    def save_configuration(self):
        """Save configuration to file"""
        try:
            # Save to hidden file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.print_success(f"Configuration saved to {CONFIG_FILE}")
            
        except Exception as e:
            self.print_error(f"Failed to save configuration: {e}")
            return False
        
        return True
    
    # v1.0.0: Main configuration wizard (v1.3.0: updated with better flow, v2.2.0: updated version, v2.3.0: updated, v2.4.0: updated, v2.5.0: updated, v2.6.0: updated, v3.0.0: updated)
    def run_configuration_wizard(self):
        """Run the complete configuration wizard"""
        self.print_header(f"SONARR CALENDAR PRO - CLI CONFIGURATION v3.0.0")
        
        print("Welcome to the Sonarr Calendar configuration tool!")
        print(f"Platform: {self.system}")
        print(f"Execution Directory: {EXECUTION_DIR}")
        print("This wizard will help you set up your calendar preferences.\n")
        print("💡 Tip: Use Ctrl+Shift+C/V or right-click to copy/paste in most terminals")
        print("🔒 API keys are masked in real-time for security")
        print("   • Asterisks appear as you type or paste")
        print("   • 40 asterisks shown as confirmation after input")
        print("   • Backspace works normally")
        print("   • Press Ctrl+C at any time to exit gracefully\n")
        
        try:
            # Run through configuration sections
            self.configure_sonarr()
            self.configure_date_range()
            self.configure_file_paths()
            self.configure_refresh()
            
            # Show summary
            self.show_config_summary()
            
            # Confirm and save
            if self.get_yes_no("\nSave this configuration?", True):
                if self.save_configuration():
                    print(f"\n{Colors.GREEN}Configuration complete!{Colors.ENDC}")
                    print(f"You can now run the main Sonarr Calendar script:")
                    # v2.2.0: Platform-specific execution instruction
                    print(f"  {Colors.BOLD}sonarr_calendar.py{Colors.ENDC}  # Use 'python sonarr_calendar.py' (Windows) or 'python3 sonarr_calendar.py' (Linux/macOS)")
            else:
                print(f"\n{Colors.YELLOW}Configuration cancelled.{Colors.ENDC}")
        except KeyboardInterrupt:
            # This should be caught by the signal handler, but just in case
            print(f"\n\n{Colors.YELLOW}⚠️  Configuration interrupted{Colors.ENDC}")
            print(f"{Colors.BLUE}ℹ️  Exiting gracefully. No changes were saved.{Colors.ENDC}\n")
            sys.exit(0)
    
    # v1.1.0: Quick configuration mode (v2.2.0: updated, v2.5.0: updated, v2.6.0: updated, v3.0.0: updated)
    def quick_configure(self, args):
        """Quick configuration using command line arguments"""
        self.print_header(f"QUICK CONFIGURATION v3.0.0")
        
        # Map command line args to config
        if args.url:
            self.config['sonarr_url'] = args.url
        if args.api_key:
            self.config['sonarr_api_key'] = args.api_key
        if args.days_past:
            self.config['days_past'] = args.days_past
        if args.days_future:
            self.config['days_future'] = args.days_future
        if args.html_file:
            self.config['output_html_file'] = args.html_file
        if args.json_file:
            self.config['output_json_file'] = args.json_file
        if args.cache_dir:
            self.config['image_cache_dir'] = args.cache_dir
        if args.refresh_interval:
            self.config['refresh_interval_hours'] = args.refresh_interval
        
        # Show summary
        self.show_config_summary()
        
        # Save
        if self.save_configuration():
            print(f"\n{Colors.GREEN}Quick configuration complete!{Colors.ENDC}")
    
    # v1.0.0: Show configuration
    def show_config(self):
        """Display current configuration"""
        if not self.config:
            self.print_warning("No configuration found.")
            return
        
        self.show_config_summary()
        print(f"\nConfig file: {CONFIG_FILE}")
    
    # v1.0.0: Reset configuration
    def reset_config(self):
        """Reset configuration to defaults"""
        if self.get_yes_no("Are you sure you want to reset all configuration?", False):
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
                self.print_success("Configuration reset to defaults")
                self.config = {}
            else:
                self.print_warning("No configuration file found")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Sonarr Calendar Pro - CLI Configuration Tool v3.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run interactive configuration wizard
  %(prog)s --show              # Show current configuration
  %(prog)s --reset              # Reset configuration to defaults
  %(prog)s --quick --url http://localhost:8989 --api-key YOUR_KEY  # Quick config
  
Platform Support:
  Windows, Linux, macOS - automatically detects and handles paths appropriately
  Files default to execution directory: current working directory
  
Copy/Paste Support:
  • Windows Terminal: Ctrl+Shift+C/V or right-click
  • Linux Terminal: Ctrl+Shift+C/V or middle-click/right-click
  • macOS Terminal: Cmd+C/V or right-click
  • All platforms support standard terminal paste operations
  
Security Features (v3.0.0):
  • Pre-execution OS validation and dependency checking
  • Real-time API key masking with asterisks
  • Visual confirmation with 40 asterisks after input
  • Graceful handling of Ctrl+C interrupts
  • Clear installation instructions for each OS
  
Default Settings:
  • Refresh Interval: 6 hours (optimized for typical usage)
  • Days Past: 7 days
  • Days Future: 30 days
  • Sonarr URL: http://localhost:8989
        """
    )
    
    # General options
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--reset', action='store_true', help='Reset configuration to defaults')
    parser.add_argument('--quick', action='store_true', help='Quick configuration mode')
    
    # Configuration options (for quick mode)
    parser.add_argument('--url', help='Sonarr URL')
    parser.add_argument('--api-key', help='Sonarr API key')
    parser.add_argument('--days-past', type=int, help='Days to look back')
    parser.add_argument('--days-future', type=int, help='Days to look forward')
    parser.add_argument('--html-file', help='HTML output file path')
    parser.add_argument('--json-file', help='JSON output file path')
    parser.add_argument('--cache-dir', help='Image cache directory')
    parser.add_argument('--refresh-interval', type=int, help='Refresh interval in hours')
    
    args = parser.parse_args()
    
    # Check for required dependencies in quick mode
    if args.quick and not (args.url and args.api_key):
        print("Error: Quick mode requires --url and --api-key")
        print("Example: python3 sonarr_config_cli.py --quick --url http://localhost:8989 --api-key YOUR_KEY")
        sys.exit(1)
    
    try:
        # Create configurator
        configurator = SonarrCLIConfig()
        
        # Handle commands
        if args.show:
            configurator.show_config()
        elif args.reset:
            configurator.reset_config()
        elif args.quick:
            configurator.quick_configure(args)
        else:
            # Run interactive wizard
            configurator.run_configuration_wizard()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Configuration interrupted by user{Colors.ENDC}")
        print(f"{Colors.BLUE}ℹ️  Exiting gracefully. No changes were saved.{Colors.ENDC}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()