"""
Authentication middleware
"""
from functools import wraps
from typing import Optional, Dict, Any
from quart import request, jsonify
from .jwt_handler import verify_jwt_token


async def get_current_user() -> Optional[Dict[str, Any]]:
	"""Get current authenticated user from JWT token in Authorization header
	
	Returns:
		User payload dict or None if not authenticated
	"""
	auth_header = request.headers.get('Authorization')
	if not auth_header:
		return None
	
	# Extract token from "Bearer <token>" format
	parts = auth_header.split()
	if len(parts) != 2 or parts[0].lower() != 'bearer':
		return None
	
	token = parts[1]
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
		
		# Check if user account is blocked
		account_status = user.get('account_status', 'active')
		if account_status == 'blocked':
			return jsonify({'error': 'Account blocked. Contact support.'}), 403
		if account_status == 'suspended':
			return jsonify({'error': 'Account suspended. Contact support.'}), 403
		
		return await f(user, *args, **kwargs)
	return decorated_function


def require_transactions_enabled(f):
	"""Decorator to require transactions to be enabled for routes
	
	This checks if user's transactions are blocked. User can login but cannot
	perform any financial transactions (transfers, bill payments, check deposits).
	
	Usage:
		@app.route('/api/transfers')
		@require_auth
		@require_transactions_enabled
		async def create_transfer(user):
			# Only executes if transactions are not blocked
			return jsonify({'success': True})
	"""
	@wraps(f)
	async def decorated_function(*args, **kwargs):
		user = await get_current_user()
		if not user:
			return jsonify({'error': 'Unauthorized'}), 401
		
		# Check if transactions are blocked
		transactions_blocked = user.get('transactions_blocked', False)
		if transactions_blocked:
			return jsonify({
				'error': 'Your transactions have been temporarily blocked. Please contact Concierge Bank support for assistance.'
			}), 403
		
		return await f(user, *args, **kwargs)
	return decorated_function
