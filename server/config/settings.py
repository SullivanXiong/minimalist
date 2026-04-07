"""
Django settings router for Minimalist project management app.

Imports the appropriate environment settings based on DJANGO_ENV.
"""

import os

env = os.getenv('DJANGO_ENV', 'development')

if env == 'production':
    from config.environments.production import *  # noqa: F401, F403
elif env == 'staging':
    from config.environments.staging import *  # noqa: F401, F403
else:
    from config.environments.development import *  # noqa: F401, F403
