"""
Tours Service Layer: Dynamic Pricing, Group Discount Engine, Availability & Slot Locking.
"""
from decimal import Decimal
from django.utils import timezone
from .models import TourPackage, TourDepartureDate, SeasonalSurcharge

class TourPricingService:
    @staticmethod
    def calculate_quote(tour_package: TourPackage, departure_date=None, adults_count=1, children_count=0, single_supplement=False):
        adult_base = tour_package.final_price_adult
        child_base = tour_package.base_price_child

        # Check if departure date has custom override
        if departure_date:
            dep = TourDepartureDate.objects.filter(tour_package=tour_package, departure_date=departure_date).first()
            if dep:
                adult_base = dep.adult_price
                child_base = dep.child_price

            # Check seasonal surcharge
            surcharge = SeasonalSurcharge.objects.filter(
                tour_package=tour_package,
                start_date__lte=departure_date,
                end_date__gte=departure_date
            ).first()
        else:
            surcharge = None

        multiplier = Decimal('1.00')
        fixed_add = Decimal('0.00')
        if surcharge:
            multiplier = surcharge.multiplier
            fixed_add = surcharge.fixed_surcharge

        adult_subtotal = (Decimal(str(adults_count)) * (adult_base * multiplier + fixed_add)).quantize(Decimal('0.01'))
        child_subtotal = (Decimal(str(children_count)) * (child_base * multiplier + fixed_add)).quantize(Decimal('0.01'))
        supplement = tour_package.single_supplement_price if single_supplement else Decimal('0.00')

        # Group Discount Matrix
        total_pax = adults_count + children_count
        group_discount_percent = Decimal('0.00')
        if total_pax >= 10:
            group_discount_percent = Decimal('15.00')
        elif total_pax >= 6:
            group_discount_percent = Decimal('10.00')
        elif total_pax >= 4:
            group_discount_percent = Decimal('5.00')

        gross_total = adult_subtotal + child_subtotal + supplement
        discount_amount = (gross_total * group_discount_percent / Decimal('100.00')).quantize(Decimal('0.01'))
        net_total = gross_total - discount_amount

        return {
            'adult_price_each': (adult_base * multiplier + fixed_add).quantize(Decimal('0.01')),
            'child_price_each': (child_base * multiplier + fixed_add).quantize(Decimal('0.01')),
            'adult_subtotal': adult_subtotal,
            'child_subtotal': child_subtotal,
            'supplement': supplement,
            'group_discount_percent': group_discount_percent,
            'discount_amount': discount_amount,
            'gross_total': gross_total,
            'net_total': net_total,
        }

class TourAvailabilityService:
    @staticmethod
    def check_availability(tour_package_id, departure_date, requested_slots=1):
        if not departure_date:
            return True, "Available"
        dep = TourDepartureDate.objects.filter(tour_package_id=tour_package_id, departure_date=departure_date).first()
        if not dep:
            return False, "Departure date not found or not scheduled."
        if dep.is_sold_out or dep.available_slots < requested_slots:
            return False, f"Only {dep.available_slots} slots available."
        return True, "Available"

    @staticmethod
    def reserve_slots(tour_package_id, departure_date, slots_count=1):
        if not departure_date:
            return True
        dep = TourDepartureDate.objects.filter(tour_package_id=tour_package_id, departure_date=departure_date).first()
        if dep and dep.available_slots >= slots_count:
            dep.booked_slots += slots_count
            if dep.booked_slots >= dep.total_slots:
                dep.is_sold_out = True
            dep.save()
            return True
        return False
