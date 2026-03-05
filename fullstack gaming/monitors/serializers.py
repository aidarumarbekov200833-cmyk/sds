from rest_framework import serializers
from .models import Monitor, CheckLog, Alert, Incident

class CheckLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckLog
        fields = ['id', 'is_up', 'status_code', 'response_time', 'error_message', 'keyword_found', 'checked_at']

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'monitor', 'alert_type', 'target', 'is_enabled', 'status', 'last_triggered', 'last_resolved', 'message', 'created_at']
        read_only_fields = ['status', 'last_triggered', 'last_resolved', 'message']

class IncidentSerializer(serializers.ModelSerializer):
    monitor_name = serializers.CharField(source='monitor.name', read_only=True)
    duration_str = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = ['id', 'monitor', 'monitor_name', 'started_at', 'resolved_at', 'cause', 'is_resolved', 'duration_str']

    def get_duration_str(self, obj):
        d = obj.duration
        total_seconds = int(d.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

class MonitorSerializer(serializers.ModelSerializer):
    uptime_24h = serializers.FloatField(read_only=True)
    uptime_7d = serializers.FloatField(read_only=True)
    uptime_30d = serializers.FloatField(read_only=True)
    avg_response_time_24h = serializers.FloatField(read_only=True)

    class Meta:
        model = Monitor
        fields = [
            'id', 'name', 'url', 'check_type', 'keyword', 'check_interval',
            'timeout', 'status', 'is_active', 'last_checked', 'last_response_time',
            'uptime_24h', 'uptime_7d', 'uptime_30d', 'avg_response_time_24h',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'last_checked', 'last_response_time']

class MonitorDetailSerializer(MonitorSerializer):
    recent_logs = serializers.SerializerMethodField()
    alerts = AlertSerializer(many=True, read_only=True)

    class Meta(MonitorSerializer.Meta):
        fields = MonitorSerializer.Meta.fields + ['recent_logs', 'alerts']

    def get_recent_logs(self, obj):
        logs = obj.check_logs.all()[:50]
        return CheckLogSerializer(logs, many=True).data

class DashboardStatsSerializer(serializers.Serializer):
    total_monitors = serializers.IntegerField()
    online_count = serializers.IntegerField()
    offline_count = serializers.IntegerField()
    slow_count = serializers.IntegerField()
    overall_uptime = serializers.FloatField()
    active_incidents = serializers.IntegerField()
