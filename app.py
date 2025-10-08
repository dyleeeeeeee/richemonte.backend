"""
Concierge Bank - Modular Quart Backend Application
Luxury banking platform with Supabase and Resend integration

Directory Structure:
backend/
├── core/           # Configuration and database
├── auth/           # Authentication logic
├── utils/          # Utility functions
├── services/       # Business logic
├── templates/      # Email templates
└── app_new.py      # Main application (this file)
"""
import logging
from datetime import datetime, timedelta
from quart import Quart, request, jsonify, make_response
from quart_cors import cors

# Core imports
from core import get_supabase_client
from core.config import FRONTEND_URL, JWT_EXPIRATION_HOURS, CARD_EXPIRY_DAYS

# Auth imports
from auth import create_jwt_token, require_auth

# Utility imports
from utils import generate_card_number, generate_account_number, generate_cvv

# Service imports
from services import send_email, log_notification, get_user_email

# Template imports
from templates import (
	welcome_email,
	account_created_email,
	card_approved_email,
	transfer_confirmation_email,
	bill_payment_email,
	check_deposit_email,
	check_order_email
)

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin=FRONTEND_URL, allow_credentials=True)

# Get Supabase client
supabase = get_supabase_client()


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
async def register():
	"""Register new user
	
	Request Body:
		{
			"email": str,
			"password": str,
			"full_name": str (optional),
			"phone": str (optional),
			"address": str (optional),
			"preferred_brand": str (optional, default: "Cartier")
		}
	
	Response:
		{
			"message": "Registration successful",
			"user": {
				"id": str,
				"email": str,
				"full_name": str
			}
		}
	"""
	data = await request.get_json()
	
	try:
		# Create user in Supabase Auth
		auth_response = supabase.auth.sign_up({
			'email': data['email'],
			'password': data['password']
		})
		
		if not auth_response.user:
			return jsonify({'error': 'Registration failed'}), 400
		
		# Create user profile in users table
		profile_data = {
			'id': auth_response.user.id,
			'email': data['email'],
			'full_name': data.get('full_name', ''),
			'phone': data.get('phone', ''),
			'address': data.get('address', ''),
			'preferred_brand': data.get('preferred_brand', 'Cartier'),
			'created_at': datetime.utcnow().isoformat()
		}
		
		supabase.table('users').insert(profile_data).execute()
		
		# Send welcome email
		html = welcome_email(data.get('full_name', ''))
		await send_email(data['email'], 'Welcome to Concierge Bank', html)
		await log_notification(supabase, auth_response.user.id, 'registration', 'Welcome email sent')
		
		# Create JWT token
		token = create_jwt_token(auth_response.user.id, data['email'])
		
		response = await make_response(jsonify({
			'message': 'Registration successful',
			'user': {
				'id': auth_response.user.id,
				'email': data['email'],
				'full_name': data.get('full_name', '')
			}
		}))
		
		response.set_cookie(
			'auth_token',
			token,
			httponly=True,
			secure=True,
			samesite='lax',
			max_age=JWT_EXPIRATION_HOURS * 3600
		)
		
		logger.info(f"User registered successfully: {data['email']}")
		return response
		
	except Exception as e:
		logger.error(f"Registration error: {str(e)}")
		return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
async def login():
	"""Login user
	
	Request Body:
		{
			"email": str,
			"password": str
		}
	
	Response:
		{
			"message": "Login successful",
			"user": {user_profile_data}
		}
	"""
	data = await request.get_json()
	
	try:
		# Authenticate with Supabase
		auth_response = supabase.auth.sign_in_with_password({
			'email': data['email'],
			'password': data['password']
		})
		
		if not auth_response.user:
			return jsonify({'error': 'Invalid credentials'}), 401
		
		# Get user profile from users table
		user_data = supabase.table('users').select('*').eq('id', auth_response.user.id).single().execute()
		
		# Create JWT token
		token = create_jwt_token(auth_response.user.id, data['email'])
		
		response = await make_response(jsonify({
			'message': 'Login successful',
			'user': user_data.data
		}))
		
		response.set_cookie(
			'auth_token',
			token,
			httponly=True,
			secure=True,
			samesite='lax',
			max_age=JWT_EXPIRATION_HOURS * 3600
		)
		
		logger.info(f"User logged in: {data['email']}")
		return response
		
	except Exception as e:
		logger.error(f"Login error: {str(e)}")
		return jsonify({'error': str(e)}), 401


@app.route('/api/auth/logout', methods=['POST'])
async def logout():
	"""Logout user"""
	response = await make_response(jsonify({'message': 'Logged out successfully'}))
	response.set_cookie('auth_token', '', expires=0)
	return response


@app.route('/api/auth/me', methods=['GET'])
@require_auth
async def get_me(user):
	"""Get current user profile
	
	Response:
		{user_profile_data from users table}
	"""
	user_data = supabase.table('users').select('*').eq('id', user['user_id']).single().execute()
	return jsonify(user_data.data)


# ==================== ACCOUNTS ROUTES ====================

@app.route('/api/accounts', methods=['GET'])
@require_auth
async def get_accounts(user):
	"""Get all accounts for authenticated user
	
	Response:
		[
			{
				"id": str,
				"user_id": str,
				"account_number": str (12 digits),
				"account_type": str ("Checking" | "Savings" | "Investment"),
				"balance": float,
				"currency": str,
				"status": str,
				"created_at": str (ISO timestamp)
			}
		]
	"""
	accounts = supabase.table('accounts').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(accounts.data)


@app.route('/api/accounts', methods=['POST'])
@require_auth
async def create_account(user):
	"""Create new account
	
	Request Body:
		{
			"account_type": str ("Checking" | "Savings" | "Investment"),
			"initial_deposit": float (optional, default: 0)
		}
	
	Response:
		{account_data from accounts table}
	"""
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
	
	# Send confirmation email
	email = await get_user_email(supabase, user['user_id'])
	if email:
		html = account_created_email(
			data['account_type'],
			account_number,
			float(data.get('initial_deposit', 0))
		)
		await send_email(email, 'New Account Confirmation', html)
		await log_notification(supabase, user['user_id'], 'account_created', f'New {data["account_type"]} account created')
	
	logger.info(f"Account created for user {user['user_id']}: {account_number}")
	return jsonify(result.data[0]), 201


@app.route('/api/accounts/<account_id>/transactions', methods=['GET'])
@require_auth
async def get_transactions(user, account_id):
	"""Get transactions for specific account
	
	Response:
		[
			{
				"id": str,
				"account_id": str,
				"type": str ("debit" | "credit"),
				"amount": float,
				"description": str,
				"merchant": str (optional),
				"category": str,
				"created_at": str (ISO timestamp)
			}
		]
	"""
	# Verify account ownership
	account = supabase.table('accounts').select('*').eq('id', account_id).eq('user_id', user['user_id']).single().execute()
	if not account.data:
		return jsonify({'error': 'Account not found'}), 404
	
	transactions = supabase.table('transactions').select('*').eq('account_id', account_id).order('created_at', desc=True).execute()
	return jsonify(transactions.data)


# ==================== CARDS ROUTES ====================

@app.route('/api/cards', methods=['GET'])
@require_auth
async def get_cards(user):
	"""Get all cards for authenticated user
	
	Response:
		[
			{
				"id": str,
				"user_id": str,
				"card_number": str (16 digits, Luhn valid),
				"card_type": str ("Credit" | "Debit"),
				"card_brand": str ("Cartier" | "Van Cleef & Arpels" | "Montblanc" | "Piaget" | "IWC"),
				"cvv": str (3 digits),
				"expiry_date": str ("MM/YY"),
				"credit_limit": float,
				"balance": float,
				"status": str ("active" | "locked" | "approved"),
				"created_at": str (ISO timestamp)
			}
		]
	"""
	cards = supabase.table('cards').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(cards.data)


@app.route('/api/cards/apply', methods=['POST'])
@require_auth
async def apply_card(user):
	"""Apply for new card
	
	Request Body:
		{
			"card_type": str ("Credit" | "Debit"),
			"card_brand": str (optional, default: "Cartier"),
			"credit_limit": float (optional, default: 10000)
		}
	
	Response:
		{card_data from cards table}
	"""
	data = await request.get_json()
	
	card_number = generate_card_number()
	cvv = generate_cvv()
	
	card_data = {
		'user_id': user['user_id'],
		'card_number': card_number,
		'card_type': data['card_type'],
		'card_brand': data.get('card_brand', 'Cartier'),
		'cvv': cvv,
		'expiry_date': (datetime.utcnow() + timedelta(days=CARD_EXPIRY_DAYS)).strftime('%m/%y'),
		'credit_limit': float(data.get('credit_limit', 10000)),
		'balance': 0,
		'status': 'approved',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('cards').insert(card_data).execute()
	
	# Send approval email
	email = await get_user_email(supabase, user['user_id'])
	if email:
		html = card_approved_email(
			data.get('card_brand', 'Cartier'),
			data['card_type'],
			card_number[-4:],
			float(data.get('credit_limit', 10000))
		)
		await send_email(email, 'Card Application Approved', html)
		await log_notification(supabase, user['user_id'], 'card_approved', f'{data["card_type"]} card approved')
	
	logger.info(f"Card approved for user {user['user_id']}: ****{card_number[-4:]}")
	return jsonify(result.data[0]), 201


@app.route('/api/cards/<card_id>/lock', methods=['POST'])
@require_auth
async def lock_card(user, card_id):
	"""Lock or unlock card
	
	Request Body:
		{
			"locked": bool (true to lock, false to unlock)
		}
	
	Response:
		{updated_card_data}
	"""
	data = await request.get_json()
	locked = data.get('locked', True)
	
	result = supabase.table('cards').update({
		'status': 'locked' if locked else 'active'
	}).eq('id', card_id).eq('user_id', user['user_id']).execute()
	
	return jsonify(result.data[0])


# ==================== TRANSFERS ROUTES ====================

@app.route('/api/transfers', methods=['POST'])
@require_auth
async def create_transfer(user):
	"""Create transfer
	
	Request Body:
		{
			"from_account_id": str,
			"to_account_id": str (optional, for internal),
			"to_external": dict (optional, for external/P2P),
			"amount": float,
			"transfer_type": str ("internal" | "external" | "p2p")
		}
	
	Response:
		{transfer_data from transfers table}
	"""
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


# ==================== BILLS ROUTES ====================

@app.route('/api/bills', methods=['GET'])
@require_auth
async def get_bills(user):
	"""Get all bill payees for authenticated user
	
	Response:
		[
			{
				"id": str,
				"user_id": str,
				"payee_name": str,
				"account_number": str,
				"bill_type": str ("utility" | "telecom" | "credit_card" | "insurance" | "other"),
				"auto_pay": bool,
				"created_at": str (ISO timestamp)
			}
		]
	"""
	bills = supabase.table('bills').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(bills.data)


@app.route('/api/bills', methods=['POST'])
@require_auth
async def add_bill(user):
	"""Add bill payee
	
	Request Body:
		{
			"payee_name": str,
			"account_number": str (optional),
			"bill_type": str (optional, default: "utility"),
			"auto_pay": bool (optional, default: false)
		}
	
	Response:
		{bill_data from bills table}
	"""
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


@app.route('/api/bills/<bill_id>/pay', methods=['POST'])
@require_auth
async def pay_bill(user, bill_id):
	"""Pay bill
	
	Request Body:
		{
			"account_id": str,
			"amount": float,
			"payment_date": str (optional, ISO timestamp)
		}
	
	Response:
		{payment_data from bill_payments table}
	"""
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


# ==================== CHECKS ROUTES ====================

@app.route('/api/checks', methods=['GET'])
@require_auth
async def get_checks(user):
	"""Get all checks for authenticated user
	
	Response:
		[
			{
				"id": str,
				"user_id": str,
				"account_id": str,
				"check_number": str,
				"amount": float,
				"payee": str (optional),
				"status": str ("pending" | "cleared" | "rejected" | "void"),
				"created_at": str (ISO timestamp)
			}
		]
	"""
	checks = supabase.table('checks').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(checks.data)


@app.route('/api/checks/deposit', methods=['POST'])
@require_auth
async def deposit_check(user):
	"""Deposit check
	
	Request Body:
		{
			"account_id": str,
			"amount": float,
			"check_number": str (optional)
		}
	
	Response:
		{check_data from checks table}
	"""
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


@app.route('/api/checks/order', methods=['POST'])
@require_auth
async def order_checks(user):
	"""Order checks
	
	Request Body:
		{
			"account_id": str,
			"design": str (optional, default: "Standard"),
			"quantity": int (optional, default: 50),
			"price": float (optional, default: 29.99)
		}
	
	Response:
		{order_data from check_orders table}
	"""
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


# ==================== NOTIFICATIONS ROUTES ====================

@app.route('/api/notifications', methods=['GET'])
@require_auth
async def get_notifications(user):
	"""Get user notifications
	
	Response:
		[
			{
				"id": str,
				"user_id": str,
				"type": str,
				"message": str,
				"delivery_method": str,
				"created_at": str (ISO timestamp)
			}
		]
	"""
	notifications = supabase.table('notifications').select('*').eq('user_id', user['user_id']).order('created_at', desc=True).limit(50).execute()
	return jsonify(notifications.data)


# ==================== SETTINGS ROUTES ====================

@app.route('/api/settings', methods=['GET'])
@require_auth
async def get_settings(user):
	"""Get user settings (same as user profile)
	
	Response:
		{user_profile_data from users table}
	"""
	user_data = supabase.table('users').select('*').eq('id', user['user_id']).single().execute()
	return jsonify(user_data.data)


@app.route('/api/settings', methods=['PUT'])
@require_auth
async def update_settings(user):
	"""Update user settings
	
	Request Body:
		{
			"full_name": str (optional),
			"phone": str (optional),
			"address": str (optional),
			"preferred_brand": str (optional)
		}
	
	Response:
		{updated_user_data}
	"""
	data = await request.get_json()
	
	result = supabase.table('users').update(data).eq('id', user['user_id']).execute()
	logger.info(f"Settings updated for user {user['user_id']}")
	return jsonify(result.data[0])


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
async def health_check():
	"""Health check endpoint
	
	Response:
		{
			"status": "healthy",
			"timestamp": str (ISO timestamp)
		}
	"""
	return jsonify({
		'status': 'healthy',
		'timestamp': datetime.utcnow().isoformat()
	})


if __name__ == '__main__':
	app.run(debug=True)
