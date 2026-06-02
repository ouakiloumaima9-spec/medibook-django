from django.core.exceptions import ValidationError
from django.db import models
from doctors.models import Doctor


class Availability(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Lundi'
        TUESDAY = 1, 'Mardi'
        WEDNESDAY = 2, 'Mercredi'
        THURSDAY = 3, 'Jeudi'
        FRIDAY = 4, 'Vendredi'
        SATURDAY = 5, 'Samedi'
        SUNDAY = 6, 'Dimanche'

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Disponibilité'
        verbose_name_plural = 'Disponibilités'
        unique_together = [['doctor', 'weekday', 'start_time']]
        ordering = ['weekday', 'start_time']

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('L’heure de fin doit être postérieure à l’heure de début.')
        if self.slot_duration_minutes < 10:
            raise ValidationError('La durée minimale d’un créneau est de 10 minutes.')

    def __str__(self):
        return f'{self.doctor} - {self.get_weekday_display()} {self.start_time}-{self.end_time}'


class TimeOff(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_offs')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Indisponibilité'
        verbose_name_plural = 'Indisponibilités'

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('La date de fin doit être postérieure ou égale à la date de début.')

    def __str__(self):
        return f'{self.doctor} : {self.start_date} → {self.end_date}'
