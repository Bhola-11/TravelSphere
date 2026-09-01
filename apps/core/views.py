"""
Core Static, Informational, and Utility Views.
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Avg
from .models import ContactInquiry, SystemConfiguration
from .services import ConfigService

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Import destination and tour packages dynamically for home showcase
        try:
            from apps.destinations.models import Destination
            from apps.tours.models import TourPackage
            from apps.hotels.models import HotelProperty
            
            context['featured_destinations'] = Destination.objects.filter(is_featured=True, is_active=True)[:6]
            context['popular_tours'] = TourPackage.objects.filter(is_featured=True, is_active=True).select_related('destination')[:6]
            context['top_hotels'] = HotelProperty.objects.filter(is_featured=True, is_active=True).select_related('city', 'city__country')[:4]
            context['stats'] = {
                'total_destinations': Destination.objects.filter(is_active=True).count(),
                'total_tours': TourPackage.objects.filter(is_active=True).count(),
                'total_hotels': HotelProperty.objects.filter(is_active=True).count(),
                'happy_travelers': '120,000+',
            }
        except Exception:
            context['featured_destinations'] = []
            context['popular_tours'] = []
            context['top_hotels'] = []
            context['stats'] = {'total_destinations': 50, 'total_tours': 120, 'total_hotels': 350, 'happy_travelers': '100K+'}
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(View):
    template_name = 'core/contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not (name and email and subject and message):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, self.template_name)

        ContactInquiry.objects.create(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        messages.success(request, 'Thank you! Your inquiry has been submitted. Our concierge team will reach out within 24 hours.')
        return redirect('contact')

class TermsView(TemplateView):
    template_name = 'core/terms.html'

class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'

class FAQView(TemplateView):
    template_name = 'core/faq.html'

class CurrencySwitcherView(View):
    def post(self, request):
        currency = request.POST.get('currency', 'USD')
        request.session['currency'] = currency
        messages.info(request, f'Currency switched to {currency}')
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        return redirect(next_url)
