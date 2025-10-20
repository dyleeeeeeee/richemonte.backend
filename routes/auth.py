"""
Authentication routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from core.config import JWT_EXPIRATION_HOURS, SUPABASE_URL, SUPABASE_KEY
from auth import create_jwt_token, require_auth
from supabase import create_client, Client
from utils.bot_prevention import validate_bot_prevention
from services import notify_user
from templates import welcome_email

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
supabase = get_supabase_client()


def get_client_ip() -> str:
	"""Extract client IP address from request"""
	try:
		# Check for X-Forwarded-For header (proxy/load balancer)
		if request.headers.get('X-Forwarded-For'):
			return request.headers.get('X-Forwarded-For').split(',')[0].strip()
		# Check for X-Real-IP header
		if request.headers.get('X-Real-IP'):
			return request.headers.get('X-Real-IP')
		# Fallback to remote_addr
		return request.remote_addr or '0.0.0.0'
	except Exception as e:
		logger.error(f"Error getting client IP: {e}")
		return '0.0.0.0'


@auth_bp.route('/register', methods=['POST'])
async def register():
    """Register new user with anti-bot protection"""
    data = await request.get_json()
    
    try:
        # Simple bot prevention (rate limiting + honeypot)
        client_ip = get_client_ip()
        is_valid, error_msg = validate_bot_prevention(client_ip, data, action='register')
        if not is_valid:
            logger.warning(f"Bot registration attempt blocked from IP {client_ip}: {error_msg}")
            return jsonify({'error': error_msg}), 429
        logger.info(f"Bot prevention passed for registration from IP {client_ip}")
        
        # Get Supabase client
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        auth_response = supabase_client.auth.sign_up({
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
        
        supabase_client.table('users').insert(profile_data).execute()
        
        # Send welcome notification
        html = welcome_email(data.get('full_name', ''))
        await notify_user(
            supabase_client,
            auth_response.user.id,
            'registration',
            'Welcome email sent',
            'Welcome to Concierge Bank',
            html
        )
        
        # Create JWT token
        token = create_jwt_token(auth_response.user.id, data['email'])
        
        logger.info(f"User registered successfully: {data['email']}")
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': auth_response.user.id,
                'email': data['email'],
                'full_name': data.get('full_name', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
async def login():
    """Login user with anti-bot protection"""
    data = await request.get_json()
    
    try:
        # Simple bot prevention (rate limiting)
        client_ip = get_client_ip()
        is_valid, error_msg = validate_bot_prevention(client_ip, data, action='login')
        if not is_valid:
            logger.warning(f"Bot login attempt blocked from IP {client_ip}: {error_msg}")
            return jsonify({'error': error_msg}), 429
        
        # Authenticate with Supabase
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        auth_response = supabase_client.auth.sign_in_with_password({
            'email': data['email'],
            'password': data['password']
        })
        
        if not auth_response.user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get user profile from users table
        user_data = supabase_client.table('users').select('*').eq('id', auth_response.user.id).single().execute()
        
        # Check if account is blocked or suspended
        account_status = user_data.data.get('account_status', 'active')
        if account_status == 'blocked':
            logger.warning(f"Blocked user login attempt: {data['email']}")
            return jsonify({'error': 'Your account has been blocked. Please contact Concierge Bank support for assistance.'}), 403
        if account_status == 'suspended':
            logger.warning(f"Suspended user login attempt: {data['email']}")
            return jsonify({'error': 'Your account has been suspended. Please contact Concierge Bank support for assistance.'}), 403
        
        # Create JWT token and return user data
        token = create_jwt_token(auth_response.user.id, data['email'])
        
        logger.info(f"User logged in: {data['email']}")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_data.data
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/logout', methods=['POST'])
async def logout():
    """Logout user"""
    return jsonify({'message': 'Logged out successfully'})


@auth_bp.route('/me', methods=['GET'])
@require_auth
async def get_me(user):
    """Get current user profile"""
    user_data = supabase.table('users').select('*').eq('id', user['user_id']).single().execute()
    return jsonify(user_data.data)
