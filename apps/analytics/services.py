"""
Analytics Service Layer: AI Recommendation Engine, Dynamic Pricing Algorithm & KPI Aggregators.
"""
from decimal import Decimal
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import RevenueDailyMetric, DynamicPriceAdjustmentLog
from apps.tours.models import TourPackage
from apps.destinations.models import Destination

class RecommendationEngine:
    @staticmethod
    def get_recommended_packages_for_user(user=None, limit=6):
        """Content-based & Popularity collaborative recommendation blend."""
        if user and user.is_authenticated:
            # Check user past bookings
            past_orders = user.orders.filter(status__in=['CONFIRMED', 'COMPLETED'])
            if past_orders.exists():
                booked_destinations = [
                    item.tour_package.destination_id for order in past_orders
                    for item in order.line_items.filter(tour_package__isnull=False)
                ]
                if booked_destinations:
                    recs = TourPackage.objects.filter(
                        destination_id__in=booked_destinations, is_active=True
                    ).order_by('-rating_average', '-booking_count')[:limit]
                    if recs.exists():
                        return recs
        
        # Fallback to high-rated featured tours
        return TourPackage.objects.filter(is_active=True, is_featured=True).order_by('-rating_average', '-booking_count')[:limit]

class DynamicPricingEngine:
    @staticmethod
    def calculate_surge_factor(tour_package: TourPackage) -> Decimal:
        """Computes real-time dynamic pricing surge based on demand and booking pace."""
        factor = Decimal('1.00')
        
        # High booking volume boost
        if tour_package.booking_count > 50:
            factor += Decimal('0.08')
        elif tour_package.booking_count > 20:
            factor += Decimal('0.04')

        # High rating boost
        if tour_package.rating_average >= Decimal('4.80'):
            factor += Decimal('0.05')

        return factor.quantize(Decimal('0.01'))
