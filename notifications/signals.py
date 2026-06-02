from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from appointments.models import Appointment
from .models import Notification


@receiver(pre_save, sender=Appointment)
def remember_old_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return
    try:
        instance._old_status = Appointment.objects.get(pk=instance.pk).status
    except Appointment.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Appointment)
def notify_appointment(sender, instance, created, **kwargs):
    patient = instance.patient
    doctor_user = instance.doctor.user
    when = f'le {instance.date:%d/%m/%Y} à {instance.time:%H:%M}'

    if created:
        Notification.objects.create(
            user=patient,
            title='Rendez-vous enregistré',
            message=f'Votre rendez-vous avec {instance.doctor} est prévu {when}.',
        )
        Notification.objects.create(
            user=doctor_user,
            title='Nouveau rendez-vous',
            message=f'{patient.display_name()} a réservé un rendez-vous {when}.',
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status and old_status != instance.status:
        Notification.objects.create(
            user=patient,
            title='Mise à jour du rendez-vous',
            message=f'Le statut de votre rendez-vous avec {instance.doctor} est maintenant : {instance.get_status_display()}.',
        )
        Notification.objects.create(
            user=doctor_user,
            title='Statut de rendez-vous mis à jour',
            message=f'Le rendez-vous avec {patient.display_name()} est maintenant : {instance.get_status_display()}.',
        )
