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
from utils.recaptcha import verify_recaptcha
from services.twofa import TwoFactorAuthService
from templates import welcome_email

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
supabase = get_supabase_client()


@auth_bp.route('/register', methods=['POST'])
async def register():
    """Register new user with anti-bot protection"""
    data = await request.get_json()
    
    try:
        # Verify reCAPTCHA token (anti-bot) - REQUIRED
        recaptcha_token = data.get('recaptcha_token')
        if not recaptcha_token:
            logger.warning("Registration without reCAPTCHA token - BLOCKED")
            return jsonify({'error': 'Security verification required. Please try again.'}), 403
        
        success, score, error = await verify_recaptcha(recaptcha_token, 'register')
        if not success:
            logger.warning(f"Bot registration attempt blocked: {error}")
            return jsonify({'error': 'Registration failed. Please try again.'}), 403
        logger.info(f"reCAPTCHA passed: score={score}")
        
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
    """Login user with anti-bot protection and 2FA support"""
    data = await request.get_json()
    
    try:
        # Verify reCAPTCHA token (anti-bot)
        recaptcha_token = data.get('recaptcha_token')
        if recaptcha_token:
            success, score, error = await verify_recaptcha(recaptcha_token, 'login')
            if not success:
                logger.warning(f"Bot login attempt blocked: {error}")
                return jsonify({'error': 'Login failed. Please try again.'}), 403
            logger.info(f"Login reCAPTCHA passed: score={score}")
        else:
            logger.warning("Login without reCAPTCHA token")
        
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
        
        # Check if 2FA is enabled
        is_2fa_enabled = await TwoFactorAuthService.is_2fa_enabled(auth_response.user.id)
        
        if is_2fa_enabled:
            # Send OTP email for 2FA verification
            otp_result = await TwoFactorAuthService.send_otp_email(
                auth_response.user.id,
                data['email'],
                user_data.data.get('full_name', '')
            )
            
            if not otp_result['success']:
                return jsonify({'error': 'Failed to send verification code'}), 500
            
            logger.info(f"2FA login initiated for user {data['email']}")
            return jsonify({
                'message': 'Verification code sent to your email',
                'requires_2fa': True,
                'user_id': auth_response.user.id,
                'email': data['email'],
                'expiry_minutes': 10
            })
        else:
            # Standard login without 2FA
            token = create_jwt_token(auth_response.user.id, data['email'])
            
            logger.info(f"User logged in: {data['email']}")
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': user_data.data,
                'requires_2fa': False
            })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/verify-2fa', methods=['POST'])
async def verify_2fa():
    """Verify 2FA code and complete login"""
    data = await request.get_json()
    
    try:
        user_id = data.get('user_id')
        email = data.get('email')
        otp_code = data.get('otp_code')
        
        if not all([user_id, email, otp_code]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify OTP
        verify_result = await TwoFactorAuthService.verify_otp(user_id, otp_code)
        
        if not verify_result['success']:
            return jsonify({'error': verify_result['error']}), 401
        
        # Get user data and create token
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_data = supabase_client.table('users').select('*').eq('id', user_id).single().execute()
        
        # Check if account is blocked or suspended (even after 2FA)
        account_status = user_data.data.get('account_status', 'active')
        if account_status == 'blocked':
            logger.warning(f"Blocked user 2FA attempt: {email}")
            return jsonify({'error': 'Your account has been blocked. Please contact Concierge Bank support for assistance.'}), 403
        if account_status == 'suspended':
            logger.warning(f"Suspended user 2FA attempt: {email}")
            return jsonify({'error': 'Your account has been suspended. Please contact Concierge Bank support for assistance.'}), 403
        
        token = create_jwt_token(user_id, email)
        
        logger.info(f"2FA verification successful for user {email}")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_data.data
        })
        
    except Exception as e:
        logger.error(f"2FA verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500


@auth_bp.route('/verify-backup-code', methods=['POST'])
async def verify_backup_code():
    """Verify backup code for 2FA recovery"""
    data = await request.get_json()
    
    try:
        user_id = data.get('user_id')
        email = data.get('email')
        backup_code = data.get('backup_code')
        
        if not all([user_id, email, backup_code]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify backup code
        verify_result = await TwoFactorAuthService.verify_backup_code(user_id, backup_code)
        
        if not verify_result['success']:
            return jsonify({'error': verify_result['error']}), 401
        
        # Get user data and create token
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_data = supabase_client.table('users').select('*').eq('id', user_id).single().execute()
        
        # Check if account is blocked or suspended (even after backup code)
        account_status = user_data.data.get('account_status', 'active')
        if account_status == 'blocked':
            logger.warning(f"Blocked user backup code attempt: {email}")
            return jsonify({'error': 'Your account has been blocked. Please contact Concierge Bank support for assistance.'}), 403
        if account_status == 'suspended':
            logger.warning(f"Suspended user backup code attempt: {email}")
            return jsonify({'error': 'Your account has been suspended. Please contact Concierge Bank support for assistance.'}), 403
        
        token = create_jwt_token(user_id, email)
        
        logger.info(f"Backup code verification successful for user {email}")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_data.data
        })
        
    except Exception as e:
        logger.error(f"Backup code verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500


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
