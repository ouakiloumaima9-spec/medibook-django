from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # ── Vues publiques ───────────────────────────────────────────────
    path('', views.doctor_list, name='list'),
    path('specialties/', views.specialty_list, name='specialties'),
    path('<int:pk>/', views.doctor_detail, name='detail'),

    # ── Vue médecin ──────────────────────────────────────────────────
    path('me/profile/', views.my_doctor_profile, name='my_profile'),

    # ── Vues admin ───────────────────────────────────────────────────
    path('admin/list/', views.admin_doctor_list, name='admin_list'),
    path('admin/add/', views.admin_add_doctor, name='admin_add'),
    path('admin/<int:pk>/edit/', views.admin_edit_doctor, name='admin_edit'),
    path('admin/<int:pk>/toggle/', views.admin_toggle_doctor, name='admin_toggle'),
]