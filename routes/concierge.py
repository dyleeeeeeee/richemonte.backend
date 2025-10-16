"""
Concierge routes for Concierge Bank - AI assistant and service requests
"""
import logging
import json
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from services import notify_user

logger = logging.getLogger(__name__)
concierge_bp = Blueprint('concierge', __name__, url_prefix='/api/concierge')
supabase = get_supabase_client()


@concierge_bp.route('/chat', methods=['POST'])
@require_auth
async def send_message(user):
	"""Send message to AI concierge assistant"""
	data = await request.get_json()
	message = data.get('message', '').strip()

	if not message:
		return jsonify({'error': 'Message cannot be empty'}), 400

	# In a real implementation, this would integrate with OpenAI or similar
	# For now, return a simulated response based on message content
	response_text = generate_concierge_response(message)

	# Store conversation in database (optional)
	conversation_data = {
		'user_id': user['user_id'],
		'message': message,
		'response': response_text,
		'timestamp': json.dumps({'created_at': 'now()'})
	}

	# For demo purposes, we'll just return the response without storing
	# In production, you'd want to store conversations

	concierge_message = {
		'id': 'temp_' + str(hash(message)),  # Temporary ID for demo
		'user_id': user['user_id'],
		'message': message,
		'response': response_text,
		'timestamp': '2024-01-01T00:00:00Z'  # Demo timestamp
	}

	logger.info(f"Concierge chat: User {user['user_id']} - {message[:50]}...")
	return jsonify(concierge_message)


@concierge_bp.route('/request', methods=['POST'])
@require_auth
async def create_request(user):
	"""Create a concierge service request"""
	data = await request.get_json()

	request_type = data.get('type', '')
	details = data.get('details', '').strip()

	if not request_type or not details:
		return jsonify({'error': 'Request type and details are required'}), 400

	# Store the request in database (you'd want a concierge_requests table)
	request_data = {
		'user_id': user['user_id'],
		'request_type': request_type,
		'details': details,
		'status': 'pending',
		'created_at': 'now()'
	}

	# For demo, we'll simulate storing and notify
	request_id = 'req_' + str(hash(f"{user['user_id']}{request_type}{details}"))

	# Send notification to user
	await notify_user(
		supabase,
		user['user_id'],
		'concierge_request',
		f'Your {request_type} request has been submitted. Our concierge team will contact you within 24 hours.',
		'Concierge Request Submitted',
		f'<p>Thank you for your {request_type} request.</p><p><strong>Details:</strong> {details}</p><p>Our concierge team will review your request and contact you within 24 hours.</p>'
	)

	# Send notification to admin/concierge team
	admin_users = supabase.table('users').select('id').eq('role', 'admin').execute()
	for admin in admin_users.data:
		await notify_user(
			supabase,
			admin['id'],
			'concierge_request_alert',
			f'New concierge request: {request_type} from user {user["user_id"]}',
			'New Concierge Request',
			f'<p><strong>Request Type:</strong> {request_type}</p><p><strong>User:</strong> {user["user_id"]}</p><p><strong>Details:</strong> {details}</p><p>Please review and respond promptly.</p>'
		)

	logger.info(f"Concierge request created: {request_type} - User {user['user_id']}")
	return jsonify({
		'id': request_id,
		'type': request_type,
		'details': details,
		'status': 'pending',
		'message': 'Your concierge request has been submitted successfully'
	}), 201


def generate_concierge_response(message: str) -> str:
	"""Generate simulated AI concierge responses based on message content"""

	message_lower = message.lower()

	# Banking questions
	if any(word in message_lower for word in ['balance', 'account', 'checking', 'savings']):
		return "I'd be happy to help you with your account information. You can view your account balances and transaction history in your dashboard. For security reasons, I can't provide specific balance information here. Is there anything specific about your accounts you'd like to know?"

	elif any(word in message_lower for word in ['transfer', 'send money', 'wire']):
		return "For transfers and payments, you have several options through your Concierge Bank dashboard: internal transfers between your accounts, external transfers to other banks, bill payments, and check deposits. Would you like me to guide you through any of these processes?"

	elif any(word in message_lower for word in ['card', 'credit', 'debit', 'atm']):
		return "Your Concierge Bank cards offer premium benefits including worldwide acceptance, contactless payments, and concierge support. You can manage your cards, report lost/stolen cards, and set spending limits through your dashboard. How can I assist with your cards?"

	# Investment/wealth management
	elif any(word in message_lower for word in ['invest', 'stock', 'portfolio', 'wealth']):
		return "Concierge Bank offers personalized wealth management services. Our relationship managers can help you with investment planning, portfolio management, and financial advisory services. Would you like me to connect you with a wealth management specialist?"

	# Premium services
	elif any(word in message_lower for word in ['concierge', 'limousine', 'travel', 'reservation']):
		return "As a Concierge Bank client, you have access to our premium concierge services including travel arrangements, reservations, personal shopping assistance, and lifestyle management. Our concierge team is available 24/7 to assist with any special requests."

	# Security
	elif any(word in message_lower for word in ['security', 'fraud', 'suspicious']):
		return "Security is our top priority at Concierge Bank. If you notice any suspicious activity, please contact us immediately or use the 'Report Issue' feature in your dashboard. We monitor all accounts 24/7 and use advanced security measures to protect your assets."

	# General assistance
	elif any(word in message_lower for word in ['help', 'support', 'contact']):
		return "I'm here to help! You can reach our concierge support team 24/7 at 1-800-CONCIERGE or through this chat. For account-specific issues, you can also use the support options in your dashboard. What can I assist you with today?"

	# Default response
	else:
		return "Thank you for your message. As your Concierge Bank assistant, I'm here to help with all your banking needs, from account management to premium services. Could you please provide more details about how I can assist you today?"
