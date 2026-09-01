"""
Agencies Views: Partner Console, Commission Summary, Package Dispatch & Payout Requests.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Agency, AgencyStaff, AgencyCommissionPayout
from .forms import AgencyProfileForm, PayoutRequestForm
from apps.bookings.models import BookingOrder
from apps.tours.models import TourPackage

class AgencyDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'agencies/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agency = getattr(self.request.user, 'owned_agency', None)
        if not agency:
            # Check staff
            staff = getattr(self.request.user, 'agency_staff_profile', None)
            if staff:
                agency = staff.agency
        
        context['agency'] = agency
        if agency:
            context['packages'] = TourPackage.objects.filter(agency=self.request.user)
            context['bookings'] = BookingOrder.objects.filter(agency=agency).order_by('-created_at')[:10]
            context['payouts'] = agency.payouts.all().order_by('-created_at')[:5]
        return context

class AgencyPackageListView(LoginRequiredMixin, ListView):
    model = TourPackage
    template_name = 'agencies/packages.html'
    context_object_name = 'packages'

    def get_queryset(self):
        return TourPackage.objects.filter(agency=self.request.user)

class AgencyPayoutRequestView(LoginRequiredMixin, View):
    template_name = 'agencies/payout_request.html'

    def get(self, request):
        agency = getattr(request.user, 'owned_agency', None)
        form = PayoutRequestForm()
        return render(request, self.template_name, {'agency': agency, 'form': form})

    def post(self, request):
        agency = getattr(request.user, 'owned_agency', None)
        form = PayoutRequestForm(request.POST)
        if form.is_valid():
            payout = form.save(commit=False)
            if payout.amount > agency.wallet_balance:
                messages.error(request, f"Requested amount exceeds wallet balance (${agency.wallet_balance}).")
            else:
                payout.agency = agency
                payout.save()
                messages.success(request, "Payout request submitted successfully.")
                return redirect('agencies:dashboard')
        return render(request, self.template_name, {'agency': agency, 'form': form})
