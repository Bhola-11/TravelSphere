"""
Comprehensive Test Suites for TravelSphere Enterprise Platform.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.core.models import SystemConfiguration, CurrencyExchangeRate
from apps.core.services import CurrencyService
from apps.destinations.models import Continent, Country, City, Destination
from apps.tours.models import TourCategory, TourPackage
from apps.tours.services import TourPricingService
from apps.bookings.models import Cart, CartItem, BookingOrder
from apps.bookings.services import CartService, BookingOrderService
from apps.payments.models import Coupon
from apps.payments.services import TaxCalculationEngine

User = get_user_model()

class TravelSphereCoreTests(TestCase):
    def setUp(self):
        self.config = SystemConfiguration.get_settings()
        CurrencyExchangeRate.objects.create(base_currency='USD', target_currency='EUR', rate=Decimal('0.92'))

    def test_currency_conversion(self):
        converted = CurrencyService.convert_amount(Decimal('100.00'), 'USD', 'EUR')
        self.assertEqual(converted, Decimal('92.00'))

    def test_home_page_status(self):
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class TourPricingAndCartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@travelsphere.com', password='TestPassword123!', first_name='Test', last_name='User')
        self.continent = Continent.objects.create(name='Europe', code='EU')
        self.country = Country.objects.create(continent=self.continent, name='France', iso2='FR')
        self.city = City.objects.create(country=self.country, name='Paris')
        self.dest = Destination.objects.create(title='Paris Tour', city=self.city, ideal_duration_days=5)
        self.tour = TourPackage.objects.create(
            code='TSP-001',
            title='Paris Tour Package',
            destination=self.dest,
            base_price_adult=Decimal('1000.00'),
            base_price_child=Decimal('500.00')
        )

    def test_tour_pricing_calculation(self):
        quote = TourPricingService.calculate_quote(self.tour, None, adults_count=2, children_count=1)
        # 2 * 1000 + 1 * 500 = 2500
        self.assertEqual(quote['gross_total'], Decimal('2500.00'))

    def test_cart_and_order_flow(self):
        cart = Cart.objects.create(user=self.user)
        CartService.add_tour_to_cart(cart, self.tour, None, adults=2, children=0)
        self.assertEqual(cart.total_items_count, 1)
        
        order, msg = BookingOrderService.create_order_from_cart(cart, self.user, {'name': 'Test User', 'email': 'test@travelsphere.com'})
        self.assertIsNotNone(order)
        self.assertEqual(order.line_items.count(), 1)
        self.assertEqual(cart.items.count(), 0)

class CouponAndTaxTests(TestCase):
    def test_tax_calculation(self):
        res = TaxCalculationEngine.calculate_taxes(Decimal('100.00'))
        self.assertEqual(res['tax_amount'], Decimal('5.00'))

    def test_coupon_discount(self):
        from django.utils import timezone
        coupon = Coupon.objects.create(
            code='SAVE10',
            description='10% Off',
            discount_percentage=Decimal('10.00'),
            max_discount_amount=Decimal('50.00'),
            min_order_amount=Decimal('100.00'),
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=30)
        )
        disc = coupon.calculate_discount(Decimal('200.00'))
        self.assertEqual(disc, Decimal('20.00'))
