# Generated by Django 4.2.5 on 2024-03-10 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawapp', '0014_appointment_appointment_date_appointment_rejected_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
    ]