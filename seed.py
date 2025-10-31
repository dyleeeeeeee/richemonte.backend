"""
Concierge Bank - Enhanced Seed Script with Wealth Context
Generates realistic historical banking data with customizable transaction magnitudes.

Usage Examples:
  python seed.py --email user@example.com --months 6
  python seed.py --email user@example.com --wealth-context wealthy
  python seed.py --email user@example.com --target-balance 34000000
  python seed.py --email user@example.com --wealth-context ultra --months 12

Wealth Contexts:
  modest    - $50K default balance, everyday transactions
  standard  - $250K default balance, mixed regular/luxury spending  
  affluent  - $2M default balance, frequent luxury purchases
  wealthy   - $10M default balance, high-value transactions
  ultra     - $50M default balance, ultra-high-net-worth patterns
"""
import argparse
import random
import sys
from datetime import datetime, timedelta
from faker import Faker
from core import get_supabase_client
from utils import generate_card_number, generate_account_number, generate_cvv

fake = Faker()
supabase = get_supabase_client()


class WealthContext:
	"""Wealth context configuration for realistic transaction generation"""
	
	def __init__(self, context_type: str = 'standard', target_balance: float = None):
		self.context_type = context_type
		self.target_balance = target_balance or self._get_default_balance(context_type)
		self.config = self._get_config(context_type)
	
	def _get_default_balance(self, context_type: str) -> float:
		"""Get default target balance for context type"""
		balances = {
			'modest': 50000,
			'standard': 250000,
			'affluent': 2000000,
			'wealthy': 10000000,
			'ultra': 50000000
		}
		return balances.get(context_type, 250000)
	
	def _get_config(self, context_type: str) -> dict:
		"""Get transaction configuration based on wealth context"""
		configs = {
			'modest': {
				'account_balance_ranges': {
					'Checking': (1000, 15000),
					'Savings': (2000, 30000),
					'Investment': (5000, 50000)
				},
				'salary_range': (3000, 8000),
				'regular_transaction_range': (5, 200),
				'luxury_transaction_range': (200, 2000),
				'utility_range': (50, 200),
				'transfer_range': (50, 2000),
				'luxury_frequency': 0.05,
				'card_limits': {'Credit': 5000, 'Debit': 0}
			},
			'standard': {
				'account_balance_ranges': {
					'Checking': (1000, 25000),
					'Savings': (5000, 75000),
					'Investment': (10000, 150000)
				},
				'salary_range': (5000, 15000),
				'regular_transaction_range': (10, 500),
				'luxury_transaction_range': (500, 8000),
				'utility_range': (100, 400),
				'transfer_range': (100, 5000),
				'luxury_frequency': 0.15,
				'card_limits': {'Credit': 25000, 'Debit': 0}
			},
			'affluent': {
				'account_balance_ranges': {
					'Checking': (5000, 100000),
					'Savings': (25000, 500000),
					'Investment': (100000, 2000000)
				},
				'salary_range': (15000, 50000),
				'regular_transaction_range': (25, 1500),
				'luxury_transaction_range': (2000, 25000),
				'utility_range': (200, 1000),
				'transfer_range': (500, 25000),
				'luxury_frequency': 0.25,
				'card_limits': {'Credit': 100000, 'Debit': 0}
			},
			'wealthy': {
				'account_balance_ranges': {
					'Checking': (10000, 500000),
					'Savings': (100000, 2000000),
					'Investment': (500000, 10000000)
				},
				'salary_range': (25000, 150000),
				'regular_transaction_range': (50, 5000),
				'luxury_transaction_range': (5000, 100000),
				'utility_range': (500, 3000),
				'transfer_range': (1000, 100000),
				'luxury_frequency': 0.35,
				'card_limits': {'Credit': 500000, 'Debit': 0}
			},
			'ultra': {
				'account_balance_ranges': {
					'Checking': (25000, 2000000),
					'Savings': (500000, 10000000),
					'Investment': (2000000, 50000000)
				},
				'salary_range': (50000, 500000),
				'regular_transaction_range': (100, 10000),
				'luxury_transaction_range': (10000, 1000000),
				'utility_range': (1000, 10000),
				'transfer_range': (5000, 1000000),
				'luxury_frequency': 0.45,
				'card_limits': {'Credit': 2000000, 'Debit': 0}
			}
		}
		return configs.get(context_type, configs['standard'])
	
	def scale_to_target(self, current_total: float) -> float:
		"""Get scaling factor to reach target balance"""
		if self.target_balance <= 0:
			return 1.0
		return self.target_balance / max(current_total, 1)
	
	def get_scaled_range(self, base_range: tuple, scale_factor: float = 1.0) -> tuple:
		"""Get scaled transaction range"""
		min_val, max_val = base_range
		return (min_val * scale_factor, max_val * scale_factor)


def get_or_create_accounts(user_id: str, wealth_context: WealthContext) -> list:
	"""Get existing accounts or create new ones with FAILSAFE
	
	Failsafe: Checks if accounts exist first. If not, creates 3 realistic ones
	with staggered creation dates for realism.
	"""
	# Check existing accounts first
	existing = supabase.table('accounts').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing accounts")
		return existing.data
	
	# Calculate scaling factor to reach target balance
	estimated_total = sum(rng[1] for rng in wealth_context.config['account_balance_ranges'].values())
	scale_factor = wealth_context.scale_to_target(estimated_total)
	
	# Create new accounts with realistic timing
	print("No accounts found. Creating new ones...")
	account_types = ['Checking', 'Savings', 'Investment']
	accounts = []
	base_date = datetime.utcnow()
	
	for i, acc_type in enumerate(account_types):
		# Stagger account creation: oldest first (Investment), then Savings, then Checking
		days_ago = 365 - (i * 180)  # Investment: 365 days, Savings: 185 days, Checking: 5 days
		created_at = base_date - timedelta(days=days_ago)
		
		# Get scaled balance range
		balance_range = wealth_context.get_scaled_range(
			wealth_context.config['account_balance_ranges'][acc_type],
			scale_factor
		)
		
		account_data = {
			'user_id': user_id,
			'account_number': generate_account_number(),
			'account_type': acc_type,
			'balance': round(random.uniform(*balance_range), 2),
			'currency': 'USD',
			'status': 'active',
			'created_at': created_at.isoformat()
		}
		
		result = supabase.table('accounts').insert(account_data).execute()
		accounts.append(result.data[0])
		print(f"  Created {acc_type} account (opened {days_ago} days ago): {account_data['account_number']}")
	
	return accounts


def get_or_create_cards(user_id: str, wealth_context: WealthContext) -> list:
	"""Get existing cards or create new ones with FAILSAFE
	
	Failsafe: Checks existing cards first. Creates realistic cards with staggered dates.
	"""
	# Check existing
	existing = supabase.table('cards').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing cards")
		return existing.data
	
	print("No cards found. Creating new ones...")
	card_configs = [
		('Credit', 'Cartier', wealth_context.config['card_limits']['Credit'], 720),  # Oldest card, 2 years old
		('Credit', 'Van Cleef & Arpels', wealth_context.config['card_limits']['Credit'] * 0.7, 365),  # 1 year old
		('Debit', 'Montblanc', 0, 90)  # Newest, 3 months old
	]
	cards = []
	base_date = datetime.utcnow()
	
	for card_type, brand, limit, days_ago in card_configs:
		created_at = base_date - timedelta(days=days_ago)
		
		card_data = {
			'user_id': user_id,
			'card_number': generate_card_number(),
			'card_type': card_type,
			'card_brand': brand,
			'cvv': generate_cvv(),
			'expiry_date': (base_date + timedelta(days=1095)).strftime('%m/%y'),  # 3 years from now
			'credit_limit': limit,
			'balance': round(random.uniform(0, limit * 0.3), 2) if card_type == 'Credit' else 0,
			'status': 'active',
			'created_at': created_at.isoformat()
		}
		
		result = supabase.table('cards').insert(card_data).execute()
		cards.append(result.data[0])
		print(f"  Created {brand} {card_type} (issued {days_ago} days ago): ****{card_data['card_number'][-4:]}")
	
	return cards


def seed_realistic_transactions(accounts: list, months: int, wealth_context: WealthContext) -> None:
	"""Generate realistic transaction patterns with proper distribution
	
	Creates transactions that look real: more recent activity, periodic payments,
	salary deposits, realistic spending patterns.
	"""
	luxury_merchants = [
		'Cartier Boutique', 'Van Cleef & Arpels', 'Montblanc Store',
		'Four Seasons Hotel', 'Ritz-Carlton', 'Louis Vuitton',
		'Hermès Paris', 'Tiffany & Co', 'Bulgari', 'Chopard Genève'
	]
	
	regular_merchants = [
		'Whole Foods Market', 'Starbucks', 'Amazon.com', 'Apple Store',
		'Netflix', 'Spotify Premium', 'Uber', 'Delta Airlines',
		'Shell Gas Station', 'CVS Pharmacy', 'AT&T Wireless'
	]
	
	utilities = ['Electric Company', 'Water Services', 'Internet Provider']
	
	base_date = datetime.utcnow()
	start_date = base_date - timedelta(days=months * 30)
	total_tx = 0
	
	print(f"Generating {months} months of transaction history...")
	
	for account in accounts:
		acc_type = account['account_type']
		
		# More transactions for checking accounts
		num_tx = random.randint(40, 150) if acc_type == 'Checking' else random.randint(10, 40)
		
		for _ in range(num_tx):
			# More recent transactions are more common (realistic behavior)
			days_ago = int(random.triangular(0, months * 30, 0))
			tx_date = base_date - timedelta(days=days_ago)
			
			# Determine transaction type and merchant
			tx_type = random.choices(['debit', 'credit'], weights=[0.7, 0.3])[0]
			
			if tx_type == 'credit':
				# Credits: salary, transfers, refunds
				if random.random() < 0.6 and acc_type == 'Checking':
					merchant = 'Salary Deposit'
					description = f'Monthly salary deposit - {fake.company()}'
					amount = round(random.uniform(*wealth_context.config['salary_range']), 2)
					category = 'Income'
				else:
					merchant = 'Transfer In'
					description = f'Funds transfer from {fake.company()}'
					amount = round(random.uniform(*wealth_context.config['transfer_range']), 2)
					category = 'Transfer'
			else:
				# Debits: spending
				is_luxury = random.random() < wealth_context.config['luxury_frequency']
				is_utility = random.random() < 0.1
				
				if is_utility:
					merchant = random.choice(utilities)
					description = f'Utility payment - {merchant}'
					amount = round(random.uniform(*wealth_context.config['utility_range']), 2)
					category = 'Utilities'
				elif is_luxury:
					merchant = random.choice(luxury_merchants)
					description = f'Purchase at {merchant}'
					amount = round(random.uniform(*wealth_context.config['luxury_transaction_range']), 2)
					category = random.choice(['Jewelry', 'Travel', 'Shopping'])
				else:
					merchant = random.choice(regular_merchants)
					description = f'Purchase at {merchant}'
					amount = round(random.uniform(*wealth_context.config['regular_transaction_range']), 2)
					category = random.choice(['Dining', 'Shopping', 'Entertainment', 'Groceries'])
			
			transaction_data = {
				'account_id': account['id'],
				'type': tx_type,
				'amount': amount,
				'description': description,
				'merchant': merchant,
				'category': category,
				'created_at': tx_date.isoformat()
			}
			
			supabase.table('transactions').insert(transaction_data).execute()
			total_tx += 1
	
	print(f"  Created {total_tx} realistic transactions")


def seed_bills(user_id: str) -> None:
	"""Create bill payees with FAILSAFE"""
	# Check existing
	existing = supabase.table('bills').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing bill payees")
		return
	
	print("No bills found. Creating payees...")
	bill_types = [
		('Con Edison Electric', 'utility'),
		('NYC Water & Sewer', 'utility'),
		('Verizon Fios', 'telecom'),
		('AT&T Wireless', 'telecom'),
		('Chase Sapphire Reserve', 'credit_card'),
		('State Farm Insurance', 'insurance')
	]
	
	for payee_name, bill_type in bill_types:
		bill_data = {
			'user_id': user_id,
			'payee_name': payee_name,
			'account_number': fake.iban(),
			'bill_type': bill_type,
			'amount': round(random.uniform(50, 500), 2),  # Realistic bill amounts
			'due_date': (datetime.utcnow() + timedelta(days=random.randint(1, 30))).date().isoformat(),  # Due within next 30 days
			'auto_pay': bill_type == 'utility',  # Auto-pay utilities by default
			'created_at': (datetime.utcnow() - timedelta(days=random.randint(90, 365))).isoformat()
		}
		
		supabase.table('bills').insert(bill_data).execute()
	
	print(f"  Created {len(bill_types)} bill payees")


def seed_checks(user_id: str, accounts: list, wealth_context: WealthContext) -> None:
	"""Create check records with FAILSAFE"""
	# Check existing
	existing = supabase.table('checks').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing checks")
		return
	
	print("No checks found. Creating history...")
	num_checks = random.randint(8, 20)
	
	for i in range(num_checks):
		# Most recent checks should be cleared, older ones can be pending
		days_ago = random.randint(5, 180)
		status = 'cleared' if days_ago > 7 else random.choice(['cleared', 'pending'])
		
		# Scale check amounts based on wealth context
		check_range = wealth_context.config['transfer_range']
		
		check_data = {
			'user_id': user_id,
			'account_id': random.choice(accounts)['id'],
			'amount': round(random.uniform(*check_range), 2),
			'check_number': str(1001 + i),
			'payee': fake.company(),
			'status': status,
			'created_at': (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
		}
		
		supabase.table('checks').insert(check_data).execute()
	
	print(f"  Created {num_checks} check records")


def seed_notifications(user_id: str, months: int, wealth_context: WealthContext) -> None:
	"""Create notification history with FAILSAFE"""
	# Check existing
	existing = supabase.table('notifications').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing notifications")
		return
	
	print("No notifications found. Creating history...")
	
	notification_templates = [
		('transaction', 'Large Purchase Alert: ${amount} spent at {brand}', 'A purchase of ${amount} was made on your {brand} card'),
		('transfer', 'Transfer Completed: ${amount}', 'Transfer of ${amount} has been completed successfully'),
		('bill_payment', 'Bill Payment Processed: ${payee}', 'Payment to {payee} for ${amount} has been processed'),
		('card_approved', 'Card Application Approved', 'Your {brand} card application has been approved'),
		('low_balance', 'Low Balance Alert', 'Your {account_type} account balance is below ${amount}'),
		('login', 'New Login Detected', 'New login to your account from {location}'),
		('security', 'Security Alert', 'Your password was changed successfully')
	]
	
	start_date = datetime.utcnow() - timedelta(days=months * 30)
	num_notifications = random.randint(15, 40)
	
	for _ in range(num_notifications):
		notif_type, title_template, message_template = random.choice(notification_templates)
		
		# Make messages more realistic based on wealth context
		max_notification_amount = int(wealth_context.config['luxury_transaction_range'][1] * 0.8)
		min_notification_amount = int(wealth_context.config['regular_transaction_range'][1])
		
		message = message_template.format(
			amount=random.randint(min_notification_amount, max_notification_amount),
			brand=random.choice(['Cartier', 'Van Cleef & Arpels', 'Montblanc']),
			payee=random.choice(['Electric Company', 'Internet Provider']),
			account_type=random.choice(['Checking', 'Savings']),
			location='New York, NY'
		)
		
		notification_data = {
			'user_id': user_id,
			'type': notif_type,
			'message': message,
			'delivery_method': 'push',  # Default to push notifications
			'read': random.choice([True, False]),
			'created_at': (start_date + timedelta(days=random.randint(0, months * 30))).isoformat()
		}
		
		supabase.table('notifications').insert(notification_data).execute()
	
	print(f"  Created {num_notifications} notifications")


def seed_users():
	"""Seed test users including admin - only called when seeding existing user"""
	# This function is called during seeding to ensure the target user has proper fields
	# It doesn't create new users, just ensures existing ones have role/account_status
	pass


def main():
	"""Main seeding function with failsafes"""
	parser = argparse.ArgumentParser(description='Seed Concierge Bank with realistic historical data')
	parser.add_argument('--email', help='User email address')
	parser.add_argument('--months', type=int, default=6, help='Months of history (2-12)')
	parser.add_argument('--list-users', action='store_true', help='List all users in database')
	parser.add_argument('--wealth-context', choices=['modest', 'standard', 'affluent', 'wealthy', 'ultra'], 
					   default='standard', help='Wealth context for transaction magnitudes')
	parser.add_argument('--target-balance', type=float, help='Target total balance (overrides wealth-context default)')
	
	args = parser.parse_args()
	
	# Handle list users command
	if args.list_users:
		print("\n" + "="*60)
		print("USERS IN DATABASE")
		print("="*60 + "\n")
		try:
			result = supabase.table('users').select('email, full_name, role, created_at').execute()
			if result.data:
				for user in result.data:
					print(f"  {user['email']}")
					print(f"    Name: {user.get('full_name', 'N/A')}")
					print(f"    Role: {user.get('role', 'user')}")
					print(f"    Created: {user.get('created_at', 'N/A')}")
					print()
				print(f"Total: {len(result.data)} users\n")
			else:
				print("  No users found in database\n")
		except Exception as e:
			print(f"Error: {e}\n")
		return
	
	# Require email for seeding
	if not args.email:
		print("ERROR: --email is required (or use --list-users)")
		sys.exit(1)
	
	# Validate input
	if args.months < 2 or args.months > 12:
		print("ERROR: Months must be between 2 and 12")
		sys.exit(1)
	
	if args.target_balance is not None and args.target_balance <= 0:
		print("ERROR: Target balance must be greater than 0")
		sys.exit(1)
	
	# Show wealth context info
	if args.target_balance:
		print(f"Custom target balance: ${args.target_balance:,.2f}")
	else:
		default_balance = WealthContext(args.wealth_context)._get_default_balance(args.wealth_context)
		print(f"Wealth context '{args.wealth_context}' with default target: ${default_balance:,.2f}")
	
	print(f"\n{'='*60}")
	print(f"CONCIERGE BANK - DATA SEEDER")
	print(f"{'='*60}")
	
	try:
		# Get user - FAILSAFE: Check if user exists (don't use .single() as it throws)
		print("Connecting to Supabase...")
		print(f"Looking up user: {args.email}")
		
		user_result = supabase.table('users').select('*').eq('email', args.email).execute()
		
		if not user_result.data or len(user_result.data) == 0:
			print(f"\n{'='*60}")
			print(f"❌ ERROR: User '{args.email}' not found in database")
			print(f"{'='*60}")
			print("\nDEBUG INFO:")
			print(f"  Supabase URL: {supabase.supabase_url}")
			print(f"  Query executed: users.select('*').eq('email', '{args.email}')")
			print(f"  Result count: 0 rows")
			print("\nPossible issues:")
			print("  1. User hasn't registered yet")
			print("  2. Email spelling is different in database")
			print("  3. Supabase connection issue")
			print("\nTroubleshooting:")
			print("  1. Check Supabase dashboard to see if user exists")
			print("  2. Register via: http://localhost:3000/register")
			print(f"\n{'='*60}\n")
			sys.exit(1)
		
		user = user_result.data[0]
		user_id = user['id']
		
		print(f"User: {args.email}")
		print(f"ID: {user_id}")
		print(f"Name: {user.get('full_name', 'N/A')}")
		print(f"Role: {user.get('role', 'user')}")
		print(f"Wealth Context: {args.wealth_context}")
		if args.target_balance:
			print(f"Target Balance: ${args.target_balance:,.2f}")
		print(f"History: {args.months} months\n")
		
		# Initialize wealth context
		wealth_context = WealthContext(args.wealth_context, args.target_balance)
		print(f"Context Configuration: {wealth_context.context_type}")
		print(f"Expected Range: ${wealth_context._get_default_balance(args.wealth_context):,.2f} default balance")
		print()
		
		# Seed with failsafes
		accounts = get_or_create_accounts(user_id, wealth_context)
		cards = get_or_create_cards(user_id, wealth_context)
		seed_realistic_transactions(accounts, args.months, wealth_context)
		seed_bills(user_id)
		seed_checks(user_id, accounts, wealth_context)
		seed_notifications(user_id, args.months, wealth_context)
		
		print(f"\n{'='*60}")
		print("✅ SEEDING COMPLETE")
		print(f"{'='*60}\n")
		
	except KeyboardInterrupt:
		print("\n\nInterrupted by user")
		sys.exit(1)
	except Exception as e:
		print(f"\nFATAL ERROR: {str(e)}")
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == '__main__':
	main()
