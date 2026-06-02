from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
 path('admin/', admin.site.urls),
 path('', include('dashboard.urls', namespace='dashboard')),
 path('accounts/', include('accounts.urls', namespace='accounts')),
 path('doctors/', include('doctors.urls', namespace='doctors')),
 path('appointments/', include('appointments.urls', namespace='appointments')),
 path('schedules/', include('schedules.urls', namespace='schedules')),
 path('ai/', include('ai_orientation.urls', namespace='ai_orientation')),
 path('notifications/', include('notifications.urls', namespace='notifications')),
]
if settings.DEBUG:
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)