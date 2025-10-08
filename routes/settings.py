"""
Settings routes for Concierge Bank
"""
import logging
from quart import Blueprint, request, jsonify

from core import get_supabase_client
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
	
	result = supabase.table('users').update(data).eq('id', user['user_id']).execute()
	logger.info(f"Settings updated for user {user['user_id']}")
	return jsonify(result.data[0])
