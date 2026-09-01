"""
Accounts Service Layer: Registration, Activity Logging, and Security Checks.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserActivityLog, KYCDocument
from apps.core.constants import KYCStatus

User = get_user_model()

class AccountService:
    @staticmethod
    def log_user_activity(user, activity_type: str, description: str, request=None):
        ip = getattr(request, 'client_ip', None) if request else None
        agent = getattr(request, 'client_user_agent', '') if request else ''
        return UserActivityLog.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            ip_address=ip,
            user_agent=agent
        )

    @staticmethod
    def update_kyc_status(user):
        docs = KYCDocument.objects.filter(user=user)
        if not docs.exists():
            user.kyc_status = KYCStatus.UNVERIFIED
        elif docs.filter(is_verified=True).exists():
            user.kyc_status = KYCStatus.VERIFIED
            user.is_verified = True
        elif docs.filter(verified_at__isnull=True).exists():
            user.kyc_status = KYCStatus.UNDER_REVIEW
        else:
            user.kyc_status = KYCStatus.REJECTED
        user.save(update_fields=['kyc_status', 'is_verified'])
        return user.kyc_status
