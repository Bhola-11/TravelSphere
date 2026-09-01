"""
Accounts CBVs: Registration, Login/Logout, Multi-Role Dashboards, KYC & Profile.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView, ListView, CreateView, View
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import (
    CustomerRegistrationForm, AgencyRegistrationForm, UserLoginForm,
    CustomerProfileUpdateForm, UserInfoUpdateForm, AddressForm, KYCUploadForm
)
from .models import CustomerProfile, AgencyProfile, UserAddress, KYCDocument, UserActivityLog
from .services import AccountService
from apps.core.constants import UserRole, KYCStatus

User = get_user_model()

class CustomerRegisterView(FormView):
    template_name = 'accounts/register_customer.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('accounts:dashboard_redirect')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
        AccountService.log_user_activity(user, 'REGISTER', 'Customer registered account.', self.request)
        messages.success(self.request, f"Welcome to TravelSphere, {user.first_name}!")
        return super().form_valid(form)

class AgencyRegisterView(FormView):
    template_name = 'accounts/register_agency.html'
    form_class = AgencyRegistrationForm
    success_url = reverse_lazy('accounts:dashboard_redirect')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
        AccountService.log_user_activity(user, 'REGISTER_AGENCY', 'Agency registered account.', self.request)
        messages.success(self.request, "Agency registered successfully! Your account is pending verification.")
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        user.last_login_ip = getattr(self.request, 'client_ip', None)
        user.save(update_fields=['last_login_ip'])
        AccountService.log_user_activity(user, 'LOGIN', 'User logged in successfully.', self.request)
        messages.success(self.request, f"Welcome back, {user.get_full_name()}!")
        return super().form_valid(form)

class CustomLogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            AccountService.log_user_activity(request.user, 'LOGOUT', 'User logged out.', request)
            logout(request)
            messages.info(request, "You have been logged out.")
        return redirect('home')

class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        if user.role == UserRole.CUSTOMER:
            return redirect('accounts:customer_dashboard')
        elif user.role in [UserRole.AGENCY_ADMIN, UserRole.AGENT]:
            return redirect('agencies:dashboard')
        elif user.role == UserRole.HOTEL_MANAGER:
            return redirect('hotels:manage_properties')
        elif user.role == UserRole.TRANSPORT_MANAGER:
            return redirect('transports:manage_schedules')
        elif user.is_staff or user.role == UserRole.SUPER_ADMIN:
            return redirect('analytics:dashboard')
        return redirect('accounts:customer_dashboard')

class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/customer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            from apps.bookings.models import BookingOrder
            from apps.tours.models import TourPackage
            context['recent_bookings'] = BookingOrder.objects.filter(customer=user).order_by('-created_at')[:6]
            context['active_bookings_count'] = BookingOrder.objects.filter(customer=user, status__in=['CONFIRMED', 'IN_PROGRESS']).count()
            context['total_completed'] = BookingOrder.objects.filter(customer=user, status='COMPLETED').count()
            context['latest_booking'] = BookingOrder.objects.filter(customer=user).order_by('-created_at').first()
            context['recommended_tours'] = TourPackage.objects.filter(is_published=True).select_related('destination', 'category')[:3]
        except Exception:
            context['recent_bookings'] = []
            context['active_bookings_count'] = 0
            context['total_completed'] = 0
            context['latest_booking'] = None
            context['recommended_tours'] = []
        
        context['kyc_status'] = user.kyc_status
        context['profile'] = getattr(user, 'customer_profile', None)
        return context

class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        user_form = UserInfoUpdateForm(instance=request.user)
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        profile_form = CustomerProfileUpdateForm(instance=profile)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })

    def post(self, request):
        user_form = UserInfoUpdateForm(request.POST, request.FILES, instance=request.user)
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        profile_form = CustomerProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            AccountService.log_user_activity(request.user, 'PROFILE_UPDATE', 'Updated profile information.', request)
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })

class KYCVerificationView(LoginRequiredMixin, View):
    template_name = 'accounts/kyc_verify.html'

    def get(self, request):
        form = KYCUploadForm()
        documents = KYCDocument.objects.filter(user=request.user)
        return render(request, self.template_name, {
            'form': form,
            'documents': documents,
        })

    def post(self, request):
        form = KYCUploadForm(request.POST, request.FILES)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.save()
            AccountService.update_kyc_status(request.user)
            AccountService.log_user_activity(request.user, 'KYC_SUBMIT', f'Submitted KYC document {kyc.get_document_type_display()}.', request)
            messages.success(request, "Document submitted for verification.")
            return redirect('accounts:kyc')

        documents = KYCDocument.objects.filter(user=request.user)
        return render(request, self.template_name, {'form': form, 'documents': documents})

class AddressBookView(LoginRequiredMixin, View):
    template_name = 'accounts/addresses.html'

    def get(self, request):
        addresses = UserAddress.objects.filter(user=request.user)
        form = AddressForm()
        return render(request, self.template_name, {'addresses': addresses, 'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, "Address saved successfully.")
            return redirect('accounts:addresses')
        addresses = UserAddress.objects.filter(user=request.user)
        return render(request, self.template_name, {'addresses': addresses, 'form': form})

class ActivityLogView(LoginRequiredMixin, ListView):
    model = UserActivityLog
    template_name = 'accounts/activity_log.html'
    context_object_name = 'logs'
    paginate_by = 20

    def get_queryset(self):
        return UserActivityLog.objects.filter(user=self.request.user)
