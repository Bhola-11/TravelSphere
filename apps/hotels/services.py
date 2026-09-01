"""
Hotels Service Layer: Availability Calendar, Multi-night Price Computation & Room Locks.
"""
from decimal import Decimal
from datetime import timedelta, date
from django.db.models import Q
from .models import HotelProperty, RoomType, RoomInventory

class HotelAvailabilityService:
    @staticmethod
    def calculate_stay_quote(room_type: RoomType, check_in: date, check_out: date, rooms_requested=1):
        if check_out <= check_in:
            return None
        
        num_nights = (check_out - check_in).days
        current_dt = check_in
        nightly_breakdown = []
        total_price = Decimal('0.00')

        while current_dt < check_out:
            inv = RoomInventory.objects.filter(room_type=room_type, date=current_dt).first()
            if inv:
                if inv.remaining_rooms < rooms_requested or inv.is_blocked:
                    return {'is_available': False, 'message': f'Sold out on {current_dt}'}
                price_for_night = inv.current_price
            else:
                price_for_night = room_type.base_price_per_night
                if current_dt.weekday() in [4, 5]:  # Friday & Saturday
                    price_for_night *= (Decimal('1.00') + (room_type.weekend_surcharge_percent / Decimal('100.00')))

            total_price += (price_for_night * Decimal(str(rooms_requested)))
            nightly_breakdown.append({
                'date': current_dt.strftime('%Y-%m-%d'),
                'price': price_for_night.quantize(Decimal('0.01'))
            })
            current_dt += timedelta(days=1)

        return {
            'is_available': True,
            'num_nights': num_nights,
            'rooms_requested': rooms_requested,
            'total_price': total_price.quantize(Decimal('0.01')),
            'average_nightly_price': (total_price / Decimal(str(num_nights))).quantize(Decimal('0.01')),
            'nightly_breakdown': nightly_breakdown
        }

    @staticmethod
    def reserve_room_inventory(room_type: RoomType, check_in: date, check_out: date, rooms_count=1):
        current_dt = check_in
        while current_dt < check_out:
            inv, created = RoomInventory.objects.get_or_create(
                room_type=room_type,
                date=current_dt,
                defaults={'available_rooms': room_type.total_rooms_count, 'booked_rooms': 0}
            )
            inv.booked_rooms += rooms_count
            inv.save()
            current_dt += timedelta(days=1)
        return True
