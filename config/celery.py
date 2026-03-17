"""
Configuration Celery pour la synchronisation périodique.

Lancer le worker :
    celery -A config worker -l info

Lancer le scheduler (Beat) :
    celery -A config beat -l info

Ou les deux en un (dev) :
    celery -A config worker -B -l info
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('sav_pharmacie')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
