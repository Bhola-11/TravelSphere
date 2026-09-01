"""
Hotels Views: Hotel Directory, Property Showcase, Room Selection & Price Calculator AJAX.
"""
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.db.models import Q
from .models import HotelProperty, RoomType, Amenity
from .forms import HotelSearchForm
from .services import HotelAvailabilityService

class HotelListView(ListView):
    model = HotelProperty
    template_name = 'hotels/hotel_list.html'
    context_object_name = 'hotels'
    paginate_by = 9

    def get_queryset(self):
        qs = HotelProperty.objects.filter(is_active=True).select_related('city', 'city__country', 'chain').prefetch_related('amenities')
        form = HotelSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            city = form.cleaned_data.get('city')
            stars = form.cleaned_data.get('min_stars')
            p_type = form.cleaned_data.get('property_type')

            if q:
                qs = qs.filter(Q(title__icontains=q) | Q(overview__icontains=q) | Q(city__name__icontains=q))
            if city:
                qs = qs.filter(city=city)
            if stars:
                qs = qs.filter(star_rating__gte=int(stars))
            if p_type:
                qs = qs.filter(property_type=p_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = HotelSearchForm(self.request.GET)
        context['amenities'] = Amenity.objects.all()[:12]
        return context

class HotelDetailView(DetailView):
    model = HotelProperty
    template_name = 'hotels/hotel_detail.html'
    context_object_name = 'hotel'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = self.object
        context['room_types'] = hotel.room_types.filter(is_active=True).prefetch_related('amenities')
        context['gallery'] = hotel.gallery_images.all()
        context['meal_plans'] = hotel.meal_plans.all()
        context['amenities_list'] = hotel.amenities.all()
        context['default_checkin'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        context['default_checkout'] = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
        return context

class RoomQuoteAjaxView(View):
    def get(self, request, pk):
        room = get_object_or_404(RoomType, pk=pk)
        cin_str = request.GET.get('check_in')
        cout_str = request.GET.get('check_out')
        rooms_count = int(request.GET.get('rooms', 1))

        try:
            check_in = datetime.strptime(cin_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(cout_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid dates provided'}, status=400)

        quote = HotelAvailabilityService.calculate_stay_quote(room, check_in, check_out, rooms_count)
        return JsonResponse(quote)
