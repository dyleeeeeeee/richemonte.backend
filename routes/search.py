"""
Search routes for Concierge Bank - Global search across all entities
"""
import logging
from datetime import datetime, timedelta
from quart import Blueprint, request, jsonify
from supabase import Client

from core import get_supabase_client
from auth import require_auth

logger = logging.getLogger(__name__)
search_bp = Blueprint('search', __name__, url_prefix='/api/search')
supabase = get_supabase_client()


@search_bp.route('', methods=['GET'])
@require_auth
async def global_search(user):
	"""Global search across all user entities"""
	query = request.args.get('q', '').strip().lower()

	if not query or len(query) < 2:
		return jsonify({
			'results': [],
			'counts': {'accounts': 0, 'transactions': 0, 'cards': 0, 'bills': 0, 'beneficiaries': 0, 'notifications': 0}
		})

	results = []
	counts = {'accounts': 0, 'transactions': 0, 'cards': 0, 'bills': 0, 'beneficiaries': 0, 'notifications': 0}

	try:
		# Search accounts
		accounts = await search_accounts(supabase, user['user_id'], query)
		results.extend(accounts)
		counts['accounts'] = len(accounts)

		# Search transactions
		transactions = await search_transactions(supabase, user['user_id'], query)
		results.extend(transactions)
		counts['transactions'] = len(transactions)

		# Search cards
		cards = await search_cards(supabase, user['user_id'], query)
		results.extend(cards)
		counts['cards'] = len(cards)

		# Search bills
		bills = await search_bills(supabase, user['user_id'], query)
		results.extend(bills)
		counts['bills'] = len(bills)

		# Search beneficiaries
		beneficiaries = await search_beneficiaries(supabase, user['user_id'], query)
		results.extend(beneficiaries)
		counts['beneficiaries'] = len(beneficiaries)

		# Search notifications
		notifications = await search_notifications(supabase, user['user_id'], query)
		results.extend(notifications)
		counts['notifications'] = len(notifications)

		# Sort by relevance (accounts first, then by priority)
		results.sort(key=lambda x: (
			0 if x['type'] == 'account' else
			1 if x['type'] == 'transaction' else
			2 if x['type'] == 'card' else
			3 if x['type'] == 'bill' else
			4 if x['type'] == 'beneficiary' else
			5,  # notifications last
			-x.get('priority', 0)  # higher priority first
		))

		# Limit total results
		results = results[:20]

		logger.info(f"Search completed for user {user['user_id']}: '{query}' -> {sum(counts.values())} results")
		return jsonify({
			'results': results,
			'counts': counts,
			'query': query
		})

	except Exception as e:
		logger.error(f"Search failed for user {user['user_id']}: {e}")
		return jsonify({'error': 'Search failed', 'results': [], 'counts': counts}), 500


async def search_accounts(supabase: Client, user_id: str, query: str):
	"""Search user accounts"""
	try:
		accounts = supabase.table('accounts').select('*').eq('user_id', user_id).execute()

		results = []
		for account in accounts.data:
			if (query in account['account_number'].lower() or
				query in account['account_type'].lower() or
				query in str(account['balance'])):

				results.append({
					'id': account['id'],
					'type': 'account',
					'title': f"{account['account_type']} Account",
					'subtitle': f"••••{account['account_number'][-4:]}",
					'amount': account['balance'],
					'status': account['status'],
					'href': f"/dashboard/accounts/{account['id']}",
					'icon': 'wallet',
					'category': account['account_type'],
					'priority': 10 if query in account['account_number'] else 5
				})

		return results
	except Exception as e:
		logger.error(f"Account search failed: {e}")
		return []


async def search_transactions(supabase: Client, user_id: str, query: str):
	"""Search user transactions"""
	try:
		# Get user's account IDs first
		accounts = supabase.table('accounts').select('id').eq('user_id', user_id).execute()
		account_ids = [acc['id'] for acc in accounts.data]

		if not account_ids:
			return []

		transactions = supabase.table('transactions').select('*, accounts(account_number)').in_('account_id', account_ids).order('created_at', desc=True).limit(50).execute()

		results = []
		for tx in transactions.data:
			if (query in (tx.get('description') or '').lower() or
				query in (tx.get('merchant') or '').lower() or
				query in (tx.get('category') or '').lower() or
				query in str(tx['amount']) or
				query in tx['type'].lower()):

				# Get relative time
				created_at = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00'))
				now = datetime.now(created_at.tzinfo)
				time_diff = now - created_at

				if time_diff.days > 0:
					time_str = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
				elif time_diff.seconds > 3600:
					hours = time_diff.seconds // 3600
					time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
				else:
					minutes = max(1, time_diff.seconds // 60)
					time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"

				results.append({
					'id': tx['id'],
					'type': 'transaction',
					'title': tx.get('description') or tx.get('merchant') or 'Transaction',
					'subtitle': tx.get('merchant') or tx.get('description') or '',
					'amount': tx['amount'],
					'date': time_str,
					'href': f"/dashboard/accounts/{tx['account_id']}",
					'icon': 'arrow_up_right' if tx['type'] == 'debit' else 'arrow_down_left',
					'category': tx.get('category', 'Uncategorized'),
					'priority': 8 if query in str(tx['amount']) else 3
				})

		return results[:10]  # Limit transaction results
	except Exception as e:
		logger.error(f"Transaction search failed: {e}")
		return []


async def search_cards(supabase: Client, user_id: str, query: str):
	"""Search user cards"""
	try:
		cards = supabase.table('cards').select('*').eq('user_id', user_id).execute()

		results = []
		for card in cards.data:
			if (query in card['card_number'] or
				query in (card.get('card_brand') or '').lower() or
				query in (card.get('card_type') or '').lower()):

				results.append({
					'id': card['id'],
					'type': 'card',
					'title': f"{card.get('card_brand', 'Card')} {card['card_type']}",
					'subtitle': f"••••{card['card_number'][-4:]}",
					'amount': card.get('balance'),
					'status': card['status'],
					'href': f"/dashboard/cards/{card['id']}",
					'icon': 'credit_card',
					'category': f"{card['card_type']} Card",
					'priority': 7
				})

		return results
	except Exception as e:
		logger.error(f"Card search failed: {e}")
		return []


async def search_bills(supabase: Client, user_id: str, query: str):
	"""Search user bills"""
	try:
		bills = supabase.table('bills').select('*').eq('user_id', user_id).execute()

		results = []
		for bill in bills.data:
			if (query in bill['payee_name'].lower() or
				query in (bill.get('bill_type') or '').lower() or
				query in str(bill['amount'])):

				due_date = datetime.fromisoformat(bill['due_date'])
				now = datetime.now(due_date.tzinfo)
				days_until_due = (due_date - now).days

				if days_until_due < 0:
					date_str = f"Overdue by {abs(days_until_due)} days"
				elif days_until_due == 0:
					date_str = "Due today"
				else:
					date_str = f"Due in {days_until_due} days"

				results.append({
					'id': bill['id'],
					'type': 'bill',
					'title': bill['payee_name'],
					'subtitle': bill.get('bill_type', 'Bill Payment'),
					'amount': bill['amount'],
					'status': 'pending' if bill['auto_pay'] else 'manual',
					'date': date_str,
					'href': f"/dashboard/bills/{bill['id']}",
					'icon': 'receipt',
					'category': bill.get('bill_type', 'Bill'),
					'priority': 6
				})

		return results
	except Exception as e:
		logger.error(f"Bill search failed: {e}")
		return []


async def search_beneficiaries(supabase: Client, user_id: str, query: str):
	"""Search user beneficiaries"""
	try:
		beneficiaries = supabase.table('beneficiaries').select('*').eq('user_id', user_id).execute()

		results = []
		for beneficiary in beneficiaries.data:
			if (query in beneficiary['full_name'].lower() or
				query in beneficiary['relationship'].lower() or
				query in (beneficiary.get('email') or '').lower()):

				results.append({
					'id': beneficiary['id'],
					'type': 'beneficiary',
					'title': beneficiary['full_name'],
					'subtitle': f"{beneficiary['relationship']} • {beneficiary['percentage']}% allocation",
					'href': '/dashboard/settings/beneficiaries',
					'icon': 'users',
					'category': 'Beneficiary',
					'priority': 4
				})

		return results
	except Exception as e:
		logger.error(f"Beneficiary search failed: {e}")
		return []


async def search_notifications(supabase: Client, user_id: str, query: str):
	"""Search user notifications"""
	try:
		notifications = supabase.table('notifications').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()

		results = []
		for notification in notifications.data:
			if (query in notification['message'].lower() or
				query in notification['type'].lower() or
				query in (notification.get('title') or '').lower()):

				created_at = datetime.fromisoformat(notification['created_at'].replace('Z', '+00:00'))
				now = datetime.now(created_at.tzinfo)
				time_diff = now - created_at

				if time_diff.days > 0:
					time_str = f"{time_diff.days}d ago"
				elif time_diff.seconds > 3600:
					hours = time_diff.seconds // 3600
					time_str = f"{hours}h ago"
				else:
					minutes = max(1, time_diff.seconds // 60)
					time_str = f"{minutes}m ago"

				results.append({
					'id': notification['id'],
					'type': 'notification',
					'title': notification.get('title') or notification['type'].replace('_', ' ').title(),
					'subtitle': notification['message'][:100] + ('...' if len(notification['message']) > 100 else ''),
					'status': 'unread' if not notification['read'] else 'read',
					'date': time_str,
					'href': '/dashboard/notifications',
					'icon': 'bell',
					'category': 'Notification',
					'priority': 1
				})

		return results[:5]  # Limit notification results
	except Exception as e:
		logger.error(f"Notification search failed: {e}")
		return []
