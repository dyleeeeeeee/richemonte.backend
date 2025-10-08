"""
Core module for Concierge Bank backend
"""
from .config import *
from .database import get_supabase_client

__all__ = [
	'JWT_SECRET',
	'JWT_ALGORITHM',
	'JWT_EXPIRATION_HOURS',
	'ACCOUNT_NUMBER_LENGTH',
	'CARD_NUMBER_LENGTH',
	'CVV_LENGTH',
	'CARD_EXPIRY_DAYS',
	'EMAIL_FROM',
	'LUXURY_GOLD_COLOR',
	'get_supabase_client'
]
