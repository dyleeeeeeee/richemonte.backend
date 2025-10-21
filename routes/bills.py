"""
Bills routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth, require_transactions_enabled, require_pin
from utils import verify_account_ownership, check_sufficient_balance, update_account_balance, insert_record
from services import notify_user
from templates import bill_payment_email

logger = logging.getLogger(__name__)
bills_bp = Blueprint('bills', __name__, url_prefix='/api/bills')
supabase = get_supabase_client()


@bills_bp.route('', methods=['GET'])
@require_auth
async def get_bills(user):
	"""Get all bill payees for authenticated user"""
	bills = supabase.table('bills').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(bills.data)


@bills_bp.route('', methods=['POST'])
@require_auth
async def add_bill(user):
	"""Add bill payee"""
	data = await request.get_json()
	
	# Validate required fields
	if not data.get('payee_name'):
		return jsonify({'error': 'Payee name is required'}), 400
	if not data.get('due_date'):
		return jsonify({'error': 'Due date is required'}), 400
	
	# Validate amount
	amount = float(data.get('amount', 0))
	if amount <= 0:
		return jsonify({'error': 'Amount must be greater than 0'}), 400
	if amount > 1000000:
		return jsonify({'error': 'Amount exceeds maximum limit'}), 400
	
	# Validate bill type
	valid_bill_types = ['utility', 'credit_card', 'insurance', 'loan', 'rent', 'subscription', 'other']
	bill_type = data.get('bill_type', 'utility')
	if bill_type not in valid_bill_types:
		return jsonify({'error': f'Invalid bill type. Must be one of: {", ".join(valid_bill_types)}'}), 400
	
	bill_data = {
		'user_id': user['user_id'],
		'payee_name': data['payee_name'].strip(),
		'account_number': data.get('account_number', '').strip(),
		'bill_type': bill_type,
		'amount': amount,
		'due_date': data['due_date'],
		'auto_pay': data.get('auto_pay', False),
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('bills').insert(bill_data).execute()
	logger.info(f"Bill payee added for user {user['user_id']}: {data['payee_name']}")
	return jsonify(result.data[0]), 201


@bills_bp.route('/<bill_id>/pay', methods=['POST'])
@require_auth
@require_transactions_enabled
@require_pin
async def pay_bill(user, bill_id):
	"""Pay bill"""
	data = await request.get_json()
	
	# Verify bill ownership
	bill = supabase.table('bills').select('*').eq('id', bill_id).eq('user_id', user['user_id']).single().execute()
	if not bill.data:
		return jsonify({'error': 'Bill not found'}), 404
	
	# Verify account ownership and balance
	success, account_data, error = await verify_account_ownership(supabase, data['account_id'], user['user_id'])
	if not success:
		return jsonify({'error': error}), 400
	
	has_balance, balance_error = await check_sufficient_balance(account_data, float(data['amount']))
	if not has_balance:
		return jsonify({'error': balance_error}), 400
	
	# Create payment record
	payment_data = {
		'user_id': user['user_id'],
		'bill_id': bill_id,
		'account_id': data['account_id'],
		'amount': float(data['amount']),
		'payment_date': data.get('payment_date', datetime.utcnow().isoformat()),
		'status': 'completed',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('bill_payments').insert(payment_data).execute()
	
	# Update account balance
	new_balance = account_data['balance'] - float(data['amount'])
	await update_account_balance(supabase, data['account_id'], new_balance)
	
	# Create transaction record for bill payment
	await create_transaction_record(
		supabase,
		data['account_id'],
		'debit',
		float(data['amount']),
		f"Bill payment to {bill.data['payee_name']}",
		'bill_payment'
	)
	
	# Send notification
	html = bill_payment_email(
		bill.data['payee_name'],
		float(data['amount']),
		data.get('payment_date', datetime.utcnow().strftime('%Y-%m-%d'))
	)
	await notify_user(
		supabase,
		user['user_id'],
		'bill_payment',
		f'Payment to {bill.data["payee_name"]} completed',
		'Bill Payment Confirmation',
		html
	)
	
	logger.info(f"Bill payment completed for user {user['user_id']}: {bill.data['payee_name']}")
	return jsonify(result.data[0]), 201
