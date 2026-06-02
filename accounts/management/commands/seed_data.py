from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import PatientProfile, User
from doctors.models import Doctor, Specialty
from schedules.models import Availability

SPECIALTIES_DATA = [
    ('Médecine générale', 'bi-heart-pulse', 'fievre temperature frissons rhume grippe toux fatigue epuisement asthenie cephalee bilan sante check-up controle annuel rhinite angine infection benigne vertiges nausee vaccination ordonnance stress insomnie'),
    ('Cardiologie', 'bi-heart', 'douleur thoracique poitrine pectorale serrement oppression palpitations tachycardie arythmie essoufflement dyspnee hypertension tension arterielle coeur cardiaque infarctus syncope cholesterol ecg echographie cardiaque'),
    ('Dermatologie', 'bi-emoji-sunglasses', 'peau cutane epiderme boutons acne eczema psoriasis rougeurs demangeaisons prurit allergie urticaire verrue grain de beaute melanome tache taches cou visage dos mycose cheveux brulure herpes zona'),
    ('Pédiatrie', 'bi-balloon-heart', 'enfant bebe nourrisson nouveau-ne pediatrique fievre vaccination croissance alimentation biberon allaitement coliques diarrhee constipation eruption otite sommeil langage adolescent'),
    ('Gynécologie', 'bi-gender-female', 'femme gynecologique grossesse enceinte regles menstruation cycle douleurs pelviennes contraception menopause frottis uterus infections fertilite seins mammographie'),
    ('Ophtalmologie', 'bi-eye', 'yeux oeil oculaire vision vue lunettes myopie presbytie astigmatisme conjonctivite oeil rouge secheresse larmoiement cataracte glaucome retine'),
    ('Dentisterie', 'bi-emoji-smile', 'dent dents dentaire dentiste carie gencive gingivite abces bouche couronne implant extraction orthodontie sensibilite haleine blanchiment'),
    ('ORL', 'bi-ear', 'oreille nez gorge orl otite audition vertiges acouphenes sinusite congestion angine pharyngite amygdales voix enrouement ronflement saignement nez'),
    ('Neurologie', 'bi-lightbulb', 'neurologique nerveux cerveau migraine cephalee vertiges equilibre epilepsie convulsions tremblements parkinson alzheimer memoire avc neuropathie fourmillements sciatique sommeil'),
    ('Radiologie', 'bi-camera', 'radio radiographie imagerie irm scanner echographie mammographie doppler fracture os bilan imagerie contraste biopsie'),
]

DOCTORS_DATA = [
    ('rachid', 'Rachid', 'Bennani', 'Cardiologie', 'LIC-001', 15, 'Casablanca'),
    ('fatima', 'Fatima', 'Alaoui', 'Pédiatrie', 'LIC-002', 10, 'Rabat'),
    ('youssef', 'Youssef', 'Tazi', 'Dermatologie', 'LIC-003', 8, 'Casablanca'),
    ('sara', 'Sara', 'El Mansouri', 'Médecine générale', 'LIC-004', 12, 'Mohammedia'),
    ('nabil', 'Nabil', 'Fassi', 'ORL', 'LIC-005', 9, 'Salé'),
    ('karima', 'Karima', 'Ouazzani', 'Gynécologie', 'LIC-006', 14, 'Rabat'),
    ('mehdi', 'Mehdi', 'Cherkaoui', 'Ophtalmologie', 'LIC-007', 7, 'Casablanca'),
    ('amina', 'Amina', 'Berrada', 'Dentisterie', 'LIC-008', 11, 'Témara'),
    ('omar', 'Omar', 'Idrissi', 'Neurologie', 'LIC-009', 16, 'Casablanca'),
    ('hind', 'Hind', 'Benjelloun', 'Radiologie', 'LIC-010', 13, 'Rabat'),
]


class Command(BaseCommand):
    help = 'Initialise les données de démonstration MediBook'

    def handle(self, *args, **kwargs):
        for name, icon, keywords in SPECIALTIES_DATA:
            specialty, _ = Specialty.objects.update_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'icon': icon,
                    'keywords': keywords,
                    'description': f'Orientation et prise de rendez-vous en {name}.',
                    'is_active': True,
                },
            )
            self.stdout.write(f'✓ Spécialité prête : {specialty.name}')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@medibook.ma', 'admin123', role=User.Role.ADMIN, first_name='Admin', last_name='MediBook')
            self.stdout.write('✓ Admin créé : admin / admin123')

        for username, first_name, last_name, specialty_name, license_number, exp, city in DOCTORS_DATA:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@medibook.ma',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': User.Role.DOCTOR,
                    'phone': '+212600000000',
                },
            )
            if created:
                user.set_password('doctor123')
                user.save()
            doctor, _ = Doctor.objects.update_or_create(
                user=user,
                defaults={
                    'license_number': license_number,
                    'years_of_experience': exp,
                    'office_address': '123 Avenue Mohammed V',
                    'city': city,
                    'languages': 'Français, Arabe',
                    'bio': f'Dr. {first_name} {last_name}, spécialiste en {specialty_name}.',
                    'is_active': True,
                },
            )
            specialty = Specialty.objects.get(name=specialty_name)
            doctor.specialties.set([specialty])
            for day in range(5):
                Availability.objects.get_or_create(doctor=doctor, weekday=day, start_time='09:00', defaults={'end_time': '17:00', 'slot_duration_minutes': 30})
            self.stdout.write(f'✓ Médecin prêt : Dr. {first_name} {last_name}')

        if not User.objects.filter(username='patient').exists():
            patient = User.objects.create_user('patient', 'patient@medibook.ma', 'patient123', first_name='Hugo', last_name='Patient', role=User.Role.PATIENT)
            PatientProfile.objects.get_or_create(user=patient)
            self.stdout.write('✓ Patient créé : patient / patient123')

        self.stdout.write(self.style.SUCCESS('Données de démonstration initialisées.'))
