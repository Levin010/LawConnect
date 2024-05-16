from django import forms
#from django.forms import fields
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import AdvocateDetails, ClientDetails, Case, Request, Updates, SetAppointment, Appointment
from .models import Bill, Review
from datetime import datetime, timedelta
from datetime import date

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'new-username', 'required': True}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete': 'new-password', 'required': True}))


class ClientSignupForm(UserCreationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'new-username', 'required': True}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'required': True}))
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete': 'new-password', 'required': True}))
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'required': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({"placeholder": field_name.replace('_', ' ').capitalize()})
            self.fields[field_name].label = ''

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data['username']
        existing_user = User.objects.filter(username=username).exists()
        if existing_user:
            raise forms.ValidationError("Username already taken. Please choose a different username.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        client_details = ClientDetails(user=user)
        client_details.save()
        
        return user
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class AdvocateSignupForm(UserCreationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': True}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'required': True}))
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': True}))
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'required': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({"placeholder": field_name.replace('_', ' ').capitalize()})
            self.fields[field_name].label = ''

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        existing_user = User.objects.filter(username=username).exists()
        if existing_user:
            raise forms.ValidationError("Username already taken. Please choose a different username.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        advocate_details = AdvocateDetails(user=user)
        advocate_details.save()
        
        return user
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class AdvocateProfileForm(forms.ModelForm):

    class Meta:
        model = AdvocateDetails
        fields = ['profile_pic', 'first_name', 'last_name', 'gender', 'phone_number', 'category', 'law_firm', 'county', 'address', 'postal_address', 'experience', 'bio', 'practicing_certificate']


    practicing_certificate = forms.FileField(required=False)


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientDetails
        fields = ['profile_pic', 'first_name', 'last_name', 'phone_number', 'city', 'postal_address']


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['first_name', 'last_name', 'role', 'case_description']


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['case_name', 'case_number', 'client_role', 'case_description']


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Updates
        fields = ['title', 'description'] 


class MpesaForm(forms.Form):
    phone_number = forms.CharField(label='Phone Number', max_length=10, widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))


class SetAppointmentForm(forms.ModelForm):

    class Meta:
        model = SetAppointment
        fields = ['from_date', 'to_date', 'morning_start', 'morning_end', 'afternoon_start', 'afternoon_end', 'evening_start', 'evening_end', 'appointment_duration']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'})
        }
        input_formats = {
            'from_date': ['%Y-%m-%d'],
            'to_date': ['%Y-%m-%d']
        }

    
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'time_slot', 'appointment_type', 'phone_number']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}),
        }
        input_formats = {
            'appointment_date': ['%Y-%m-%d'],
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')

        # Check for appointments with the same date and time slot
        if appointment_date and time_slot:
            conflicting_appointments = Appointment.objects.filter(appointment_date=appointment_date, time_slot=time_slot)
            if self.instance:
                conflicting_appointments = conflicting_appointments.exclude(pk=self.instance.pk)

            if conflicting_appointments.exists():
                self.add_error('time_slot', 'This time slot is not available. Please choose a different time.')

        return cleaned_data


    

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['amount', 'description']    

      
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
 
    
