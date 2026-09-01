"""
Tours Views: Tour Directory, Tour Detail, Interactive Day-by-Day Itinerary, Slot Quotes.
"""
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.db.models import Q, F
from .models import TourPackage, TourCategory, TourDepartureDate, DayItinerary
from .forms import TourSearchFilterForm
from .services import TourPricingService, TourAvailabilityService
from apps.destinations.models import Destination

class TourPackageListView(ListView):
    model = TourPackage
    template_name = 'tours/tour_list.html'
    context_object_name = 'tours'
    paginate_by = 9

    def get_queryset(self):
        qs = TourPackage.objects.filter(is_active=True).select_related('destination', 'category', 'destination__city__country')
        form = TourSearchFilterForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            dest = form.cleaned_data.get('destination')
            cat = form.cleaned_data.get('category')
            min_d = form.cleaned_data.get('min_days')
            max_d = form.cleaned_data.get('max_days')
            max_p = form.cleaned_data.get('max_price')
            diff = form.cleaned_data.get('difficulty')

            if q:
                qs = qs.filter(
                    Q(title__icontains=q) |
                    Q(subtitle__icontains=q) |
                    Q(summary__icontains=q) |
                    Q(destination__title__icontains=q)
                )
            if dest:
                qs = qs.filter(destination=dest)
            if cat:
                qs = qs.filter(category=cat)
            if min_d:
                qs = qs.filter(duration_days__gte=min_d)
            if max_d:
                qs = qs.filter(duration_days__lte=max_d)
            if max_p:
                qs = qs.filter(base_price_adult__lte=max_p)
            if diff:
                qs = qs.filter(difficulty_level=diff)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TourSearchFilterForm(self.request.GET)
        context['categories'] = TourCategory.objects.all()
        return context

class TourPackageDetailView(DetailView):
    model = TourPackage
    template_name = 'tours/tour_detail.html'
    context_object_name = 'tour'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        TourPackage.objects.filter(pk=obj.pk).update(view_count=F('view_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour = self.object
        context['itinerary_days'] = tour.itinerary_days.prefetch_related('activities').all()
        context['inclusions'] = tour.inclusions_exclusions.filter(is_included=True)
        context['exclusions'] = tour.inclusions_exclusions.filter(is_included=False)
        context['departures'] = tour.departures.filter(is_sold_out=False).order_by('departure_date')[:8]
        context['faqs'] = tour.faqs.all()
        context['packing_list'] = tour.packing_list.all()
        context['similar_tours'] = TourPackage.objects.filter(
            destination=tour.destination, is_active=True
        ).exclude(id=tour.id)[:3]
        return context

class TourQuoteAjaxView(View):
    def get(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        dep_date_str = request.GET.get('departure_date')
        adults = int(request.GET.get('adults', 1))
        children = int(request.GET.get('children', 0))
        supplement = request.GET.get('single_supplement') == 'true'

        from datetime import datetime
        try:
            dep_date = datetime.strptime(dep_date_str, '%Y-%m-%d').date() if dep_date_str else None
        except ValueError:
            dep_date = None

        quote = TourPricingService.calculate_quote(tour, dep_date, adults, children, supplement)
        return JsonResponse(quote)
