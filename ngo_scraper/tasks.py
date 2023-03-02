from contextlib import suppress
import requests
from celery import shared_task


@shared_task(name="notify", queue="notify")
def notify(message, webhook_url):
    with suppress(Exception):
        data = {"text": message}
        response = requests.post(webhook_url, json=data)
        if response.status_code != 200:
            print(f"Unable to send message to slack: {response.status_code}")
        return response.status_code    
    return 0