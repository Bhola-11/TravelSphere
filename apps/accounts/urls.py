from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .views import (
    CustomerRegisterView, AgencyRegisterView, CustomLoginView, CustomLogoutView,
    DashboardRedirectView, CustomerDashboardView, ProfileView, KYCVerificationView,
    AddressBookView, ActivityLogView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='register_customer'),
    path('register/customer/', CustomerRegisterView.as_view(), name='register_customer_alias'),
    path('register/agency/', AgencyRegisterView.as_view(), name='register_agency'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard_redirect'),
    path('dashboard/customer/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('kyc/', KYCVerificationView.as_view(), name='kyc'),
    path('addresses/', AddressBookView.as_view(), name='addresses'),
    path('activity/', ActivityLogView.as_view(), name='activity_logs'),
    path('password-change/', PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
]
