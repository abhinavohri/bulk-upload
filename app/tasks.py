from app.celery_app import celery
from app import create_app, db
from app.models import Product, UploadJob, Webhook
import pandas as pd
import os
import requests
from datetime import datetime


@celery.task(bind=True)
def process_csv_upload(self, file_path, job_id):
    """
    Process CSV file upload in background

    Args:
        file_path: Path to the uploaded CSV file
        job_id: ID of the UploadJob record
    """
    app = create_app(os.environ.get('FLASK_ENV'))

    with app.app_context():
        job = UploadJob.query.get(job_id)
        if not job:
            return {'error': 'Job not found'}

        try:
            job.status = 'processing'
            db.session.commit()

            with open(file_path, 'r') as f:
                total_rows = sum(1 for line in f) - 1

            job.total_rows = total_rows
            db.session.commit()

            chunk_size = 1000
            processed = 0

            # Streaming csv instead of loading the whole file into memory
            for chunk_df in pd.read_csv(file_path, chunksize=chunk_size):
                for _, row in chunk_df.iterrows():
                    sku = str(row.get('sku', '')).strip()

                    if not sku:
                        continue

                    product = Product.query.filter(Product.sku.ilike(sku)).first()

                    if product:
                        product.name = str(row.get('name', product.name)).strip()
                        product.description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else product.description
                        product.price = row.get('price') if pd.notna(row.get('price')) else product.price
                    else:
                        product = Product(
                            sku=sku,
                            name=str(row.get('name', '')).strip(),
                            description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                            price=row.get('price') if pd.notna(row.get('price')) else None,
                            active=True
                        )
                        db.session.add(product)

                    processed += 1

                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed,
                        'total': total_rows,
                        'percent': int((processed / total_rows) * 100)
                    }
                )

            job.status = 'completed'
            job.processed_rows = total_rows
            db.session.commit()

            trigger_webhooks('product.bulk_upload', {
                'job_id': job_id,
                'total_rows': total_rows,
                'filename': job.filename
            })

            if os.path.exists(file_path):
                os.remove(file_path)

            return {
                'status': 'completed',
                'processed': total_rows,
                'job_id': job_id
            }

        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()

            if os.path.exists(file_path):
                os.remove(file_path)

            raise


def trigger_webhooks(event_type, data):
    """
    Trigger all enabled webhooks for a given event type

    Args:
        event_type: Type of event (e.g., 'product.created', 'product.bulk_upload')
        data: Event data to send
    """
    webhooks = Webhook.query.filter_by(event_type=event_type, enabled=True).all()

    for webhook in webhooks:
        try:
            payload = {
                'event': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data
            }

            requests.post(
                webhook.url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            print(f"Webhook error for {webhook.url}: {str(e)}")
