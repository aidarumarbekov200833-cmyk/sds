from django.db import models
from django.utils import timezone
from datetime import timedelta

class Monitor(models.Model):

    class Status(models.TextChoices):
        ONLINE = 'online', 'Online'
        OFFLINE = 'offline', 'Offline'
        SLOW = 'slow', 'Slow'
        PENDING = 'pending', 'Pending'

    class CheckType(models.TextChoices):
        HTTP = 'http', 'HTTP Status'
        KEYWORD = 'keyword', 'Keyword Search'

    name = models.CharField(max_length=255, help_text="Friendly name for this monitor")
    url = models.URLField(max_length=500, help_text="URL to monitor")
    check_type = models.CharField(
        max_length=20,
        choices=CheckType.choices,
        default=CheckType.HTTP,
    )
    keyword = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Keyword to search for on the page (only for keyword check type)",
    )
    check_interval = models.PositiveIntegerField(
        default=60,
        help_text="Check interval in seconds",
    )
    timeout = models.PositiveIntegerField(
        default=30,
        help_text="Request timeout in seconds",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    last_response_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Last response time in milliseconds",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.url})"

    @property
    def uptime_24h(self):

        since = timezone.now() - timedelta(hours=24)
        logs = self.check_logs.filter(checked_at__gte=since)
        total = logs.count()
        if total == 0:
            return 100.0
        successful = logs.filter(is_up=True).count()
        return round((successful / total) * 100, 2)

    @property
    def uptime_7d(self):

        since = timezone.now() - timedelta(days=7)
        logs = self.check_logs.filter(checked_at__gte=since)
        total = logs.count()
        if total == 0:
            return 100.0
        successful = logs.filter(is_up=True).count()
        return round((successful / total) * 100, 2)

    @property
    def uptime_30d(self):

        since = timezone.now() - timedelta(days=30)
        logs = self.check_logs.filter(checked_at__gte=since)
        total = logs.count()
        if total == 0:
            return 100.0
        successful = logs.filter(is_up=True).count()
        return round((successful / total) * 100, 2)

    @property
    def avg_response_time_24h(self):

        since = timezone.now() - timedelta(hours=24)
        logs = self.check_logs.filter(
            checked_at__gte=since,
            response_time__isnull=False,
        )
        avg = logs.aggregate(models.Avg('response_time'))['response_time__avg']
        return round(avg, 2) if avg else None

class CheckLog(models.Model):

    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
        related_name='check_logs',
    )
    is_up = models.BooleanField(default=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Response time in milliseconds",
    )
    error_message = models.TextField(blank=True, default='')
    keyword_found = models.BooleanField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['monitor', '-checked_at']),
            models.Index(fields=['-checked_at']),
        ]

    def __str__(self):
        status = "UP" if self.is_up else "DOWN"
        return f"{self.monitor.name} - {status} at {self.checked_at}"

class Alert(models.Model):

    class AlertType(models.TextChoices):
        EMAIL = 'email', 'Email'
        TELEGRAM = 'telegram', 'Telegram'

    class AlertStatus(models.TextChoices):
        TRIGGERED = 'triggered', 'Triggered'
        RESOLVED = 'resolved', 'Resolved'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'

    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
        related_name='alerts',
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
        default=AlertType.EMAIL,
    )
    target = models.CharField(
        max_length=255,
        help_text="Email address or Telegram chat ID",
    )
    is_enabled = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.RESOLVED,
    )
    last_triggered = models.DateTimeField(null=True, blank=True)
    last_resolved = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert for {self.monitor.name} via {self.alert_type}"

class Incident(models.Model):

    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
        related_name='incidents',
    )
    started_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    cause = models.TextField(blank=True, default='')
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        status = "Resolved" if self.is_resolved else "Ongoing"
        return f"{self.monitor.name} incident ({status}) - {self.started_at}"

    @property
    def duration(self):
        end = self.resolved_at or timezone.now()
        return end - self.started_at
