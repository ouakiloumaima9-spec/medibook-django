from django.conf import settings
from django.db import models
from django.urls import reverse


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True, help_text="Mots-clés séparés par des espaces ou virgules, utilisés par l'IA")
    icon = models.CharField(max_length=50, default='bi-heart-pulse')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Spécialité'
        verbose_name_plural = 'Spécialités'
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialties = models.ManyToManyField(Specialty, related_name='doctors')
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=200.00)
    office_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default='Casablanca')
    languages = models.CharField(max_length=150, blank=True, help_text='Ex. Français, Arabe, Anglais')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f'Dr. {self.user.display_name()}'

    def get_absolute_url(self):
        return reverse('doctors:detail', kwargs={'pk': self.pk})
