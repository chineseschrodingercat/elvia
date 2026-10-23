"""Bounded ROR v2 suggestions; no account/profile data is sent upstream."""
from collections import OrderedDict
import json
import threading
import time
import requests


class InstitutionSearch:
    def __init__(self):
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.slots = threading.BoundedSemaphore(2)

    def search(self, query):
        query = ' '.join(query.split())[:150]
        if len(query) < 2:
            return {'items': [], 'available': True}
        key = query.casefold()
        now = time.monotonic()
        with self.lock:
            cached = self.cache.get(key)
            if cached and cached[0] > now:
                return cached[1]
        unavailable = {'items': [], 'available': False}
        if not self.slots.acquire(blocking=False):
            return unavailable
        try:
            with requests.Session() as session:
                session.trust_env = False
                with session.get('https://api.ror.org/v2/organizations',
                                 params={'query': query}, timeout=(2, 4),
                                 headers={'User-Agent': 'ELVIA/1.0 (https://elvia-atlas.org/contact.html)'},
                                 allow_redirects=False, stream=True) as response:
                    if response.status_code != 200:
                        return unavailable
                    raw = response.raw.read(1048577, decode_content=True)
                    if len(raw) > 1048576:
                        return unavailable
                    payload = json.loads(raw)
            items = []
            for item in payload.get('items', [])[:12]:
                names = item.get('names', [])
                display = next((n['value'] for n in names if 'ror_display' in n.get('types', [])), '')
                if not display:
                    continue
                place = (item.get('locations') or [{}])[0].get('geonames_details', {})
                location = ', '.join(x for x in [place.get('name'), place.get('country_name')] if x)
                items.append({'name': display[:300], 'location': location[:200]})
            result = {'items': items, 'available': True}
            with self.lock:
                self.cache[key] = (now + 86400, result)
                self.cache.move_to_end(key)
                while len(self.cache) > 256:
                    self.cache.popitem(last=False)
            return result
        except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError, OSError):
            return unavailable
        finally:
            self.slots.release()
