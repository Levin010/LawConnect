from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .forms import LoginForm
from .forms import ClientSignupForm, AdvocateSignupForm, AdvocateProfileForm, ClientProfileForm, RequestForm
from .forms import UpdateForm, CaseForm, SetAppointmentForm, AppointmentForm, MpesaForm
from .forms import BillForm, ReviewForm
from django.utils import timezone
from datetime import timedelta, datetime
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from lawapp.models import User, AdvocateDetails, ClientDetails, Updates, Case, SetAppointment
from lawapp.models import Appointment, Bill, Review, Request
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.forms import formset_factory, BaseFormSet
from django_daraja.mpesa.core import MpesaClient
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from fpdf import FPDF
from django.conf import settings
from django.templatetags.static import static
from django.contrib.staticfiles import finders
import os

# Create your views here.



def index(request):
    return render(request, "lawapp/index.html")

def signup(request):
    client_form = ClientSignupForm()
    advocate_form = AdvocateSignupForm()
    
    if request.method == 'POST':
        if 'client-form-submit' in request.POST:
            client_form = ClientSignupForm(request.POST)
            if client_form.is_valid():
                user = client_form.save()
                # get the username from the form
                username = client_form.cleaned_data.get('username')
                # get the group name from the database
                group = Group.objects.get(name='client')
                # save the user as per the specified group
                user.groups.add(group)
                messages.success(request, "Client account created successfully for "+ username)
                return redirect('login')
            else:
                messages.error(request, 'Invalid client form data. Please try again.')

        elif 'advocate-form-submit' in request.POST:
            advocate_form = AdvocateSignupForm(request.POST)
            if advocate_form.is_valid():
                user = advocate_form.save()
                # get the username from the form
                username = advocate_form.cleaned_data.get('username')
                # get the group name from the database
                group = Group.objects.get(name='advocate')
                # save the user as per the specified group
                user.groups.add(group)
                messages.success(request, "Advocate account created successfully for "+ username)
                return redirect('login')
            else:
                messages.error(request, 'Invalid advocate form data. Please try again.')
            

    context = {
        'client_form': client_form,
        'advocate_form': advocate_form,
    }

    return render(request, "lawapp/signup.html", context) 

def login(request):
    form=LoginForm()

    if request.method == 'POST':
        if "login-form-submit" in request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST.get('username')
                password = request.POST.get('password')
                user = authenticate(request, username=username, password=password)

                if user is not None:
                    if user.groups.filter(name='client').exists():
                # User belongs to the 'client' group
                        auth_login(request, user)
                        return redirect('client_dash')
                    elif user.groups.filter(name='advocate').exists():
                # User belongs to the 'advocate' group
                        auth_login(request, user)
                        return redirect('advoc_dash')
                    elif user.groups.filter(name='admin').exists():
                # User belongs to the 'admin' group
                        auth_login(request, user)
                        return redirect('admin_dash')
                    else:
                        next_url = request.POST.get('next')
                
                        if next_url:
                            auth_login(request, user)
                            return redirect(next_url) 
            else:
                messages.info(request, 'Username or Password is incorrect')
        pass        
    else:
        form = LoginForm()
        

    context = {
        'next': request.GET.get('next'),
        'form': form
    }
    return render(request, "lawapp/login.html", context)    

############# Advocate

@login_required
def client_dash(request):
    
    return render(request, "lawapp/client/client_dash.html") 

@login_required
def advoc_dash(request):

    open_cases = Case.objects.filter(advocate=request.user, open_status=True).order_by('-date_launched')
    
    appointments = Appointment.objects.filter(advocate=request.user, cancelled=False, rejected=False).order_by('appointment_date')

    context = {
        'open_cases': open_cases,
        'appointments': appointments,
    }
    
    return render(request, "lawapp/advocate/advoc_dash.html", context)

def advoc_list(request):
    queryset = AdvocateDetails.objects.all()
    search_term = request.GET.get('search')
    filter_category = request.GET.get('filter_category')
    filter_county = request.GET.get('filter_county')

    if search_term:
        queryset = queryset.filter(
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term) |
            Q(county__icontains=search_term) |
            Q(category__icontains=search_term)
        )

    if filter_category and filter_category != 'All Categories':
        queryset = queryset.filter(category=filter_category)

    if filter_county and filter_county != 'All Counties':
        queryset = queryset.filter(county=filter_county)

    all_advocates = AdvocateDetails.objects.all()

    # Get distinct categories and counties from the queryset
    categories = ['All Categories'] + list(queryset.order_by('category').values_list('category', flat=True).distinct())
    counties = ['All Counties'] + list(queryset.order_by('county').values_list('county', flat=True).distinct())

    context = {
        'all_advocates': all_advocates,
        'advocates': queryset,
        'categories': categories,
        'counties': counties,
        }
    
    return render(request, "lawapp/advoc_list.html", context)

@login_required
def dummy_view(request, advocate_id):
    
    # Fetch the AdvocateDetails object based on the user associated with the advocate
    advocate_details = get_object_or_404(AdvocateDetails, id=advocate_id)

    client_details = get_object_or_404(ClientDetails, user=request.user)

    initial_data = {
        'first_name': client_details.first_name,
        'last_name': client_details.last_name,
    }

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.client = request.user
            request_obj.advocate_id = advocate_id
            request_obj.save()
            messages.success(request, 'Representation request submitted successfully.')
            return redirect('sent_requests')
        else:
            messages.error(request, 'Failed to submit representation request. Please check the form.')
               
    else:
        form = RequestForm(initial=initial_data)

    context = {
        'form': form ,
        'advocate_details': advocate_details,
        'client_details': client_details,
         
        }
    
    
    return render(request, "lawapp/advoc_view.html", context)


def advoc_view(request, advocate_id):
    advocate_details = get_object_or_404(AdvocateDetails, id=advocate_id)
    client_details = get_object_or_404(ClientDetails, user=request.user)


    initial_data = {
        'first_name': client_details.first_name,
        'last_name': client_details.last_name,
    }


    reviews = Review.objects.filter(advocate=advocate_details.user).order_by('-id')

    if request.method == 'POST':
        if 'request-submit' in request.POST:
            # Handle the request form submission
            form = RequestForm(request.POST)
            if form.is_valid():
                request_obj = form.save(commit=False)
                request_obj.client = request.user
                request_obj.advocate_id = advocate_id
                request_obj.save()
                messages.success(request, 'Representation request submitted successfully.')
                return redirect('sent_requests')
            else:
                messages.error(request, 'Failed to submit representation request. Please check the form.')
        elif 'review-submit' in request.POST:
            # Handle the review form submission
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_obj = review_form.save(commit=False)
                review_obj.client = request.user
                review_obj.advocate_id = advocate_id
                review_obj.save()
                messages.success(request, 'Review submitted successfully.')
                
                return redirect('client_dash')
            else:
                messages.error(request, 'Failed to submit review. Please check the form.')
    else:
        form = RequestForm(initial=initial_data)
        review_form = ReviewForm()

    context = {
        'form': form,
        'review_form': review_form,
        'advocate_details': advocate_details,
        'client_details': client_details,
        'reviews': reviews,
    }

    return render(request, "lawapp/advoc_view.html", context)


def make_appt(request, advocate_id):

    advocate_details = get_object_or_404(AdvocateDetails, id=advocate_id)

    client_details = get_object_or_404(ClientDetails, user=request.user)

    initial_data = {
        'phone_number': client_details.phone_number,
    }

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_obj = form.save(commit=False)
            appointment_obj.client = request.user
            appointment_obj.advocate_id = advocate_id
            appointment_obj.save()
            messages.success(request, 'Appointment booked successfully.')
            return redirect('client_appts')
        else:
            messages.error(request, 'Failed to book appointment. Please check the form.')
    else:
        form = AppointmentForm(initial=initial_data)

    context = {
        'form': form ,
        'advocate_details': advocate_details,
        'client_details': client_details,
        }

    return render(request, "lawapp/client/make_appt.html", context)



def calculate_available_slots(settings):

    #print("Morning Start:", settings.morning_start)
    #print("Morning End:", settings.morning_end)
    #print("Afternoon Start:", settings.afternoon_start)
    #print("Afternoon End:", settings.afternoon_end)
    #print("Evening Start:", settings.evening_start)
    #print("Evening End:", settings.evening_end)

    morning_start = datetime.strptime(settings.morning_start, '%H:%M').time()
    morning_end = datetime.strptime(settings.morning_end, '%H:%M').time()
    afternoon_start = datetime.strptime(settings.afternoon_start, '%H:%M').time()
    afternoon_end = datetime.strptime(settings.afternoon_end, '%H:%M').time()
    evening_start = datetime.strptime(settings.evening_start, '%H:%M').time()
    evening_end = datetime.strptime(settings.evening_end, '%H:%M').time()

    morning_slots = calculate_slots(morning_start, morning_end, settings.appointment_duration)
    afternoon_slots = calculate_slots(afternoon_start, afternoon_end, settings.appointment_duration)
    evening_slots = calculate_slots(evening_start, evening_end, settings.appointment_duration)
    return [('morning', slot) for slot in morning_slots] + [('afternoon', slot) for slot in afternoon_slots] + [('evening', slot) for slot in evening_slots]

def calculate_slots(start_time, end_time, duration):
    slots = []
    current_time = datetime.combine(datetime.today(), start_time)  # Combine with today's date to create a datetime object
    end_datetime = datetime.combine(datetime.today(), end_time)     # Combine with today's date to create a datetime object
    while current_time < end_datetime:
        slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=duration)
    return slots

@login_required
def client_profile(request):
    client_profile = ClientDetails.objects.get(user=request.user)
    context = {'profile': client_profile}
    
    return render(request, "lawapp/client/client_profile.html",context)

@login_required
def advoc_profile(request):
    advocate_profile = AdvocateDetails.objects.get(user=request.user)
    context = {'profile': advocate_profile}
    
    return render(request, "lawapp/advocate/advoc_profile.html", context)

@login_required
def advoc_editprofile(request):
    try:
        # Attempt to get the existing AdvocateDetails instance for the current user
        advocate_profile = AdvocateDetails.objects.get(user=request.user)
    except AdvocateDetails.DoesNotExist:
        # If the instance doesn't exist, create a new one for the user
        advocate_profile = AdvocateDetails(user=request.user)

    form = AdvocateProfileForm(request.POST or None, request.FILES or None, instance=advocate_profile)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('advoc_profile')
        else:
            messages.error(request, 'Invalid form data. Please try again.')
            print(form.errors)
  
    context = {'form': form}
    
    
    return render(request, "lawapp/advocate/advoc_editprofile.html", context)

@login_required
def client_editprofile(request):
    client_profile = ClientDetails.objects.get(user=request.user)
    form = ClientProfileForm(instance=client_profile)

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=client_profile)
        if form.is_valid():
            form.save()
            return redirect('client_profile')
        else:
                messages.error(request, 'Invalid form data. Please try again.')
    
  
    context = {'form': form}
    
    
    return render(request, "lawapp/client/client_editprofile.html", context)

@login_required
def advoc_mycases(request):

    # Retrieve all cases belonging to the specific advocate user
    open_cases = Case.objects.filter(advocate=request.user, open_status=True).order_by('-date_launched')
    closed_cases = Case.objects.filter(advocate=request.user, open_status=False).order_by('-date_launched')

    context= {
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        }
    
    return render(request, "lawapp/advocate/advoc_mycases.html", context)

@login_required
def advoc_casedetails(request, case_id):

    case = get_object_or_404(Case, id=case_id)

    updates = Updates.objects.filter(case=case).order_by('-id')

    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            update_obj = form.save(commit=False)
            update_obj.advocate = request.user
            update_obj.case_id = case_id
            update_obj.save()
            messages.success(request, 'Update submitted successfully.')
            form = UpdateForm()
        else:
            messages.error(request, 'Failed to submit update. Please check the form.')    
    else:
        form = UpdateForm()

    context = {
        'updates': updates, 
        'form': form,
        'case': case
        }    
    
    return render(request, "lawapp/advocate/advoc_casedetails.html", context)


def make_bill(request):

    # Retrieve all cases belonging to the specific advocate user
    open_cases = Case.objects.filter(advocate=request.user, open_status=True).order_by('-date_launched')
    closed_cases = Case.objects.filter(advocate=request.user, open_status=False).order_by('-date_launched')

    context= {
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        }

    return render(request, "lawapp/advocate/make_bill.html")



def make_bill(request, case_id):

    case = get_object_or_404(Case, id=case_id)

    if request.method == 'POST':
        form = BillForm(request.POST, instance=case)
        if form.is_valid():
            
            advocate = request.user
            
            
            client = case.client

            
            form.instance.advocate = advocate
            form.instance.client = client
            form.instance.case = case

            form.save()
            return redirect('advoc_casedetails', case_id=case_id)  
    else:
        form = BillForm(instance=case)


    context = {
        'form': form, 
        'case': case
        }
    
    return render(request, "lawapp/advocate/bill_client.html", context)


def bill_client(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            advocate = request.user
            client = case.client

            bill_instance = form.save(commit=False)  # Create a Bill instance without saving to the database yet
            bill_instance.case = case
            bill_instance.advocate = advocate
            bill_instance.client = client
            bill_instance.save()

            return redirect('advoc_casedetails', case_id=case_id)  
    else:
        form = BillForm()

    context = {
        'form': form, 
        'case': case
    }
    
    return render(request, "lawapp/advocate/bill_client.html", context)


def advoc_bills(request):

    bills = Bill.objects.filter(advocate=request.user).order_by('-date_sent')
    context = {
        'bills': bills
    }
    
    return render(request, "lawapp/advocate/advoc_bills.html", context)


def client_bills(request):

    bills = Bill.objects.filter(paid=False, client=request.user).order_by('-date_sent')
    context = {
        'bills': bills
    }
    
    return render(request, "lawapp/client/client_bills.html", context)


def close_case(request, case_id):

    case = get_object_or_404(Case, pk=case_id)
    
    case.open_status = False
    
    case.save()

    messages.success(request, 'Case closed successfully.')
    
    return redirect("advoc_casedetails", case_id=case_id)


def reopen_case(request, case_id):
    
    case = get_object_or_404(Case, pk=case_id)
    
    case.open_status = True
    
    case.save()

    messages.success(request, 'Case reopened successfully.')
    
    return redirect("advoc_casedetails", case_id=case_id)


def edit_case(request, case_id):
    

    case = get_object_or_404(Case, id=case_id)

    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            form.save()
            messages.success(request, 'Case edited successfully.')
            return redirect('advoc_casedetails', case_id=case_id)  # Redirect to case details page after editing
        else:
            messages.error(request, 'Failed to edit case. Please check the form.')
    else:
        form = CaseForm(instance=case)

    context = {
        'form': form,
        'case': case,

    }
    
    return render(request, "lawapp/advocate/edit_case.html", context)  


def edit_update(request, update_id):
    

    update = get_object_or_404(Updates, id=update_id)
    

    if request.method == 'POST':
        form = UpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Update edited successfully.')
            return redirect('advoc_casedetails', case_id=update.case.id)  # Redirect to case details page after editing
        else:
            messages.error(request, 'Failed to edit update. Please check the form.')
    else:
        form = UpdateForm(instance=update)

    context = {
        'form': form,
        'update': update,

    }
    
    return render(request, "lawapp/advocate/edit_update.html", context)



@login_required
def client_mycases(request):
    
    open_cases = Case.objects.filter(client=request.user, open_status=True).order_by('-date_launched')
    closed_cases = Case.objects.filter(client=request.user, open_status=False).order_by('-date_launched')

    context= {
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        }
    
    return render(request, "lawapp/client/client_mycases.html", context)

@login_required
def client_casedetails(request, case_id):
    
    case = get_object_or_404(Case, id=case_id)

    updates = Updates.objects.filter(case=case).order_by('-id')

    context = {
        'updates': updates, 
        'case': case
        }
    
    return render(request, "lawapp/client/client_casedetails.html", context)

@login_required
def received_requests(request):

    received_requests = Request.objects.filter(advocate=request.user, accepted=False, rejected=False).order_by('-date_created')
    context = {
        'received_requests': received_requests
    }
    
    return render(request, "lawapp/advocate/received_requests.html", context)


def reject_request(request, request_id):
    if request.method == 'POST':
        request_obj = Request.objects.filter(id=request_id, advocate=request.user).first()
        if request_obj:
            request_obj.rejected = True
            request_obj.save()
            messages.success(request, 'Case rejected successfully')
            return redirect('received_requests')
        else:
            messages.error(request, 'Failed to reject the request. Please try again.')
            

def accept_request(request, request_id):
    if request.method == 'POST':
        # Retrieve the request object
        request_obj = get_object_or_404(Request, id=request_id, advocate=request.user)

        # Update the accepted status
        request_obj.accepted = True
        request_obj.save()

        
        messages.success(request, 'Case launched successfully. Please fill in the details of your new case.')

        # Redirect to the new_case view with the request ID
        return redirect('new_case', request_id=request_id)
        

    
    messages.error(request, 'Failed to launch the case. Please try again.')
    return redirect('received_requests')
        

@login_required
def sent_requests(request):

    sent_requests = Request.objects.filter(client=request.user).order_by('-date_created')
    context = {
        'sent_requests': sent_requests
    }
    
    return render(request, "lawapp/client/sent_requests.html", context)

@login_required
def advoc_appts(request):

    appointments = Appointment.objects.filter(advocate=request.user, cancelled=False, rejected=False).order_by('-date_created')
    context = {
        'appointments': appointments
    }
    
    return render(request, "lawapp/advocate/advoc_appts.html", context)


def reject_appt(request, appointment_id):
    if request.method == 'POST':
        appointment_obj = Appointment.objects.filter(id=appointment_id, advocate=request.user).first()
        if appointment_obj:
            appointment_obj.rejected = True
            appointment_obj.save()
            messages.success(request, 'Appointment cancelled successfully')
            return redirect('advoc_appts')
        else:
            messages.error(request, 'Failed to cancel the appointment. Please try again.')


@login_required
def client_appts(request):

    appointments = Appointment.objects.filter(client=request.user, cancelled=False).order_by('-date_created')
    context = {
        'appointments': appointments
    }
    
    return render(request, "lawapp/client/client_appts.html", context)

def cancel_appt(request, appointment_id):
    if request.method == 'POST':
        appointment_obj = Appointment.objects.filter(id=appointment_id, client=request.user).first()
        if appointment_obj:
            appointment_obj.cancelled = True
            appointment_obj.save()
            messages.success(request, 'Appointment cancelled successfully')
            return redirect('client_appts')
        else:
            messages.error(request, 'Failed to cancel the appointment. Please try again.')



def newnew_case(request):

    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case_obj = form.save(commit=False)
            case_obj.advocate = request.user
            case_obj.save()
            messages.success(request, 'Case created successfully.')
            return redirect('advoc_mycases')
        else:
            messages.error(request, 'Failed to create new case. Please check the form.')
    else:
        form = CaseForm()

    context = {
        'form': form ,
        }
    
    return render(request, "lawapp/advocate/newnew_case.html", context)


@login_required
def new_case(request, request_id):

    # Pass request_id to the template context
    #request_id = request.GET.get('request_id')

    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            # Get advocate and client from the request
            advocate = request.user
            request_id = request.POST.get('request_id')  
            #representation_request = Request.objects.get(id=request_id)
            representation_request = get_object_or_404(Request, id=request_id)
            client = representation_request.client

            # Add advocate and client to the form data before saving
            form.instance.advocate = advocate
            form.instance.client = client

            form.save()
            return redirect('advoc_mycases')  # Redirect to a success page or do something else
    else:
        form = CaseForm()


    # Retrieve the request details using the request_id
    request_details = get_object_or_404(Request, id=request_id)

    context = {
        'form': form, 
        'request_id': request_id,
        'request_details': request_details
        }
    
    return render(request, "lawapp/advocate/new_case.html", context)    




@login_required
def set_appointment(request):

    # Calculate future dates within the next 7 days
    today = datetime.now().date()


    # Get the advocate's appointment settings if they exist, otherwise create a new instance
    appointment_settings, created = SetAppointment.objects.get_or_create(advocate=request.user)

    if request.method == 'POST':
        form = SetAppointmentForm(request.POST, instance=appointment_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment settings updated successfully.')
            return redirect('advoc_dash')
        else:
            messages.error(request, 'Error updating appointment settings.')
    else:
        form = SetAppointmentForm(instance=appointment_settings)

        

    context = {
        'form': form  
               }
    
    
    return render(request, "lawapp/advocate/set_appointment.html", context)

@login_required
def book_appointment(request):
    #if request.method == 'POST':
        #form = AppointmentForm(request.POST)
        #if form.is_valid():
            #appointment = form.save(commit=False)
            #appointment.client = request.user
            #appointment.advocate = SetAppointment.objects.get(advocate=appointment.client)
            #appointment.save()
            #return redirect('client_dashboard')  # Redirect to client's dashboard
    #else:
        #form = AppointmentForm(initial={'date': datetime.now().date()})
    
    #{'form': form}

    return render(request, 'lawapp/book_appointment.html')


############## Payment

def mpesa_bills(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    client_details = get_object_or_404(ClientDetails, user=request.user)

    if request.method == 'POST':
        form = MpesaForm(request.POST)
        if form.is_valid():
            cl = MpesaClient()
            phone_number = form.cleaned_data['phone_number']
            amount = bill.amount  # Use the amount from the bill
            account_reference = 'reference'
            transaction_desc = 'Description'
            callback_url = 'https://darajambili.herokuapp.com/express-payment'
            response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
            messages.success(request, 'Check your phone to complete the payment.')
            
            # Mark the bill as paid
            bill.paid = True
            bill.save()
            
            return redirect('client_bills')
        else:
            messages.error(request, 'Payment failed. Please check the form.')
    else:
        # Pre-fill the form with the client's phone number
        initial_data = {
            'phone_number': client_details.phone_number,
        }
        form = MpesaForm(initial=initial_data)

    context = {
        'form': form,
        'bill': bill  # Pass the bill object to the template for reference
    }
    
    return render(request, "lawapp/client/mpesa_bills.html", context)



def mpesa(request):
    if request.method == 'POST':
        form = MpesaForm(request.POST)
        if form.is_valid():
            cl = MpesaClient()
            phone_number = form.cleaned_data['phone_number']
            amount = 50000
            account_reference = 'reference'
            transaction_desc = 'Description'
            callback_url = 'https://darajambili.herokuapp.com/express-payment'
            response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
            messages.success(request, 'Check your phone to complete the payment.')
            form = MpesaForm()
        else:
            messages.error(request, 'Payment failed. Please check the form.')
    else:
        form = MpesaForm()

    context = {
        'form': form
    }
    
    return render(request, "lawapp/client/mpesa.html", context)


def stk_push_callback(request):
    data = request.body



############# Admin
    
def admin_dash(request):

    advocate_users_count = User.objects.filter(groups__name='advocate').count()
    client_users_count = User.objects.filter(groups__name='client').count()
    total_users_count = advocate_users_count + client_users_count

    
    context = {
        'advocate_users_count': advocate_users_count,
        'client_users_count': client_users_count,
        'total_users_count': total_users_count,
    }

    return render(request, "lawapp/admin/admin_dash.html", context)


def advocates(request):

    advocate_details = AdvocateDetails.objects.all()
    context = {
        'advocate_details': advocate_details
    }
    return render(request, "lawapp/admin/advocates.html", context)


def clients(request):

    client_details = ClientDetails.objects.all()
    context = {
        'client_details': client_details
    }
    return render(request, "lawapp/admin/clients.html", context)


def all_cases(request):

    cases = Case.objects.all()
    context = {
        'cases': cases
    }
    return render(request, "lawapp/admin/all_cases.html", context)


def case_list(request):

    cases = Case.objects.all()
    context = {
        'cases': cases
    }
    return render(request, "lawapp/admin/case_list.html", context)

def case_report(request, case_id):

    case = get_object_or_404(Case, pk=case_id)

    context = {
        'case': case
    }
    
    return render(request, "lawapp/admin/case_report.html", context)


def all_appts(request):

    
    return render(request, "lawapp/admin/all_appts.html")

def appt_list(request):

    
    return render(request, "lawapp/admin/appt_list.html")


def bills(request):

    bills = Bill.objects.all()
    context = {
        'bills': bills
    }
    return render(request, "lawapp/admin/bills.html", context)


def requests(request):

    requests = Request.objects.all()
    context = {
        'requests': requests
    }
    return render(request, "lawapp/admin/clients.html", context)



############## GENERATE PDFs


def advocates_pdf(request):
    # Get advocate detailsfrom the database
    advocate_details = AdvocateDetails.objects.all()
    
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    # Add header with logo
    # Replace 'logo.png' with the path to your logo image file
    image_path = finders.find('images/legal_scales_logo.png')
    pdf.image(image_path, x=10, y=8, w=40, h=10)

    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "Advocate Users", 0, 1, 'C')

    # Underline the heading
    pdf.set_draw_color(0, 0, 0)  # Set color to black
    pdf.set_line_width(0.5)  # Set line width
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    
    # Add footer
    pdf.set_y(-15)
    pdf.set_font('Times', 'I', 8)
    pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'C')

    
    # Add table header
    pdf.set_font("Times", "B", 10)
    pdf.set_xy(10, 30)
    pdf.cell(8, 10, "ID", 1)
    pdf.cell(35, 10, "Name", 1)
    pdf.cell(20, 10, "Gender", 1)
    pdf.cell(30, 10, "Phone Number", 1)
    pdf.cell(35, 10, "Category", 1)
    pdf.cell(25, 10, "County", 1)
    pdf.cell(35, 10, "Last Login", 1)

    # Add table data
    pdf.set_font("Times", size=10)
    y_position = 40
    for index, advocate_detail in enumerate(advocate_details, start=1):
        user = advocate_detail.user
        last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ""
        pdf.set_xy(10, y_position)
        pdf.cell(8, 10, f"{index}", 1)
        pdf.cell(35, 10, f"{advocate_detail.first_name} {advocate_detail.last_name}", 1)
        pdf.cell(20, 10, f"{advocate_detail.get_gender_display()}", 1)
        pdf.cell(30, 10, f"{advocate_detail.phone_number}", 1)
        pdf.cell(35, 10, f"{advocate_detail.get_category_display()}", 1)
        pdf.cell(25, 10, f"{advocate_detail.county}", 1)
        pdf.cell(35, 10, f"{last_login}", 1)

        y_position += 10
    
    # Get the base directory of your Django project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Specify the directory path where you want to store PDF files
    pdf_directory = os.path.join(BASE_DIR, 'pdf_files')
    
    # Create the directory if it doesn't exist
    os.makedirs(pdf_directory, exist_ok=True)
    
    # Specify the file path for the PDF
    pdf_path = os.path.join(pdf_directory, 'advocates.pdf')
    
    # Output PDF to the provided file path
    pdf.output(pdf_path)
    
    # Serve the PDF file as a download
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="advocates.pdf"'
    
    return response


def clients_pdf(request):
    # Get advocate detailsfrom the database
    client_details = ClientDetails.objects.all()
    
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    # Add header with logo
    # Replace 'logo.png' with the path to your logo image file
    image_path = finders.find('images/legal_scales_logo.png')
    pdf.image(image_path, x=10, y=8, w=40, h=10)

    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "Client Users", 0, 1, 'C')

    # Underline the heading
    pdf.set_draw_color(0, 0, 0)  # Set color to black
    pdf.set_line_width(0.5)  # Set line width
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    
    # Add footer
    pdf.set_y(-15)
    pdf.set_font('Times', 'I', 8)
    pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'C')

    
    # Add table header
    pdf.set_font("Times", "B", 10)
    pdf.set_xy(10, 30)
    pdf.cell(8, 10, "ID", 1)
    pdf.cell(30, 10, "Name", 1)
    pdf.cell(25, 10, "Phone Number", 1)
    pdf.cell(20, 10, "City", 1)
    pdf.cell(25, 10, "Postal Address", 1)
    pdf.cell(40, 10, "Date Joined", 1)
    pdf.cell(40, 10, "Last Login", 1)

    # Add table data
    pdf.set_font("Times", size=10)
    y_position = 40
    for index, client_detail in enumerate(client_details, start=1):
        user = client_detail.user
        last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ""
        date_joined = user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else ""
        pdf.set_xy(10, y_position)
        pdf.cell(8, 10, f"{index}", 1)
        pdf.cell(30, 10, f"{client_detail.first_name} {client_detail.last_name}", 1)
        pdf.cell(25, 10, f"{client_detail.phone_number}", 1)
        pdf.cell(20, 10, f"{client_detail.city}", 1)
        pdf.cell(25, 10, f"{client_detail.postal_address}", 1)
        pdf.cell(40, 10, f"{date_joined}", 1)
        pdf.cell(40, 10, f"{last_login}", 1)

        y_position += 10
    
    # Get the base directory of your Django project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Specify the directory path where you want to store PDF files
    pdf_directory = os.path.join(BASE_DIR, 'pdf_files')
    
    # Create the directory if it doesn't exist
    os.makedirs(pdf_directory, exist_ok=True)
    
    # Specify the file path for the PDF
    pdf_path = os.path.join(pdf_directory, 'clients.pdf')
    
    # Output PDF to the provided file path
    pdf.output(pdf_path)
    
    # Serve the PDF file as a download
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="clients.pdf"'
    
    return response



def all_cases_pdf(request):
    # Get advocate detailsfrom the database
    cases = Case.objects.all()
    
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    # Add header with logo
    # Replace 'logo.png' with the path to your logo image file
    image_path = finders.find('images/legal_scales_logo.png')
    pdf.image(image_path, x=10, y=8, w=40, h=10)

    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "All Cases", 0, 1, 'C')

    # Underline the heading
    pdf.set_draw_color(0, 0, 0)  # Set color to black
    pdf.set_line_width(0.5)  # Set line width
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    
    # Add footer
    pdf.set_y(-15)
    pdf.set_font('Times', 'I', 8)
    pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'C')

    
    # Add table header
    pdf.set_font("Times", "B", 10)
    pdf.set_xy(10, 30)
    pdf.cell(8, 10, "ID", 1)
    pdf.cell(35, 10, "Case Name", 1)
    pdf.cell(35, 10, "Case Number", 1)
    pdf.cell(25, 10, "Advocate", 1)
    pdf.cell(25, 10, "Client", 1)
    pdf.cell(40, 10, "Date Launched", 1)
    pdf.cell(20, 10, "Status", 1)

    # Add table data
    pdf.set_font("Times", size=10)
    y_position = 40
    for index, case in enumerate(cases, start=1):
        date_launched = case.date_launched.strftime('%Y-%m-%d %H:%M:%S') if case.date_launched else ""
        status = "Open" if case.open_status else "Closed"
        pdf.set_xy(10, y_position)
        pdf.cell(8, 10, f"{index}", 1)
        pdf.cell(35, 10, f"{case.case_name}", 1)
        pdf.cell(35, 10, f"{case.case_number}", 1)
        pdf.cell(25, 10, f"{case.advocate}", 1)
        pdf.cell(25, 10, f"{case.client}", 1)
        pdf.cell(40, 10, f"{date_launched}", 1)
        pdf.cell(20, 10, f"{status}", 1)

        y_position += 10
    
    # Get the base directory of your Django project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Specify the directory path where you want to store PDF files
    pdf_directory = os.path.join(BASE_DIR, 'pdf_files')
    
    # Create the directory if it doesn't exist
    os.makedirs(pdf_directory, exist_ok=True)
    
    # Specify the file path for the PDF
    pdf_path = os.path.join(pdf_directory, 'allCases.pdf')
    
    # Output PDF to the provided file path
    pdf.output(pdf_path)
    
    # Serve the PDF file as a download
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="allCases.pdf"'
    
    return response



def gen_case_report(request, case_id):

    case = get_object_or_404(Case, pk=case_id)

    template_path = 'lawapp/admin_pdf/case_reportpdf.html'

     # Get the current date
    today_date = date.today().strftime("%B %d, %Y")

    context = {
        'case': case,
        'logo_path': os.path.join(settings.STATIC_URL, 'images', 'legal_scales_logo.png'),
        'date': today_date  # Include the current date in the context  
    
     }

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="CaseReport.pdf"'

    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response





############# logout
def logout_view(request):
    logout(request)
    return redirect('index')



############# Admin PDF

def all_casespdf(request):

    cases = Case.objects.all()
    context = {
        'cases': cases
    }
    return render(request, "lawapp/admin/all_casespdf.html", context)




def delete_update(request, update_id):
    update = get_object_or_404(Updates, id=update_id)
    case_id = update.case.id  # Get the case ID before deleting the update
    if request.method == 'POST':
        update.delete()
        messages.success(request, 'Update deleted successfully.')
    return redirect('advoc_casedetails', case_id=case_id)



def bills_pdf(request):
    # Get advocate detailsfrom the database
    bills = Bill.objects.all()
    
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=5)
    
    # Add header with logo
    # Replace 'logo.png' with the path to your logo image file
    image_path = finders.find('images/legal_scales_logo.png')
    pdf.image(image_path, x=10, y=8, w=40, h=10)

    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "All Bills", 0, 1, 'C')

    # Underline the heading
    pdf.set_draw_color(0, 0, 0)  # Set color to black
    pdf.set_line_width(0.5)  # Set line width
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    
    # Add footer
    pdf.set_y(-15)
    pdf.set_font('Times', 'I', 8)
    pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'C')

    
    # Add table header
    pdf.set_font("Times", "B", 10)
    pdf.set_xy(10, 30)
    pdf.cell(8, 10, "ID", 1)
    pdf.cell(35, 10, "Advocate", 1)
    pdf.cell(35, 10, "Client", 1)
    pdf.cell(25, 10, "Amount", 1)
    pdf.cell(40, 10, "Date Sent", 1)
    pdf.cell(20, 10, "Status", 1)

    # Add table data
    pdf.set_font("Times", size=10)
    y_position = 40
    for index, bill in enumerate(bills, start=1):
        date_sent = bill.date_sent.strftime('%Y-%m-%d %H:%M:%S') if bill.date_sent else ""
        status = "Paid" if bill.paid else "Pending"
        pdf.set_xy(10, y_position)
        pdf.cell(8, 10, f"{index}", 1)
        pdf.cell(35, 10, f"{bill.advocate}", 1)
        pdf.cell(35, 10, f"{bill.client}", 1)
        pdf.cell(25, 10, f"{bill.amount}", 1)
        pdf.cell(40, 10, f"{date_sent}", 1)
        pdf.cell(20, 10, f"{status}", 1)

        y_position += 10
    
    # Get the base directory of your Django project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Specify the directory path where you want to store PDF files
    pdf_directory = os.path.join(BASE_DIR, 'pdf_files')
    
    # Create the directory if it doesn't exist
    os.makedirs(pdf_directory, exist_ok=True)
    
    # Specify the file path for the PDF
    pdf_path = os.path.join(pdf_directory, 'bills.pdf')
    
    # Output PDF to the provided file path
    pdf.output(pdf_path)
    
    # Serve the PDF file as a download
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bills.pdf"'
    
    return response
