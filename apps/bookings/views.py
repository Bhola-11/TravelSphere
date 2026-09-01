"""
Bookings Views: Cart Manager, Multi-Step Checkout, Itinerary Snapshot, Order Confirmation & Booking History.
"""
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Cart, CartItem, BookingOrder, BookingLineItem, PassengerDetail
from .services import CartService, BookingOrderService
from .forms import CheckoutBillingForm, PassengerDetailForm
from apps.tours.models import TourPackage
from apps.hotels.models import RoomType
from apps.transports.models import TransportSchedule, SeatClass

class CartView(View):
    template_name = 'bookings/cart.html'

    def get(self, request):
        cart = CartService.get_or_create_cart(request)
        return render(request, self.template_name, {'cart': cart})

class AddTourToCartView(View):
    def post(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        dep_date_str = request.POST.get('departure_date')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))

        try:
            dep_date = datetime.strptime(dep_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Please select a valid departure date.')
            return redirect('tours:detail', slug=tour.slug)

        cart = CartService.get_or_create_cart(request)
        CartService.add_tour_to_cart(cart, tour, dep_date, adults, children)
        messages.success(request, f'"{tour.title}" has been added to your travel cart!')
        return redirect('bookings:cart')

class AddHotelToCartView(View):
    def post(self, request, pk):
        room = get_object_or_404(RoomType, pk=pk)
        cin_str = request.POST.get('check_in')
        cout_str = request.POST.get('check_out')
        rooms = int(request.POST.get('rooms', 1))

        try:
            check_in = datetime.strptime(cin_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(cout_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Invalid check-in or check-out date.')
            return redirect('hotels:detail', slug=room.hotel.slug)

        cart = CartService.get_or_create_cart(request)
        item, msg = CartService.add_hotel_to_cart(cart, room, check_in, check_out, rooms)
        if item:
            messages.success(request, f'{room.name} at {room.hotel.title} added to cart!')
        else:
            messages.error(request, msg)
        return redirect('bookings:cart')

class AddTransportToCartView(View):
    def post(self, request, pk):
        schedule = get_object_or_404(TransportSchedule, pk=pk)
        seat_class_id = request.POST.get('seat_class_id')
        seats_count = int(request.POST.get('seats_count', 1))
        seat_class = get_object_or_404(SeatClass, id=seat_class_id, schedule=schedule)

        cart = CartService.get_or_create_cart(request)
        item, msg = CartService.add_transport_to_cart(cart, schedule, seat_class, seats_count)
        if item:
            messages.success(request, f'Transport ticket for {schedule.route.route_code} added to cart!')
        else:
            messages.error(request, msg)
        return redirect('bookings:cart')

class RemoveCartItemView(View):
    def post(self, request, pk):
        cart = CartService.get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        messages.info(request, "Item removed from cart.")
        return redirect('bookings:cart')

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'bookings/checkout.html'

    def get(self, request):
        cart = CartService.get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect('bookings:cart')

        initial_data = {
            'name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': getattr(request.user, 'phone_number', ''),
        }
        form = CheckoutBillingForm(initial=initial_data)
        return render(request, self.template_name, {'cart': cart, 'form': form})

    def post(self, request):
        cart = CartService.get_or_create_cart(request)
        form = CheckoutBillingForm(request.POST)
        if form.is_valid():
            order, msg = BookingOrderService.create_order_from_cart(cart, request.user, form.cleaned_data)
            if order:
                return redirect('payments:initiate', order_id=order.id)
            messages.error(request, msg)
        return render(request, self.template_name, {'cart': cart, 'form': form})

class BookingConfirmationView(LoginRequiredMixin, DetailView):
    model = BookingOrder
    template_name = 'bookings/booking_confirmation.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return BookingOrder.objects.filter(customer=self.request.user)

class BookingHistoryListView(LoginRequiredMixin, ListView):
    model = BookingOrder
    template_name = 'bookings/booking_history.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return BookingOrder.objects.filter(customer=self.request.user).order_by('-created_at')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = BookingOrder
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        if self.request.user.is_staff:
            return BookingOrder.objects.all()
        return BookingOrder.objects.filter(customer=self.request.user)
