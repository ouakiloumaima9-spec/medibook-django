from django.contrib import admin
from .models import Availability, TimeOff


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'weekday', 'start_time', 'end_time', 'slot_duration_minutes', 'is_active')
    list_filter = ('weekday', 'is_active')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'start_date', 'end_date', 'reason')
    list_filter = ('start_date', 'end_date')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'reason')
