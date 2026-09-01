"""
Comprehensive Test Suites for TravelSphere Enterprise Platform:
Testing Auth, RBAC, Destinations, Tours, Hotels, Transports, Bookings, Payments, Reviews & Analytics.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import SystemConfiguration, CurrencyExchangeRate, AuditLog
from apps.core.services import CurrencyService, GeoSpatialUtils
from apps.core.constants import UserRole, KYCStatus, BookingStatus, PaymentStatus, RoomCategoryEnum
from apps.destinations.models import Continent, Country, City, DestinationCategory, Destination, PointOfInterest
from apps.tours.models import TourCategory, TourPackage, DayItinerary, TourDepartureDate, SeasonalSurcharge
from apps.tours.services import TourPricingService, TourAvailabilityService
from apps.hotels.models import HotelProperty, RoomType, Amenity
from apps.hotels.services import HotelAvailabilityService
from apps.transports.models import TransportOperator, StationStop, TransportRoute, TransportSchedule, SeatClass
from apps.transports.services import TransportSearchService
from apps.bookings.models import Cart, CartItem, BookingOrder, BookingLineItem
from apps.bookings.services import CartService, BookingOrderService
from apps.payments.models import Coupon, TaxRate, PaymentTransaction, Invoice
from apps.payments.services import TaxCalculationEngine, PaymentGatewayService
from apps.agencies.models import Agency
from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from apps.analytics.services import RecommendationEngine, DynamicPricingEngine

User = get_user_model()

class TravelSphereComprehensiveTestSuite(TestCase):
    def setUp(self):
        # 1. System Config
        self.config = SystemConfiguration.get_settings()
        CurrencyExchangeRate.objects.create(base_currency='USD', target_currency='EUR', rate=Decimal('0.92'))
        CurrencyExchangeRate.objects.create(base_currency='USD', target_currency='GBP', rate=Decimal('0.78'))

        # 2. Users
        self.client = Client()
        self.customer = User.objects.create_user(
            email='alice@example.com',
            password='AlicePassword123!',
            first_name='Alice',
            last_name='Walker',
            role=UserRole.CUSTOMER,
            is_verified=True,
            kyc_status=KYCStatus.VERIFIED
        )
        self.agency_user = User.objects.create_user(
            email='agency@voyages.com',
            password='AgencyPassword123!',
            first_name='Agency',
            last_name='Admin',
            role=UserRole.AGENCY_ADMIN
        )
        self.agency = Agency.objects.create(
            owner=self.agency_user,
            company_name='Voyages Worldwide',
            license_number='LIC-10029',
            official_email='agency@voyages.com',
            phone_number='+1 555-1234'
        )

        # 3. Geography
        self.continent = Continent.objects.create(name='Europe', code='EU')
        self.country = Country.objects.create(continent=self.continent, name='France', iso2='FR')
        self.city = City.objects.create(country=self.country, name='Paris', is_airport_hub=True)
        self.cat = DestinationCategory.objects.create(name='Historical Culture')
        self.destination = Destination.objects.create(
            title='Paris City of Lights',
            city=self.city,
            category=self.cat,
            tagline='Iconic monuments and art.',
            overview='Experience world class museums and cuisine.',
            ideal_duration_days=5,
            is_featured=True
        )

        # 4. Tour Package
        self.tour_cat = TourCategory.objects.create(name='Private Luxury')
        self.tour = TourPackage.objects.create(
            code='TSP-PAR-001',
            title='Parisian Grand Discovery',
            subtitle='5 days in Paris',
            destination=self.destination,
            category=self.tour_cat,
            agency=self.agency_user,
            duration_days=5,
            duration_nights=4,
            base_price_adult=Decimal('1200.00'),
            base_price_child=Decimal('600.00'),
            is_featured=True
        )
        self.dep_date = timezone.now().date() + timedelta(days=20)
        self.departure = TourDepartureDate.objects.create(
            tour_package=self.tour,
            departure_date=self.dep_date,
            return_date=self.dep_date + timedelta(days=5),
            total_slots=20,
            adult_price=Decimal('1200.00'),
            child_price=Decimal('600.00')
        )

        # 5. Hotel & Room
        self.hotel = HotelProperty.objects.create(
            title='Grand Hotel Paris',
            city=self.city,
            destination=self.destination,
            star_rating=5,
            address='1 Rue de Rivoli, Paris'
        )
        self.room = RoomType.objects.create(
            hotel=self.hotel,
            name='Superior King Suite',
            category=RoomCategoryEnum.SUPERIOR,
            base_price_per_night=Decimal('250.00'),
            total_rooms_count=10
        )

    def test_core_currency_and_geospatial(self):
        eur = CurrencyService.convert_amount(Decimal('100.00'), 'USD', 'EUR')
        self.assertEqual(eur, Decimal('92.00'))
        
        # Test Haversine distance
        dist = GeoSpatialUtils.calculate_haversine_distance(48.8566, 2.3522, 51.5074, -0.1278) # Paris to London
        self.assertTrue(330.0 <= dist <= 360.0)

    def test_tour_pricing_and_availability(self):
        quote = TourPricingService.calculate_quote(self.tour, self.dep_date, adults_count=2, children_count=1)
        self.assertEqual(quote['gross_total'], Decimal('3000.00'))

        avail, msg = TourAvailabilityService.check_availability(self.tour.id, self.dep_date, requested_slots=2)
        self.assertTrue(avail)

    def test_hotel_stay_quote(self):
        cin = timezone.now().date() + timedelta(days=5)
        cout = cin + timedelta(days=3)
        quote = HotelAvailabilityService.calculate_stay_quote(self.room, cin, cout, rooms_requested=1)
        self.assertTrue(quote['is_available'])
        self.assertEqual(quote['num_nights'], 3)
        self.assertTrue(quote['total_price'] >= Decimal('750.00'))

    def test_full_cart_checkout_and_payment_flow(self):
        # 1. Add to cart
        cart = Cart.objects.create(user=self.customer)
        CartService.add_tour_to_cart(cart, self.tour, self.dep_date, adults=2, children=0)
        self.assertEqual(cart.total_items_count, 1)

        # 2. Checkout
        billing_data = {
            'name': 'Alice Walker',
            'email': 'alice@example.com',
            'phone': '+1 555-9988',
            'address': '123 Main St, New York, NY'
        }
        order, msg = BookingOrderService.create_order_from_cart(cart, self.customer, billing_data)
        self.assertIsNotNone(order)
        self.assertEqual(order.status, BookingStatus.PENDING_PAYMENT)
        self.assertEqual(order.line_items.count(), 1)

        # 3. Process Payment
        txn = PaymentGatewayService.process_payment(order, 'STRIPE', self.customer)
        self.assertEqual(txn.status, PaymentStatus.SUCCESS)
        
        order.refresh_from_db()
        self.assertEqual(order.status, BookingStatus.CONFIRMED)
        self.assertTrue(hasattr(order, 'invoice'))
        self.assertTrue(order.invoice.is_paid)

    def test_reviews_and_ratings(self):
        review = Review.objects.create(
            user=self.customer,
            tour_package=self.tour,
            rating=5,
            title='Sensational Journey',
            comment='Everything was perfectly organized.',
            is_approved=True
        )
        ReviewService.recalculate_entity_rating(tour=self.tour)
        self.tour.refresh_from_db()
        self.assertEqual(self.tour.review_count, 1)
        self.assertEqual(self.tour.rating_average, Decimal('5.00'))

    def test_recommendation_engine(self):
        recs = RecommendationEngine.get_recommended_packages_for_user(self.customer, limit=4)
        self.assertTrue(len(recs) >= 1)
