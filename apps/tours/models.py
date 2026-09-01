"""
Tours App Models: Tour Packages, Day-Wise Itineraries, Activities, Pricing Tiers, Guides & Slots.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from apps.core.models import AuditableModel, SluggedModel, TimeStampedModel
from apps.destinations.models import Destination

class TourCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, default='bi-compass')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Tour Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TourGuide(AuditableModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tour_guide_profile')
    languages_spoken = models.CharField(max_length=255, help_text="Comma-separated languages, e.g., English, Spanish, French")
    experience_years = models.PositiveIntegerField(default=3)
    license_number = models.CharField(max_length=100, blank=True)
    bio = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    def __str__(self):
        return f"Guide: {self.user.get_full_name()} ({self.experience_years} yrs)"

class TourPackage(AuditableModel, SluggedModel):
    """Core multi-day or single-day curated tour package."""
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='tour_packages')
    category = models.ForeignKey(TourCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='packages')
    agency = models.ForeignKey('accounts.TravelSphereUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_packages')
    assigned_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, null=True, blank=True, related_name='tours')
    
    code = models.CharField(max_length=30, unique=True, help_text="Unique SKU code, e.g. TSP-EUR-001")
    subtitle = models.CharField(max_length=255)
    summary = models.TextField()
    
    # Timing & Group
    duration_days = models.PositiveIntegerField(default=3)
    duration_nights = models.PositiveIntegerField(default=2)
    min_group_size = models.PositiveIntegerField(default=1)
    max_group_size = models.PositiveIntegerField(default=20)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('EASY', 'Easy / Leisure'),
        ('MODERATE', 'Moderate Walking'),
        ('STRENUOUS', 'Strenuous / Trekking'),
        ('EXTREME', 'Extreme Adventure'),
    ], default='EASY')
    
    # Pricing Baseline
    base_price_adult = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('199.00'))
    base_price_child = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('99.00'))
    single_supplement_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Flags & Stats
    featured_image = models.ImageField(upload_to='tours/featured/%Y/%m/', null=True, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_all_inclusive = models.BooleanField(default=False)
    instant_confirmation = models.BooleanField(default=True)
    cancellation_policy = models.TextField(default="Full refund up to 7 days before departure. 50% refund up to 48 hours.")
    
    view_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_featured', '-booking_count', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.duration_days}D/{self.duration_nights}N) - ${self.base_price_adult}"

    @property
    def final_price_adult(self):
        if self.discount_percentage > 0:
            discount = (self.base_price_adult * self.discount_percentage) / Decimal('100.00')
            return (self.base_price_adult - discount).quantize(Decimal('0.01'))
        return self.base_price_adult

class DayItinerary(TimeStampedModel):
    """Day-by-day sequence of a tour package."""
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='itinerary_days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    meals_included = models.CharField(max_length=100, default='Breakfast', help_text="e.g. Breakfast, Lunch, Dinner")
    accommodation = models.CharField(max_length=200, blank=True, help_text="Hotel / Resort name or type")
    overnight_city = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['day_number']
        unique_together = ('tour_package', 'day_number')

    def __str__(self):
        return f"Day {self.day_number}: {self.title} ({self.tour_package.title})"

class ItineraryActivity(TimeStampedModel):
    """Granular time-slot activity within a day itinerary."""
    day_itinerary = models.ForeignKey(DayItinerary, on_delete=models.CASCADE, related_name='activities')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location_name = models.CharField(max_length=200, blank=True)
    is_optional = models.BooleanField(default=False)
    extra_cost = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['start_time', 'id']

    def __str__(self):
        return f"{self.title} (Day {self.day_itinerary.day_number})"

class TourInclusionExclusion(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='inclusions_exclusions')
    item_text = models.CharField(max_length=255)
    is_included = models.BooleanField(default=True, help_text="True for Included, False for Excluded")

    def __str__(self):
        prefix = "[+] Included" if self.is_included else "[-] Excluded"
        return f"{prefix}: {self.item_text}"

class TourDepartureDate(TimeStampedModel):
    """Scheduled departure batches and available seat allocations."""
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='departures')
    departure_date = models.DateField(db_index=True)
    return_date = models.DateField()
    total_slots = models.PositiveIntegerField(default=20)
    booked_slots = models.PositiveIntegerField(default=0)
    adult_price = models.DecimalField(max_digits=10, decimal_places=2)
    child_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_guaranteed_departure = models.BooleanField(default=True)
    is_sold_out = models.BooleanField(default=False)

    class Meta:
        ordering = ['departure_date']
        unique_together = ('tour_package', 'departure_date')

    @property
    def available_slots(self):
        return max(0, self.total_slots - self.booked_slots)

    def __str__(self):
        return f"{self.tour_package.title} - {self.departure_date} ({self.available_slots} left)"

class SeasonalSurcharge(TimeStampedModel):
    """Seasonal price adjustment rules (Peak season, Holiday surge)."""
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='seasonal_surcharges')
    name = models.CharField(max_length=100, help_text="e.g. Summer High Season, Christmas Surcharge")
    start_date = models.DateField()
    end_date = models.DateField()
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.15'), help_text="e.g. 1.20 for 20% surge")
    fixed_surcharge = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date}) - {self.multiplier}x"

class TourPackingItem(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='packing_list')
    category = models.CharField(max_length=50, default='General', choices=[
        ('CLOTHING', 'Clothing & Footwear'),
        ('DOCUMENTS', 'Travel Documents & ID'),
        ('GEAR', 'Trekking / Sports Gear'),
        ('MEDICATION', 'Health & Medication'),
        ('ELECTRONICS', 'Electronics & Adapters'),
    ])
    item_name = models.CharField(max_length=150)
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item_name} ({self.category})"

class TourFAQ(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.question
