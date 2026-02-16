import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, UTC
from sonarr_calendar.utils import GracefulInterruptHandler
from sonarr_calendar.utils import DateRange

logger = logging.getLogger(__name__)

class SonarrClient:
    def __init__(self, base_url: str, api_key: str, interrupt_handler: GracefulInterruptHandler):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.handler = interrupt_handler
        self.session = requests.Session()
        self.session.headers.update({'X-Api-Key': api_key})
        # Retry strategy
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get(self, path: str, params: Optional[Dict] = None, timeout: int = 30) -> Optional[Dict]:
        if self.handler.check_interrupt():
            raise KeyboardInterrupt
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s", e)
            return None

    def get_calendar(self, days_past: int, days_future: int) -> Tuple[List[Dict], DateRange]:
        today = datetime.now(UTC)
        start = today - timedelta(days=days_past)
        end = today + timedelta(days=days_future)
        params = {
            'start': start.date().isoformat(),
            'end': end.date().isoformat(),
            'includeSeries': 'true',
            'includeEpisodeFile': 'true',
            'unmonitored': 'true'
        }
        data = self._get('/api/v3/calendar', params=params)
        if data is None:
            return [], DateRange(start.date(), end.date())
        # Filter again to be safe
        filtered = []
        for ep in data:
            air = ep.get('airDate')
            if air:
                air_date = datetime.fromisoformat(air).date()
                if start.date() <= air_date <= end.date():
                    filtered.append(ep)
        return filtered, DateRange(start.date(), end.date())

    def get_all_series(self) -> List[Dict]:
        data = self._get('/api/v3/series')
        return data if data is not None else []

    def get_series(self, series_id: int) -> Optional[Dict]:
        return self._get(f'/api/v3/series/{series_id}')

    def get_episode_file(self, file_id: int) -> Optional[Dict]:
        return self._get(f'/api/v3/episodefile/{file_id}')

    def close(self):
        self.session.close()