from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from doctors.models import Doctor, Specialty


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CONFIRMED = 'CONFIRMED', 'Confirmé'
        CANCELLED = 'CANCELLED', 'Annulé'
        COMPLETED = 'COMPLETED', 'Terminé'
        NO_SHOW = 'NO_SHOW', 'Absent'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'PATIENT'},
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(help_text='Motif de consultation')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['doctor', 'date', 'time']),
            models.Index(fields=['patient', 'date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.patient.display_name()} → {self.doctor} le {self.date} à {self.time}'

    @property
    def is_future(self):
        today = timezone.localdate()
        now_time = timezone.localtime().time()
        return self.date > today or (self.date == today and self.time > now_time)

    @property
    def can_be_cancelled(self):
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED] and self.is_future

    @property
    def can_be_rescheduled(self):
        return self.can_be_cancelled

    def clean(self):
        if self.date and self.date < timezone.localdate():
            raise ValidationError('Il est impossible de réserver un rendez-vous dans le passé.')
        if self.doctor_id and self.date and self.time and self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            conflict = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                time=self.time,
                status__in=[self.Status.PENDING, self.Status.CONFIRMED],
            )
            if self.pk:
                conflict = conflict.exclude(pk=self.pk)
            if conflict.exists():
                raise ValidationError('Ce créneau est déjà réservé pour ce médecin.')

    def status_badge_class(self):
        return {
            self.Status.PENDING: 'bg-warning text-dark',
            self.Status.CONFIRMED: 'bg-success',
            self.Status.CANCELLED: 'bg-danger',
            self.Status.COMPLETED: 'bg-secondary',
            self.Status.NO_SHOW: 'bg-dark',
        }.get(self.status, 'bg-secondary')


class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    summary = models.TextField(help_text='Résumé administratif de consultation, sans diagnostic médical détaillé')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Résumé administratif du RDV #{self.appointment_id}'


class Review(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Avis {self.rating}/5 - RDV #{self.appointment_id}'
