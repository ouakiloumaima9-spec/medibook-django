from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('specialties/', views.specialty_list, name='specialties'),
    path('me/profile/', views.my_doctor_profile, name='my_profile'),
    path('<int:pk>/', views.doctor_detail, name='detail'),
]
