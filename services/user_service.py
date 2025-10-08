"""
User-related services
"""
import logging
from typing import Optional, Dict, Any
from supabase import Client

logger = logging.getLogger(__name__)


async def get_user_email(supabase: Client, user_id: str) -> Optional[str]:
	"""Get user's email address from database
	
	Args:
		supabase: Supabase client instance
		user_id: User's unique identifier
	
	Returns:
		User's email address or None if not found
	"""
	try:
		result = supabase.table('users').select('email').eq('id', user_id).single().execute()
		return result.data.get('email') if result.data else None
	except Exception as e:
		logger.error(f"Failed to get email for user {user_id}: {str(e)}")
		return None


async def get_user_profile(supabase: Client, user_id: str) -> Optional[Dict[str, Any]]:
	"""Get user's full profile from database
	
	Args:
		supabase: Supabase client instance
		user_id: User's unique identifier
	
	Returns:
		User profile dict or None if not found
	"""
	try:
		result = supabase.table('users').select('*').eq('id', user_id).single().execute()
		return result.data if result.data else None
	except Exception as e:
		logger.error(f"Failed to get profile for user {user_id}: {str(e)}")
		return None
