"""
Cards routes for Concierge Bank
"""
import logging
from datetime import datetime, timedelta
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from core.config import CARD_EXPIRY_DAYS
from auth import require_auth
from utils import generate_card_number, generate_cvv
from services import notify_user
from templates import card_approved_email

logger = logging.getLogger(__name__)
cards_bp = Blueprint('cards', __name__, url_prefix='/api/cards')
supabase = get_supabase_client()


@cards_bp.route('', methods=['GET'])
@require_auth
async def get_cards(user):
	"""Get all cards for authenticated user"""
	cards = supabase.table('cards').select('*').eq('user_id', user['user_id']).execute()
	return jsonify(cards.data)


@cards_bp.route('/apply', methods=['POST'])
@require_auth
async def apply_card(user):
	"""Apply for new card"""
	data = await request.get_json()
	
	# Validate required fields
	if not data.get('card_type'):
		return jsonify({'error': 'Card type is required'}), 400
	
	# Validate card type
	valid_card_types = ['Debit', 'Credit', 'Platinum', 'Black Card']
	if data['card_type'] not in valid_card_types:
		return jsonify({'error': f'Invalid card type. Must be one of: {", ".join(valid_card_types)}'}), 400
	
	# Validate credit limit
	try:
		credit_limit = float(data.get('credit_limit', 10000))
	except (ValueError, TypeError):
		return jsonify({'error': 'Invalid credit limit format'}), 400
	
	if credit_limit < 1000:
		return jsonify({'error': 'Credit limit must be at least $1,000'}), 400
	if credit_limit > 1000000:
		return jsonify({'error': 'Credit limit cannot exceed $1,000,000'}), 400
	
	card_number = generate_card_number()
	cvv = generate_cvv()
	
	card_data = {
		'user_id': user['user_id'],
		'card_number': card_number,
		'card_type': data['card_type'],
		'card_brand': data.get('card_brand', 'Cartier'),
		'cvv': cvv,
		'expiry_date': (datetime.utcnow() + timedelta(days=CARD_EXPIRY_DAYS)).strftime('%m/%y'),
		'credit_limit': credit_limit,
		'balance': 0,
		'status': 'approved',
		'created_at': datetime.utcnow().isoformat()
	}
	
	result = supabase.table('cards').insert(card_data).execute()
	
	# Send notification
	html = card_approved_email(
		data.get('card_brand', 'Cartier'),
		data['card_type'],
		card_number[-4:],
		float(data.get('credit_limit', 10000))
	)
	await notify_user(
		supabase,
		user['user_id'],
		'card_approved',
		f'{data["card_type"]} card approved',
		'Card Application Approved',
		html
	)
	
	logger.info(f"Card approved for user {user['user_id']}: ****{card_number[-4:]}")
	return jsonify(result.data[0]), 201


@cards_bp.route('/<card_id>/lock', methods=['POST'])
@require_auth
async def lock_card(user, card_id):
	"""Lock or unlock card"""
	data = await request.get_json()
	locked = data.get('locked', True)
	
	result = supabase.table('cards').update({
		'status': 'locked' if locked else 'active'
	}).eq('id', card_id).eq('user_id', user['user_id']).execute()
	
	return jsonify(result.data[0])


@cards_bp.route('/<card_id>/report-issue', methods=['POST'])
@require_auth
async def report_card_issue(user, card_id):
	"""Report card issue (lost, stolen, damaged)"""
	data = await request.get_json()

	# Verify card ownership
	card = supabase.table('cards').select('*').eq('id', card_id).eq('user_id', user['user_id']).execute()
	if not card.data:
		return jsonify({'error': 'Card not found'}), 404

	# Create issue report
	report_data = {
		'user_id': user['user_id'],
		'card_id': card_id,
		'issue_type': data['issue_type'],
		'description': data.get('description', ''),
		'status': 'investigating',
		'created_at': datetime.utcnow().isoformat()
	}

	report_result = supabase.table('card_issue_reports').insert(report_data).execute()

	# Update card status to reported
	supabase.table('cards').update({
		'status': 'reported',
		'updated_at': datetime.utcnow().isoformat()
	}).eq('id', card_id).execute()

	# Send notification to user
	await notify_user(
		supabase,
		user['user_id'],
		'card_issue_reported',
		f'Your {card.data[0]["card_brand"]} {card.data[0]["card_type"]} card has been reported as {data["issue_type"]}.',
		'Card Issue Reported',
		f'<p>Your card ending in ****{card.data[0]["card_number"][-4:]} has been reported as {data["issue_type"]}.</p><p>Our security team will investigate and contact you within 24 hours.</p><p>For your protection, the card has been temporarily suspended.</p>'
	)

	# Send alert to admins (could be enhanced to send emails/SMS)
	admin_users = supabase.table('users').select('id').eq('role', 'admin').execute()
	for admin in admin_users.data:
		await notify_user(
			supabase,
			admin['id'],
			'admin_card_issue_alert',
			f'Card issue reported: {data["issue_type"]} - User {user["user_id"]} - Card ****{card.data[0]["card_number"][-4:]}',
			'Card Issue Alert',
			f'<p>A card issue has been reported that requires admin attention.</p><p>User: {user["user_id"]}</p><p>Card: ****{card.data[0]["card_number"][-4:]}</p><p>Issue: {data["issue_type"]}</p><p>Description: {data.get("description", "None")}</p>'
		)

	logger.info(f"Card issue reported for user {user['user_id']}: {data['issue_type']} - Card ****{card.data[0]['card_number'][-4:]}")
	return jsonify({'message': 'Card issue reported successfully', 'report_id': report_result.data[0]['id']})


@cards_bp.route('/admin/issue-reports', methods=['GET'])
@require_auth
async def get_card_issue_reports(user):
	"""Get all card issue reports (admin only)"""
	if user.get('role') != 'admin':
		return jsonify({'error': 'Admin access required'}), 403

	reports = supabase.table('card_issue_reports').select('*, cards(card_number, card_brand, card_type), users(full_name, email)').execute()
	return jsonify(reports.data)


@cards_bp.route('/admin/issue-reports/<report_id>/resolve', methods=['POST'])
@require_auth
async def resolve_card_issue_report(user, report_id):
	"""Resolve a card issue report (admin only)"""
	if user.get('role') != 'admin':
		return jsonify({'error': 'Admin access required'}), 403

	data = await request.get_json()
	action = data.get('action', 'resolve')  # 'resolve' or 'block'
	admin_notes = data.get('admin_notes', '')

	# Get the report
	report = supabase.table('card_issue_reports').select('*').eq('id', report_id).execute()
	if not report.data:
		return jsonify({'error': 'Report not found'}), 404

	report_data = report.data[0]

	# Update report status
	if action == 'block':
		supabase.table('card_issue_reports').update({
			'status': 'card_blocked',
			'admin_notes': admin_notes,
			'resolved_at': datetime.utcnow().isoformat()
		}).eq('id', report_id).execute()

		# Block the card permanently
		supabase.table('cards').update({
			'status': 'blocked',
			'updated_at': datetime.utcnow().isoformat()
		}).eq('id', report_data['card_id']).execute()

		# Notify user
		await notify_user(
			supabase,
			report_data['user_id'],
			'card_blocked',
			'Your reported card has been permanently blocked for security reasons.',
			'Card Permanently Blocked',
			f'<p>Your card ending in ****{report_data["card_id"]} has been permanently blocked.</p><p>Reason: Reported as {report_data["issue_type"]}</p><p>A replacement card will be issued within 3-5 business days.</p>'
		)

	else:  # resolve - issue the new card
		supabase.table('card_issue_reports').update({
			'status': 'resolved',
			'admin_notes': admin_notes,
			'resolved_at': datetime.utcnow().isoformat()
		}).eq('id', report_id).execute()

		# Generate new card for the user
		new_card_number = generate_card_number()
		new_cvv = generate_cvv()

		supabase.table('cards').update({
			'card_number': new_card_number,
			'cvv': new_cvv,
			'expiry_date': (datetime.utcnow() + timedelta(days=CARD_EXPIRY_DAYS)).strftime('%m/%y'),
			'status': 'active',
			'updated_at': datetime.utcnow().isoformat()
		}).eq('id', report_data['card_id']).execute()

		# Notify user of new card
		await notify_user(
			supabase,
			report_data['user_id'],
			'card_replaced',
			'Your card has been replaced and is now active.',
			'New Card Issued',
			f'<p>Your new card ending in ****{new_card_number[-4:]} is now active and will arrive within 3-5 business days.</p><p>Your CVV and card details are available in your dashboard under Cards.</p><p>Please update any recurring payments with the new card details.</p>'
		)

	logger.info(f"Card issue report {report_id} resolved by admin {user['user_id']}: {action}")
	return jsonify({'message': f'Card issue report {action}ed successfully'})
