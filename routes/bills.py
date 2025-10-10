"""
Bills routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from services import send_email, log_notification, get_user_email
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
	
	bill_data = {
		'user_id': user['user_id'],
		'payee_name': data['payee_name'],
		'account_number': data.get('account_number', ''),
		'bill_type': data.get('bill_type', 'utility'),
		'auto_pay': data.get('auto_pay', False),
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('bills').insert(bill_data).execute()
	logger.info(f"Bill payee added for user {user['user_id']}: {data['payee_name']}")
	return jsonify(result.data[0]), 201


@bills_bp.route('/<bill_id>/pay', methods=['POST'])
@require_auth
async def pay_bill(user, bill_id):
	"""Pay bill"""
	data = await request.get_json()
	
	# Verify bill ownership
	bill = supabase.table('bills').select('*').eq('id', bill_id).eq('user_id', user['user_id']).single().execute()
	if not bill.data:
		return jsonify({'error': 'Bill not found'}), 404
	
	# Verify account ownership and balance
	account = supabase.table('accounts').select('*').eq('id', data['account_id']).eq('user_id', user['user_id']).single().execute()
	if not account.data:
		return jsonify({'error': 'Invalid account'}), 400
	
	if account.data['balance'] < float(data['amount']):
		return jsonify({'error': 'Insufficient funds'}), 400
	
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
	new_balance = account.data['balance'] - float(data['amount'])
	supabase.table('accounts').update({'balance': new_balance}).eq('id', data['account_id']).execute()
	
	# Send confirmation email
	email = await get_user_email(supabase, user['user_id'])
	if email:
		html = bill_payment_email(
			bill.data['payee_name'],
			float(data['amount']),
			data.get('payment_date', datetime.utcnow().strftime('%Y-%m-%d'))
		)
		await send_email(email, 'Bill Payment Confirmation', html)
		await log_notification(supabase, user['user_id'], 'bill_payment', f'Payment to {bill.data["payee_name"]} completed')
	
	logger.info(f"Bill payment completed for user {user['user_id']}: {bill.data['payee_name']}")
	return jsonify(result.data[0]), 201
