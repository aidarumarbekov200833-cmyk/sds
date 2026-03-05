from django.contrib import admin
from .models import Monitor, CheckLog, Alert, Incident

@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'url', 'status', 'is_active', 'check_type',
        'check_interval', 'last_checked', 'last_response_time',
    ]
    list_filter = ['status', 'is_active', 'check_type']
    search_fields = ['name', 'url']
    readonly_fields = ['last_checked', 'last_response_time', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'url', 'is_active')
        }),
        ('Monitoring Settings', {
            'fields': ('check_type', 'keyword', 'check_interval', 'timeout')
        }),
        ('Status', {
            'fields': ('status', 'last_checked', 'last_response_time')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CheckLog)
class CheckLogAdmin(admin.ModelAdmin):
    list_display = [
        'monitor', 'is_up', 'status_code', 'response_time',
        'keyword_found', 'checked_at',
    ]
    list_filter = ['is_up', 'checked_at']
    search_fields = ['monitor__name', 'monitor__url']
    readonly_fields = ['checked_at']
    date_hierarchy = 'checked_at'
    ordering = ['-checked_at']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'monitor', 'alert_type', 'target', 'is_enabled', 'status',
        'last_triggered', 'last_resolved',
    ]
    list_filter = ['alert_type', 'is_enabled', 'status']
    search_fields = ['monitor__name', 'target']
    readonly_fields = ['last_triggered', 'last_resolved', 'created_at']

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = [
        'monitor', 'started_at', 'resolved_at', 'is_resolved', 'get_duration',
    ]
    list_filter = ['is_resolved', 'started_at']
    search_fields = ['monitor__name', 'cause']
    readonly_fields = ['started_at']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']

    def get_duration(self, obj):
        d = obj.duration
        total_seconds = int(d.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    get_duration.short_description = 'Duration'
