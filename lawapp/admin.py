from django.contrib import admin
from .models import User, AdvocateDetails, ClientDetails, Request, Case, Appointment, Updates, Bill

# Register your models here. 
admin.site.register(AdvocateDetails),
admin.site.register(ClientDetails),
admin.site.register(Request)
admin.site.register(Case),
admin.site.register(Appointment),
admin.site.register(Updates),
admin.site.register(Bill),