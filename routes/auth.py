"""
Authentication routes for Concierge Bank
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify, make_response

from core import get_supabase_client
from core.config import JWT_EXPIRATION_HOURS, SUPABASE_URL, SUPABASE_KEY
from auth import create_jwt_token, require_auth
from supabase import create_client, Client
from utils.recaptcha import verify_recaptcha
from services import notify_user
from templates import welcome_email

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
supabase = get_supabase_client()


@auth_bp.route('/register', methods=['POST'])
async def register():
    """Register new user with anti-bot protection"""
    data = await request.get_json()
    
    try:
        # Verify reCAPTCHA token (anti-bot)
        recaptcha_token = data.get('recaptcha_token')
        if recaptcha_token:
            success, score, error = await verify_recaptcha(recaptcha_token, 'register')
            if not success:
                logger.warning(f"Bot registration attempt blocked: {error}")
                return jsonify({'error': 'Registration failed. Please try again.'}), 403
            logger.info(f"reCAPTCHA passed: score={score}")
        else:
            logger.warning("Registration without reCAPTCHA token")
        
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
        
        response = await make_response(jsonify({
            'message': 'Registration successful',
            'user': {
                'id': auth_response.user.id,
                'email': data['email'],
                'full_name': data.get('full_name', '')
            }
        }))
        
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=JWT_EXPIRATION_HOURS * 3600
        )
        
        logger.info(f"User registered successfully: {data['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
async def login():
    """Login user"""
    data = await request.get_json()
    
    try:
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
        
        # Create JWT token
        token = create_jwt_token(auth_response.user.id, data['email'])
        
        response = await make_response(jsonify({
            'message': 'Login successful',
            'user': user_data.data
        }))
        
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=JWT_EXPIRATION_HOURS * 3600
        )
        
        logger.info(f"User logged in: {data['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/logout', methods=['POST'])
async def logout():
    """Logout user"""
    response = await make_response(jsonify({'message': 'Logged out successfully'}))
    response.set_cookie('auth_token', '', expires=0)
    return response


@auth_bp.route('/me', methods=['GET'])
@require_auth
async def get_me(user):
    """Get current user profile"""
    user_data = supabase.table('users').select('*').eq('id', user['user_id']).single().execute()
    return jsonify(user_data.data)
