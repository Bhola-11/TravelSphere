"""
Destinations Views: Explorer, City Hubs, Detail, POI Directory & Advisories.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import F
from .models import Destination, PointOfInterest, Continent, Country, TravelAdvisory, DestinationCategory
from .forms import DestinationFilterForm
from .services import DestinationService

class DestinationListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    context_object_name = 'destinations'
    paginate_by = 12

    def get_queryset(self):
        form = DestinationFilterForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            continent = form.cleaned_data.get('continent')
            country = form.cleaned_data.get('country')
            category = form.cleaned_data.get('category')
            duration = form.cleaned_data.get('duration')
            return DestinationService.search_destinations(
                query=q,
                continent_id=continent.id if continent else None,
                country_id=country.id if country else None,
                category_id=category.id if category else None,
                max_duration=duration
            )
        return Destination.objects.filter(is_active=True).select_related('city', 'city__country', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DestinationFilterForm(self.request.GET)
        context['categories'] = DestinationCategory.objects.all()
        context['featured_continents'] = Continent.objects.all()
        return context

class DestinationDetailView(DetailView):
    model = Destination
    template_name = 'destinations/destination_detail.html'
    context_object_name = 'destination'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Destination.objects.filter(pk=obj.pk).update(view_count=F('view_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dest = self.object
        context['pois'] = dest.points_of_interest.filter(is_active=True)
        context['gallery'] = dest.gallery_images.all()
        context['climate_data'] = dest.climate_data.all()
        context['advisories'] = TravelAdvisory.objects.filter(
            country=dest.city.country, is_active=True
        )
        # Related Tour Packages
        try:
            from apps.tours.models import TourPackage
            context['tours'] = TourPackage.objects.filter(destination=dest, is_active=True)[:4]
        except Exception:
            context['tours'] = []
        return context

class ContinentExplorerView(DetailView):
    model = Continent
    template_name = 'destinations/continent_detail.html'
    context_object_name = 'continent'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = self.object.countries.all()
        context['destinations'] = Destination.objects.filter(city__country__continent=self.object, is_active=True)[:9]
        return context

class CountryDetailView(DetailView):
    model = Country
    template_name = 'destinations/country_detail.html'
    context_object_name = 'country'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destination.objects.filter(city__country=self.object, is_active=True)
        context['advisories'] = self.object.advisories.filter(is_active=True)
        return context

class POIDetailView(DetailView):
    model = PointOfInterest
    template_name = 'destinations/poi_detail.html'
    context_object_name = 'poi'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
