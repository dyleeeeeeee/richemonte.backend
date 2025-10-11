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
	"""Send email and log notification in one call
	
	Args:
		supabase: Supabase client instance
		user_id: User identifier
		notification_type: Type of notification
		notification_message: Notification message for DB
		email_subject: Optional email subject
		email_html: Optional email HTML content
	"""
	# Log notification to database
	await log_notification(supabase, user_id, notification_type, notification_message)
	
	# Send email if subject and HTML provided
	if email_subject and email_html:
		email = await get_user_email(supabase, user_id)
		if email:
			await send_email(email, email_subject, email_html)
			logger.debug(f"Email sent to {user_id}: {email_subject}")
