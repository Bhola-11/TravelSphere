"""
Analytics Views: Executive Business Intelligence, Revenue Charts, and Dynamic Pricing Simulation.
"""
from decimal import Decimal
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Avg
from apps.bookings.models import BookingOrder
from apps.tours.models import TourPackage
from apps.destinations.models import Destination
from apps.accounts.models import TravelSphereUser
from .services import RecommendationEngine

class AdminAnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_rev = BookingOrder.objects.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        total_orders = BookingOrder.objects.count()
        confirmed_orders = BookingOrder.objects.filter(status='CONFIRMED').count()
        total_users = TravelSphereUser.objects.count()
        
        context['kpis'] = {
            'total_revenue': total_rev,
            'total_bookings': total_orders,
            'confirmed_bookings': confirmed_orders,
            'total_users': total_users,
            'total_tours': TourPackage.objects.filter(is_active=True).count(),
            'total_destinations': Destination.objects.filter(is_active=True).count(),
        }
        
        context['recent_orders'] = BookingOrder.objects.select_related('customer').order_by('-created_at')[:8]
        context['top_tours'] = TourPackage.objects.filter(is_active=True).order_by('-booking_count')[:5]
        return context

class RecommendationFeedView(TemplateView):
    template_name = 'analytics/recommendations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recommended_tours'] = RecommendationEngine.get_recommended_packages_for_user(self.request.user, limit=8)
        return context
