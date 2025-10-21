"""
Checks routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from services import notify_user
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
	
	# Validate required fields
	if not data.get('account_id'):
		return jsonify({'error': 'Account ID is required'}), 400
	if not data.get('amount'):
		return jsonify({'error': 'Amount is required'}), 400
	
	# Validate amount
	try:
		amount = float(data['amount'])
	except (ValueError, TypeError):
		return jsonify({'error': 'Invalid amount format'}), 400
	
	if amount <= 0:
		return jsonify({'error': 'Amount must be greater than 0'}), 400
	if amount > 100000:
		return jsonify({'error': 'Check amount exceeds maximum limit of $100,000'}), 400
	
	# Verify account ownership
	from utils import verify_account_ownership, update_account_balance, create_transaction_record
	success, account_data, error = await verify_account_ownership(supabase, data['account_id'], user['user_id'])
	if not success:
		return jsonify({'error': error}), 400
	
	check_data = {
		'user_id': user['user_id'],
		'account_id': data['account_id'],
		'check_number': data.get('check_number', '').strip(),
		'amount': amount,
		'status': 'pending',  # Checks need time to clear
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('checks').insert(check_data).execute()
	
	# Credit account (checks typically clear in 1-2 business days, but we'll credit immediately)
	new_balance = account_data['balance'] + amount
	await update_account_balance(supabase, data['account_id'], new_balance)
	
	# Create transaction record for check deposit
	await create_transaction_record(
		supabase,
		data['account_id'],
		'credit',
		amount,
		f"Check deposit #{data.get('check_number', 'N/A')}",
		'deposit'
	)
	
	# Send notification
	html = check_deposit_email(float(data['amount']), data.get('check_number', 'N/A'))
	await notify_user(
		supabase,
		user['user_id'],
		'check_deposit',
		f'Check deposit of ${float(data["amount"]):,.2f}',
		'Check Deposit Confirmation',
		html
	)
	
	logger.info(f"Check deposited for user {user['user_id']}: ${float(data['amount']):.2f}")
	return jsonify(result.data[0]), 201


@checks_bp.route('/order', methods=['POST'])
@require_auth
async def order_checks(user):
	"""Order checks"""
	data = await request.get_json()
	
	# Validate required fields
	if not data.get('account_id'):
		return jsonify({'error': 'Account ID is required'}), 400
	
	# Verify account ownership
	from utils import verify_account_ownership
	success, account_data, error = await verify_account_ownership(supabase, data['account_id'], user['user_id'])
	if not success:
		return jsonify({'error': error}), 400
	
	# Validate quantity
	try:
		quantity = int(data.get('quantity', 50))
	except (ValueError, TypeError):
		return jsonify({'error': 'Invalid quantity format'}), 400
	
	if quantity < 50:
		return jsonify({'error': 'Minimum order is 50 checks'}), 400
	if quantity > 500:
		return jsonify({'error': 'Maximum order is 500 checks'}), 400
	if quantity % 50 != 0:
		return jsonify({'error': 'Quantity must be in multiples of 50'}), 400
	
	order_data = {
		'user_id': user['user_id'],
		'account_id': data['account_id'],
		'design': data.get('design', 'Standard'),
		'quantity': quantity,
		'price': float(data.get('price', 29.99)),
		'status': 'processing',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('check_orders').insert(order_data).execute()
	
	# Send notification
	html = check_order_email(
		data.get('design', 'Standard'),
		int(data.get('quantity', 50)),
		float(data.get('price', 29.99))
	)
	await notify_user(
		supabase,
		user['user_id'],
		'check_order',
		f'Check order placed: {data.get("design")}',
		'Check Order Confirmation',
		html
	)
	
	logger.info(f"Check order placed for user {user['user_id']}: {data.get('design')}")
	return jsonify(result.data[0]), 201
