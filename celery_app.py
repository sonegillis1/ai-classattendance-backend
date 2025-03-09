import os
from celery_app import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classattendance.settings.development')

celery_app = Celery('classattendance')

# Load configuration from Django settings
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed Django apps
celery_app.autodiscover_tasks()

