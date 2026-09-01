from django.contrib import admin
from .models import (
    Continent, Country, StateProvince, City, DestinationCategory,
    DestinationTag, Destination, DestinationImage, PointOfInterest,
    TravelAdvisory, ClimateMonthlyData
)

class DestinationImageInline(admin.TabularInline):
    model = DestinationImage
    extra = 2

class PointOfInterestInline(admin.StackedInline):
    model = PointOfInterest
    extra = 1

class ClimateMonthlyDataInline(admin.TabularInline):
    model = ClimateMonthlyData
    extra = 0

@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'continent', 'iso2', 'capital', 'currency_code', 'is_popular')
    list_filter = ('continent', 'is_popular')
    search_fields = ('name', 'iso2', 'capital')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'state', 'timezone', 'is_airport_hub')
    list_filter = ('country', 'is_airport_hub')
    search_fields = ('name', 'country__name')

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'category', 'ideal_duration_days', 'is_featured', 'rating_average', 'view_count', 'is_active')
    list_filter = ('is_featured', 'is_active', 'category', 'city__country')
    search_fields = ('title', 'city__name', 'overview')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DestinationImageInline, PointOfInterestInline, ClimateMonthlyDataInline]

@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'poi_type', 'entry_fee_usd', 'recommended_time_hours')
    list_filter = ('poi_type', 'destination__city__country')
    search_fields = ('title', 'destination__title')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(TravelAdvisory)
class TravelAdvisoryAdmin(admin.ModelAdmin):
    list_display = ('headline', 'country', 'severity', 'is_active', 'valid_until')
    list_filter = ('severity', 'is_active')
    search_fields = ('headline', 'country__name')

@admin.register(DestinationCategory)
class DestinationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_class')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(DestinationTag)
