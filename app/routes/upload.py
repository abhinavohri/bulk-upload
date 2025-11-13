from flask import request, jsonify
from werkzeug.utils import secure_filename
from app.routes import main_bp
from app import db
from app.models import UploadJob
from app.tasks import process_csv_upload
import os


ALLOWED_EXTENSIONS = ['csv']


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    try:
        filename = secure_filename(file.filename)
        upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.abspath(os.path.join(upload_folder, filename))
        file.save(file_path)

        print(f"[DEBUG] File saved to: {file_path}")
        print(f"[DEBUG] File exists: {os.path.exists(file_path)}")

        job = UploadJob(
            task_id='',
            filename=filename,
            status='pending'
        )
        db.session.add(job)
        db.session.commit()

        print(f"[DEBUG] Job created with ID: {job.id}")

        task = process_csv_upload.apply_async(args=[file_path, job.id])

        print(f"[DEBUG] Task dispatched with ID: {task.id}")

        job.task_id = task.id
        db.session.commit()

        return jsonify({
            'message': 'File upload started',
            'task_id': task.id,
            'job_id': job.id
        }), 202

    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/upload/status/<task_id>', methods=['GET'])
def upload_status(task_id):
    """Get upload task status"""
    from app.celery_app import celery

    task = celery.AsyncResult(task_id)

    job = UploadJob.query.filter_by(task_id=task_id).first()

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    response = {
        'task_id': task_id,
        'status': task.state,
        'job': job.to_dict()
    }

    if task.state == 'PROGRESS':
        response['progress'] = task.info
    elif task.state == 'SUCCESS':
        response['result'] = task.info

    return jsonify(response)
