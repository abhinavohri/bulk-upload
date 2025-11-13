"""
Common utility functions
"""
from app.models import Webhook
import requests
from datetime import datetime, timezone


def trigger_webhook(event_type, data):
    """
    Trigger webhooks for a given event type

    Args:
        event_type: Type of event (e.g., 'product.created', 'product.bulk_upload')
        data: Event data to send in webhook payload
    """
    try:
        webhooks = Webhook.query.filter_by(event_type=event_type, enabled=True).all()
        print(f"[Webhook] Found {len(webhooks)} webhooks for {event_type}")

        for webhook in webhooks:
            try:
                payload = {
                    'event': event_type,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'data': data
                }
                print(f"[Webhook] Sending {event_type} to {webhook.url}")
                response = requests.post(
                    webhook.url,
                    json=payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"[Webhook] Response: {response.status_code}")
            except Exception as e:
                print(f"[Webhook Error] {webhook.url}: {str(e)}")
    except Exception as e:
        print(f"[Webhook Error] Failed to query webhooks: {str(e)}")
