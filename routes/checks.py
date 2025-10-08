"""
Checks routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from services import send_email, log_notification, get_user_email
from templates import check_deposit_email, check_order_email

logger = logging.getLogger(__name__)
checks_bp = Blueprint('checks', __name__, url_prefix='/api/checks')
supabase = get_supabase_client()


@checks_bp.route('', methods=['GET'])
@require_auth
async def get_checks(user):
	"""Get all checks for authenticated user"""
	checks = supabase.table('checks').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(checks.data)


@checks_bp.route('/deposit', methods=['POST'])
@require_auth
async def deposit_check(user):
	"""Deposit check"""
	data = await request.get_json()
	
	check_data = {
		'user_id': user['user_id'],
		'account_id': data['account_id'],
		'check_number': data.get('check_number', ''),
		'amount': float(data['amount']),
		'status': 'pending',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('checks').insert(check_data).execute()
	
	# Send confirmation email
	email = await get_user_email(supabase, user['user_id'])
	if email:
		html = check_deposit_email(float(data['amount']), data.get('check_number', 'N/A'))
		await send_email(email, 'Check Deposit Confirmation', html)
		await log_notification(supabase, user['user_id'], 'check_deposit', f'Check deposit of ${float(data["amount"]):,.2f}')
	
	logger.info(f"Check deposited for user {user['user_id']}: ${float(data['amount']):.2f}")
	return jsonify(result.data[0]), 201


@checks_bp.route('/order', methods=['POST'])
@require_auth
async def order_checks(user):
	"""Order checks"""
	data = await request.get_json()
	
	order_data = {
		'user_id': user['user_id'],
		'account_id': data['account_id'],
		'design': data.get('design', 'Standard'),
		'quantity': int(data.get('quantity', 50)),
		'price': float(data.get('price', 29.99)),
		'status': 'processing',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('check_orders').insert(order_data).execute()
	
	# Send confirmation email
	email = await get_user_email(supabase, user['user_id'])
	if email:
		html = check_order_email(
			data.get('design', 'Standard'),
			int(data.get('quantity', 50)),
			float(data.get('price', 29.99))
		)
		await send_email(email, 'Check Order Confirmation', html)
		await log_notification(supabase, user['user_id'], 'check_order', f'Check order placed: {data.get("design")}')
	
	logger.info(f"Check order placed for user {user['user_id']}: {data.get('design')}")
	return jsonify(result.data[0]), 201
