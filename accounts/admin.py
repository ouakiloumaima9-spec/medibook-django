from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PatientProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations MediBook', {'fields': ('role', 'phone', 'date_of_birth', 'address', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rôle MediBook', {'fields': ('role',)}),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'blood_group', 'emergency_contact')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'emergency_contact')
