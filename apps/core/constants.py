"""
Core Constants, Enums, and Choice definitions for TravelSphere Platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    CUSTOMER = 'CUSTOMER', _('Customer')
    AGENCY_ADMIN = 'AGENCY_ADMIN', _('Agency Admin')
    AGENT = 'AGENT', _('Travel Agent')
    HOTEL_MANAGER = 'HOTEL_MANAGER', _('Hotel Manager')
    TRANSPORT_MANAGER = 'TRANSPORT_MANAGER', _('Transport Manager')
    SUPER_ADMIN = 'SUPER_ADMIN', _('System Super Administrator')

class KYCStatus(models.TextChoices):
    UNVERIFIED = 'UNVERIFIED', _('Unverified')
    SUBMITTED = 'SUBMITTED', _('Documents Submitted')
    UNDER_REVIEW = 'UNDER_REVIEW', _('Under Review')
    VERIFIED = 'VERIFIED', _('Verified')
    REJECTED = 'REJECTED', _('Rejected')

class BookingStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    PENDING_PAYMENT = 'PENDING_PAYMENT', _('Pending Payment')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    ON_HOLD = 'ON_HOLD', _('On Hold')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress / Traveling')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')
    REFUNDED = 'REFUNDED', _('Refunded')

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    SUCCESS = 'SUCCESS', _('Successful')
    FAILED = 'FAILED', _('Failed')
    REFUNDED = 'REFUNDED', _('Fully Refunded')
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', _('Partially Refunded')
    DISPUTED = 'DISPUTED', _('Disputed / Chargeback')

class PaymentMethod(models.TextChoices):
    CREDIT_CARD = 'CREDIT_CARD', _('Credit / Debit Card')
    NET_BANKING = 'NET_BANKING', _('Net Banking')
    UPI = 'UPI', _('UPI / Instant Transfer')
    STRIPE = 'STRIPE', _('Stripe Checkout')
    RAZORPAY = 'RAZORPAY', _('Razorpay')
    PAYPAL = 'PAYPAL', _('PayPal')
    BANK_WIRE = 'BANK_WIRE', _('Bank Wire Transfer')
    WALLET = 'WALLET', _('TravelSphere Wallet')

class TransportTypeEnum(models.TextChoices):
    FLIGHT = 'FLIGHT', _('Flight')
    TRAIN = 'TRAIN', _('Train')
    BUS = 'BUS', _('Intercity Luxury Bus')
    PRIVATE_TRANSFER = 'PRIVATE_TRANSFER', _('Private Transfer / Chauffeur')
    FERRY = 'FERRY', _('Ferry / Cruise')

class SeatClassEnum(models.TextChoices):
    ECONOMY = 'ECONOMY', _('Economy Class')
    PREMIUM_ECONOMY = 'PREMIUM_ECONOMY', _('Premium Economy')
    BUSINESS = 'BUSINESS', _('Business Class')
    FIRST_CLASS = 'FIRST_CLASS', _('First Class')
    SLEEPER = 'SLEEPER', _('Sleeper Berth')
    AC_TIER_1 = 'AC_TIER_1', _('1st AC')
    AC_TIER_2 = 'AC_TIER_2', _('2nd AC')
    AC_TIER_3 = 'AC_TIER_3', _('3rd AC')

class RoomCategoryEnum(models.TextChoices):
    STANDARD = 'STANDARD', _('Standard Room')
    DELUXE = 'DELUXE', _('Deluxe Room')
    SUPERIOR = 'SUPERIOR', _('Superior Suite')
    EXECUTIVE_SUITE = 'EXECUTIVE_SUITE', _('Executive Suite')
    PRESIDENTIAL = 'PRESIDENTIAL', _('Presidential Suite')
    VILLA = 'VILLA', _('Private Luxury Villa')
    CHALET = 'CHALET', _('Mountain Chalet')

class CurrencyCode(models.TextChoices):
    USD = 'USD', _('US Dollar ($)')
    EUR = 'EUR', _('Euro (€)')
    GBP = 'GBP', _('British Pound (£)')
    INR = 'INR', _('Indian Rupee (₹)')
    AUD = 'AUD', _('Australian Dollar (A$)')
    CAD = 'CAD', _('Canadian Dollar (C$)')
    JPY = 'JPY', _('Japanese Yen (¥)')
    AED = 'AED', _('UAE Dirham (AED)')

class ReviewRating(models.IntegerChoices):
    ONE = 1, _('1 - Poor')
    TWO = 2, _('2 - Fair')
    THREE = 3, _('3 - Good')
    FOUR = 4, _('4 - Very Good')
    FIVE = 5, _('5 - Excellent')
