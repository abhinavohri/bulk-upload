#!/usr/bin/env bash

set -e

gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --log-level info &

celery -A celery_worker.celery worker --loglevel=info --concurrency=2