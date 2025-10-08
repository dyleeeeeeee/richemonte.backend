"""
Concierge Bank - Data Seeding Script
Generates realistic banking data for testing
Usage: python seed_new.py --email user@example.com --months 6
"""
import argparse
import random
from datetime import datetime, timedelta
from faker import Faker
from core import get_supabase_client
from utils import generate_card_number, generate_account_number, generate_cvv

fake = Faker()
supabase = get_supabase_client()


def seed_accounts(user_id: str, num_accounts: int = 3) -> list:
	"""Create bank accounts for user
	
	Args:
		user_id: User's unique identifier
		num_accounts: Number of accounts to create
	
	Returns:
		List of created account records
	"""
	account_types = ['Checking', 'Savings', 'Investment']
	accounts = []
	
	for i in range(num_accounts):
		account_data = {
			'user_id': user_id,
			'account_number': generate_account_number(),
			'account_type': account_types[i] if i < len(account_types) else random.choice(account_types),
			'balance': round(random.uniform(1000, 50000), 2),
			'currency': 'USD',
			'status': 'active',
			'created_at': (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat()
		}
		
		result = supabase.table('accounts').insert(account_data).execute()
		accounts.append(result.data[0])
		print(f"Created {account_data['account_type']} account: {account_data['account_number']}")
	
	return accounts


def seed_cards(user_id: str, num_cards: int = 3) -> list:
	"""Create credit/debit cards for user
	
	Args:
		user_id: User's unique identifier
		num_cards: Number of cards to create
	
	Returns:
		List of created card records
	"""
	card_types = ['Credit', 'Debit']
	card_brands = ['Cartier', 'Van Cleef & Arpels', 'Montblanc', 'Piaget', 'IWC']
	cards = []
	
	for i in range(num_cards):
		card_data = {
			'user_id': user_id,
			'card_number': generate_card_number(),
			'card_type': random.choice(card_types),
			'card_brand': random.choice(card_brands),
			'cvv': generate_cvv(),
			'expiry_date': (datetime.utcnow() + timedelta(days=random.randint(365, 1825))).strftime('%m/%y'),
			'credit_limit': round(random.uniform(5000, 50000), 2),
			'balance': round(random.uniform(0, 5000), 2),
			'status': 'active',
			'created_at': (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat()
		}
		
		result = supabase.table('cards').insert(card_data).execute()
		cards.append(result.data[0])
		print(f"Created {card_data['card_brand']} {card_data['card_type']} card: ****{card_data['card_number'][-4:]}")
	
	return cards


def seed_transactions(accounts: list, months: int = 2) -> None:
	"""Generate transactions for accounts
	
	Args:
		accounts: List of account records
		months: Number of months of transaction history
	"""
	categories = [
		'Jewelry', 'Travel', 'Dining', 'Shopping', 'Entertainment',
		'Groceries', 'Utilities', 'Healthcare', 'Education', 'Transfer'
	]
	
	luxury_merchants = [
		'Cartier Boutique', 'Van Cleef & Arpels', 'Montblanc Store',
		'Four Seasons Hotel', 'Ritz-Carlton', 'Louis Vuitton',
		'Hermès', 'Tiffany & Co.', 'Bulgari', 'Chopard'
	]
	
	regular_merchants = [
		'Whole Foods', 'Starbucks', 'Amazon', 'Apple Store',
		'Netflix', 'Spotify', 'Uber', 'Delta Airlines'
	]
	
	start_date = datetime.utcnow() - timedelta(days=months * 30)
	total_transactions = 0
	
	for account in accounts:
		num_transactions = random.randint(20, 100)
		
		for _ in range(num_transactions):
			is_luxury = random.random() < 0.3
			merchant = random.choice(luxury_merchants if is_luxury else regular_merchants)
			amount = round(random.uniform(500, 5000) if is_luxury else random.uniform(10, 500), 2)
			
			transaction_data = {
				'account_id': account['id'],
				'type': random.choice(['debit', 'credit']),
				'amount': amount,
				'description': f"Purchase at {merchant}",
				'merchant': merchant,
				'category': random.choice(categories),
				'created_at': (start_date + timedelta(days=random.randint(0, months * 30))).isoformat()
			}
			
			supabase.table('transactions').insert(transaction_data).execute()
			total_transactions += 1
	
	print(f"Created {total_transactions} transactions")


def seed_bills(user_id: str) -> None:
	"""Create bill payees
	
	Args:
		user_id: User's unique identifier
	"""
	bill_types = [
		('Electric Company', 'utility'),
		('Water & Sewer', 'utility'),
		('Internet Provider', 'telecom'),
		('Mobile Phone', 'telecom'),
		('Credit Card Payment', 'credit_card'),
		('Insurance Premium', 'insurance')
	]
	
	for payee_name, bill_type in bill_types:
		bill_data = {
			'user_id': user_id,
			'payee_name': payee_name,
			'account_number': fake.iban(),
			'bill_type': bill_type,
			'auto_pay': random.choice([True, False]),
			'created_at': (datetime.utcnow() - timedelta(days=random.randint(30, 180))).isoformat()
		}
		
		supabase.table('bills').insert(bill_data).execute()
	
	print(f"Created {len(bill_types)} bill payees")


def seed_checks(user_id: str, accounts: list) -> None:
	"""Create check records
	
	Args:
		user_id: User's unique identifier
		accounts: List of account records
	"""
	num_checks = random.randint(5, 15)
	
	for _ in range(num_checks):
		check_data = {
			'user_id': user_id,
			'account_id': random.choice(accounts)['id'],
			'amount': round(random.uniform(100, 5000), 2),
			'check_number': str(random.randint(1000, 9999)),
			'payee': fake.company(),
			'status': random.choice(['cleared', 'pending', 'void']),
			'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat()
		}
		
		supabase.table('checks').insert(check_data).execute()
	
	print(f"Created {num_checks} check records")


def seed_notifications(user_id: str, months: int = 2) -> None:
	"""Create notification history
	
	Args:
		user_id: User's unique identifier
		months: Number of months of notification history
	"""
	notification_types = [
		('transaction', 'Large transaction alert'),
		('transfer', 'Transfer completed'),
		('bill_payment', 'Bill payment processed'),
		('card_approved', 'Card application approved'),
		('low_balance', 'Low balance alert')
	]
	
	start_date = datetime.utcnow() - timedelta(days=months * 30)
	num_notifications = random.randint(10, 30)
	
	for _ in range(num_notifications):
		notif_type, message = random.choice(notification_types)
		notification_data = {
			'user_id': user_id,
			'type': notif_type,
			'message': message,
			'delivery_method': 'email',
			'created_at': (start_date + timedelta(days=random.randint(0, months * 30))).isoformat()
		}
		
		supabase.table('notifications').insert(notification_data).execute()
	
	print(f"Created {num_notifications} notifications")


def main():
	"""Main seeding function"""
	parser = argparse.ArgumentParser(description='Seed Concierge Bank database with test data')
	parser.add_argument('--email', required=True, help='User email address')
	parser.add_argument('--months', type=int, default=2, help='Number of months of data (2-12)')
	
	args = parser.parse_args()
	
	# Validate months
	if args.months < 2 or args.months > 12:
		print("Error: months must be between 2 and 12")
		return
	
	# Get user by email
	try:
		user_result = supabase.table('users').select('*').eq('email', args.email).single().execute()
		if not user_result.data:
			print(f"Error: User with email {args.email} not found")
			return
		
		user_id = user_result.data['id']
		print(f"\nSeeding data for user: {args.email}")
		print(f"User ID: {user_id}")
		print(f"Months of data: {args.months}\n")
		
		# Seed data
		accounts = seed_accounts(user_id)
		cards = seed_cards(user_id)
		seed_transactions(accounts, args.months)
		seed_bills(user_id)
		seed_checks(user_id, accounts)
		seed_notifications(user_id, args.months)
		
		print("\n✅ Seeding completed successfully!")
		
	except Exception as e:
		print(f"Error during seeding: {str(e)}")


if __name__ == '__main__':
	main()
