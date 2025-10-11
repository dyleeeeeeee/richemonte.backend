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
