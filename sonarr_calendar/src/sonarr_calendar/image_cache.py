# src/sonarr_calendar/image_cache.py
import os
from pathlib import Path
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Union
import logging
from sonarr_calendar.utils import GracefulInterruptHandler

logger = logging.getLogger(__name__)

def get_poster_url(series_info: Union[Dict, 'SeriesInfo'], quality: str = 'fanart', base_url: str = '') -> Optional[str]:
    """
    Extract the best available image URL from series information.
    Priority order (hardcoded): fanart → poster → banner → any image.
    The 'quality' parameter is kept for compatibility but not strictly used.
    """
    if hasattr(series_info, 'images'):
        images = series_info.images
    else:
        images = series_info.get('images', [])

    priority = ['fanart', 'poster', 'banner']

    for cover_type in priority:
        for img in images:
            if img.get('coverType') == cover_type:
                url = img.get('url')
                if url:
                    if url.startswith('http'):
                        return url
                    elif base_url:
                        return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                    else:
                        return url

    for img in images:
        url = img.get('url')
        if url:
            if url.startswith('http'):
                return url
            elif base_url:
                return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
            else:
                return url
    return None

def get_image_by_type(series_info: Union[Dict, 'SeriesInfo'], cover_type: str, base_url: str = '') -> Optional[str]:
    """
    Attempt to fetch a specific image type (e.g., 'poster') from the series.
    Returns None if that type is not available.
    """
    if hasattr(series_info, 'images'):
        images = series_info.images
    else:
        images = series_info.get('images', [])

    for img in images:
        if img.get('coverType') == cover_type:
            url = img.get('url')
            if url:
                if url.startswith('http'):
                    return url
                elif base_url:
                    return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                else:
                    return url
    return None

class ImageCache:
    def __init__(self, cache_dir: Path, interrupt_handler: GracefulInterruptHandler, base_url: str = ''):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.handler = interrupt_handler
        self.base_url = base_url

    def _download_one(self, series_id: int, url: str, image_type: str = 'fanart') -> bool:
        if self.handler.check_interrupt():
            return False
        dest = self.cache_dir / f"{series_id}_{image_type}.jpg"
        if dest.exists():
            return True
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return True
        except Exception as e:
            logger.debug("Failed to download %s: %s", url, e)
            return False

    def download_all_posters(self, all_series: List[Dict]) -> int:
        """Download images for all series in parallel. Uses fanart priority."""
        tasks = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for series in all_series:
                series_id = series['id']
                url = get_poster_url(series, 'fanart', self.base_url)
                if url:
                    tasks.append(executor.submit(self._download_one, series_id, url, 'fanart'))
            success = 0
            for future in as_completed(tasks):
                if self.handler.check_interrupt():
                    break
                if future.result():
                    success += 1
        return success