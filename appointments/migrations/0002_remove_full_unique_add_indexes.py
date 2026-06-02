# Generated manually for MediBook corrections
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together=set(),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['doctor', 'date', 'time'], name='appointmen_doctor__3ec0d7_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['patient', 'date'], name='appointmen_patient_95899e_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['status'], name='appointmen_status_38a96f_idx'),
        ),
    ]
