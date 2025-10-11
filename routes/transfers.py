"""
Transfers routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from utils import verify_account_ownership, check_sufficient_balance, update_account_balance, create_transaction_record
from services import notify_user
from templates import transfer_confirmation_email

logger = logging.getLogger(__name__)
transfers_bp = Blueprint('transfers', __name__, url_prefix='/api/transfers')
supabase = get_supabase_client()


@transfers_bp.route('', methods=['POST'])
@require_auth
async def create_transfer(user):
	"""Create transfer"""
	data = await request.get_json()
	
	# Verify account ownership and balance
	success, account_data, error = await verify_account_ownership(supabase, data['from_account_id'], user['user_id'])
	if not success:
		return jsonify({'error': error}), 400
	
	has_balance, balance_error = await check_sufficient_balance(account_data, float(data['amount']))
	if not has_balance:
		return jsonify({'error': balance_error}), 400
	
	# Create transfer record
	transfer_data = {
		'user_id': user['user_id'],
		'from_account_id': data['from_account_id'],
		'to_account_id': data.get('to_account_id'),
		'to_external': data.get('to_external', {}),
		'amount': float(data['amount']),
		'transfer_type': data.get('transfer_type', 'internal'),
		'status': 'completed',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('transfers').insert(transfer_data).execute()
	
	# Update balance and create transaction
	new_balance = account_data['balance'] - float(data['amount'])
	await update_account_balance(supabase, data['from_account_id'], new_balance)
	await create_transaction_record(
		supabase,
		data['from_account_id'],
		'debit',
		float(data['amount']),
		f"Transfer to {data.get('to_external', {}).get('name', 'account')}",
		'transfer'
	)
	
	# Send notification
	html = transfer_confirmation_email(float(data['amount']), new_balance)
	await notify_user(
		supabase,
		user['user_id'],
		'transfer',
		f'Transfer of ${float(data["amount"]):,.2f} completed',
		'Transfer Confirmation',
		html
	)
	
	logger.info(f"Transfer completed for user {user['user_id']}: ${float(data['amount']):.2f}")
	return jsonify(result.data[0]), 201
