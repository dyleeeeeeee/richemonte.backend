"""
Email templates for Concierge Bank
"""
from .email_templates import (
	welcome_email,
	account_created_email,
	card_approved_email,
	transfer_confirmation_email,
	bill_payment_email,
	check_deposit_email,
	check_order_email
)
from .twofa import (
	twofa_code_email,
	twofa_setup_email
)

__all__ = [
	'welcome_email',
	'account_created_email',
	'card_approved_email',
	'transfer_confirmation_email',
	'bill_payment_email',
	'check_deposit_email',
	'check_order_email',
	'twofa_code_email',
	'twofa_setup_email'
]
