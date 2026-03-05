import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring_service.settings')
django.setup()

from monitors.models import Monitor, CheckLog, Alert, Incident
from django.utils import timezone
from datetime import timedelta
import random

monitors_data = [
    {'name': 'Google', 'url': 'https://www.google.com', 'status': 'online', 'last_response_time': 145.2},
    {'name': 'GitHub', 'url': 'https://github.com', 'status': 'online', 'last_response_time': 320.5},
    {'name': 'My API', 'url': 'https://httpbin.org/get', 'status': 'slow', 'last_response_time': 2450.0},
    {'name': 'Example Site', 'url': 'https://example.com', 'status': 'offline', 'last_response_time': None},
]

for data in monitors_data:
    m, created = Monitor.objects.get_or_create(url=data['url'], defaults={
        'name': data['name'],
        'status': data['status'],
        'last_response_time': data['last_response_time'],
        'last_checked': timezone.now(),
        'is_active': True,
    })
    if created:
        for i in range(48):
            is_up = data['status'] != 'offline'
            rt = random.uniform(100, 500) if is_up else None
            CheckLog.objects.create(
                monitor=m,
                is_up=is_up,
                status_code=200 if is_up else None,
                response_time=rt,
                checked_at=timezone.now() - timedelta(hours=i),
            )
        if data['status'] == 'offline':
            Incident.objects.create(
                monitor=m,
                started_at=timezone.now() - timedelta(hours=2),
                cause='Connection refused',
                is_resolved=False,
            )
        Alert.objects.create(
            monitor=m,
            alert_type='email',
            target='admin@example.com',
            is_enabled=True,
        )
        print(f'Created: {data["name"]}')
    else:
        print(f'Already exists: {data["name"]}')

print('Done! Demo data ready.')
