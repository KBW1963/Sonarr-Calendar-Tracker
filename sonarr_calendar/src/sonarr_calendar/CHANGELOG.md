# Changelog

All notable changes to the Sonarr Calendar Tracker project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## Sonarr Calendar Tracker (Main Application)


### [2.7.0] - 2026-02-19
#### Added
- `get_image_by_type()` in `image_cache.py` to fetch a specific image type (e.g., poster) without altering the main fanart priority.
- `poster_image` field in `ProcessedShow` dataclass, storing the dedicated poster URL for each show.
- **Recently Completed Seasons section now uses poster images** for a more professional look, while main show cards continue to use fanart.

#### Changed
- `calculate_completed_seasons_in_range()` now uses `show.poster_image` instead of the fanart URL.

### [2.6.0] - 2026-02-18
#### Changed
- **Image priority** – The application now uses **fanart** as the primary image for show cards, with fallback to poster and then banner. This provides wider, more scenic images.
- Modified `get_poster_url()` in `image_cache.py` to implement priority order: fanart → poster → banner → any image.
- Updated `config.py` to search for configuration file in the user's home directory (`~/.sonarr_calendar_config/`) as well as the traditional locations.
- **Configuration file location** – The main application now also looks in `~/.sonarr_calendar_config/` (where the config script saves) to avoid permission issues.
- Updated help text in `cli.py` to mention the new config search path.

#### Fixed
- Resolved indentation error in `cli.py` that caused a `SyntaxError` when running the script.
- Ensured that the image cache correctly downloads fanart when available.

### [2.5.1] - 2026-02-16
#### Added
- Graceful interrupt handling – Press `Ctrl+C` once to exit cleanly, twice to force quit.
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
- Cleaner footer layout.

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

## [2.6.0] - 2026-02-18 (Summary)
- **Fanart priority** implemented in main application.
- Configuration file now searched in user's home directory.
- CLI config tool v3.1.2 fixes NameError.
- CLI config tool now saves config in home directory.
- All scripts updated for better cross‑platform reliability.
