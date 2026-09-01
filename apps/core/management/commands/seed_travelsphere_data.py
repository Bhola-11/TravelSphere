from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.core.models import SystemConfiguration, CurrencyExchangeRate
from apps.core.constants import UserRole, KYCStatus, TransportTypeEnum, RoomCategoryEnum, SeatClassEnum
from apps.destinations.models import Continent, Country, City, DestinationCategory, Destination, PointOfInterest
from apps.tours.models import TourCategory, TourPackage, DayItinerary, ItineraryActivity, TourDepartureDate, TourInclusionExclusion
from apps.hotels.models import HotelProperty, RoomType, Amenity
from apps.transports.models import TransportOperator, StationStop, TransportRoute, TransportSchedule, SeatClass
from apps.agencies.models import Agency
from apps.reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial enterprise TravelSphere dataset.'

    def handle(self, *args, **options):
        self.stdout.write("Starting TravelSphere database seed...")

        # 1. System Configuration & Currency Rates
        SystemConfiguration.get_settings()
        currencies = [
            ('USD', 'EUR', Decimal('0.92')),
            ('USD', 'GBP', Decimal('0.78')),
            ('USD', 'INR', Decimal('83.25')),
            ('USD', 'AUD', Decimal('1.52')),
            ('USD', 'JPY', Decimal('154.50')),
        ]
        for base, target, rate in currencies:
            CurrencyExchangeRate.objects.get_or_create(base_currency=base, target_currency=target, defaults={'rate': rate})

        # 2. Superadmin & Demo Users
        admin_user, _ = User.objects.get_or_create(
            email='admin@travelsphere.com',
            defaults={
                'first_name': 'System',
                'last_name': 'Admin',
                'role': UserRole.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
                'kyc_status': KYCStatus.VERIFIED
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()

        cust_user, _ = User.objects.get_or_create(
            email='traveler@example.com',
            defaults={
                'first_name': 'Sophia',
                'last_name': 'Bennett',
                'role': UserRole.CUSTOMER,
                'is_verified': True,
                'kyc_status': KYCStatus.VERIFIED
            }
        )
        cust_user.set_password('TravelerPass123!')
        cust_user.save()

        agency_user, _ = User.objects.get_or_create(
            email='agency@apexvoyages.com',
            defaults={
                'first_name': 'Marcus',
                'last_name': 'Vance',
                'role': UserRole.AGENCY_ADMIN,
                'is_verified': True,
                'kyc_status': KYCStatus.VERIFIED
            }
        )
        agency_user.set_password('AgencyPass123!')
        agency_user.save()

        Agency.objects.get_or_create(
            owner=agency_user,
            defaults={
                'company_name': 'Apex Global Voyages',
                'license_number': 'IATA-998241',
                'official_email': 'agency@apexvoyages.com',
                'phone_number': '+1 (415) 888-9900',
                'address': '100 Financial Way, New York, NY',
                'is_verified': True
            }
        )

        # 3. Continents & Countries
        europe, _ = Continent.objects.get_or_create(name='Europe', code='EU', defaults={'description': 'Historic capitals, Mediterranean coasts, and Alpine peaks.'})
        asia, _ = Continent.objects.get_or_create(name='Asia', code='AS', defaults={'description': 'Ancient heritage, tropical isles, and futuristic skylines.'})
        americas, _ = Continent.objects.get_or_create(name='North America', code='NA', defaults={'description': 'National parks, iconic cities, and vast coastlines.'})

        france, _ = Country.objects.get_or_create(continent=europe, name='France', iso2='FR', defaults={'capital': 'Paris', 'currency_code': 'EUR', 'is_popular': True})
        italy, _ = Country.objects.get_or_create(continent=europe, name='Italy', iso2='IT', defaults={'capital': 'Rome', 'currency_code': 'EUR', 'is_popular': True})
        japan, _ = Country.objects.get_or_create(continent=asia, name='Japan', iso2='JP', defaults={'capital': 'Tokyo', 'currency_code': 'JPY', 'is_popular': True})
        usa, _ = Country.objects.get_or_create(continent=americas, name='United States', iso2='US', defaults={'capital': 'Washington D.C.', 'currency_code': 'USD', 'is_popular': True})

        # 4. Cities
        paris, _ = City.objects.get_or_create(country=france, name='Paris', defaults={'is_airport_hub': True})
        nice, _ = City.objects.get_or_create(country=france, name='Nice', defaults={'is_airport_hub': True})
        rome, _ = City.objects.get_or_create(country=italy, name='Rome', defaults={'is_airport_hub': True})
        tokyo, _ = City.objects.get_or_create(country=japan, name='Tokyo', defaults={'is_airport_hub': True})
        kyoto, _ = City.objects.get_or_create(country=japan, name='Kyoto')

        # 5. Categories & Destinations
        cat_cult, _ = DestinationCategory.objects.get_or_create(name='Cultural & Heritage', defaults={'icon_class': 'bi-bank'})
        cat_beach, _ = DestinationCategory.objects.get_or_create(name='Beach & Island Escape', defaults={'icon_class': 'bi-water'})
        cat_adv, _ = DestinationCategory.objects.get_or_create(name='Adventure & Trekking', defaults={'icon_class': 'bi-compass'})

        dest_paris, _ = Destination.objects.get_or_create(
            title='Paris — City of Lights',
            defaults={
                'city': paris,
                'category': cat_cult,
                'tagline': 'The epicenter of art, haute gastronomy, and timeless romance.',
                'overview': 'From the majestic iron spire of the Eiffel Tower to world-renowned culinary bistros in Saint-Germain-des-Prés.',
                'highlights': 'Eiffel Tower Sunrise\nLouvre Masterpieces\nSeine Sunset Cruise',
                'best_time_to_visit': 'April to October',
                'ideal_duration_days': 5,
                'is_featured': True,
                'rating_average': Decimal('4.92')
            }
        )

        dest_tokyo, _ = Destination.objects.get_or_create(
            title='Tokyo & Mount Fuji',
            defaults={
                'city': tokyo,
                'category': cat_cult,
                'tagline': 'Ultra-futuristic metropolis meets ancient Shinto shrines.',
                'overview': 'Explore the neon-lit alleyways of Shinjuku, serene temples of Asakusa, and sacred vistas of Mt. Fuji.',
                'highlights': 'Shibuya Crossing\nMeiji Jingu Shrine\nMount Fuji 5th Station',
                'best_time_to_visit': 'March to May & Sept to Nov',
                'ideal_duration_days': 7,
                'is_featured': True,
                'rating_average': Decimal('4.95')
            }
        )

        # POIs
        PointOfInterest.objects.get_or_create(
            destination=dest_paris,
            title='Eiffel Tower',
            defaults={'poi_type': 'MONUMENT', 'description': 'The quintessential Parisian landmark offering 360-degree city panoramas.', 'entry_fee_usd': Decimal('28.00')}
        )
        PointOfInterest.objects.get_or_create(
            destination=dest_tokyo,
            title='Senso-ji Temple',
            defaults={'poi_type': 'TEMPLE', 'description': 'Tokyos oldest and most significant ancient Buddhist temple.', 'entry_fee_usd': Decimal('0.00')}
        )

        # 6. Tour Packages
        tour_cat_exp, _ = TourCategory.objects.get_or_create(name='Luxury Expeditions', defaults={'icon_class': 'bi-gem'})
        
        tour_paris, _ = TourPackage.objects.get_or_create(
            code='TSP-PARIS-001',
            defaults={
                'title': 'Grand Parisian Art, Gastronomy & Seine Romance',
                'subtitle': 'A 5-day curated immersion into Parisian high culture and Michelin-starred dining.',
                'destination': dest_paris,
                'category': tour_cat_exp,
                'agency': agency_user,
                'duration_days': 5,
                'duration_nights': 4,
                'base_price_adult': Decimal('1499.00'),
                'base_price_child': Decimal('899.00'),
                'summary': 'Enjoy private skip-the-line tours of the Louvre, sunset champagne cruises on the Seine, and a day trip to Versailles.',
                'is_featured': True,
                'rating_average': Decimal('4.90'),
                'booking_count': 34
            }
        )

        # Day Itinerary for Paris
        d1, _ = DayItinerary.objects.get_or_create(tour_package=tour_paris, day_number=1, defaults={'title': 'Arrival & Seine Evening Champagne Cruise', 'description': 'Private chauffeur transfer to hotel followed by evening welcome dinner.', 'meals_included': 'Dinner', 'overnight_city': 'Paris'})
        d2, _ = DayItinerary.objects.get_or_create(tour_package=tour_paris, day_number=2, defaults={'title': 'Exclusive Louvre Masterpieces & Montmartre Walk', 'description': 'Private art historian guide through the Louvre and artists district.', 'meals_included': 'Breakfast, Lunch', 'overnight_city': 'Paris'})
        
        ItineraryActivity.objects.get_or_create(day_itinerary=d1, title='Private Airport Chauffeur Transfer', defaults={'description': 'Mercedes S-Class pickup from CDG Airport.'})
        ItineraryActivity.objects.get_or_create(day_itinerary=d1, title='Sunset Seine Yacht Cruise', defaults={'description': 'Glass of Moet champagne with live jazz trio.'})

        # Departures
        for i in range(1, 5):
            dep_dt = timezone.now().date() + timedelta(days=15 * i)
            TourDepartureDate.objects.get_or_create(
                tour_package=tour_paris,
                departure_date=dep_dt,
                defaults={
                    'return_date': dep_dt + timedelta(days=5),
                    'total_slots': 16,
                    'adult_price': Decimal('1499.00'),
                    'child_price': Decimal('899.00')
                }
            )

        # 7. Hotels & Rooms
        wifi, _ = Amenity.objects.get_or_create(name='High-Speed Fiber WiFi', icon_class='bi-wifi')
        pool, _ = Amenity.objects.get_or_create(name='Infinity Heated Pool', icon_class='bi-water')
        spa, _ = Amenity.objects.get_or_create(name='Signature Wellness Spa', icon_class='bi-flower1')

        hotel_paris, _ = HotelProperty.objects.get_or_create(
            title='The Ritz Paris & Grand Salon',
            defaults={
                'city': paris,
                'destination': dest_paris,
                'star_rating': 5,
                'property_type': 'HOTEL',
                'address': '15 Place Vendome, 75001 Paris',
                'overview': 'Legendary Belle Epoque palace hotel overlooking Place Vendome.',
                'is_featured': True,
                'rating_average': Decimal('4.98')
            }
        )
        hotel_paris.amenities.add(wifi, spa)

        RoomType.objects.get_or_create(
            hotel=hotel_paris,
            name='Deluxe Executive Vendome Suite',
            defaults={
                'category': RoomCategoryEnum.EXECUTIVE_SUITE,
                'base_price_per_night': Decimal('650.00'),
                'total_rooms_count': 8,
                'max_adults': 2
            }
        )

        # 8. Transports
        air_france, _ = TransportOperator.objects.get_or_create(name='Air France', code='AF', defaults={'transport_type': TransportTypeEnum.FLIGHT})
        jfk, _ = StationStop.objects.get_or_create(city=City.objects.get_or_create(country=usa, name='New York')[0], code='JFK', defaults={'name': 'John F. Kennedy Intl Airport', 'station_type': TransportTypeEnum.FLIGHT})
        cdg, _ = StationStop.objects.get_or_create(city=paris, code='CDG', defaults={'name': 'Charles de Gaulle Airport', 'station_type': TransportTypeEnum.FLIGHT})

        route_ny_paris, _ = TransportRoute.objects.get_or_create(
            operator=air_france,
            origin_station=jfk,
            destination_station=cdg,
            defaults={'route_code': 'AF-007', 'distance_km': 5850, 'estimated_duration_minutes': 430}
        )

        sched, _ = TransportSchedule.objects.get_or_create(
            route=route_ny_paris,
            departure_time=timezone.now() + timedelta(days=3),
            defaults={
                'arrival_time': timezone.now() + timedelta(days=3, hours=7, minutes=30),
                'vehicle_identifier': 'Boeing 777-300ER',
                'is_direct': True
            }
        )

        SeatClass.objects.get_or_create(
            schedule=sched,
            class_type=SeatClassEnum.BUSINESS,
            defaults={'base_price': Decimal('1850.00'), 'total_capacity': 48}
        )

        self.stdout.write(self.style.SUCCESS("TravelSphere database seeded successfully!"))
