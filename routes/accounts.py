"""
Accounts routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from utils import generate_account_number
from services import notify_user
from templates import account_created_email

logger = logging.getLogger(__name__)
accounts_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')
supabase = get_supabase_client()


@accounts_bp.route('', methods=['GET'])
@require_auth
async def get_accounts(user):
	"""Get all accounts for authenticated user"""
	accounts = supabase.table('accounts').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(accounts.data)


@accounts_bp.route('', methods=['POST'])
@require_auth
async def create_account(user):
	"""Create new account"""
	data = await request.get_json()
	
	account_number = generate_account_number()
	
	account_data = {
		'user_id': user['user_id'],
		'account_number': account_number,
		'account_type': data['account_type'],
		'balance': float(data.get('initial_deposit', 0)),
		'currency': 'USD',
		'status': 'active',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('accounts').insert(account_data).execute()
	
	# Send notification
	html = account_created_email(
		data['account_type'],
		account_number,
		float(data.get('initial_deposit', 0))
	)
	await notify_user(
		supabase,
		user['user_id'],
		'account_created',
		f'New {data["account_type"]} account created',
		'New Account Confirmation',
		html
	)
	
	logger.info(f"Account created for user {user['user_id']}: {account_number}")
	return jsonify(result.data[0]), 201


@accounts_bp.route('/<account_id>/transactions', methods=['GET'])
@require_auth
async def get_transactions(user, account_id):
	"""Get transactions for specific account"""
	# Verify account ownership
	account = supabase.table('accounts').select('*').eq('id', account_id).eq('user_id', user['user_id']).single().execute()
	if not account.data:
		return jsonify({'error': 'Account not found'}), 404
	
	transactions = supabase.table('transactions').select('*').eq('account_id', account_id).order('created_at', desc=True).execute()
	return jsonify(transactions.data)
