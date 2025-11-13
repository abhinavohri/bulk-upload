from app.celery_app import celery
from app import create_app, db
from app.models import Product, UploadJob
from app.utils import trigger_webhook
import pandas as pd
import os
from datetime import datetime, timezone


def filter_valid_rows(df):
    """Filter out empty rows and rows with empty SKUs"""
    df = df.dropna(how='all')
    df = df[df['sku'].notna()]
    df = df[df['sku'].astype(str).str.strip() != '']
    return df


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
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")

            job.status = 'processing'
            db.session.commit()

            df_sample = filter_valid_rows(pd.read_csv(file_path))
            total_rows = len(df_sample)

            if total_rows == 0:
                raise ValueError("CSV file is empty or has no valid data rows")

            job.total_rows = total_rows
            db.session.commit()

            chunk_size = 1000
            processed = 0

            try:
                for chunk_df in pd.read_csv(file_path, chunksize=chunk_size):
                    chunk_df = filter_valid_rows(chunk_df)

                    for _, row in chunk_df.iterrows():
                        processed += 1
                        sku = str(row.get('sku', '')).strip()

                        product = Product.query.filter(Product.sku.ilike(sku)).first()

                        if product:
                            product.name = str(row.get('name', product.name)).strip()
                            product.description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else product.description
                        else:
                            product = Product(
                                sku=sku,
                                name=str(row.get('name', '')).strip(),
                                description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                                active=True
                            )
                            db.session.add(product)

                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': processed,
                            'total': total_rows,
                            'percent': int((processed / total_rows) * 100)
                        }
                    )

                db.session.commit()

            except Exception as e:
                db.session.rollback()
                raise Exception(f"Upload failed at row {processed}: {str(e)}")

            job.status = 'completed'
            job.processed_rows = total_rows
            db.session.commit()

            trigger_webhook('product.bulk_upload', {
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


