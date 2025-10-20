"""
Settings routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify
from supabase import create_client

from core import get_supabase_client
from core.config import SUPABASE_URL, SUPABASE_KEY
from auth import require_auth

logger = logging.getLogger(__name__)
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')
supabase = get_supabase_client()


@settings_bp.route('', methods=['GET'])
@require_auth
async def get_settings(user):
	"""Get user settings (same as user profile)"""
	user_data = supabase.table('users').select('*').eq('id', user['user_id']).single().execute()
	return jsonify(user_data.data)


@settings_bp.route('', methods=['PUT'])
@require_auth
async def update_settings(user):
	"""Update user settings"""
	data = await request.get_json()
	
	# Add updated_at timestamp
	data['updated_at'] = datetime.utcnow().isoformat()
	
	result = supabase.table('users').update(data).eq('id', user['user_id']).execute()
	logger.info(f"Settings updated for user {user['user_id']}")
	return jsonify(result.data[0])


@settings_bp.route('/profile', methods=['PUT'])
@require_auth
async def update_profile(user):
	"""Update user profile information"""
	data = await request.get_json()
	
	# Extract allowed profile fields
	profile_data = {}
	if 'full_name' in data:
		profile_data['full_name'] = data['full_name']
	if 'phone' in data:
		profile_data['phone'] = data['phone']
	if 'address' in data:
		profile_data['address'] = data['address']
	if 'preferred_brand' in data:
		profile_data['preferred_brand'] = data['preferred_brand']
	if 'photo_url' in data:
		profile_data['photo_url'] = data['photo_url']
	
	profile_data['updated_at'] = datetime.utcnow().isoformat()
	
	result = supabase.table('users').update(profile_data).eq('id', user['user_id']).execute()
	logger.info(f"Profile updated for user {user['user_id']}")
	return jsonify(result.data[0])


@settings_bp.route('/password', methods=['PUT'])
@require_auth
async def change_password(user):
	"""Change user password"""
	data = await request.get_json()
	
	if not data.get('current_password') or not data.get('new_password'):
		return jsonify({'error': 'Current and new password required'}), 400
	
	try:
		# Get Supabase client with user context
		supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
		
		# Verify current password by attempting to sign in
		user_data = supabase.table('users').select('email').eq('id', user['user_id']).single().execute()
		email = user_data.data['email']
		
		try:
			auth_response = supabase_client.auth.sign_in_with_password({
				'email': email,
				'password': data['current_password']
			})
			if not auth_response.user:
				return jsonify({'error': 'Current password is incorrect'}), 401
		except Exception:
			return jsonify({'error': 'Current password is incorrect'}), 401
		
		# Update password using Supabase auth
		supabase_client.auth.update_user({
			'password': data['new_password']
		})
		
		logger.info(f"Password changed for user {user['user_id']}")
		return jsonify({'message': 'Password updated successfully'})
		
	except Exception as e:
		logger.error(f"Password change error: {str(e)}")
		return jsonify({'error': 'Failed to update password'}), 500


@settings_bp.route('/notifications', methods=['GET'])
@require_auth
async def get_notification_preferences(user):
	"""Get notification preferences"""
	user_data = supabase.table('users').select('notification_preferences').eq('id', user['user_id']).single().execute()
	return jsonify(user_data.data.get('notification_preferences', {}))


@settings_bp.route('/notifications', methods=['PUT'])
@require_auth
async def update_notification_preferences(user):
	"""Update notification preferences"""
	data = await request.get_json()
	
	update_data = {
		'notification_preferences': data,
		'updated_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('users').update(update_data).eq('id', user['user_id']).execute()
	logger.info(f"Notification preferences updated for user {user['user_id']}")
	return jsonify(result.data[0]['notification_preferences'])
