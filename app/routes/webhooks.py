from flask import request, jsonify
from app.routes import webhook_bp
from app import db
from app.models import Webhook
import requests


@webhook_bp.route('', methods=['GET'])
def get_webhooks():
    """Get all webhooks"""
    webhooks = Webhook.query.all()
    return jsonify([webhook.to_dict() for webhook in webhooks])


@webhook_bp.route('/<int:webhook_id>', methods=['GET'])
def get_webhook(webhook_id):
    """Get a single webhook by ID"""
    webhook = Webhook.query.get_or_404(webhook_id)
    return jsonify(webhook.to_dict())


@webhook_bp.route('', methods=['POST'])
def create_webhook():
    """Create a new webhook"""
    data = request.get_json()

    # Validate required fields
    if not data.get('url') or not data.get('event_type'):
        return jsonify({'error': 'URL and event_type are required'}), 400

    webhook = Webhook(
        url=data['url'].strip(),
        event_type=data['event_type'].strip(),
        enabled=data.get('enabled', True)
    )

    db.session.add(webhook)
    db.session.commit()

    return jsonify(webhook.to_dict()), 201


@webhook_bp.route('/<int:webhook_id>', methods=['PUT'])
def update_webhook(webhook_id):
    """Update an existing webhook"""
    webhook = Webhook.query.get_or_404(webhook_id)
    data = request.get_json()

    if 'url' in data:
        webhook.url = data['url'].strip()
    if 'event_type' in data:
        webhook.event_type = data['event_type'].strip()
    if 'enabled' in data:
        webhook.enabled = data['enabled']

    db.session.commit()

    return jsonify(webhook.to_dict())


@webhook_bp.route('/<int:webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    """Delete a webhook"""
    webhook = Webhook.query.get_or_404(webhook_id)
    db.session.delete(webhook)
    db.session.commit()

    return jsonify({'message': 'Webhook deleted successfully'}), 200


@webhook_bp.route('/<int:webhook_id>/test', methods=['POST'])
def test_webhook(webhook_id):
    """Test a webhook by sending a test payload"""
    webhook = Webhook.query.get_or_404(webhook_id)

    test_payload = {
        'event': webhook.event_type,
        'test': True,
        'data': {
            'message': 'This is a test webhook call'
        }
    }

    try:
        response = requests.post(
            webhook.url,
            json=test_payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )

        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'message': 'Webhook test successful'
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Webhook test failed'
        }), 500
