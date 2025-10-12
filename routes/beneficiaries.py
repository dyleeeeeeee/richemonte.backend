"""
Beneficiaries routes for Concierge Bank
"""
import logging
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth

logger = logging.getLogger(__name__)
beneficiaries_bp = Blueprint('beneficiaries', __name__, url_prefix='/api/beneficiaries')
supabase = get_supabase_client()


@beneficiaries_bp.route('', methods=['GET'])
@require_auth
async def get_beneficiaries(user):
	"""Get all beneficiaries for current user"""
	try:
		result = supabase.table('beneficiaries').select('*').eq('user_id', user['user_id']).execute()
		return jsonify(result.data)
	except Exception as e:
		logger.error(f"Get beneficiaries error: {str(e)}")
		return jsonify({'error': str(e)}), 500


@beneficiaries_bp.route('', methods=['POST'])
@require_auth
async def add_beneficiary(user):
	"""Add new beneficiary"""
	data = await request.get_json()
	
	try:
		beneficiary_data = {
			'user_id': user['user_id'],
			'full_name': data['full_name'],
			'relationship': data['relationship'],
			'email': data.get('email'),
			'phone': data.get('phone'),
			'percentage': data['percentage']
		}
		
		result = supabase.table('beneficiaries').insert(beneficiary_data).execute()
		logger.info(f"Beneficiary added for user {user['user_id']}")
		return jsonify(result.data[0])
	except Exception as e:
		logger.error(f"Add beneficiary error: {str(e)}")
		return jsonify({'error': str(e)}), 500


@beneficiaries_bp.route('/<beneficiary_id>', methods=['PUT'])
@require_auth
async def update_beneficiary(user, beneficiary_id):
	"""Update beneficiary"""
	data = await request.get_json()
	
	try:
		result = supabase.table('beneficiaries').update(data).eq('id', beneficiary_id).eq('user_id', user['user_id']).execute()
		
		if not result.data:
			return jsonify({'error': 'Beneficiary not found'}), 404
			
		logger.info(f"Beneficiary {beneficiary_id} updated for user {user['user_id']}")
		return jsonify(result.data[0])
	except Exception as e:
		logger.error(f"Update beneficiary error: {str(e)}")
		return jsonify({'error': str(e)}), 500


@beneficiaries_bp.route('/<beneficiary_id>', methods=['DELETE'])
@require_auth
async def delete_beneficiary(user, beneficiary_id):
	"""Delete beneficiary"""
	try:
		result = supabase.table('beneficiaries').delete().eq('id', beneficiary_id).eq('user_id', user['user_id']).execute()
		
		if not result.data:
			return jsonify({'error': 'Beneficiary not found'}), 404
			
		logger.info(f"Beneficiary {beneficiary_id} deleted for user {user['user_id']}")
		return jsonify({'message': 'Beneficiary deleted successfully'})
	except Exception as e:
		logger.error(f"Delete beneficiary error: {str(e)}")
		return jsonify({'error': str(e)}), 500
