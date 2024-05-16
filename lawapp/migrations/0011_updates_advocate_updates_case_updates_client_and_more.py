# Generated by Django 4.2.5 on 2024-03-02 14:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lawapp', '0010_alter_setappointment_afternoon_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='updates',
            name='advocate',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='advocate_updates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='updates',
            name='case',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='lawapp.case'),
        ),
        migrations.AddField(
            model_name='updates',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='client_updates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='updates',
            name='update_document',
            field=models.FileField(blank=True, null=True, upload_to='documents/update_document'),
        ),
    ]