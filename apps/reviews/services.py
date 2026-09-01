"""
Reviews Service Layer: Rating Aggregation, Sentiment Scoring & Moderation.
"""
from django.db.models import Avg, Count
from .models import Review

class ReviewService:
    @staticmethod
    def recalculate_entity_rating(tour=None, hotel=None, destination=None):
        if tour:
            stats = Review.objects.filter(tour_package=tour, is_approved=True).aggregate(
                avg_rating=Avg('rating'), count=Count('id')
            )
            tour.rating_average = stats['avg_rating'] or 5.0
            tour.review_count = stats['count'] or 0
            tour.save(update_fields=['rating_average', 'review_count'])
        
        if hotel:
            stats = Review.objects.filter(hotel=hotel, is_approved=True).aggregate(
                avg_rating=Avg('rating'), count=Count('id')
            )
            hotel.rating_average = stats['avg_rating'] or 5.0
            hotel.review_count = stats['count'] or 0
            hotel.save(update_fields=['rating_average', 'review_count'])
