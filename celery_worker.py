"""
Celery worker entry point
"""
from app.celery_app import celery
from app import create_app
import os

# Create Flask app context for Celery
app = create_app(os.environ.get('FLASK_ENV', 'default'))
app.app_context().push()

# Import tasks to register them
from app.tasks import process_csv_upload

if __name__ == '__main__':
    celery.start()
