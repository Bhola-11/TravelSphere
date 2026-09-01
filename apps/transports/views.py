"""
Transports Views: Search Schedules, Compare Multi-modal Options & Seat Class Selection.
"""
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import TransportSchedule, TransportOperator, StationStop, SeatClass
from .forms import TransportSearchForm
from .services import TransportSearchService

class TransportSearchView(ListView):
    model = TransportSchedule
    template_name = 'transports/transport_list.html'
    context_object_name = 'schedules'
    paginate_by = 10

    def get_queryset(self):
        form = TransportSearchForm(self.request.GET)
        if form.is_valid():
            origin = form.cleaned_data.get('origin_city')
            destination = form.cleaned_data.get('destination_city')
            dep_date = form.cleaned_data.get('departure_date')
            t_type = form.cleaned_data.get('transport_type')

            if origin and destination and dep_date:
                return TransportSearchService.search_trips(
                    origin.id, destination.id, dep_date, t_type
                )
        return TransportSchedule.objects.filter(is_active=True).select_related(
            'route', 'route__operator', 'route__origin_station', 'route__destination_station'
        ).prefetch_related('seat_classes')[:15]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TransportSearchForm(self.request.GET)
        context['operators'] = TransportOperator.objects.all()[:8]
        return context

class TransportScheduleDetailView(DetailView):
    model = TransportSchedule
    template_name = 'transports/transport_detail.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seat_classes'] = self.object.seat_classes.all()
        return context
