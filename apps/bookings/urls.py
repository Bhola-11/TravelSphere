from django.urls import path
from .views import (
    CartView, AddTourToCartView, AddHotelToCartView, AddTransportToCartView,
    RemoveCartItemView, CheckoutView, BookingConfirmationView,
    BookingHistoryListView, BookingDetailView
)

app_name = 'bookings'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add-tour/<int:pk>/', AddTourToCartView.as_view(), name='add_tour'),
    path('cart/add-hotel/<int:pk>/', AddHotelToCartView.as_view(), name='add_hotel'),
    path('cart/add-transport/<int:pk>/', AddTransportToCartView.as_view(), name='add_transport'),
    path('cart/remove/<int:pk>/', RemoveCartItemView.as_view(), name='remove_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('confirmation/<uuid:pk>/', BookingConfirmationView.as_view(), name='confirmation'),
    path('history/', BookingHistoryListView.as_view(), name='history'),
    path('<uuid:pk>/', BookingDetailView.as_view(), name='detail'),
]
