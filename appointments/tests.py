from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from accounts.models import User
from doctors.models import Doctor, Specialty
from schedules.models import Availability
from .models import Appointment


class AppointmentConflictTests(TestCase):
    def setUp(self):
        self.specialty = Specialty.objects.create(name='Cardiologie', slug='cardiologie', keywords='coeur cardiaque')
        doctor_user = User.objects.create_user('doctor', password='doctor123', role=User.Role.DOCTOR, first_name='Doc')
        self.doctor = Doctor.objects.create(user=doctor_user, license_number='LIC-T', office_address='Cabinet')
        self.doctor.specialties.add(self.specialty)
        Availability.objects.create(doctor=self.doctor, weekday=(date.today() + timedelta(days=1)).weekday(), start_time=time(9, 0), end_time=time(10, 0), slot_duration_minutes=30)
        self.patient1 = User.objects.create_user('p1', password='patient123', role=User.Role.PATIENT)
        self.patient2 = User.objects.create_user('p2', password='patient123', role=User.Role.PATIENT)
        self.target_date = date.today() + timedelta(days=1)

    def test_active_conflicting_appointments_are_rejected(self):
        Appointment.objects.create(patient=self.patient1, doctor=self.doctor, specialty=self.specialty, date=self.target_date, time=time(9, 0), reason='test')
        appointment = Appointment(patient=self.patient2, doctor=self.doctor, specialty=self.specialty, date=self.target_date, time=time(9, 0), reason='test')
        with self.assertRaises(ValidationError):
            appointment.full_clean()

    def test_cancelled_appointment_does_not_block_slot(self):
        Appointment.objects.create(patient=self.patient1, doctor=self.doctor, specialty=self.specialty, date=self.target_date, time=time(9, 0), reason='test', status=Appointment.Status.CANCELLED)
        appointment = Appointment(patient=self.patient2, doctor=self.doctor, specialty=self.specialty, date=self.target_date, time=time(9, 0), reason='test')
        appointment.full_clean()
