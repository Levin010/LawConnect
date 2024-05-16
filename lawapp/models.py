from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator
from datetime import datetime
from django.core.exceptions import ValidationError


class AdvocateDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    profile_pic = models.ImageField(upload_to='images/advoc_profile_pics', default='images/default_avatar.png')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    CATEGORY_CHOICES = (
        ('general_practice', 'General Practice'),
        ('corporate_law', 'Corporate Law'),
        ('criminal_defense', 'Criminal Defense'),
        ('environmental_law', 'Environmental Law'),
        ('entertainment_law', 'Entertainment Law'),
        ('family_law', 'Family Law'),
        ('finance_law', 'Finance Law'),
        ('immigration_law', 'Immigration Law'),
        ('land_law', 'Land Law'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    law_firm = models.CharField(max_length=100, null=True, blank=True)
    county = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_address = models.CharField(max_length=100, null=True, blank=True)
    experience = models.PositiveIntegerField(validators=[MaxValueValidator(80)], default=1)
    bio = models.TextField(null=True, blank=True)
    practicing_certificate = models.FileField(upload_to='documents/practicing_certificates', null=True, blank=True)
    

    def __str__(self):
        return self.user.username

    def update_profile(self, profile_pic, first_name, last_name, gender, phone_number, category, law_firm, county, address, postal_address, experience, bio, practicing_certificate):
        self.profile_pic = profile_pic
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.phone_number = phone_number
        self.category = category
        self.law_firm = law_firm
        self.county = county
        self.address = address
        self.postal_address = postal_address
        self.experience = experience
        self.bio = bio
        self.practicing_certificate = practicing_certificate

        
        self.save()


class ClientDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    profile_pic = models.ImageField(upload_to='images/client_profile_pics', default='images/default_avatar.png')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100)
    postal_address = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def update_profile(self, profile_pic, first_name, last_name, phone_number, city, postal_address):
        self.profile_pic = profile_pic
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.city = city
        self.postal_address = postal_address
        self.save()


class Request(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=[('plaintiff', 'Plaintiff/Petitioner'), ('defendant', 'Defendant/Respondent')])
    case_description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"Request from {self.client.username} to {self.advocate.username}"


class Case(models.Model):
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cases')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_cases', null=True, blank=True)
    case_name = models.CharField(max_length=512)
    case_number = models.CharField(max_length=255, null=True, blank=True)
    client_role = models.CharField(max_length=20, choices=(('plaintiff', 'Plaintiff/Petitioner'), ('defendant', 'Defendant/Respondent')))
    case_description = models.TextField()
    date_launched = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    open_status = models.BooleanField(default=True)

    def __str__(self):
        return f"Case {self.case_name} for {self.client.username} by {self.advocate.username}"
    
    def update_case(self, case_name, case_number, client_role, case_description):
        try:
            self.case_name = case_name
            self.case_number = case_number
            self.client_role = client_role
            self.case_description = case_description
            self.save()
        except ValidationError as e:
            # Handle validation errors
            pass


class Updates(models.Model):
    case = models.ForeignKey('Case', on_delete=models.CASCADE, related_name='updates', default=1)
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advocate_updates', default=1)
    title = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    description = models.TextField()
    update_document = models.FileField(upload_to='documents/update_document', null=True, blank=True)

    def __str__(self):
        return f"{self.title} for Case {self.case.case_name}"

    def update_updates(self, title, description, update_document):
        try:
            self.title = title
            self.description = description
            self.update_document = update_document
            self.save()
        except ValidationError as e:
            # Handle validation errors
            pass


class SetAppointment(models.Model):
    advocate = models.OneToOneField(User, on_delete=models.CASCADE)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    MORNING_CHOICES = [(f'{i:02}:00', f'{i:02}:00') for i in range(6, 13)]  # Adjusted choices to store time directly
    AFTERNOON_CHOICES = [(f'{i:02}:00', f'{i:02}:00') for i in range(12, 17)]
    EVENING_CHOICES = [(f'{i:02}:00', f'{i:02}:00') for i in range(16, 23)]
    morning_start = models.CharField(max_length=5, choices=MORNING_CHOICES, default='06:00', null=True, blank=True)
    morning_end = models.CharField(max_length=5, choices=MORNING_CHOICES, default='12:00', null=True, blank=True)
    afternoon_start = models.CharField(max_length=5, choices=AFTERNOON_CHOICES, default='12:00', null=True, blank=True)
    afternoon_end = models.CharField(max_length=5, choices=AFTERNOON_CHOICES, default='16:00', null=True, blank=True)
    evening_start = models.CharField(max_length=5, choices=EVENING_CHOICES, default='16:00', null=True, blank=True)
    evening_end = models.CharField(max_length=5, choices=EVENING_CHOICES, default='22:00', null=True, blank=True)
    DURATION_CHOICES = [
        (15, '15 minutes'),
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '1 hour'),
    ]
    appointment_duration = models.PositiveSmallIntegerField(choices=DURATION_CHOICES, default=15, null=True, blank=True)

    def __str__(self):
        return f"Appointment settings for {self.advocate.username}"
    
    

    def update_settings(self, date, morning_start, morning_end, afternoon_start, afternoon_end, evening_start, evening_end, appointment_duration):
        self.date = date
        self.morning_start = morning_start
        self.morning_end = morning_end
        self.afternoon_start = afternoon_start
        self.afternoon_end = afternoon_end
        self.evening_start = evening_start
        self.evening_end = evening_end
        self.appointment_duration = appointment_duration

        self.save()


class Appointment(models.Model):
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advoc_myappts')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_myappts')
    appointment_date = models.DateField(null=True, blank=True)
    TIME_SLOT_CHOICES = [
        ('8:00 - 8:30', '8:00 - 8:30'),
        ('8:30 - 9:00', '8:30 - 9:00'),
        ('9:00 - 9:30', '9:00 - 9:30'),
        ('9:30 - 10:00', '9:30 - 10:00'),
        ('10:00 - 10:30', '10:00 - 10:30'),
        ('10:30 - 11:00', '10:30 - 11:00'),
        ('11:00 - 11:30', '11:00 - 11:30'),
        ('11:30 - 12:00', '11:30 - 12:00'),
        ('12:00 - 12:30', '12:00 - 12:30'),
        ('12:30 - 13:00', '12:30 - 13:00'),
        ('14:00 - 14:30', '14:00 - 14:30'),
        ('14:30 - 15:00', '14:30 - 15:00'),
        ('15:00 - 15:30', '15:00 - 15:30'),
        ('15:30 - 16:00', '15:30 - 16:00'),
        ('16:00 - 16:30', '16:00 - 16:30'),
        ('16:30 - 17:00', '16:30 - 17:00'),
    ]
    time_slot = models.CharField(max_length=25, choices=TIME_SLOT_CHOICES)
    APPOINTMENT_TYPES = [
        ('in_office', 'In-Office'),
        ('phone', 'Phone')
    ]
    appointment_type = models.CharField(max_length=10, choices=APPOINTMENT_TYPES)
    phone_number = models.CharField(max_length=15)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    cancelled = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment for {self.advocate.username} with {self.client.username}"
    


class Bill(models.Model):
    case = models.ForeignKey('Case', on_delete=models.CASCADE)
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills_generated')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills_received')
    amount = models.IntegerField()
    description = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        case_name = self.case.case_name if self.case else "Unknown Case"
        advocate_username = self.advocate.username if self.advocate else "Unknown Advocate"
        client_username = self.client.username if self.client else "Unknown Client"
        return f"Bill for Case: {case_name}, Advocate: {advocate_username}, Client: {client_username}, Amount: {self.amount}"



class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advocate_reviews')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)  # Optional comment
    date_created = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Review for Advocate: {self.advocate.username} by Client: {self.client.username}, Rating: {self.get_rating_display()}"