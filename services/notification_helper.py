"""
Combined notification and email service
Reduces code duplication - DRY principle
"""
import logging
from typing import Optional
from supabase import Client
from .email_service import send_email
from .notification_service import log_notification
from .user_service import get_user_email

logger = logging.getLogger(__name__)


async def notify_user(
	supabase: Client,
	user_id: str,
	notification_type: str,
	notification_message: str,
	email_subject: Optional[str] = None,
	email_html: Optional[str] = None
) -> None:
	"""Send email and log notification in one call, respecting user preferences
	
	Args:
		supabase: Supabase client instance
		user_id: User identifier
		notification_type: Type of notification (e.g., 'transaction', 'security', 'bills')
		notification_message: Notification message for DB
		email_subject: Optional email subject
		email_html: Optional email HTML content
	"""
	# Get user notification preferences
	user_response = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
	user_prefs = user_response.data.get('notification_preferences', {}) if user_response.data else {}
	
	# Default preferences - all enabled if not set
	default_prefs = {
		'email_transactions': True,
		'email_bills': True,
		'email_security': True,
		'email_marketing': False,
		'sms_transactions': False,
		'sms_security': True,
		'push_transactions': True,
		'push_bills': True,
	}
	
	# Merge user prefs with defaults
	prefs = {**default_prefs, **user_prefs}
	
	# Check if email should be sent based on notification type
	should_send_email = False
	if notification_type in ['transaction', 'transfer', 'account_created']:
		should_send_email = prefs.get('email_transactions', True)
	elif notification_type in ['bill_payment', 'bill_due']:
		should_send_email = prefs.get('email_bills', True)
	elif notification_type in ['security', 'login_alert', 'card_issue_reported', 'password_changed']:
		should_send_email = prefs.get('email_security', True)
	else:
		# For other types, send email by default unless specifically disabled
		should_send_email = True
	
	# Always log notification to database (for in-app notifications)
	await log_notification(supabase, user_id, notification_type, notification_message)
	
	# Send email only if user preferences allow it and email content provided
	if should_send_email and email_subject and email_html:
		email = await get_user_email(supabase, user_id)
		if email:
			await send_email(email, email_subject, email_html)
			logger.debug(f"Email sent to {user_id}: {email_subject}")
		else:
			logger.warning(f"Could not send email to {user_id}: no email address found")
