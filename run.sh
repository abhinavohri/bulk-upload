#!/usr/bin/env bash

set -e

python init_db.py

gunicorn run:app --bind 0.0.0.0:$PORT --timeout 300 --log-level info --workers 1 &

if [[ "$OSTYPE" == "darwin"* ]]; then
    celery -A celery_worker.celery worker --loglevel=info --pool=solo
else
    celery -A celery_worker.celery worker --loglevel=info --concurrency=2
fi