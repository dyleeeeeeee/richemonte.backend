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
	notifications = supabase.table('notifications').select('*').eq('user_id', user['user_id']).eq('delivery_method', 'push').order('created_at', desc=True).limit(50).execute()
	return jsonify(notifications.data)


@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
@require_auth
async def mark_notification_read(user, notification_id):
	"""Mark single notification as read"""
	result = supabase.table('notifications')\
		.update({'read': True})\
		.eq('id', notification_id)\
		.eq('user_id', user['user_id'])\
		.execute()
	return jsonify({'message': 'Marked as read'})


@notifications_bp.route('/mark-all-read', methods=['PUT'])
@require_auth
async def mark_all_read(user):
	"""Mark all notifications as read"""
	result = supabase.table('notifications')\
		.update({'read': True})\
		.eq('user_id', user['user_id'])\
		.execute()
	return jsonify({'message': 'All marked as read'})
