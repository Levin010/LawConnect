from django.urls import path
from . import views 


urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("advoc_list/", views.advoc_list, name="advoc_list"),
    path("advoc_view/<int:advocate_id>/", views.advoc_view, name="advoc_view"),


    # Client
    path("client_dash/", views.client_dash, name="client_dash"),

    path("make_appt/<int:advocate_id>/", views.make_appt, name="make_appt"),
    path("client_appts/", views.client_appts, name="client_appts"),
    path("cancel_appt/<int:appointment_id>/", views.cancel_appt, name="cancel_appt"),
    path("client_bills/", views.client_bills, name="client_bills"),
    path("dummy_view/<int:advocate_id>/", views.dummy_view, name="dummy_view"),


    # Advocate
    path("advoc_dash/", views.advoc_dash, name="advoc_dash"),

    path("make_bill/", views.make_bill, name="make_bill"),
    path("bill_client/<int:case_id>/", views.bill_client, name="bill_client"),
    path("close_case/<int:case_id>/", views.close_case, name="close_case"),
    path("edit_case/<int:case_id>/", views.edit_case, name="edit_case"),
    path("edit_update/<int:update_id>/", views.edit_update, name="edit_update"),
    path("reopen_case/<int:case_id>/", views.reopen_case, name="reopen_case"),
    path("advoc_appts/", views.advoc_appts, name="advoc_appts"),
    path("reject_appt/<int:appointment_id>/", views.reject_appt, name="reject_appt"),
    path("advoc_bills/", views.advoc_bills, name="advoc_bills"),
    path('delete_update/<int:update_id>/', views.delete_update, name='delete_update'),
    
    
    path("client_profile/", views.client_profile, name="client_profile"),
    path("advoc_profile/", views.advoc_profile, name="advoc_profile"),
    path("advoc_editprofile/", views.advoc_editprofile, name="advoc_editprofile"),
    path("client_editprofile/", views.client_editprofile, name="client_editprofile"),
    path("advoc_mycases/", views.advoc_mycases, name="advoc_mycases"),
    path("client_mycases/", views.client_mycases, name="client_mycases"),
    path("advoc_casedetails/<int:case_id>/", views.advoc_casedetails, name="advoc_casedetails"),
    path("client_casedetails/<int:case_id>/", views.client_casedetails, name="client_casedetails"),
    path("received_requests/", views.received_requests, name="received_requests"),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path("sent_requests/", views.sent_requests, name="sent_requests"),
    path("new_case/<int:request_id>/", views.new_case, name="new_case"),
    path("newnew_case/", views.newnew_case, name="newnew_case"),
    path('set_appointment/', views.set_appointment, name='set_appointment'),


    # Payment
    path("mpesa/", views.mpesa, name="mpesa"),
    path('stk_push_callback/', views.stk_push_callback, name='stk_push_callback'),
    path("mpesa_bills/<int:bill_id>/", views.mpesa_bills, name="mpesa_bills"),


    # Admin
    path("admin_dash/", views.admin_dash, name="admin_dash"),

    path("advocates/", views.advocates, name="advocates"),
    path("advocates_pdf/", views.advocates_pdf, name="advocates_pdf"),

    path("clients/", views.clients, name="clients"),
    path("clients_pdf/", views.clients_pdf, name="clients_pdf"),

    path("all_cases/", views.all_cases, name="all_cases"),
    path("all_cases_pdf/", views.all_cases_pdf, name="all_cases_pdf"),
    path("case_list/", views.case_list, name="case_list"),
    path("case_report/<int:case_id>/", views.case_report, name="case_report"),
    path("gen_case_report/<int:case_id>/", views.gen_case_report, name="gen_case_report"),

    path("all_appts/", views.all_appts, name="all_appts"),
    path("appt_list/", views.appt_list, name="appt_list"),

    path("bills/", views.bills, name="bills"),
    path("bills_pdf/", views.bills_pdf, name="bills_pdf"),

    path("requests/", views.requests, name="requests"),
    


    # Admin pdf
    
    path("all_casespdf/", views.all_casespdf, name="all_casespdf"),
    
    
]
