"""
Transports Service Layer: Route Search, Multi-modal Trip Finder & Seat Allocation.
"""
from django.db.models import Q
from .models import TransportSchedule, SeatClass, StationStop
from apps.core.constants import TransportTypeEnum

class TransportSearchService:
    @staticmethod
    def search_trips(origin_city_id, destination_city_id, departure_date, transport_type=None):
        qs = TransportSchedule.objects.filter(
            is_active=True,
            route__origin_station__city_id=origin_city_id,
            route__destination_station__city_id=destination_city_id,
            departure_time__date=departure_date
        ).select_related(
            'route', 'route__operator', 'route__origin_station', 'route__destination_station'
        ).prefetch_related('seat_classes')

        if transport_type:
            qs = qs.filter(route__operator__transport_type=transport_type)

        return qs

    @staticmethod
    def book_seats(seat_class_id, seats_count=1):
        sc = SeatClass.objects.filter(id=seat_class_id).first()
        if sc and sc.available_seats >= seats_count:
            sc.booked_count += seats_count
            sc.save()
            return True
        return False
