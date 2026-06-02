from django.test import TestCase
from doctors.models import Specialty
from .ai_engine import engine


class AiOrientationTests(TestCase):
    def setUp(self):
        Specialty.objects.create(name='Cardiologie', slug='cardiologie', keywords='coeur cardiaque poitrine palpitations')
        Specialty.objects.create(name='Dermatologie', slug='dermatologie', keywords='peau boutons rougeurs taches cou demangeaisons')
        engine.train(force=True)

    def test_cardiology_suggestion(self):
        results = engine.predict('J ai des palpitations et une douleur à la poitrine')
        self.assertTrue(results)
        self.assertEqual(results[0]['specialty'].name, 'Cardiologie')

    def test_dermatology_suggestion_for_taches_cou(self):
        results = engine.predict('J ai des taches au cou et des rougeurs')
        self.assertTrue(results)
        self.assertEqual(results[0]['specialty'].name, 'Dermatologie')
