"""Application configuration with environment-aware server profiles."""

import os

# Environment: development, staging, production
MINIMALIST_ENV = os.getenv('MINIMALIST_ENV', 'development')

# Server profiles
_PROFILES = {
    'development': {
        'server_host': os.getenv('SERVER_HOST', 'localhost'),
        'server_port': os.getenv('SERVER_PORT', '8000'),
        'scheme': 'http',
        'ws_scheme': 'ws',
        'auth_required': False,
    },
    'staging': {
        'server_host': os.getenv('SERVER_HOST', 'minimalist-stage.example.com'),
        'server_port': os.getenv('SERVER_PORT', '443'),
        'scheme': 'https',
        'ws_scheme': 'wss',
        'auth_required': True,
    },
    'production': {
        'server_host': os.getenv('SERVER_HOST', 'minimalist.example.com'),
        'server_port': os.getenv('SERVER_PORT', '443'),
        'scheme': 'https',
        'ws_scheme': 'wss',
        'auth_required': True,
    },
}

_profile = _PROFILES.get(MINIMALIST_ENV, _PROFILES['development'])

SERVER_HOST = _profile['server_host']
SERVER_PORT = _profile['server_port']
AUTH_REQUIRED = _profile['auth_required']

# Build URLs — omit port for standard ports (443/80)
if SERVER_PORT in ('443', '80'):
    SERVER_URL = f"{_profile['scheme']}://{SERVER_HOST}"
    WS_URL = f"{_profile['ws_scheme']}://{SERVER_HOST}"
else:
    SERVER_URL = f"{_profile['scheme']}://{SERVER_HOST}:{SERVER_PORT}"
    WS_URL = f"{_profile['ws_scheme']}://{SERVER_HOST}:{SERVER_PORT}"

DEFAULT_WORKSPACE_SLUG = 'default'

DEFAULT_SETTINGS = {
    'last_workspace_slug': DEFAULT_WORKSPACE_SLUG,
    'last_project_id': None,
    'window_width': 1200,
    'window_height': 800,
    'sidebar_width': 220,
    'view_mode': 'board',
    'server_url': None,
}
