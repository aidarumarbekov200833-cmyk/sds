from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('monitors.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Monitoring Service Admin"
admin.site.site_title = "Monitoring Service"
admin.site.index_title = "Welcome to Monitoring Service Administration"
