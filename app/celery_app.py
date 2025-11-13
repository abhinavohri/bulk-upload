from celery import Celery
from config import config
import os


def make_celery(app_name=__name__):
    """Create Celery instance"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    app_config = config[config_name]

    celery = Celery(
        app_name,
        broker=app_config.CELERY_BROKER_URL,
        backend=app_config.CELERY_RESULT_BACKEND
    )

    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600,  # 1 hour
        task_soft_time_limit=3300,  # 55 minutes
        broker_connection_retry_on_startup=True,
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )

    return celery


celery = make_celery()
