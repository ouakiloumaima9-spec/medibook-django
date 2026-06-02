from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Médecin'
        ADMIN = 'ADMIN', 'Administrateur'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_patient(self):
        return self.role == self.Role.PATIENT

    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def display_name(self):
        return self.get_full_name() or self.username

    def __str__(self):
        return f'{self.display_name()} ({self.get_role_display()})'


class PatientProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Homme'
        FEMALE = 'F', 'Femme'
        OTHER = 'O', 'Autre'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'Profil patient de {self.user.display_name()}'
