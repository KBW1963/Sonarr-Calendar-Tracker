# Sonarr Calendar Tracker

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Sonarr](https://img.shields.io/badge/Sonarr-v3%2Fv4-orange)

A beautiful, feature‑rich HTML dashboard for your Sonarr shows.  
Track upcoming episodes over a specified date range, monitor overall progress, and see which seasons have been completed – all in a sleek, customisable interface.

### [Screenshot] - [https://github.com/KBW1963/sonarr_calendar/sonarr_calendar_screenshot.png](https://github.com/KBW1963/sonarr_calendar/blob/main/sonarr_calendar/sonarr_calendar_screenshot.png)
---
**NOTE: I am not a SW developer or a coder by trade. I am just using some skills from my past and my hobbyist approach to build this project. 
And YES! a lot of research was needed to help me understand and develop the code, along with some AI suggestions, which to be fair is hard to not do with search engines today.

So, please be understanding! ☺️.

---

## ✨ Features

- 📅 **Customisable date range** – Choose how many days past and future to display (configurable).
- 🖼️ **Image caching** – Show posters or fanart are downloaded and stored locally for faster loading. **Fanart is now the default priority**, with fallback to poster and banner. 
- 🎨 **Dark/light theme toggle** – Switch between themes with a click (your choice is saved in your browser).
- 📊 **Overall & per‑show progress** – See at a glance how much of your library is downloaded, and drill down into each series. Badges are used to highlight, Premiere episodes and Season Finale.
- 🏆 **Recently completed seasons** – Shows that finished their current season within the date range are highlighted. Poster is forced for a more professional UI.
- 🔄 **Auto‑refresh mode** – Keep the dashboard running and update periodically (configurable).
- ⌨️ **Graceful interrupt handling** – Press `Ctrl+C` once to exit cleanly, twice to force quit.
- 🌍 **OS‑aware date formatting** – Dates automatically adapt to your system’s locale (e.g. `DD/MM/YYYY` or `MM/DD/YYYY`).
- 🔗 **Direct links to Sonarr** – Click any show card to open its page in Sonarr.
- 🔒 **Secure API key handling** – All API key inputs are masked in real‑time with asterisks.
---

## 📦 Requirements

- **Python 3.8 or higher** - `requests>=2.28.0` ; `jinja2>=3.1.0` ; `colorama>=0.4.6`   # optional, for cross‑platform coloured output
- **Sonarr** (v3 or v4) with API access
- Operating systems: Windows, macOS, Linux (all fully supported)

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/KBW1963/sonarr-calendar.git
cd sonarr-calendar
```
### 2.  Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Configure the application
You have two ways to create the configuration file:

Option A – Use one of the interactive configuration scripts (recommended). Refer to the config apps folder
```bash
python sonarr_config_cli.py
```

Follow the prompts. The configuration file will be saved in your home directory under .sonarr_calendar_config/ to avoid permission issues.

Option B – Create the file manually

Create a file named .sonarr_calendar_config.json in one of the following locations (searched in order):

- Current working directory
- Same directory as the script (src/sonarr_calendar/)
- Parent of the script directory (src/)
- Your home directory (~/.sonarr_calendar_config/)

Minimal configuration:
```json
{
    "sonarr_url": "http://localhost:8989",
    "sonarr_api_key": "YOUR_API_KEY",
    "days_past": 7,
    "days_future": 7,
    "output_html_file": "sonarr_calendar.html"
}
```
See Configuration for all available options.

### 4.  Run the calendar generator
```bash
# One‑time run. Runs once and exits.
python -m sonarr_calendar --once

# Auto‑refresh mode. Refreshers based on config setting.
python -m sonarr_calendar
```
---
### ⚙️ Configuration
All settings are optional except `sonarr_url` and `sonarr_api_key`. Defaults are shown below.

| Field |	Description |	Default
|-------|-------------|---------|
|`sonarr_url`| Your Sonarr instance URL (including port) | required
|`sonarr_api_key`| API key from Sonarr (Settings → General)| required
|`days_past`|Number of past days to include | 7
|`days_future`|	Number of future days to include| 7 
|`output_html_file`	| Path where the HTML file will be save	| sonarr_calendar.html (in current dir)
|`output_json_file`| Optional JSON output (metadata only)| null (no JSON)
|`image_cache_dir`| Directory for cached images	|sonarr_images (in current dir)
|`refresh_interval_hours`| Hours between auto‑refreshes	|6
|`html_theme`|dark or light	|dark
|`image_quality`|Preferred image type (hint; actual priority is hardcoded: fanart → poster → banner) | fanart
|`enable_image_cache`| Whether to cache images locally	|true (recommended)


### 📁 Configuration File Location
The configuration script (sonarr_config_cli.py) saves the file in your home directory:

- Windows: C:\Users\YourName\.sonarr_calendar_config\.sonarr_calendar_config.json
- Linux/macOS: /home/yourname/.sonarr_calendar_config/.sonarr_calendar_config.json
The main application searches multiple locations (current directory, script directory, project root, and home directory) so you can place the file wherever convenient.
---

### 🖼️ Image Priority
The application prioritises fanart images for show cards, providing wider, more scenic artwork. If fanart is not available for a series, it falls back to poster, then banner, and finally any available image.
To force a refresh of cached images, delete the contents of your image_cache_dir and run the generator again.

---

### 🔧 Troubleshooting
|Problem	|Solution |
|---------|---------|
|'ImportError: No module named jinja2'	|Run `pip install -r requirements.txt`
|Configuration file not found	|Ensure the file exists in one of the search paths. Run `sonarr_config_cli.py` to create it or manually create.
|Sonarr connection failed|	Verify `sonarr_url` and `sonarr_api_key`. Ensure Sonarr is reachable from your machine.
|No episodes shown	|Check your `days_past` and `days_future` settings. The date range might not contain any air dates.
|Images not loading	|Ensure `enable_image_cache` is `true` and the cache directory is writable.
|Permission denied when saving config	|The script now saves to your home directory – this should no longer occur.
|Fanart not downloading	|The image priority is now fanart; if fanart is unavailable, poster is used. Check Sonarr for fanart availability.
---

### 📜 Scripts Overview
Main Application (sonarr_calendar/)
- `cli.py` – Command‑line entry point, handles auto‑refresh and interrupt.
- `config.py` – Configuration loading and validation.
- `api_client.py` – Sonarr API client with retries.
- `models.py` – Data models and business logic.
- `image_cache.py` – Parallel image downloading with fanart priority.
- `html_generator.py` – Jinja2 HTML generation.
- `utils.py` – Shared utilities (interrupt handler, date formatting, etc.).
---

## 📄 License
This project is licensed under the MIT License – see the LICENSE file for details.

Happy tracking! 📺

