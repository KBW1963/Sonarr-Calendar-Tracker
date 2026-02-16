
## **SYNOPSIS.md**
# Project Synopsis – Sonarr Calendar Tracker

It is intended for those who want to understand the internal structure. The document explains the purpose of each script/module in the project. 

## 📁 `src/sonarr_calendar/` – Main package

### `__init__.py`
Marks the directory as a Python package and may contain the version string.

### `__main__.py`
Allows the package to be executed with `python -m sonarr_calendar`. Simply imports and calls `cli.main()`.

### `cli.py` – Command‑line interface
- Parses command‑line arguments (`--once`, `--config`, `--verbose`).
- Loads configuration using `config.load_config()`.
- Creates a single `GracefulInterruptHandler` for the whole application.
- Orchestrates the main workflow: fetching data, caching images, processing shows, generating HTML, and optionally writing JSON.
- Handles auto‑refresh loop with interrupt checking.

### `config.py` – Configuration management
- Defines the `Config` dataclass with all settings and default values.
- Provides `load_config()` to locate and read the JSON config file.
- Validates essential fields (URL format, non‑negative days, positive refresh interval).

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
- `calculate_completed_seasons_in_range()` identifies shows that completed their current season within the date range.

### `image_cache.py` – Poster caching
- `get_poster_url()` extracts the best available poster URL from series info, handling relative paths.
- `ImageCache` manages a local directory of cached images.
- `_download_one()` downloads a single image if missing or older than 7 days.
- `download_all_posters()` uses a thread pool to download all posters in parallel, returning a count of successful downloads.

### `html_generator.py` – HTML rendering with Jinja2
- Loads the Jinja2 environment from the `templates/` folder.
- Registers custom filters and global functions (`format_date`, `slugify`, `get_episode_badge`, etc.).
- `generate()` computes overall statistics and completed seasons, then renders `calendar.html.j2` with all context variables.

### `utils.py` – Shared utilities
- `GracefulInterruptHandler`: catches `SIGINT`, prints a message, and raises `KeyboardInterrupt` on the first press.
- `DateRange`: simple dataclass for start/end dates.
- Date formatting functions: `get_system_date_format()`, `format_date_for_display()`, `days_until()`.
- `get_progress_bar_color()` – maps a percentage to a CSS colour.
- Episode display helpers: `get_episode_badge()`, `get_days_class()`, `get_days_text()`.
- `slugify()` – converts a show title to a URL‑friendly slug.
- `setup_logging()` – configures the `logging` module based on verbosity.

### 📁 `templates/`
- `calendar.html.j2` – The Jinja2 template containing the entire HTML/CSS/JavaScript. It uses placeholders for dynamic data and relies on the filters/functions registered in `html_generator.py`.

---

## Root files

- `setup.py`: Makes the package installable, defines dependencies, and creates the `sonarr-calendar` console script.
- `requirements.txt`: Lists runtime dependencies for quick installation.
- `README.md`: User‑facing documentation.
- `CONTRIBUTING.md`: Guidelines for contributors.
- `CHANGELOG.md`: Version history.
- `LICENSE`: MIT license file.

---

## Data flow

1. User runs `sonarr-calendar`.
2. `cli.py` loads config and creates a `GracefulInterruptHandler`.
3. Fetches episodes and series from Sonarr via `SonarrClient`.
4. Downloads/caches posters in parallel.
5. `process_calendar_data()` transforms raw data into `ProcessedShow` objects.
6. `HTMLGenerator` computes statistics and renders the template.
7. HTML file is written to disk (and optionally JSON metadata).
8. If in auto‑refresh mode, the script sleeps (checking for interrupts) and repeats.

---
