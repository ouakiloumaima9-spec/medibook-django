from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('mine/', views.my_appointments, name='my_appointments'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book'),
    path('<int:pk>/', views.appointment_detail, name='detail'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('<int:pk>/reschedule/', views.reschedule_appointment, name='reschedule'),
    path('<int:pk>/confirm/', views.confirm_appointment, name='confirm'),
    path('<int:pk>/complete/', views.complete_appointment, name='complete'),
    path('<int:pk>/no-show/', views.mark_no_show, name='no_show'),
    path('<int:pk>/consultation/', views.add_consultation_summary, name='consultation'),
    path('<int:pk>/review/', views.add_review, name='review'),
    path('api/slots/<int:doctor_id>/', views.get_slots_ajax, name='slots_ajax'),
]
