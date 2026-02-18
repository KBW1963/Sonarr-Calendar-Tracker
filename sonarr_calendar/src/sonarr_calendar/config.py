# src/sonarr_calendar/config.py
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Config:
    sonarr_url: str
    sonarr_api_key: str
    days_past: int
    days_future: int
    output_html_file: str
    # Optional fields with defaults
    output_json_file: Optional[str] = None
    image_cache_dir: str = "sonarr_images"
    refresh_interval_hours: int = 6
    html_theme: str = "dark"
    grid_columns: int = 4
    image_quality: str = "fanart"
    enable_image_cache: bool = True
    html_title: str = "Sonarr Calendar Pro"

    def __post_init__(self):
        if not self.sonarr_url.startswith(('http://', 'https://')):
            raise ValueError("sonarr_url must start with http:// or https://")
        if self.days_past < 0 or self.days_future < 0:
            raise ValueError("days_past and days_future must be non‑negative")
        if self.refresh_interval_hours <= 0:
            raise ValueError("refresh_interval_hours must be positive")

def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from a JSON file.
    Search order:
      1. Explicitly provided path.
      2. Current working directory.
      3. Directory of this script (src/sonarr_calendar).
      4. Parent of the script directory (project root).
      5. User's home directory ( ~/.sonarr_calendar_config/ ) – where the config script now saves.
    """
    if config_path is None:
        candidates = [
            Path.cwd() / '.sonarr_calendar_config.json',
            Path(__file__).parent / '.sonarr_calendar_config.json',
            Path(__file__).parent.parent / '.sonarr_calendar_config.json',
            Path.home() / '.sonarr_calendar_config' / '.sonarr_calendar_config.json',  # <-- new
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                logger.debug(f"Found config at {config_path}")
                break
        else:
            raise FileNotFoundError(
                f"Configuration file not found in any of:\n  " +
                "\n  ".join(str(p) for p in candidates)
            )
    else:
        if not config_path.exists():
            raise FileNotFoundError(f"Specified configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return Config(**data)