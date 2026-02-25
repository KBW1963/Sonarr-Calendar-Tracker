## **SYNOPSIS.md**
# Project Synopsis – Sonarr Calendar Tracker

It is intended for those who want to understand the internal structure. The document explains the purpose of each script/module in the project. 

This document explains the purpose of each script/module in the project. It is intended for developers and contributors who want to understand the internal structure and recent updates.

**Current Versions:**
- Main Application: `2.7.0`
- CLI Configuration Tool: `3.1.3`
- GUI Configuration Tool: `2.2.4`
---

## 📁 `src/sonarr_calendar/` – Main package

### `__init__.py`
- Marks the directory as a Python package.
- Defines the application version and image type:
  ```python
  __version__ = "2.7.0"
  __image_type__ = "fanart"
  __display_version__ = f"{__version__}-{__image_type__}"

- `__display_version__` is used in the HTML footer and JSON output to show both version and active image priority (e.g., `2.7.0-fanart`).

### `__main__.py`
Allows the package to be executed with `python -m sonarr_calendar`.
Simply imports and calls `cli.main()`.

### `cli.py` – Command‑line interface
- Parses command‑line arguments (`--once, --config, --verbose`).
- Loads configuration using `config.load_config()` (searches current dir, script dir, project root, and home directory).
- Creates a single `GracefulInterruptHandler` for the whole application.

Orchestrates the main workflow:
1. Fetch calendar data and series from Sonarr.
2. Cache images (fanart priority) in parallel.
3. Process data into `ProcessedShow` objects.
4. Generate HTML via `HTMLGenerator`.
5. Optionally write JSON metadata (using `__display_version__`).
- Handles auto‑refresh loop with interrupt checking.
- Updated in v2.7.0: Uses dynamic version from `__init__.py`; JSON version now matches HTML footer.

### `config.py` – Configuration management
- Defines the `Config` dataclass with all settings and default values.
- Provides `load_config()` to locate and read the JSON config file.
- Search order: explicit `--config` → current dir → script dir → project root → home directory (`~/.sonarr_calendar_config/`).
- Logs the path of the loaded config file (visible with `--verbose`).
- All optional fields have defaults (e.g., `image_quality="fanart", "html_title": "Your_TITLE"`).

### `api_client.py` – Sonarr API client
- Wraps Sonarr’s REST API with retry logic and session reuse.
- `SonarrClient.get_calendar()` fetches episodes in the given date range and returns them together with a `DateRange` object.
- `get_all_series()` retrieves all series for image caching and statistics.
- Uses the shared `GracefulInterruptHandler` to abort requests when interrupted.

### `models.py` – Data models and business logic
- Defines dataclasses: `SeriesInfo`, `Episode`, `ProcessedShow`.
- `SeriesInfo.from_api()` converts raw API JSON into a structured object, extracting episode counts and season maps.
- `Episode.from_api()` builds an `Episode` with computed fields like `days_until` and `formatted_season_episode`.
- `calculate_progress()` computes overall progress, current season stats, and colour codes.
- `process_calendar_data()` groups episodes by series, enriches them with series info, and returns a list of `ProcessedShow`.
- `calculate_overall_statistics()` aggregates data from all shows for the summary cards.
- `calculate_completed_seasons_in_range()` identifies shows that completed their current season within the date range, using `poster_image` for display.
- New in v2.7.0: `ProcessedShow` includes `poster_url` (fanart) and `poster_image` (poster) fields – the latter used only for the completed seasons section.
  
### `image_cache.py` – Poster caching
- `get_poster_url()` extracts the best available poster URL from series info, handling relative paths.
- `ImageCache` manages a local directory of cached images.
- `_download_one()` downloads a single image if missing or older than 7 days.
- `download_all_posters()` uses a thread pool to download all posters in parallel, returning a count of successful downloads.
- Updated in v2.6.0: Fanart priority added; cleaned up error handling.

### `html_generator.py` – HTML rendering with Jinja2
- Loads the Jinja2 environment from the `templates/` folder.
- Registers custom filters and global functions (`format_date`, `slugify`, `get_episode_badge`, etc.).
- `generate()` computes overall statistics and completed seasons, then renders `calendar.html.j2` with all context variables.
- Updated in v2.7.0: Passes __display_version__ to the template (footer shows e.g., Version 2.7.0-fanart).

### `utils.py` – Shared utilities
- `GracefulInterruptHandler`: catches `SIGINT`, prints a message, and raises `KeyboardInterrupt` on the first press.
- `DateRange`: simple dataclass for start/end dates.
- Date formatting functions: `get_system_date_format()`, `format_date_for_display()`, `days_until()`.
- `get_progress_bar_color()` – maps a percentage to a CSS colour.
- Episode display helpers: `get_episode_badge()`, `get_days_class()`, `get_days_text()`.
- `slugify()` – converts a show title to a URL‑friendly slug.
- `setup_logging()` – configures the `logging` module based on verbosity.

### 📁 `templates/`
- `calendar.html.j2` – The Jinja2 template containing the entire HTML/CSS/JavaScript. It uses placeholders for dynamic data and relies on the filters/functions registered in `html_generator.py`. Now receives fanart URLs via `show.poster_url`.

---

## 📁 Configuration Tools – 

## `sonarr_config_cli.py`

Interactive wizard for creating and managing configuration files.

- **Features:**

- Real‑time API key masking with platform‑specific paste instructions.
- Connection testing (if `requests` is installed).
- Image cache enable/disable option (`--enable-image-cache`).
- Configuration saved in user's home directory (`~/.sonarr_calendar_config/`).
- Pre‑execution OS validation and dependency checking.
- Quick mode for non‑interactive setup.
- **Input sanitization** – accidental arrow keys or other control characters are automatically removed, preventing path corruption.
- Graceful interrupt handling (`Ctrl+C`).

## `sonarr_calendar_config.py`
Simple graphical interface for quick configuration.

Features:
- Right‑click context menu with cut/copy/paste (fixed paste in v2.2.4).
- API key visibility toggle (show/hide).
- Connection testing.
- Image cache enable/disable checkbox.
- Saves configuration to home directory (fallback to script directory for migration).
- Scrollable summary dialog with always‑visible Close button.
- Cross‑platform (Windows, Linux, macOS) with native look.

---

## Root files

- `setup.py`: Makes the package installable, defines dependencies, and creates the `sonarr-calendar` console script.
- `requirements.txt`: Lists runtime dependencies for quick installation.
- `README.md`: User‑facing documentation.
- `SYNOPSIS.md`: This file – developer overview.
- `CONTRIBUTING.md`: Guidelines for contributors.
- `CHANGELOG.md`: Version history.
- `LICENSE`: MIT license file.

---

🔄 Data Flow (Current)
1. User runs `sonarr-calendar` (or `python -m sonarr_calendar`).
2. `cli.py` loads config (searching multiple locations, logs the path).
3. Fetches episodes and series from Sonarr via `SonarrClient`.
4. Image cache (`image_cache.py`) downloads fanart (or fallback) for all series in parallel.
5. `process_calendar_data()` transforms raw data into `ProcessedShow` objects:
    - `poster_url` → fanart (for main cards)
    - `poster_image` → poster (for completed seasons)
6. `HTMLGenerator` computes statistics and renders the template, using:
    - `__display_version__` for the footer
    - `poster_image` for completed seasons
7. HTML file is written to disk (and optionally JSON metadata with version).
8. If in auto‑refresh mode, the script sleeps (checking for interrupts) and repeats.

---
### 🆕 Recent Major Changes (Newest to Oldest)
- v2.7.0 (Main App) – Version suffix includes image type (2.7.0-fanart); JSON version now matches HTML footer; fanart priority finalised; completed seasons section now uses poster images.
- v2.2.4 (GUI Config) – Improved summary dialog layout – Close button always visible, larger default window.
- v2.2.3 (GUI Config) – Configuration now saved in user's home directory; migration fallback from old location; displays config file path on load.
- v3.1.3 (CLI Config) – Platform‑specific paste instructions; config file path displayed at startup.
- v2.2.2 (GUI Config) – Fixed right‑click paste; displays config file path on load.
- v2.6.0 (Main App) – Fanart priority implemented; config search now includes home directory.
- v3.1.1 (CLI Config) – Changed config save location to home directory (permission fix).

All scripts remain fully cross‑platform (Windows, Linux, macOS).
