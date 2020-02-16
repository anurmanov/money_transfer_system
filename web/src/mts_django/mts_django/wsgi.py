#!/var/www/money_transfer_system/.env/bin/python3
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mts_django.settings')
application = get_wsgi_application()
