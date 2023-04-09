import os
from celery import Celery
from .orchestrator import all_tasks
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ngo_scraper.settings')
app = Celery('ngo_scraper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = all_tasks