# Product Bulk Upload System

A Flask-based web application for managing products with CSV bulk upload functionality, real-time progress tracking, and webhook notifications.

## Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Redis 6+

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd bulk-upload
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create a new database:

```bash
psql -U postgres
CREATE DATABASE bulk_upload;
\q
```

### 5. Set up Redis

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping  # Should return: PONG
```

### 6. Configure environment variables

Create a `.env` file in the project root by taking a reference from the `.env.example` file.

## Running the Application

```bash
chmod +x run.sh
./run.sh
```

The script will:
- Initialize database tables (products, upload_jobs, webhooks)
- Start Gunicorn web server on the port specified in `.env`
- Start Celery worker for background tasks
- Automatically configure Celery based on OS (solo pool for macOS, prefork for Linux)

## Usage

### Access the Application

Open your browser and navigate to:
- **Home**: http://localhost:5005
- **Upload CSV**: http://localhost:5005/upload
- **Manage Products**: http://localhost:5005/products
- **Manage Webhooks**: http://localhost:5005/webhooks


### Testing Webhooks Locally

Use the included webhook test server:

```bash
python webhook_test_server.py
```

This starts a test server on http://localhost:5003 that displays received webhooks in real-time.

## API Endpoints

### Products
- `GET /api/products` - List products (with pagination & search)
- `GET /api/products/<id>` - Get single product
- `POST /api/products` - Create product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product
- `DELETE /api/products/bulk-delete` - Delete all products

### Upload
- `POST /api/upload` - Upload CSV file
- `GET /api/upload/status/<task_id>` - Get upload progress

### Webhooks
- `GET /api/webhooks` - List webhooks
- `GET /api/webhooks/<id>` - Get single webhook
- `POST /api/webhooks` - Create webhook
- `PUT /api/webhooks/<id>` - Update webhook
- `DELETE /api/webhooks/<id>` - Delete webhook
- `POST /api/webhooks/<id>/test` - Test webhook


## Troubleshooting

### Celery fork errors on macOS
If you see `objc[PID]: +[NSMutableString initialize] may have been in progress`:
- The run.sh script automatically uses `--pool=solo` on macOS
- This is expected behavior and handled automatically


## License

MIT
