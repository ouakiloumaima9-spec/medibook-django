from django.contrib import admin
from .models import Doctor, Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'keywords', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'city', 'years_of_experience', 'consultation_fee', 'is_active')
    list_filter = ('city', 'is_active', 'specialties')
    search_fields = ('user__first_name', 'user__last_name', 'license_number', 'city')
    filter_horizontal = ('specialties',)
