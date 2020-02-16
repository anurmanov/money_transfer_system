import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mts_django.settings')

app = Celery('mts_django')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
app.conf.result_expires = 60