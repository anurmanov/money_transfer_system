import re
from datetime import date
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings
from project.celery import app
from money.models import Currency, Course

@app.task(bind = True, expires = 120, acks_late = True)
def update_courses(self, fetch_courses_url = settings.FETCH_COURSES_URL):
    """Celery task function is intended for periodic fetching currency courses"""
    response = requests.get(fetch_courses_url)
    response = response.json()
    rates = response['rates']
    base_currency_name = response['base']
    date_str = response['date']
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if m:
        dt = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    else:
        raise Exception('Date format "yyyy-mm-dd" was changed in json!')

    base_currency, created = Currency.objects.get_or_create(name=base_currency_name)
    for currency_name in rates:
        currency = Currency.objects.get_or_create(name=currency_name)
        Course.objects.get_or_create(Q(base_currency=base_currency) & Q(currency=currency) & Q(date=dt), defaults={'course': rates[currency_name]})

#Config dictionary for periodic Celery task
app.conf.beat_schedule = {
    'frequently-data-fetching': {
        'task': 'money.tasks.update_courses',
        'schedule': settings.FETCH_COURSES_FREQUENCY_IN_SECONDS
    },
}