"""
Reviews App Models: Multi-Target Polymorphic Reviews, Ratings, Media Attachments & Moderation Queue.
"""
from django.db import models
from django.conf import settings
from apps.core.models import AuditableModel, TimeStampedModel
from apps.core.constants import ReviewRating

class Review(AuditableModel):
    """Universal verified reviews for Tour Packages, Hotel Properties, Transports & Destinations."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    
    # Target entities
    tour_package = models.ForeignKey('tours.TourPackage', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    hotel = models.ForeignKey('hotels.HotelProperty', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    destination = models.ForeignKey('destinations.Destination', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    booking = models.ForeignKey('bookings.BookingOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_reviews')
    
    rating = models.PositiveSmallIntegerField(choices=ReviewRating.choices, default=ReviewRating.FIVE)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    is_verified_booking = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating}★ ({self.title})"

class ReviewImage(TimeStampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/photos/%Y/%m/')
    caption = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Image for Review #{self.review.id}"

class ReviewReply(TimeStampedModel):
    """Official reply from Agency, Hotel Manager or Platform Admin."""
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='official_reply')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply_text = models.TextField()

    def __str__(self):
        return f"Reply to {self.review.title} by {self.responder.get_full_name()}"
