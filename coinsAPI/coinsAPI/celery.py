from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coinsAPI.settings')

app = Celery('coinsAPI')



app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'add-every-60-seconds': {
        'task': 'coins.tasks.update_payments',
        'schedule': timedelta(seconds=6)
    },
}


app.autodiscover_tasks()



@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))