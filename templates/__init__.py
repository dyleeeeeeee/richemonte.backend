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

__all__ = [
	'welcome_email',
	'account_created_email',
	'card_approved_email',
	'transfer_confirmation_email',
	'bill_payment_email',
	'check_deposit_email',
	'check_order_email'
]
