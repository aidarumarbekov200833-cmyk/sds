import json
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Monitor, CheckLog, Alert, Incident
from .serializers import (
    MonitorSerializer, MonitorDetailSerializer,
    CheckLogSerializer, AlertSerializer,
    IncidentSerializer, DashboardStatsSerializer,
)
from .forms import MonitorForm, AlertForm

def dashboard(request):

    monitors = Monitor.objects.all()
    context = {
        'monitors': monitors,
        'total': monitors.count(),
        'online': monitors.filter(status='online').count(),
        'offline': monitors.filter(status='offline').count(),
        'slow': monitors.filter(status='slow').count(),
    }
    return render(request, 'monitors/dashboard.html', context)

def monitor_detail(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    alerts = Alert.objects.filter(monitor=monitor)
    recent_incidents = Incident.objects.filter(monitor=monitor)[:10]
    context = {
        'monitor': monitor,
        'alerts': alerts,
        'incidents': recent_incidents,
    }
    return render(request, 'monitors/detail.html', context)

def monitor_create(request):

    if request.method == 'POST':
        form = MonitorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = MonitorForm()
    return render(request, 'monitors/monitor_form.html', {'form': form, 'title': 'Add Monitor'})

def monitor_edit(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    if request.method == 'POST':
        form = MonitorForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            return redirect('monitor_detail', pk=pk)
    else:
        form = MonitorForm(instance=monitor)
    return render(request, 'monitors/monitor_form.html', {'form': form, 'title': 'Edit Monitor', 'monitor': monitor})

def monitor_delete(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    if request.method == 'POST':
        monitor.delete()
        return redirect('dashboard')
    return render(request, 'monitors/monitor_confirm_delete.html', {'monitor': monitor})

def alert_create(request, monitor_pk):

    monitor = get_object_or_404(Monitor, pk=monitor_pk)
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.monitor = monitor
            alert.save()
            return redirect('monitor_detail', pk=monitor_pk)
    else:
        form = AlertForm()
    return render(request, 'monitors/alert_form.html', {'form': form, 'monitor': monitor})

def alert_delete(request, pk):

    alert = get_object_or_404(Alert, pk=pk)
    monitor_pk = alert.monitor.pk
    if request.method == 'POST':
        alert.delete()
        return redirect('monitor_detail', pk=monitor_pk)
    return render(request, 'monitors/alert_confirm_delete.html', {'alert': alert})

def status_page(request):

    monitors = Monitor.objects.filter(is_active=True)
    since = timezone.now() - timedelta(days=90)
    incidents = Incident.objects.filter(started_at__gte=since).select_related('monitor')

    monitors_data = []
    for monitor in monitors:
        monitors_data.append({
            'monitor': monitor,
            'uptime_24h': monitor.uptime_24h,
            'uptime_7d': monitor.uptime_7d,
            'uptime_30d': monitor.uptime_30d,
        })

    context = {
        'monitors_data': monitors_data,
        'incidents': incidents,
        'total_monitors': monitors.count(),
        'all_operational': not monitors.filter(status='offline').exists(),
    }
    return render(request, 'monitors/status_page.html', context)

@api_view(['GET'])
def api_dashboard_stats(request):

    monitors = Monitor.objects.all()
    total = monitors.count()
    online = monitors.filter(status='online').count()
    offline = monitors.filter(status='offline').count()
    slow = monitors.filter(status='slow').count()

    if total > 0:
        uptimes = [m.uptime_24h for m in monitors]
        overall_uptime = round(sum(uptimes) / len(uptimes), 2)
    else:
        overall_uptime = 100.0

    active_incidents = Incident.objects.filter(is_resolved=False).count()

    data = {
        'total_monitors': total,
        'online_count': online,
        'offline_count': offline,
        'slow_count': slow,
        'overall_uptime': overall_uptime,
        'active_incidents': active_incidents,
    }
    return Response(data)

@api_view(['GET'])
def api_monitors_list(request):

    monitors = Monitor.objects.all()
    serializer = MonitorSerializer(monitors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_monitor_detail(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    serializer = MonitorDetailSerializer(monitor)
    return Response(serializer.data)

@api_view(['GET'])
def api_monitor_logs(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    hours = int(request.query_params.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)
    logs = CheckLog.objects.filter(
        monitor=monitor,
        checked_at__gte=since,
    ).order_by('checked_at')
    serializer = CheckLogSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_response_time_chart(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    hours = int(request.query_params.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)
    logs = CheckLog.objects.filter(
        monitor=monitor,
        checked_at__gte=since,
        response_time__isnull=False,
    ).order_by('checked_at').values_list('checked_at', 'response_time')

    labels = [log[0].strftime('%H:%M') for log in logs]
    data = [log[1] for log in logs]

    return Response({
        'labels': labels,
        'data': data,
        'monitor_name': monitor.name,
    })

@api_view(['GET'])
def api_uptime_chart(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    days = int(request.query_params.get('days', 30))

    labels = []
    data = []
    for i in range(days - 1, -1, -1):
        day_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        logs = CheckLog.objects.filter(
            monitor=monitor,
            checked_at__gte=day_start,
            checked_at__lt=day_end,
        )
        total = logs.count()
        if total > 0:
            up = logs.filter(is_up=True).count()
            uptime = round((up / total) * 100, 2)
        else:
            uptime = 100.0
        labels.append(day_start.strftime('%b %d'))
        data.append(uptime)

    return Response({
        'labels': labels,
        'data': data,
        'monitor_name': monitor.name,
    })

@api_view(['POST'])
def api_check_now(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    from .tasks import check_monitor
    check_monitor.delay(monitor.id)
    return Response({'status': 'Check queued', 'monitor': monitor.name})

@api_view(['POST'])
def api_toggle_monitor(request, pk):

    monitor = get_object_or_404(Monitor, pk=pk)
    monitor.is_active = not monitor.is_active
    monitor.save(update_fields=['is_active', 'updated_at'])
    return Response({
        'id': monitor.id,
        'is_active': monitor.is_active,
        'name': monitor.name,
    })

@api_view(['GET'])
def api_incidents(request):

    days = int(request.query_params.get('days', 90))
    since = timezone.now() - timedelta(days=days)
    incidents = Incident.objects.filter(started_at__gte=since).select_related('monitor')
    serializer = IncidentSerializer(incidents, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_status_page(request):

    monitors = Monitor.objects.filter(is_active=True)
    data = []
    for monitor in monitors:
        data.append({
            'id': monitor.id,
            'name': monitor.name,
            'url': monitor.url,
            'status': monitor.status,
            'uptime_24h': monitor.uptime_24h,
            'uptime_7d': monitor.uptime_7d,
            'uptime_30d': monitor.uptime_30d,
            'last_checked': monitor.last_checked,
            'last_response_time': monitor.last_response_time,
        })

    all_operational = not monitors.filter(status='offline').exists()
    return Response({
        'monitors': data,
        'all_operational': all_operational,
        'total': monitors.count(),
    })
