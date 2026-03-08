import httpx

N8N_WEBHOOK_URL = "http://localhost:5678/webhook/incident-alert"


def send_notification(payload: dict):

    try:
        response = httpx.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        print("Notification sent to n8n:", response.status_code)

    except Exception as e:
        print("Notification error:", e)