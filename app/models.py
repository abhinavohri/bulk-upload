from datetime import datetime, timezone
from app import db
from sqlalchemy.dialects.postgresql import CITEXT


def utc_now():
    return datetime.now(timezone.utc)


class Product(db.Model):
    """Product model for storing product information"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(CITEXT(), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now(), onupdate=utc_now(), nullable=False)

    def __repr__(self):
        return f'<Product {self.sku}: {self.name}>'

    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Webhook(db.Model):
    """Webhook model for managing webhook configurations"""
    __tablename__ = 'webhooks'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now(), onupdate=utc_now(), nullable=False)

    def __repr__(self):
        return f'<Webhook {self.event_type}: {self.url}>'

    def to_dict(self):
        """Convert webhook to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'event_type': self.event_type,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class UploadJob(db.Model):
    """Upload job model for tracking CSV upload progress"""
    __tablename__ = 'upload_jobs'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    total_rows = db.Column(db.Integer, default=0)
    processed_rows = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now(), onupdate=utc_now(), nullable=False)

    def __repr__(self):
        return f'<UploadJob {self.task_id}: {self.status}>'

    def to_dict(self):
        """Convert upload job to dictionary"""
        progress = (self.processed_rows / self.total_rows * 100) if self.total_rows > 0 else 0
        return {
            'id': self.id,
            'task_id': self.task_id,
            'filename': self.filename,
            'total_rows': self.total_rows,
            'processed_rows': self.processed_rows,
            'progress': round(progress, 2),
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
