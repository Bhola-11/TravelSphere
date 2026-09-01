"""
Destinations App Models: Geographic Entities, Continents, Countries, Cities, Destinations, POIs & Advisories.
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from apps.core.models import AuditableModel, SluggedModel, TimeStampedModel

class Continent(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='continents/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Country(TimeStampedModel):
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name='countries')
    name = models.CharField(max_length=150, unique=True)
    iso2 = models.CharField(max_length=2, unique=True)
    iso3 = models.CharField(max_length=3, blank=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    capital = models.CharField(max_length=100, blank=True)
    currency_code = models.CharField(max_length=3, default='USD')
    dial_code = models.CharField(max_length=10, blank=True)
    visa_requirements = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='countries/', null=True, blank=True)
    flag_image = models.ImageField(upload_to='countries/flags/', null=True, blank=True)
    is_popular = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.iso2})"

class StateProvince(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('country', 'name')

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class City(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    state = models.ForeignKey(StateProvince, on_delete=models.SET_NULL, null=True, blank=True, related_name='cities')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_airport_hub = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ('country', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.country.iso2}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class DestinationCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, default='bi-compass')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Destination Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class DestinationTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.name}"

class Destination(AuditableModel, SluggedModel):
    """Core Destination entity representing a holiday hotspot, island, mountain resort, or historic city."""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='destinations')
    category = models.ForeignKey(DestinationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='destinations')
    tags = models.ManyToManyField(DestinationTag, blank=True, related_name='destinations')
    
    tagline = models.CharField(max_length=255)
    overview = models.TextField()
    highlights = models.TextField(help_text="Line-separated key highlights")
    best_time_to_visit = models.CharField(max_length=200, help_text="e.g. October to April")
    ideal_duration_days = models.PositiveIntegerField(default=5)
    
    # Geography & Logistics
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    climate_type = models.CharField(max_length=100, blank=True, help_text="e.g. Tropical, Alpine, Mediterranean")
    average_temperature_celsius = models.IntegerField(null=True, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to='destinations/%Y/%m/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='destinations/banners/%Y/%m/', null=True, blank=True)
    
    # Metrics
    is_featured = models.BooleanField(default=False, db_index=True)
    view_count = models.PositiveIntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_featured', '-view_count', 'title']

    def __str__(self):
        return f"{self.title} ({self.city.name}, {self.city.country.name})"

    @property
    def highlights_list(self):
        if not self.highlights:
            return []
        return [h.strip() for h in self.highlights.split('\n') if h.strip()]

class DestinationImage(TimeStampedModel):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='destinations/gallery/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Gallery for {self.destination.title}"

class PointOfInterest(AuditableModel, SluggedModel):
    """Specific tourist attraction, monument, landmark, beach or viewpoint."""
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='points_of_interest')
    poi_type = models.CharField(max_length=50, choices=[
        ('MONUMENT', 'Historical Monument'),
        ('BEACH', 'Beach / Coastal Point'),
        ('MUSEUM', 'Museum / Art Gallery'),
        ('NATURE', 'National Park / Nature Trail'),
        ('TEMPLE', 'Religious / Spiritual Site'),
        ('ADVENTURE', 'Adventure / Theme Park'),
        ('VIEWPOINT', 'Panoramic Viewpoint'),
    ])
    description = models.TextField()
    entry_fee_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    recommended_time_hours = models.DecimalField(max_digits=4, decimal_places=1, default=2.0)
    opening_hours = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='pois/%Y/%m/', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.destination.title}"

class TravelAdvisory(TimeStampedModel):
    """Safety alerts, weather warnings, entry rules, or visa notifications."""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='advisories')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='advisories')
    severity = models.CharField(max_length=20, choices=[
        ('INFO', 'General Travel Info'),
        ('WARNING', 'Advisory Warning'),
        ('CRITICAL', 'Urgent / High Risk'),
    ], default='INFO')
    headline = models.CharField(max_length=255)
    details = models.TextField()
    is_active = models.BooleanField(default=True)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Travel Advisories"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.headline} ({self.country.name})"

class ClimateMonthlyData(models.Model):
    """Month-by-month climate patterns for intelligent travel recommendations."""
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='climate_data')
    month = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 13)])
    avg_temp_c = models.DecimalField(max_digits=4, decimal_places=1)
    rainfall_mm = models.DecimalField(max_digits=6, decimal_places=1)
    sunlight_hours = models.DecimalField(max_digits=4, decimal_places=1)
    is_peak_season = models.BooleanField(default=False)

    class Meta:
        unique_together = ('destination', 'month')
        ordering = ['month']

    def __str__(self):
        return f"Month {self.month} for {self.destination.title}"
