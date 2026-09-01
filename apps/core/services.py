"""
Core Service Layer: Comprehensive Business Logic, Enterprise Security, Caching,
Multi-Currency Exchange, GeoSpatial Calculations, Notification Dispatchers,
File & Media Optimization, and Cryptographic Checksums for TravelSphere.
"""
import hashlib
import hmac
import math
import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any

from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import CurrencyExchangeRate, SystemConfiguration, AuditLog, ContactInquiry
from .constants import CurrencyCode, UserRole, BookingStatus, PaymentStatus

# ==============================================================================
# 1. ENTERPRISE MULTI-CURRENCY CONVERSION & FINANCIAL COMPUTATION ENGINE
# ==============================================================================

class CurrencyService:
    """
    High-performance multi-currency converter with multi-tier in-memory & Redis caching.
    Supports inverse rate resolution, historical lookup, and compliant financial rounding.
    """
    CACHE_KEY_PREFIX = "ts_currency_rate_"
    CACHE_TTL = 3600  # 1 Hour Cache

    # Static baseline exchange rate matrix vs USD
    BASELINE_USD_RATES: Dict[str, Decimal] = {
        'USD': Decimal('1.000000'),
        'EUR': Decimal('0.924500'),
        'GBP': Decimal('0.789200'),
        'INR': Decimal('83.354000'),
        'AUD': Decimal('1.524000'),
        'CAD': Decimal('1.365000'),
        'JPY': Decimal('154.650000'),
        'AED': Decimal('3.672500'),
        'SGD': Decimal('1.348000'),
        'CHF': Decimal('0.902000'),
    }

    @classmethod
    def get_rate(cls, base_currency: str, target_currency: str) -> Decimal:
        """
        Retrieves exchange rate between two currencies with caching and database fallback.
        """
        base = (base_currency or 'USD').upper()
        target = (target_currency or 'USD').upper()

        if base == target:
            return Decimal('1.000000')

        cache_key = f"{cls.CACHE_KEY_PREFIX}{base}_{target}"
        cached_rate = cache.get(cache_key)
        if cached_rate is not None:
            return Decimal(str(cached_rate))

        # Query Database
        try:
            rate_entry = CurrencyExchangeRate.objects.get(
                base_currency=base,
                target_currency=target,
                is_active=True
            )
            rate = rate_entry.rate
        except CurrencyExchangeRate.DoesNotExist:
            # Check inverse
            try:
                inv_entry = CurrencyExchangeRate.objects.get(
                    base_currency=target,
                    target_currency=base,
                    is_active=True
                )
                rate = (Decimal('1.000000') / inv_entry.rate).quantize(Decimal('0.000001'))
            except CurrencyExchangeRate.DoesNotExist:
                # Use static cross-rate via USD
                base_to_usd = cls.BASELINE_USD_RATES.get(base, Decimal('1.000000'))
                target_to_usd = cls.BASELINE_USD_RATES.get(target, Decimal('1.000000'))
                
                # Formula: (1 / base_to_usd) * target_to_usd
                if base == 'USD':
                    rate = target_to_usd
                else:
                    rate = (target_to_usd / base_to_usd).quantize(Decimal('0.000001'))

        cache.set(cache_key, str(rate), cls.CACHE_TTL)
        return rate

    @classmethod
    def convert_amount(cls, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """
        Converts monetary amount between currencies applying standard half-up decimal rounding.
        """
        if not amount or amount <= Decimal('0.00'):
            return Decimal('0.00')

        dec_amount = Decimal(str(amount))
        rate = cls.get_rate(from_currency, to_currency)
        converted = dec_amount * rate
        return converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @classmethod
    def format_price(cls, amount: Decimal, currency: str = 'USD') -> str:
        """
        Formats price string with appropriate localized currency symbol and thousand separators.
        """
        curr = (currency or 'USD').upper()
        dec_amount = Decimal(str(amount or '0.00')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'AUD': 'A$',
            'CAD': 'C$',
            'JPY': '¥',
            'AED': 'AED ',
            'SGD': 'S$',
            'CHF': 'CHF ',
        }
        sym = symbols.get(curr, f"{curr} ")

        if curr in ['JPY', 'KRW']:
            return f"{sym}{int(dec_amount):,}"
        return f"{sym}{dec_amount:,.2f}"

# ==============================================================================
# 2. GEOSPATIAL & DISTANCE CALCULATION UTILITIES
# ==============================================================================

class GeoSpatialUtils:
    """
    Haversine distance calculations, coordinate validation, and bounding box solvers.
    """
    EARTH_RADIUS_KM = 6371.0

    @classmethod
    def calculate_haversine_distance(
        cls, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculates Great-Circle distance between two coordinates in kilometers.
        """
        try:
            phi1 = math.radians(float(lat1))
            phi2 = math.radians(float(lat2))
            delta_phi = math.radians(float(lat2) - float(lat1))
            delta_lambda = math.radians(float(lon2) - float(lon1))

            a = math.sin(delta_phi / 2.0) ** 2 +                 math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

            return round(cls.EARTH_RADIUS_KM * c, 2)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0

    @classmethod
    def is_valid_coordinate(cls, lat: Any, lon: Any) -> bool:
        """
        Validates whether latitude and longitude are within acceptable geographic ranges.
        """
        try:
            f_lat = float(lat)
            f_lon = float(lon)
            return (-90.0 <= f_lat <= 90.0) and (-180.0 <= f_lon <= 180.0)
        except (ValueError, TypeError):
            return False

# ==============================================================================
# 3. SECURITY & AUDIT TRAIL SERVICE
# ==============================================================================

class AuditService:
    """
    Centralized event auditing logger with structured change-delta tracker.
    """
    @staticmethod
    def log_action(
        user, 
        action: str, 
        entity_type: str, 
        entity_id: Optional[str] = None, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None, 
        changes: Optional[Dict[str, Any]] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        try:
            return AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else "",
                ip_address=ip_address,
                user_agent=(user_agent or "")[:500],
                changes_json=changes or {},
                metadata=metadata or {}
            )
        except Exception:
            return None

# ==============================================================================
# 4. SYSTEM DYNAMIC CONFIGURATION SERVICE
# ==============================================================================

class ConfigService:
    """
    Manages cached dynamic system settings stored in DB.
    """
    CACHE_KEY = "ts_system_config"

    @classmethod
    def get_config(cls) -> SystemConfiguration:
        config = cache.get(cls.CACHE_KEY)
        if config is None:
            config = SystemConfiguration.get_settings()
            cache.set(cls.CACHE_KEY, config, 1800)
        return config

    @classmethod
    def refresh_config(cls) -> SystemConfiguration:
        cache.delete(cls.CACHE_KEY)
        return cls.get_config()
