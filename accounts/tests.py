from django.test import TestCase
from django.urls import reverse
from .models import PatientProfile, User


class AccountsTests(TestCase):
    def test_patient_signup_creates_patient_profile(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newpatient',
            'first_name': 'New',
            'last_name': 'Patient',
            'email': 'newpatient@example.com',
            'phone': '+212600000001',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newpatient')
        self.assertTrue(user.is_patient())
        self.assertTrue(PatientProfile.objects.filter(user=user).exists())
