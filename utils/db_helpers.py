"""
Database helper utilities for common operations
Reduces code duplication across routes
"""
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)


async def verify_account_ownership(
	supabase: Client,
	account_id: str,
	user_id: str
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
	"""Verify user owns account and get account data
	
	Args:
		supabase: Supabase client instance
		account_id: Account identifier
		user_id: User identifier
	
	Returns:
		Tuple of (success, account_data, error_message)
	"""
	try:
		result = supabase.table('accounts').select('*').eq('id', account_id).eq('user_id', user_id).single().execute()
		if not result.data:
			return False, None, 'Account not found'
		return True, result.data, None
	except Exception as e:
		logger.error(f"Account verification failed: {str(e)}")
		return False, None, str(e)


async def check_sufficient_balance(
	account_data: Dict[str, Any],
	amount: float
) -> Tuple[bool, Optional[str]]:
	"""Check if account has sufficient balance
	
	Args:
		account_data: Account data dictionary
		amount: Amount to check
	
	Returns:
		Tuple of (success, error_message)
	"""
	if account_data['balance'] < amount:
		return False, 'Insufficient funds'
	return True, None


async def update_account_balance(
	supabase: Client,
	account_id: str,
	new_balance: float
) -> None:
	"""Update account balance
	
	Args:
		supabase: Supabase client instance
		account_id: Account identifier
		new_balance: New balance amount
	"""
	supabase.table('accounts').update({
		'balance': new_balance,
		'updated_at': datetime.utcnow().isoformat()
	}).eq('id', account_id).execute()


async def create_transaction_record(
	supabase: Client,
	account_id: str,
	transaction_type: str,
	amount: float,
	description: str,
	category: str = 'general',
	merchant: Optional[str] = None
) -> Dict[str, Any]:
	"""Create transaction record
	
	Args:
		supabase: Supabase client instance
		account_id: Account identifier
		transaction_type: 'debit' or 'credit'
		amount: Transaction amount
		description: Transaction description
		category: Transaction category
		merchant: Optional merchant name
	
	Returns:
		Created transaction data
	"""
	transaction_data = {
		'account_id': account_id,
		'type': transaction_type,
		'amount': amount,
		'description': description,
		'category': category,
		'created_at': datetime.utcnow().isoformat()
	}
	
	if merchant:
		transaction_data['merchant'] = merchant
	
	result = supabase.table('transactions').insert(transaction_data).execute()
	return result.data[0]


async def insert_record(
	supabase: Client,
	table: str,
	data: Dict[str, Any],
	add_timestamp: bool = True
) -> Dict[str, Any]:
	"""Generic insert with automatic timestamp
	
	Args:
		supabase: Supabase client instance
		table: Table name
		data: Data dictionary
		add_timestamp: Whether to add created_at timestamp
	
	Returns:
		Created record data
	"""
	if add_timestamp and 'created_at' not in data:
		data['created_at'] = datetime.utcnow().isoformat()
	
	result = supabase.table(table).insert(data).execute()
	return result.data[0]


async def get_user_records(
	supabase: Client,
	table: str,
	user_id: str,
	order_by: Optional[str] = None,
	desc: bool = True
) -> list:
	"""Get all records for user from table
	
	Args:
		supabase: Supabase client instance
		table: Table name
		user_id: User identifier
		order_by: Optional field to order by
		desc: Sort descending (default True)
	
	Returns:
		List of records
	"""
	query = supabase.table(table).select('*').eq('user_id', user_id)
	
	if order_by:
		query = query.order(order_by, desc=desc)
	
	result = query.execute()
	return result.data
