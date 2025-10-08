"""
Notifications routes for Concierge Bank
"""
from quart import Blueprint, jsonify

from core import get_supabase_client
from auth import require_auth

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')
supabase = get_supabase_client()


@notifications_bp.route('', methods=['GET'])
@require_auth
async def get_notifications(user):
	"""Get user notifications"""
	notifications = supabase.table('notifications').select('*').eq('user_id', user['user_id']).order('created_at', desc=True).limit(50).execute()
	return jsonify(notifications.data)
