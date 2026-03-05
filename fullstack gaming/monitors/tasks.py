import requests
import time
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def check_all_monitors():

    from .models import Monitor
    monitors = Monitor.objects.filter(is_active=True)
    for monitor in monitors:
        check_monitor.delay(monitor.id)
    return f"Dispatched checks for {monitors.count()} monitors"

@shared_task
def check_monitor(monitor_id):

    from .models import Monitor, CheckLog, Alert, Incident

    try:
        monitor = Monitor.objects.get(id=monitor_id)
    except Monitor.DoesNotExist:
        logger.error(f"Monitor {monitor_id} not found")
        return

    is_up = False
    status_code = None
    response_time = None
    error_message = ''
    keyword_found = None

    try:
        start_time = time.time()
        response = requests.get(
            monitor.url,
            timeout=monitor.timeout,
            headers={
                'User-Agent': 'MonitoringService/1.0',
                'Accept': 'text/html,application/json',
            },
            allow_redirects=True,
        )
        elapsed = (time.time() - start_time) * 1000
        response_time = round(elapsed, 2)
        status_code = response.status_code

        if 200 <= status_code < 400:
            is_up = True

        if monitor.check_type == Monitor.CheckType.KEYWORD and monitor.keyword:
            keyword_found = monitor.keyword.lower() in response.text.lower()
            if not keyword_found:
                is_up = False
                error_message = f"Keyword '{monitor.keyword}' not found on page"

        slow_threshold = getattr(settings, 'SLOW_RESPONSE_THRESHOLD', 2000)
        if is_up and response_time > slow_threshold:
            new_status = Monitor.Status.SLOW
        elif is_up:
            new_status = Monitor.Status.ONLINE
        else:
            new_status = Monitor.Status.OFFLINE
            if not error_message:
                error_message = f"HTTP {status_code}"

    except requests.exceptions.Timeout:
        error_message = "Request timed out"
        new_status = Monitor.Status.OFFLINE
    except requests.exceptions.ConnectionError:
        error_message = "Connection failed"
        new_status = Monitor.Status.OFFLINE
    except requests.exceptions.SSLError:
        error_message = "SSL certificate error"
        new_status = Monitor.Status.OFFLINE
    except requests.exceptions.RequestException as e:
        error_message = str(e)[:500]
        new_status = Monitor.Status.OFFLINE

    CheckLog.objects.create(
        monitor=monitor,
        is_up=is_up,
        status_code=status_code,
        response_time=response_time,
        error_message=error_message,
        keyword_found=keyword_found,
    )

    previous_status = monitor.status

    monitor.status = new_status
    monitor.last_checked = timezone.now()
    monitor.last_response_time = response_time
    monitor.save(update_fields=['status', 'last_checked', 'last_response_time', 'updated_at'])

    if new_status == Monitor.Status.OFFLINE and previous_status != Monitor.Status.OFFLINE:

        Incident.objects.create(
            monitor=monitor,
            started_at=timezone.now(),
            cause=error_message,
        )

        _trigger_alerts(monitor, error_message)

    elif new_status != Monitor.Status.OFFLINE and previous_status == Monitor.Status.OFFLINE:

        open_incidents = Incident.objects.filter(
            monitor=monitor,
            is_resolved=False,
        )
        open_incidents.update(
            is_resolved=True,
            resolved_at=timezone.now(),
        )

        _resolve_alerts(monitor)

    return f"Monitor {monitor.name}: {new_status} ({response_time}ms)"

def _trigger_alerts(monitor, error_message):

    from .models import Alert

    alerts = Alert.objects.filter(monitor=monitor, is_enabled=True)
    for alert in alerts:
        alert.status = Alert.AlertStatus.TRIGGERED
        alert.last_triggered = timezone.now()
        alert.message = f"🔴 {monitor.name} is DOWN!\nURL: {monitor.url}\nError: {error_message}\nTime: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        alert.save()

        if alert.alert_type == Alert.AlertType.EMAIL:
            logger.info(f"[EMAIL ALERT] To: {alert.target} | {alert.message}")
        elif alert.alert_type == Alert.AlertType.TELEGRAM:
            logger.info(f"[TELEGRAM ALERT] Chat: {alert.target} | {alert.message}")

def _resolve_alerts(monitor):

    from .models import Alert

    alerts = Alert.objects.filter(
        monitor=monitor,
        status=Alert.AlertStatus.TRIGGERED,
    )
    for alert in alerts:
        alert.status = Alert.AlertStatus.RESOLVED
        alert.last_resolved = timezone.now()
        alert.message = f"✅ {monitor.name} is back ONLINE!\nURL: {monitor.url}\nTime: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        alert.save()

        if alert.alert_type == Alert.AlertType.EMAIL:
            logger.info(f"[EMAIL RESOLVED] To: {alert.target} | {alert.message}")
        elif alert.alert_type == Alert.AlertType.TELEGRAM:
            logger.info(f"[TELEGRAM RESOLVED] Chat: {alert.target} | {alert.message}")
