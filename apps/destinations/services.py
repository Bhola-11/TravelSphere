"""
Destinations Service Layer: Search Queries, Weather Aggregate, and Recommendation Matcher.
"""
from django.db.models import Q, Avg, Count
from .models import Destination, PointOfInterest, Country

class DestinationService:
    @staticmethod
    def search_destinations(query=None, continent_id=None, country_id=None, category_id=None, max_duration=None):
        qs = Destination.objects.filter(is_active=True).select_related('city', 'city__country', 'category').prefetch_related('tags')
        
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(tagline__icontains=query) |
                Q(overview__icontains=query) |
                Q(city__name__icontains=query) |
                Q(city__country__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()

        if continent_id:
            qs = qs.filter(city__country__continent_id=continent_id)
        if country_id:
            qs = qs.filter(city__country_id=country_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if max_duration:
            qs = qs.filter(ideal_duration_days__lte=max_duration)

        return qs

    @staticmethod
    def get_featured_destinations(limit=6):
        return Destination.objects.filter(is_featured=True, is_active=True).select_related('city', 'city__country')[:limit]

    @staticmethod
    def increment_view_count(destination_id):
        Destination.objects.filter(id=destination_id).update(view_count=models.F('view_count') + 1)
