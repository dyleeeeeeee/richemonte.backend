"""
Transfers routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from services import send_email, log_notification, get_user_email
from templates import transfer_confirmation_email

logger = logging.getLogger(__name__)
transfers_bp = Blueprint('transfers', __name__, url_prefix='/api/transfers')
supabase = get_supabase_client()


@transfers_bp.route('', methods=['POST'])
@require_auth
async def create_transfer(user):
	"""Create transfer"""
	data = await request.get_json()
	
	# Verify from account ownership and balance
	from_account = supabase.table('accounts').select('*').eq('id', data['from_account_id']).eq('user_id', user['user_id']).single().execute()
	if not from_account.data:
		return jsonify({'error': 'Invalid from account'}), 400
	
	if from_account.data['balance'] < float(data['amount']):
		return jsonify({'error': 'Insufficient funds'}), 400
	
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
	
	# Update account balance
	new_balance = from_account.data['balance'] - float(data['amount'])
	supabase.table('accounts').update({'balance': new_balance}).eq('id', data['from_account_id']).execute()
	
	# Create transaction record
	supabase.table('transactions').insert({
		'account_id': data['from_account_id'],
		'type': 'debit',
		'amount': float(data['amount']),
		'description': f"Transfer to {data.get('to_external', {}).get('name', 'account')}",
		'category': 'transfer',
		'created_at': datetime.utcnow().isoformat()
	}).execute()
	
	# Send confirmation email
	email = await get_user_email(supabase, user['user_id'])
	if email:
		html = transfer_confirmation_email(float(data['amount']), new_balance)
		await send_email(email, 'Transfer Confirmation', html)
		await log_notification(supabase, user['user_id'], 'transfer', f'Transfer of ${float(data["amount"]):,.2f} completed')
	
	logger.info(f"Transfer completed for user {user['user_id']}: ${float(data['amount']):.2f}")
	return jsonify(result.data[0]), 201
