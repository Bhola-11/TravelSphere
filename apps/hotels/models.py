"""
Hotels App Models: Properties, Room Types, Dynamic Tariffs, Room Inventory & Amenities.
"""
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from apps.core.models import AuditableModel, SluggedModel, TimeStampedModel
from apps.destinations.models import City, Destination
from apps.core.constants import RoomCategoryEnum

class Amenity(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, default='bi-check-circle', help_text="Bootstrap Icon class, e.g. bi-wifi, bi-water")
    category = models.CharField(max_length=50, default='GENERAL', choices=[
        ('GENERAL', 'General Services'),
        ('WELLNESS', 'Spa & Wellness'),
        ('FOOD', 'Dining & Drinks'),
        ('ROOM', 'In-Room Perks'),
        ('BUSINESS', 'Business & Events'),
    ])

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name

class HotelChain(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    logo = models.ImageField(upload_to='hotels/chains/', null=True, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name

class HotelProperty(AuditableModel, SluggedModel):
    """Hotel, Resort, Villa, Boutique Stay, or Chalet property."""
    chain = models.ForeignKey(HotelChain, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='hotels')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hotels')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_hotels')
    
    star_rating = models.PositiveSmallIntegerField(default=4, choices=[(i, f"{i} Stars") for i in range(1, 6)])
    property_type = models.CharField(max_length=50, default='HOTEL', choices=[
        ('HOTEL', 'Luxury Hotel'),
        ('RESORT', 'Beach / Mountain Resort'),
        ('BOUTIQUE', 'Boutique Heritage Inn'),
        ('VILLA', 'Private Villa Estate'),
        ('APARTMENT', 'Serviced Apartment'),
    ])
    
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=30, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    overview = models.TextField()
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='hotels')
    
    check_in_time = models.TimeField(default='14:00:00')
    check_out_time = models.TimeField(default='11:00:00')
    cancellation_policy = models.TextField(default="Free cancellation up to 48 hours before check-in.")
    
    cover_image = models.ImageField(upload_to='hotels/properties/%Y/%m/', null=True, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=4.80)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Hotel Properties"
        ordering = ['-is_featured', '-rating_average', 'title']

    def __str__(self):
        return f"{self.title} ({self.star_rating}★, {self.city.name})"

class HotelImage(TimeStampedModel):
    hotel = models.ForeignKey(HotelProperty, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='hotels/gallery/%Y/%m/')
    caption = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.hotel.title}"

class RoomType(AuditableModel):
    """Specific room classification (e.g. Deluxe Ocean View Suite)."""
    hotel = models.ForeignKey(HotelProperty, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=RoomCategoryEnum.choices, default=RoomCategoryEnum.DELUXE)
    description = models.TextField(blank=True)
    
    max_adults = models.PositiveIntegerField(default=2)
    max_children = models.PositiveIntegerField(default=1)
    bed_type = models.CharField(max_length=100, default='1 King Bed or 2 Twin Beds')
    room_size_sqm = models.PositiveIntegerField(default=35)
    
    base_price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('120.00'))
    weekend_surcharge_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    total_rooms_count = models.PositiveIntegerField(default=10)
    
    image = models.ImageField(upload_to='hotels/rooms/%Y/%m/', null=True, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='room_types')

    def __str__(self):
        return f"{self.name} - {self.hotel.title} (${self.base_price_per_night}/night)"

class RoomInventory(TimeStampedModel):
    """Date-wise room availability & dynamic override tariffs."""
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='inventory_records')
    date = models.DateField(db_index=True)
    available_rooms = models.PositiveIntegerField()
    booked_rooms = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room_type', 'date')
        verbose_name_plural = "Room Inventories"
        ordering = ['date']

    @property
    def current_price(self):
        if self.price_override is not None:
            return self.price_override
        return self.room_type.base_price_per_night

    @property
    def remaining_rooms(self):
        if self.is_blocked:
            return 0
        return max(0, self.available_rooms - self.booked_rooms)

    def __str__(self):
        return f"{self.room_type.name} on {self.date}: {self.remaining_rooms} remaining"

class HotelMealPlan(models.Model):
    hotel = models.ForeignKey(HotelProperty, on_delete=models.CASCADE, related_name='meal_plans')
    code = models.CharField(max_length=20, choices=[
        ('RO', 'Room Only / European Plan'),
        ('BB', 'Bed & Breakfast (Continental)'),
        ('HB', 'Half Board (Breakfast + Dinner)'),
        ('FB', 'Full Board (All 3 Meals)'),
        ('AI', 'All Inclusive (Unlimited Meals & Drinks)'),
    ])
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('25.00'))

    def __str__(self):
        return f"{self.get_code_display()} (+${self.price_per_person}/pax)"
