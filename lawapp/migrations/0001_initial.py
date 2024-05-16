# Generated by Django 4.2.5 on 2024-02-06 14:21

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('plaintiff', 'Plaintiff'), ('defendant', 'Defendant')], max_length=10)),
                ('case_description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Updates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ClientDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_pic', models.ImageField(default='images/default_avatar.png', upload_to='images/client_profile_pics')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('city', models.CharField(max_length=100)),
                ('postal_address', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdvocateDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_pic', models.ImageField(default='images/default_avatar.png', upload_to='images/advoc_profile_pics')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='male', max_length=10)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('category', models.CharField(choices=[('general_practice', 'General Practice'), ('corporate_law', 'Corporate Law'), ('criminal_defense', 'Criminal Defense'), ('environmental_law', 'Environmental Law'), ('entertainment_law', 'Entertainment Law'), ('family_law', 'Family Law'), ('finance_law', 'Finance Law'), ('immigration_law', 'Immigration Law')], max_length=20)),
                ('law_firm', models.CharField(blank=True, max_length=100, null=True)),
                ('county', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('postal_address', models.CharField(blank=True, max_length=100, null=True)),
                ('experience', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(80)])),
                ('bio', models.TextField(blank=True, null=True)),
                ('practicing_certificate', models.FileField(blank=True, null=True, upload_to='documents/practicing_certificates')),
                ('user', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]