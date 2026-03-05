from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('monitor/add/', views.monitor_create, name='monitor_create'),
    path('monitor/<int:pk>/', views.monitor_detail, name='monitor_detail'),
    path('monitor/<int:pk>/edit/', views.monitor_edit, name='monitor_edit'),
    path('monitor/<int:pk>/delete/', views.monitor_delete, name='monitor_delete'),
    path('monitor/<int:monitor_pk>/alert/add/', views.alert_create, name='alert_create'),
    path('alert/<int:pk>/delete/', views.alert_delete, name='alert_delete'),
    path('status/', views.status_page, name='status_page'),

    path('api/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/monitors/', views.api_monitors_list, name='api_monitors_list'),
    path('api/monitors/<int:pk>/', views.api_monitor_detail, name='api_monitor_detail'),
    path('api/monitors/<int:pk>/logs/', views.api_monitor_logs, name='api_monitor_logs'),
    path('api/monitors/<int:pk>/chart/response-time/', views.api_response_time_chart, name='api_response_time_chart'),
    path('api/monitors/<int:pk>/chart/uptime/', views.api_uptime_chart, name='api_uptime_chart'),
    path('api/monitors/<int:pk>/check-now/', views.api_check_now, name='api_check_now'),
    path('api/monitors/<int:pk>/toggle/', views.api_toggle_monitor, name='api_toggle_monitor'),
    path('api/incidents/', views.api_incidents, name='api_incidents'),
    path('api/status/', views.api_status_page, name='api_status_page'),
]
