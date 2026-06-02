# Generated manually for MediBook corrections
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='languages',
            field=models.CharField(blank=True, help_text='Ex. Français, Arabe, Anglais', max_length=150),
        ),
    ]
