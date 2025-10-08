"""
Authentication middleware
"""
from functools import wraps
from typing import Optional, Dict, Any
from quart import request, jsonify
from .jwt_handler import verify_jwt_token


async def get_current_user() -> Optional[Dict[str, Any]]:
	"""Get current authenticated user from JWT cookie
	
	Returns:
		User payload dict or None if not authenticated
	"""
	token = request.cookies.get('auth_token')
	if not token:
		return None
	
	payload = verify_jwt_token(token)
	if not payload:
		return None
	
	return payload


def require_auth(f):
	"""Decorator to require authentication for routes
	
	Usage:
		@app.route('/api/protected')
		@require_auth
		async def protected_route(user):
			# user is automatically injected
			return jsonify({'user_id': user['user_id']})
	"""
	@wraps(f)
	async def decorated_function(*args, **kwargs):
		user = await get_current_user()
		if not user:
			return jsonify({'error': 'Unauthorized'}), 401
		return await f(user, *args, **kwargs)
	return decorated_function
