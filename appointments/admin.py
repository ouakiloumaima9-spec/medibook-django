from django.contrib import admin
from .models import Appointment, Consultation, Review


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'specialty', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'specialty', 'date')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__first_name', 'doctor__user__last_name', 'reason')
    date_hierarchy = 'date'


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'created_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name', 'summary')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('comment',)
