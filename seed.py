"""
Concierge Bank - Seed Script with Failsafes
Generates realistic historical banking data. Linus-approved: no bullshit, just working code.

Usage: python seed.py --email user@example.com --months 6
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


def get_or_create_accounts(user_id: str) -> list:
	"""Get existing accounts or create new ones with FAILSAFE
	
	Failsafe: Checks if accounts exist first. If not, creates 3 realistic ones
	with staggered creation dates for realism.
	"""
	# Check existing accounts first
	existing = supabase.table('accounts').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing accounts")
		return existing.data
	
	# Create new accounts with realistic timing
	print("No accounts found. Creating new ones...")
	account_types = ['Checking', 'Savings', 'Investment']
	accounts = []
	base_date = datetime.utcnow()
	
	for i, acc_type in enumerate(account_types):
		# Stagger account creation: oldest first (Investment), then Savings, then Checking
		days_ago = 365 - (i * 180)  # Investment: 365 days, Savings: 185 days, Checking: 5 days
		created_at = base_date - timedelta(days=days_ago)
		
		account_data = {
			'user_id': user_id,
			'account_number': generate_account_number(),
			'account_type': acc_type,
			'balance': round(random.uniform(5000, 75000) if acc_type == 'Investment' else random.uniform(1000, 25000), 2),
			'currency': 'USD',
			'status': 'active',
			'created_at': created_at.isoformat()
		}
		
		result = supabase.table('accounts').insert(account_data).execute()
		accounts.append(result.data[0])
		print(f"  Created {acc_type} account (opened {days_ago} days ago): {account_data['account_number']}")
	
	return accounts


def get_or_create_cards(user_id: str) -> list:
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
		('Credit', 'Cartier', 50000, 720),  # Oldest card, 2 years old
		('Credit', 'Van Cleef & Arpels', 35000, 365),  # 1 year old
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


def seed_realistic_transactions(accounts: list, months: int) -> None:
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
					amount = round(random.uniform(5000, 15000), 2)
					category = 'Income'
				else:
					merchant = 'Transfer In'
					amount = round(random.uniform(100, 5000), 2)
					category = 'Transfer'
			else:
				# Debits: spending
				is_luxury = random.random() < 0.15
				is_utility = random.random() < 0.1
				
				if is_utility:
					merchant = random.choice(utilities)
					amount = round(random.uniform(50, 300), 2)
					category = 'Utilities'
				elif is_luxury:
					merchant = random.choice(luxury_merchants)
					amount = round(random.uniform(800, 8000), 2)
					category = random.choice(['Jewelry', 'Travel', 'Shopping'])
				else:
					merchant = random.choice(regular_merchants)
					amount = round(random.uniform(5, 500), 2)
					category = random.choice(['Dining', 'Shopping', 'Entertainment', 'Groceries'])
			
			transaction_data = {
				'account_id': account['id'],
				'type': tx_type,
				'amount': amount,
				'description': f"{merchant}",
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
			'auto_pay': bill_type == 'utility',  # Auto-pay utilities by default
			'created_at': (datetime.utcnow() - timedelta(days=random.randint(90, 365))).isoformat()
		}
		
		supabase.table('bills').insert(bill_data).execute()
	
	print(f"  Created {len(bill_types)} bill payees")


def seed_checks(user_id: str, accounts: list) -> None:
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
		
		check_data = {
			'user_id': user_id,
			'account_id': random.choice(accounts)['id'],
			'amount': round(random.uniform(100, 5000), 2),
			'check_number': str(1001 + i),
			'payee': fake.company(),
			'status': status,
			'created_at': (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
		}
		
		supabase.table('checks').insert(check_data).execute()
	
	print(f"  Created {num_checks} check records")


def seed_notifications(user_id: str, months: int) -> None:
	"""Create notification history with FAILSAFE"""
	# Check existing
	existing = supabase.table('notifications').select('*').eq('user_id', user_id).execute()
	
	if existing.data and len(existing.data) > 0:
		print(f"Found {len(existing.data)} existing notifications")
		return
	
	print("No notifications found. Creating history...")
	
	notification_templates = [
		('transaction', 'Large Purchase Alert', 'A purchase of ${amount} was made on your {brand} card'),
		('transfer', 'Transfer Complete', 'Transfer of ${amount} has been completed successfully'),
		('bill_payment', 'Bill Payment Processed', 'Payment to {payee} for ${amount} has been processed'),
		('card_approved', 'Card Application Approved', 'Your {brand} card application has been approved'),
		('low_balance', 'Low Balance Alert', 'Your {account_type} account balance is below ${amount}'),
		('login', 'New Login Detected', 'New login to your account from {location}'),
		('security', 'Security Alert', 'Your password was changed successfully')
	]
	
	start_date = datetime.utcnow() - timedelta(days=months * 30)
	num_notifications = random.randint(15, 40)
	
	for _ in range(num_notifications):
		notif_type, title, message_template = random.choice(notification_templates)
		
		# Make messages more realistic
		message = message_template.format(
			amount=random.randint(100, 5000),
			brand=random.choice(['Cartier', 'Van Cleef & Arpels', 'Montblanc']),
			payee=random.choice(['Electric Company', 'Internet Provider']),
			account_type=random.choice(['Checking', 'Savings']),
			location='New York, NY'
		)
		
		notification_data = {
			'user_id': user_id,
			'type': notif_type,
			'title': title,
			'message': message,
			'read': random.choice([True, False]),
			'created_at': (start_date + timedelta(days=random.randint(0, months * 30))).isoformat()
		}
		
		supabase.table('notifications').insert(notification_data).execute()
	
	print(f"  Created {num_notifications} notifications")


def main():
	"""Main seeding function with failsafes"""
	parser = argparse.ArgumentParser(description='Seed Concierge Bank with realistic historical data')
	parser.add_argument('--email', help='User email address')
	parser.add_argument('--months', type=int, default=6, help='Months of history (2-12)')
	parser.add_argument('--list-users', action='store_true', help='List all users in database')
	
	args = parser.parse_args()
	
	# Handle list users command
	if args.list_users:
		print("\n" + "="*60)
		print("USERS IN DATABASE")
		print("="*60 + "\n")
		try:
			result = supabase.table('users').select('email, full_name, created_at').execute()
			if result.data:
				for user in result.data:
					print(f"  {user['email']}")
					print(f"    Name: {user.get('full_name', 'N/A')}")
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
	
	print(f"\n{'='*60}")
	print(f"CONCIERGE BANK - DATA SEEDER")
	print(f"{'='*60}")
	
	try:
		# Get user - FAILSAFE: Check if user exists (don't use .single() as it throws)
		print("Connecting to Supabase...")
		print(f"Looking up user: {args.email}")
		
		user_result = supabase.table('users').select('*').eq('email', args.email).execute()
		
		print(f"Query result: {user_result}")
		print(f"Data returned: {user_result.data}")
		print(f"Number of rows: {len(user_result.data) if user_result.data else 0}")
		
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
		
		print(f"\nUser: {args.email}")
		print(f"ID: {user_id}")
		print(f"Name: {user.get('full_name', 'N/A')}")
		print(f"History: {args.months} months\n")
		
		# Seed with failsafes
		accounts = get_or_create_accounts(user_id)
		cards = get_or_create_cards(user_id)
		seed_realistic_transactions(accounts, args.months)
		seed_bills(user_id)
		seed_checks(user_id, accounts)
		seed_notifications(user_id, args.months)
		
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
