# Changelog

All notable changes to the Sonarr Calendar Tracker project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## Sonarr Calendar Tracker (Main Application)

### [2.7.0] - 2026-02-22
#### Added
- Display version now includes the primary image type – e.g., `2.7.0-fanart` in HTML footer and JSON output. The image type suffix is defined in `__init__.py` (`__image_type__`) and automatically appended.
- JSON output now correctly uses the dynamic version (`__display_version__`), ensuring consistency with the HTML footer.

#### Changed
- `setup.py` now reads the version dynamically from `__init__.py` (via `get_version()`), so the package version always matches the internal version.
- Removed all traces of the old monolithic script; the application is now purely modular and installed via `pip`.

#### Fixed
- JSON version no longer shows stale `2.6.0`; it now reflects the actual version.
- Indentation errors in `html_generator.py` and `cli.py` resolved.

### [2.6.0] - 2026-02-18
#### Added
- **Fanart priority** – the application now uses fanart as the primary image for show cards, with fallback to poster and banner.
- Configuration file search now includes the user's home directory (`~/.sonarr_calendar_config/`) to match the config tool's new default location.
- Help text in `cli.py` updated to mention the new config search path.

#### Fixed
- Indentation error in `cli.py` that caused a `SyntaxError`.

### [2.5.1] - 2026-02-16
#### Added
- Graceful interrupt handling – press `Ctrl+C` once to exit cleanly, twice to force quit.
- Coloured terminal output with emojis.
- OS‑aware date formatting (system locale settings).

### [2.5.0] - 2026-02-15
#### Added
- Uniform card heights with visual padding items.
- Interactive expand/collapse for episode lists, with hover‑away reset.
- Episode badges for Premieres, Season Finales, and Series Finales.
- Last execution date/time in footer.
- Version number in footer.
- Next update projection in footer.
- Cleaner footer layout (removed redundant instruction text).

#### Fixed
- Complete Shows KPI now correctly counts shows that completed their **current season**.
- Theme toggle: all UI elements (progress sections, completed seasons) now stay dark in light mode.
- Light mode background set to `#F5F5F5` (softer).
- Footer text now pure black (`#000000`) in light mode.
- Season finale badge detection using proper season episode counts.
- Correct episode counts for multi‑episode releases.

### [2.4.0] - 2026-02-14
#### Added
- Light theme background changed to `#F5F5F5` (softer).
- Footer text readability improved in light mode.
- Proper season finale badge detection.
- Season episode count tracking for finale detection.

### [2.3.0] - 2026-02-13
#### Added
- Full cross‑platform support with platform‑specific optimisations.
- Better terminal handling and file path handling.

### [2.2.0] - 2026-02-12
#### Added
- API key masking in logs.
- Improved connection error handling.
- Better timeout management.
- Enhanced validation.

### [2.1.0] - 2026-02-11
#### Added
- Auto‑refresh capability.
- Improved cache handling.
- Better performance.
- Status bar updates.

### [2.0.0] - 2026-02-10
#### Added
- Theme selection (dark/light).
- Grid layout customisation.
- Image quality options.
- Cache management improvements.

### [1.3.0] - 2026-02-09
#### Added
- Emoji icons for better UX.
- Improved error messages.
- Better status feedback.
- Enhanced HTML styling.

### [1.2.0] - 2026-02-08
#### Added
- Episode details and summaries.
- Improved image loading.
- Better date range handling.
- Added series information display.

### [1.1.0] - 2026-02-07
#### Added
- Multi‑platform support (Windows, Linux, macOS).
- Platform‑specific path handling.
- Cross‑platform directory operations.
- Better error handling.

### [1.0.0] - 2026-02-06
#### Added
- Initial release.
- Basic calendar generation.
- Sonarr API integration.
- HTML output with dark theme.
- Image caching support.

---

## CLI Configuration Tool (`sonarr_config_cli.py`)

### [3.1.3] - 2026-02-21
#### Added
- Platform‑specific paste instructions in API key prompts (Ctrl+V on Windows, Ctrl+Shift+V/right‑click on Unix).
- Display of the loaded configuration file path at startup.

#### Fixed
- Improved masked input to better handle pasted text; right‑click paste now works more reliably on supported terminals.

### [3.1.2] - 2026-02-18
#### Fixed
- **NameError in connection test** – moved requests import check inside the class to avoid scoping issues.
- Connection test now works correctly.

### [3.1.1] - 2026-02-18
#### Changed
- Configuration directory changed from script folder to user's home directory (`~/.sonarr_calendar_config/`) to avoid permission problems.
- Added automatic directory creation when saving the configuration file.

### [3.1.0] - 2026-02-18
#### Added
- **Image cache enable/disable option** – interactive prompt and command‑line flag `--enable-image-cache`.
- Configuration now includes `enable_image_cache` boolean.
- Updated summary display to show cache status.
- Parity with main calendar generator configuration.

### [3.0.0] - 2026-02-16
#### Added
- Pre‑execution OS validation and dependency checking.
- Platform‑specific installation instructions.
- Python version validation.
- Terminal capability checking.

### [2.6.0] - 2026-02-15
#### Added
- Real‑time API key masking with asterisks while typing/pasting.
- Visual confirmation shows 40 asterisks after input.
- Backspace and delete keys work normally.
- Cross‑platform compatibility for all terminal types.

### [2.5.0] - 2026-02-14
#### Fixed
- API key input now shows 40 asterisks when pasted.
- Auto‑submit after paste with visual confirmation.
- Graceful handling of Ctrl+C interrupts.

### [2.4.0] - 2026-02-13
#### Added
- Enhanced connection error handling with restart option.
- Connection failure now prompts user to restart configuration.
- API key input shows 40 asterisks when pasted.

### [2.3.0] - 2026-02-12
#### Added
- API key input now masked with asterisks during typing.
- Refresh interval default set to 6 hours.

### [2.2.0] - 2026-02-11
#### Added
- Config file existence check at startup.
- Option to use existing values as defaults.
- API key masking in prompts – displays only last 6 characters.
- Improved platform‑specific execution instructions.

### [2.1.0] - 2026-02-10
#### Added
- Terminal native copy/paste support (Ctrl+Shift+C/V, right‑click).
- Cross‑platform clipboard compatibility.

### [1.3.0] - 2026-02-09
#### Added
- Emoji icons for better UX.
- Configuration summary display.
- Status messages with colour coding.

### [1.2.0] - 2026-02-08
#### Added
- `requests` library integration.
- Sonarr connection testing.
- API key masking in display.

### [1.1.0] - 2026-02-07
#### Added
- Multi‑platform support.
- Platform‑specific path handling.
- Cross‑platform directory operations.

### [1.0.0] - 2026-02-06
#### Added
- Initial release.
- Basic configuration wizard.
- Sonarr connection settings.
- Date range configuration.
- File path configuration.
- Refresh interval in hours.

---

## GUI Configuration Tool (`sonarr_calendar_config.py`)

### [2.2.4] - 2026-02-22
#### Changed
- **Summary dialog layout improved**: The Close button is now always visible at the bottom without needing to scroll. Default window size increased to `700x500`, with proper `pack` layout that keeps the button fixed while the text area expands.

### [2.2.3] - 2026-02-22
#### Added
- Configuration now saved in the user's home directory (`~/.sonarr_calendar_config/`) by default, avoiding permission issues.
- When loading, the tool searches the home directory first, then falls back to the old script directory (migration support).
- Displays the full path of the loaded configuration file in the status bar and a message box.

#### Changed
- Summary dialog button renamed from "OK" to "Close" for clarity.
- Version dates updated to 2026 throughout the script.

### [2.2.2] - 2026-02-21
#### Fixed
- Right‑click paste now correctly uses the `<<Paste>>` virtual event, ensuring reliable pasting.
- Displays the full path of the loaded configuration file in status bar and dialog.

### [2.2.1] - 2026-02-20
#### Fixed
- Minor fixes and improvements.

### [2.2.0] - 2026-02-19
#### Added
- Checkbox to enable/disable image caching.
- Fixed double‑paste in input fields.
- Increased window height to prevent bottom truncation.
- Configuration now includes `enable_image_cache` (default `true`).

### [2.1.0] - 2026-02-19
#### Added
- Right-click context menu for all input fields (Cut, Copy, Paste, Select All).
- Keyboard shortcuts (Ctrl+X/C/V/A, Cmd+X/C/V/A on macOS).
- Cross-platform clipboard support.

### [2.0.0] - 2026-02-18
#### Added
- Redesigned layout with sections and improved spacing.
- Connection testing with visual feedback.
- API key visibility toggle (show/hide).
- Configuration validation before saving.
- Summary dialog after saving.
- Status bar for user feedback.
- Platform-specific window icon support.
- Window centering on all platforms.

### [1.3.0] - 2026-02-17
#### Added
- Configuration validation.
- Summary display after save.
- Improved error messages.
- Better layout with section headers.

### [1.2.0] - 2026-02-16
#### Added
- Connection test button with status display.
- API key visibility toggle.
- Check for `requests` library (optional).

### [1.1.0] - 2026-02-15
#### Added
- Platform detection for paths and clipboard.
- Cross-platform directory/file browsers.
- Window icon support (Windows, Linux, macOS).
- Window centering.

### [1.0.0] - 2026-02-14
#### Added
- Basic GUI for configuration.
- Sonarr URL, API key, date range, file paths, refresh interval.
- Save/load/reset functionality.

---

## Infrastructure & Documentation

### [2026-02-22]
#### Changed
- `setup.py` now dynamically reads the version from `src/sonarr_calendar/__init__.py` instead of hardcoding it. This ensures the package version always matches the internal application version.
- The project is now installable via `pip install -e .` and the `sonarr-calendar` console script works reliably from any location.
- Removed the obsolete monolithic `sonarr_calendar.py` script.

---