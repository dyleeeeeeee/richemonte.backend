"""
Transfers routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth, require_transactions_enabled, require_pin
from utils import verify_account_ownership, check_sufficient_balance, update_account_balance, create_transaction_record
from services import notify_user
from templates import transfer_confirmation_email

logger = logging.getLogger(__name__)
transfers_bp = Blueprint('transfers', __name__, url_prefix='/api/transfers')
supabase = get_supabase_client()


@transfers_bp.route('', methods=['GET'])
@require_auth
async def get_transfers(user):
	"""Get user's transfer history"""
	try:
		transfers = supabase.table('transfers').select('*').eq('user_id', user['user_id']).order('created_at', desc=True).execute()
		return jsonify(transfers.data)
	except Exception as e:
		logger.error(f"Failed to fetch transfers for user {user['user_id']}: {e}")
		return jsonify({'error': 'Failed to fetch transfer history'}), 500


@transfers_bp.route('', methods=['POST'])
@require_auth
@require_transactions_enabled
@require_pin
async def create_transfer(user):
	"""Create transfer with full validation and proper handling"""
	data = await request.get_json()
	
	# Validate required fields
	if not data.get('from_account_id'):
		return jsonify({'error': 'Source account is required'}), 400
	if not data.get('amount'):
		return jsonify({'error': 'Amount is required'}), 400
	
	# Validate amount
	try:
		amount = float(data['amount'])
	except (ValueError, TypeError):
		return jsonify({'error': 'Invalid amount format'}), 400
	
	if amount <= 0:
		return jsonify({'error': 'Amount must be greater than 0'}), 400
	if amount > 1000000:
		return jsonify({'error': 'Transfer amount exceeds maximum limit of $1,000,000'}), 400
	if amount < 0.01:
		return jsonify({'error': 'Amount must be at least $0.01'}), 400
	
	# Validate transfer type
	transfer_type = data.get('transfer_type', 'internal')
	if transfer_type not in ['internal', 'external', 'p2p']:
		return jsonify({'error': 'Invalid transfer type. Must be internal, external, or p2p'}), 400
	
	description = data.get('description', '').strip()[:200]  # Limit description length
	
	# Verify source account ownership and balance
	success, from_account, error = await verify_account_ownership(supabase, data['from_account_id'], user['user_id'])
	if not success:
		return jsonify({'error': error}), 400
	
	has_balance, balance_error = await check_sufficient_balance(from_account, amount)
	if not has_balance:
		return jsonify({'error': balance_error}), 400
	
	# Determine recipient info and status
	recipient_name = 'Unknown'
	status = 'completed'
	
	if transfer_type == 'internal':
		# Verify destination account exists and get info
		to_account_id = data.get('to_account_id')
		if not to_account_id:
			return jsonify({'error': 'Destination account required for internal transfer'}), 400
		
		to_success, to_account, to_error = await verify_account_ownership(supabase, to_account_id, user['user_id'])
		if not to_success:
			return jsonify({'error': 'Destination account not found or access denied'}), 400
		
		recipient_name = f"{to_account['account_type']} account ••••{to_account['account_number'][-4:]}"
		status = 'completed'
		
	elif transfer_type == 'external':
		external = data.get('to_external', {})
		account_num = external.get('account_number', '')
		routing_num = external.get('routing_number', '')
		
		# Validate external bank info
		if not account_num or not routing_num:
			return jsonify({'error': 'Account and routing numbers required'}), 400
		if len(routing_num) != 9 or not routing_num.isdigit():
			return jsonify({'error': 'Invalid routing number (must be 9 digits)'}), 400
		if not account_num.isdigit() or len(account_num) < 4:
			return jsonify({'error': 'Invalid account number'}), 400
		
		recipient_name = external.get('name', f"External account ••••{account_num[-4:]}")
		status = 'pending'  # External transfers take 1-3 business days
		
	elif transfer_type == 'p2p':
		external = data.get('to_external', {})
		email = external.get('email', '')
		phone = external.get('phone', '')
		
		if not email and not phone:
			return jsonify({'error': 'Email or phone required for P2P transfer'}), 400
		
		recipient_name = email or phone
		status = 'pending'  # P2P requires recipient acceptance
	
	# Create transfer record
	transfer_data = {
		'user_id': user['user_id'],
		'from_account_id': data['from_account_id'],
		'to_account_id': data.get('to_account_id'),
		'to_external': data.get('to_external', {}),
		'amount': amount,
		'transfer_type': transfer_type,
		'status': status,
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('transfers').insert(transfer_data).execute()
	
	# Debit source account
	new_from_balance = from_account['balance'] - amount
	await update_account_balance(supabase, data['from_account_id'], new_from_balance)
	
	# Create debit transaction
	tx_description = description or f"Transfer to {recipient_name}"
	await create_transaction_record(
		supabase,
		data['from_account_id'],
		'debit',
		amount,
		tx_description,
		'transfer'
	)
	
	# For internal transfers, credit destination account immediately
	if transfer_type == 'internal' and data.get('to_account_id'):
		new_to_balance = to_account['balance'] + amount
		await update_account_balance(supabase, data['to_account_id'], new_to_balance)
		
		# Create credit transaction for recipient
		await create_transaction_record(
			supabase,
			data['to_account_id'],
			'credit',
			amount,
			f"Transfer from {from_account['account_type']} account",
			'transfer'
		)
	
	# Send email notification
	html = transfer_confirmation_email(
		amount, 
		new_from_balance,
		recipient_name,
		transfer_type,
		status
	)
	await notify_user(
		supabase,
		user['user_id'],
		'transfer',
		f'Transfer of ${amount:,.2f} to {recipient_name} {status}',
		'Transfer Confirmation',
		html
	)
	
	logger.info(f"Transfer {status} for user {user['user_id']}: ${amount:.2f} ({transfer_type}) to {recipient_name}")
	return jsonify(result.data[0]), 201
