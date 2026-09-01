"""
Bookings Service Layer: Cart Operations, Order Creation, Inventory Reservation & State Machine.
"""
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import Cart, CartItem, BookingOrder, BookingLineItem, BookingStatusHistory, BookingVoucher
from apps.core.constants import BookingStatus
from apps.payments.services import TaxCalculationEngine

class CartService:
    @staticmethod
    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            session_key = getattr(request.session, 'session_key', None)
            if session_key:
                anon_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
                if anon_cart:
                    for item in anon_cart.items.all():
                        item.cart = cart
                        item.save()
                    anon_cart.delete()
            return cart
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user__isnull=True)
            return cart

    @staticmethod
    def add_tour_to_cart(cart, tour_package, departure_date=None, adults=1, children=0):
        from apps.tours.services import TourPricingService
        quote = TourPricingService.calculate_quote(tour_package, departure_date, adults, children)
        item = CartItem.objects.create(
            cart=cart,
            item_type='TOUR',
            tour_package=tour_package,
            start_date=departure_date,
            adults_count=adults,
            children_count=children,
            quantity=1,
            unit_price=quote['net_total'],
            metadata={'quote': {k: str(v) for k, v in quote.items()}}
        )
        return item

    @staticmethod
    def add_hotel_to_cart(cart, room_type, check_in, check_out, rooms=1):
        from apps.hotels.services import HotelAvailabilityService
        quote = HotelAvailabilityService.calculate_stay_quote(room_type, check_in, check_out, rooms)
        if not quote or not quote['is_available']:
            return None, "Room not available for requested dates."
        
        item = CartItem.objects.create(
            cart=cart,
            item_type='HOTEL',
            room_type=room_type,
            start_date=check_in,
            end_date=check_out,
            quantity=rooms,
            unit_price=quote['total_price'],
            metadata={'num_nights': quote['num_nights']}
        )
        return item, "Added successfully"

    @staticmethod
    def add_transport_to_cart(cart, schedule, seat_class, seats_count=1):
        if seat_class.available_seats < seats_count:
            return None, "Not enough seats available."
        
        item = CartItem.objects.create(
            cart=cart,
            item_type='TRANSPORT',
            transport_schedule=schedule,
            seat_class=seat_class,
            start_date=schedule.departure_time.date(),
            quantity=seats_count,
            unit_price=seat_class.base_price * Decimal(str(seats_count)),
            metadata={'class_name': seat_class.get_class_type_display()}
        )
        return item, "Added successfully"

class BookingOrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart: Cart, user, billing_data: dict):
        if not cart.items.exists():
            return None, "Cart is empty"

        subtotal = cart.subtotal
        taxes = TaxCalculationEngine.calculate_taxes(subtotal)
        tax_total = taxes['tax_amount']
        total = subtotal + tax_total

        order = BookingOrder.objects.create(
            customer=user,
            status=BookingStatus.PENDING_PAYMENT,
            currency='USD',
            subtotal_amount=subtotal,
            tax_amount=tax_total,
            discount_amount=Decimal('0.00'),
            total_amount=total,
            billing_name=billing_data.get('name', user.get_full_name()),
            billing_email=billing_data.get('email', user.email),
            billing_phone=billing_data.get('phone', getattr(user, 'phone_number', '') or ''),
            billing_address=billing_data.get('address', ''),
            special_requests=billing_data.get('special_requests', '')
        )

        for item in cart.items.all():
            title = "Travel Item"
            if item.tour_package:
                title = f"Tour: {item.tour_package.title}"
            elif item.room_type:
                title = f"Hotel Stay: {item.room_type.hotel.title} ({item.room_type.name})"
            elif item.transport_schedule:
                title = f"Transport: {item.transport_schedule.route.route_code}"

            BookingLineItem.objects.create(
                booking=order,
                item_type=item.item_type,
                title=title,
                tour_package=item.tour_package,
                room_type=item.room_type,
                transport_schedule=item.transport_schedule,
                seat_class=item.seat_class,
                start_date=item.start_date,
                end_date=item.end_date,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.subtotal,
                snapshot_data=item.metadata
            )

        BookingStatusHistory.objects.create(
            booking=order,
            old_status='NONE',
            new_status=BookingStatus.PENDING_PAYMENT,
            changed_by=user,
            notes="Order initialized from shopping cart."
        )

        # Clear cart
        cart.items.all().delete()
        return order, "Order created successfully"
