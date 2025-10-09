"""
Configuration constants for Concierge Bank backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Account Configuration
ACCOUNT_NUMBER_LENGTH = 12
CARD_NUMBER_LENGTH = 16
CVV_LENGTH = 3
CARD_EXPIRY_YEARS = 5
CARD_EXPIRY_DAYS = 365 * CARD_EXPIRY_YEARS  # 1825 days

# Email Configuration
EMAIL_FROM = 'Concierge Bank <noreply@conciergebank.com>'
LUXURY_GOLD_COLOR = '#B8860B'

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Resend Configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

# CORS Configuration
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG').upper()  # DEBUG, INFO, WARNING, ERROR, CRITICAL
