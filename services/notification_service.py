"""
Notification logging service
"""
import logging
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)


async def log_notification(
	supabase: Client,
	user_id: str,
	notification_type: str,
	message: str,
	delivery_method: str = 'email'
) -> None:
	"""Log notification to database
	
	Args:
		supabase: Supabase client instance
		user_id: User's unique identifier
		notification_type: Type of notification (e.g., 'registration', 'transfer')
		message: Notification message
		delivery_method: Delivery method (default 'email')
	"""
	try:
		supabase.table('notifications').insert({
			'user_id': user_id,
			'type': notification_type,
			'message': message,
			'delivery_method': delivery_method,
			'created_at': datetime.utcnow().isoformat()
		}).execute()
		logger.info(f"Notification logged for user {user_id}: {notification_type}")
	except Exception as e:
		logger.error(f"Failed to log notification for user {user_id}: {str(e)}")
