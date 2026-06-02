from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    path('manage/', views.manage_availabilities, name='manage'),
    path('availability/<int:pk>/delete/', views.delete_availability, name='delete'),
    path('timeoff/add/', views.add_timeoff, name='add_timeoff'),
    path('timeoff/<int:pk>/delete/', views.delete_timeoff, name='delete_timeoff'),
]
