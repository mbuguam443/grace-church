import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

LOG_PATH = os.path.join(BASE_DIR, 'startup.log')
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')

import django
django.setup()

from django.conf import settings
try:
    from django.core.management import call_command
    marker = os.path.join(BASE_DIR, '.dbsynced')
    if not settings.DEBUG and not os.path.exists(marker):
        logger.info('First start: running migrate + collectstatic...')
        call_command('migrate', interactive=False)
        call_command('collectstatic', '--noinput')
        with open(marker, 'w') as f:
            f.write('Database schema synced on first start.\n')
        logger.info('Initial sync complete.')
except Exception as exc:
    logger.exception('Startup sync failed: %s', exc)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
