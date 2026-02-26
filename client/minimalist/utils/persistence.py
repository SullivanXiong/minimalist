"""Local settings persistence (~/.config/minimalist/settings.json)."""

import json
import os

from ..config import DEFAULT_SETTINGS

SETTINGS_DIR = os.path.expanduser('~/.config/minimalist')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'settings.json')


def load_settings():
    """Load settings from disk, returning defaults for missing keys."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE) as f:
            stored = json.load(f)
            settings.update(stored)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return settings


def save_settings(settings):
    """Save settings to disk."""
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)
