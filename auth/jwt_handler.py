"""
JWT token handling
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

logger = logging.getLogger(__name__)


def create_jwt_token(
	user_id: str, 
	email: str, 
	role: str = 'user', 
	account_status: str = 'active',
	transactions_blocked: bool = False
) -> str:
	"""Create JWT token for authenticated user
	
	Args:
		user_id: User's unique identifier
		email: User's email address
		role: User role (user, admin)
		account_status: Account status (active, suspended, blocked)
		transactions_blocked: Whether transactions are blocked for this user
	
	Returns:
		Encoded JWT token string
	"""
	payload = {
		'user_id': user_id,
		'email': email,
		'role': role,
		'account_status': account_status,
		'transactions_blocked': transactions_blocked,
		'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
	}
	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
	"""Verify and decode JWT token
	
	Args:
		token: JWT token string
	
	Returns:
		Decoded payload dict or None if invalid
	"""
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
		return payload
	except jwt.ExpiredSignatureError:
		logger.warning("JWT token expired")
		return None
	except jwt.InvalidTokenError:
		logger.warning("Invalid JWT token")
		return None
