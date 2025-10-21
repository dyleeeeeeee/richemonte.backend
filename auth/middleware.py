"""
Authentication middleware
"""
import logging
from functools import wraps
from typing import Optional, Dict, Any
from quart import request, jsonify
from .jwt_handler import verify_jwt_token

logger = logging.getLogger(__name__)


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
	
	This checks if user's transactions are blocked by querying the database
	for the most current status. User can login but cannot perform any 
	financial transactions (transfers, bill payments, check deposits).
	
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
		
		# Query database for current transaction blocking status
		from core import get_supabase_client
		supabase = get_supabase_client()
		try:
			user_data = supabase.table('users').select('transactions_blocked').eq('id', user['user_id']).single().execute()
			transactions_blocked = user_data.data.get('transactions_blocked', False) if user_data.data else False
		except Exception as e:
			# If database query fails, default to blocked for security
			logger.warning(f"Failed to check transaction blocking status for user {user['user_id']}: {e}")
			transactions_blocked = True
		
		if transactions_blocked:
			return jsonify({
				'error': 'Your transactions have been temporarily blocked. Please contact Concierge Bank support for assistance.'
			}), 403
		
		return await f(user, *args, **kwargs)
	return decorated_function


def require_pin(f):
	"""Decorator to require PIN verification for high-value transactions
	
	This checks the user's transaction PIN against the provided PIN.
	Used for finalizing transfers, bill payments, and other financial operations.
	
	Usage:
		@transfers_bp.route('/verify-pin', methods=['POST'])
		@require_auth
		@require_pin
		async def verify_transfer_pin(user, pin_valid):
			# pin_valid is True if PIN matches
			return jsonify({'pin_valid': pin_valid})
	"""
	@wraps(f)
	async def decorated_function(*args, **kwargs):
		user = await get_current_user()
		if not user:
			return jsonify({'error': 'Unauthorized'}), 401
		
		# Get PIN from request body
		data = await request.get_json()
		provided_pin = data.get('pin')
		
		if not provided_pin:
			return jsonify({'error': 'Transaction PIN is required'}), 400
		
		if not isinstance(provided_pin, str) or not provided_pin.isdigit() or len(provided_pin) != 6:
			return jsonify({'error': 'Transaction PIN must be exactly 6 digits'}), 400
		
		# Query database for PIN hash
		from core import get_supabase_client
		supabase = get_supabase_client()
		try:
			user_data = supabase.table('users').select('transaction_pin_hash').eq('id', user['user_id']).single().execute()
			stored_hash = user_data.data.get('transaction_pin_hash') if user_data.data else None
			
			if not stored_hash:
				return jsonify({'error': 'Transaction PIN not set. Please contact support.'}), 400
			
			# Verify PIN - compare plain text
			pin_valid = provided_pin == stored_hash
			
			if not pin_valid:
				return jsonify({'error': 'Invalid transaction PIN'}), 403
			
			# PIN is valid, proceed with the function
			return await f(user, *args, **kwargs)
			
		except Exception as e:
			logger.error(f"Failed to verify PIN for user {user['user_id']}: {e}")
			return jsonify({'error': 'PIN verification failed. Please try again.'}), 500
	
	return decorated_function
