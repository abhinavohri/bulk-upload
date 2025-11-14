#!/usr/bin/env python3
"""
Simple webhook test server to receive and display webhook events
Usage: python webhook_test_server.py
Then configure webhook URL: http://localhost:5003/webhook
"""
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json

app = Flask(__name__)

# Store received webhooks in memory
webhooks_received = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Test Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .webhook {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .webhook-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .event-type {
            font-weight: bold;
            color: #4CAF50;
            font-size: 1.1em;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }
        .no-webhooks {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .clear-btn {
            background: #f44336;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .clear-btn:hover {
            background: #d32f2f;
        }
        .count {
            color: #666;
            font-size: 0.9em;
        }
    </style>
    <script>
        // Auto-refresh every 2 seconds
        setTimeout(() => location.reload(), 2000);
    </script>
</head>
<body>
    <h1>🪝 Webhook Test Server</h1>

    <div class="info">
        <strong>Webhook URL:</strong> <code>http://localhost:5003/webhook</code><br>
        <strong>Status:</strong> <span style="color: green;">● Running</span><br>
        <strong>Auto-refreshing every 2 seconds...</strong>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div class="count">Total webhooks received: {{ webhooks|length }}</div>
        <button class="clear-btn" onclick="clearWebhooks()">Clear All</button>
    </div>

    {% if webhooks %}
        {% for webhook in webhooks %}
        <div class="webhook">
            <div class="webhook-header">
                <div class="event-type">{{ webhook.event }}</div>
                <div class="timestamp">{{ webhook.received_at }}</div>
            </div>
            <pre>{{ webhook.payload }}</pre>
        </div>
        {% endfor %}
    {% else %}
        <div class="no-webhooks">
            <h2>No webhooks received yet</h2>
            <p>Waiting for incoming webhook events...</p>
        </div>
    {% endif %}

    <script>
        function clearWebhooks() {
            fetch('/clear', { method: 'POST' })
                .then(() => location.reload());
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Display received webhooks"""
    return render_template_string(HTML_TEMPLATE, webhooks=list(reversed(webhooks_received)))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive webhook POST requests"""
    data = request.get_json()

    webhook_data = {
        'event': data.get('event', 'unknown'),
        'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': json.dumps(data, indent=2)
    }

    webhooks_received.append(webhook_data)

    # Keep only last 50 webhooks
    if len(webhooks_received) > 50:
        webhooks_received.pop(0)

    print(f"\n[{webhook_data['received_at']}] Webhook received: {webhook_data['event']}")
    print(json.dumps(data, indent=2))

    return jsonify({'status': 'received'}), 200

@app.route('/clear', methods=['POST'])
def clear():
    """Clear all received webhooks"""
    webhooks_received.clear()
    return jsonify({'status': 'cleared'}), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🪝 Webhook Test Server Starting...")
    print("="*60)
    print("\n1. Open in browser: http://localhost:5003")
    print("2. Configure webhook URL: http://localhost:5003/webhook")
    print("\nPress Ctrl+C to stop\n")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5003, debug=False)
