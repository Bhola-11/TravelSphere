"""
Transports App Models: Flights, Trains, Buses, Private Chauffeur Transfers & Seat Allocations.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import AuditableModel, TimeStampedModel
from apps.destinations.models import City
from apps.core.constants import TransportTypeEnum, SeatClassEnum

class TransportOperator(TimeStampedModel):
    """Airline, Railway Company, Luxury Bus Liner, or Private Chauffeur Fleet."""
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="e.g. EK (Emirates), SNCF, GREY")
    transport_type = models.CharField(max_length=30, choices=TransportTypeEnum.choices, default=TransportTypeEnum.FLIGHT)
    logo = models.ImageField(upload_to='transports/operators/', null=True, blank=True)
    customer_support_phone = models.CharField(max_length=30, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.50)

    def __str__(self):
        return f"{self.name} [{self.get_transport_type_display()}]"

class StationStop(TimeStampedModel):
    """Airport, Railway Station, Bus Terminal, or Cruise Port."""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='stations')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, help_text="IATA (e.g. JFK, LHR) or Station code")
    station_type = models.CharField(max_length=30, choices=TransportTypeEnum.choices, default=TransportTypeEnum.FLIGHT)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = ('code', 'station_type')
        ordering = ['city__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.city.name}"

class TransportRoute(TimeStampedModel):
    """Origin to Destination network link."""
    operator = models.ForeignKey(TransportOperator, on_delete=models.CASCADE, related_name='routes')
    origin_station = models.ForeignKey(StationStop, on_delete=models.CASCADE, related_name='departing_routes')
    destination_station = models.ForeignKey(StationStop, on_delete=models.CASCADE, related_name='arriving_routes')
    route_code = models.CharField(max_length=50, help_text="e.g. EK-201, TGV-9840")
    distance_km = models.PositiveIntegerField(default=500)
    estimated_duration_minutes = models.PositiveIntegerField(default=120)

    def __str__(self):
        return f"{self.route_code}: {self.origin_station.code} -> {self.destination_station.code} ({self.operator.name})"

class TransportSchedule(AuditableModel):
    """Daily or periodic scheduled trip instance."""
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.DateTimeField(db_index=True)
    arrival_time = models.DateTimeField()
    
    vehicle_identifier = models.CharField(max_length=100, default='Boeing 777-300ER', help_text="Aircraft / Train type or Bus Reg")
    is_direct = models.BooleanField(default=True)
    stops_summary = models.CharField(max_length=255, default='Non-stop')
    
    luggage_allowance = models.CharField(max_length=150, default='1 Check-in (23kg) + 1 Cabin (7kg)')
    meal_service_included = models.BooleanField(default=True)
    wifi_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['departure_time']

    def __str__(self):
        return f"{self.route.route_code} | {self.departure_time.strftime('%Y-%m-%d %H:%M')}"

class SeatClass(TimeStampedModel):
    """Tiered travel classes per schedule (Economy, Business, First)."""
    schedule = models.ForeignKey(TransportSchedule, on_delete=models.CASCADE, related_name='seat_classes')
    class_type = models.CharField(max_length=30, choices=SeatClassEnum.choices, default=SeatClassEnum.ECONOMY)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('150.00'))
    total_capacity = models.PositiveIntegerField(default=180)
    booked_count = models.PositiveIntegerField(default=0)
    refundable = models.BooleanField(default=True)

    class Meta:
        unique_together = ('schedule', 'class_type')

    @property
    def available_seats(self):
        return max(0, self.total_capacity - self.booked_count)

    def __str__(self):
        return f"{self.get_class_type_display()} on {self.schedule.route.route_code} (${self.base_price})"
