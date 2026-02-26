"""Version information and update checking."""

import threading

import requests


__version__ = '0.1.0'

RELEASES_URL = 'https://api.github.com/repos/SullivanXiong/minimalist/releases/latest'


def check_for_updates(callback):
    """Check for updates in a background thread.

    Calls callback(latest_version, download_url) if an update is available,
    or callback(None, None) if up to date or check fails.
    """
    def _check():
        try:
            resp = requests.get(RELEASES_URL, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                latest = data.get('tag_name', '').lstrip('v')
                if latest and latest != __version__:
                    url = data.get('html_url', '')
                    callback(latest, url)
                    return
        except requests.RequestException:
            pass
        callback(None, None)

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
