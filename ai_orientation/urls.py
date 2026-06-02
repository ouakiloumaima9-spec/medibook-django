from django.urls import path
from . import views
app_name = 'ai_orientation'
urlpatterns = [path('orient/', views.orient, name='orient')]
