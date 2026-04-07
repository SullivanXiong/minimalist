"""Development environment settings."""

import os

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

AUTH_REQUIRED = False

# DRF: Allow unauthenticated access in development
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [  # noqa: F405
    'rest_framework.permissions.AllowAny',
]

# In development, optionally use in-memory channels
if os.getenv('USE_IN_MEMORY_CHANNELS', 'False') == 'True':
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
