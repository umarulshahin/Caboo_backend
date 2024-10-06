# Caboo_backend/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Caboo_backend.settings')

app = Celery('Caboo_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: ['Authentication_app'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
