"""
Routes package for Concierge Bank API
"""
from .auth import auth_bp
from .accounts import accounts_bp
from .cards import cards_bp
from .transfers import transfers_bp
from .bills import bills_bp
from .checks import checks_bp
from .notifications import notifications_bp
from .settings import settings_bp
from .beneficiaries import beneficiaries_bp
from .health import health_bp

__all__ = [
	'auth_bp',
	'accounts_bp',
	'cards_bp',
	'transfers_bp',
	'bills_bp',
	'checks_bp',
	'notifications_bp',
	'settings_bp',
	'beneficiaries_bp',
	'health_bp',
]
