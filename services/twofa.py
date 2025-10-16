"""
Two-Factor Authentication service for Concierge Bank
Handles OTP generation, verification, and email delivery
"""
import logging
import random
import string
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

from core import get_supabase_client
from services import notify_user
from templates import twofa_code_email, twofa_setup_email

logger = logging.getLogger(__name__)
supabase = get_supabase_client()


class TwoFactorAuthService:
    """Complete 2FA service with OTP email delivery"""

    # OTP settings
    OTP_LENGTH = 6
    OTP_VALIDITY_MINUTES = 10
    MAX_FAILED_ATTEMPTS = 3

    @staticmethod
    def generate_otp() -> str:
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=TwoFactorAuthService.OTP_LENGTH))

    @staticmethod
    def hash_otp(otp: str, salt: str) -> str:
        """Hash OTP for secure storage"""
        return hashlib.sha256(f"{otp}{salt}".encode()).hexdigest()

    @staticmethod
    def verify_otp_hash(otp: str, stored_hash: str, salt: str) -> bool:
        """Verify OTP against stored hash"""
        return hmac.compare_digest(
            TwoFactorAuthService.hash_otp(otp, salt),
            stored_hash
        )

    @classmethod
    async def setup_2fa(cls, user_id: str, email: str, full_name: str = "") -> Dict[str, Any]:
        """Set up 2FA for a user - generates backup codes and sends setup email"""
        try:
            # Generate backup codes (8 codes, 10 characters each)
            backup_codes = []
            backup_codes_hashed = []

            for _ in range(8):
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                backup_codes.append(code)
                # Hash backup codes for storage
                backup_codes_hashed.append(cls.hash_otp(code, user_id))

            # Store 2FA setup in database
            setup_data = {
                'two_factor_enabled': True,
                'two_factor_setup_date': datetime.utcnow().isoformat(),
                'backup_codes': backup_codes_hashed,
                'failed_attempts': 0,
                'last_failed_attempt': None,
                'updated_at': datetime.utcnow().isoformat()
            }

            # Update user preferences
            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            existing_prefs = user_data.data.get('notification_preferences', {}) or {}
            existing_prefs.update(setup_data)

            supabase.table('users').update({
                'notification_preferences': existing_prefs,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            # Send setup confirmation email
            html = twofa_setup_email(full_name or "Valued Client", backup_codes)
            await notify_user(
                supabase,
                user_id,
                'security',
                '2FA Setup Complete',
                'Two-Factor Authentication Enabled',
                html
            )

            logger.info(f"2FA setup completed for user {user_id}")
            return {
                'success': True,
                'backup_codes': backup_codes,  # Plain text for one-time display
                'message': '2FA has been enabled. Please save your backup codes.'
            }

        except Exception as e:
            logger.error(f"2FA setup failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to set up 2FA'
            }

    @classmethod
    async def disable_2fa(cls, user_id: str) -> bool:
        """Disable 2FA for a user"""
        try:
            # Update user preferences
            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            existing_prefs = user_data.data.get('notification_preferences', {}) or {}

            # Remove 2FA related fields
            twofa_fields = ['two_factor_enabled', 'two_factor_setup_date', 'backup_codes',
                          'failed_attempts', 'last_failed_attempt']
            for field in twofa_fields:
                existing_prefs.pop(field, None)

            supabase.table('users').update({
                'notification_preferences': existing_prefs,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            logger.info(f"2FA disabled for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"2FA disable failed for user {user_id}: {e}")
            return False

    @classmethod
    async def send_otp_email(cls, user_id: str, email: str, full_name: str = "") -> Dict[str, Any]:
        """Generate and send OTP via email"""
        try:
            # Generate OTP
            otp = cls.generate_otp()
            salt = f"{user_id}_{int(time.time())}"

            # Hash OTP for storage
            otp_hash = cls.hash_otp(otp, salt)
            expiry = datetime.utcnow() + timedelta(minutes=cls.OTP_VALIDITY_MINUTES)

            # Store OTP in database
            otp_data = {
                'otp_hash': otp_hash,
                'otp_salt': salt,
                'otp_expiry': expiry.isoformat(),
                'otp_attempts': 0,
                'updated_at': datetime.utcnow().isoformat()
            }

            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            existing_prefs = user_data.data.get('notification_preferences', {}) or {}
            existing_prefs.update(otp_data)

            supabase.table('users').update({
                'notification_preferences': existing_prefs,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            # Send OTP email
            html = twofa_code_email(full_name or "Valued Client", otp)
            await notify_user(
                supabase,
                user_id,
                'security',
                'Login Verification Code',
                f'Your verification code: {otp}',
                html
            )

            logger.info(f"OTP sent to user {user_id}")
            return {
                'success': True,
                'message': 'Verification code sent to your email',
                'expiry_minutes': cls.OTP_VALIDITY_MINUTES
            }

        except Exception as e:
            logger.error(f"OTP send failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to send verification code'
            }

    @classmethod
    async def verify_otp(cls, user_id: str, otp: str) -> Dict[str, Any]:
        """Verify OTP code"""
        try:
            # Get user 2FA data
            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            prefs = user_data.data.get('notification_preferences', {}) or {}

            if not prefs.get('two_factor_enabled'):
                return {'success': False, 'error': '2FA not enabled'}

            otp_hash = prefs.get('otp_hash')
            otp_salt = prefs.get('otp_salt')
            otp_expiry = prefs.get('otp_expiry')
            attempts = prefs.get('otp_attempts', 0)

            if not otp_hash or not otp_salt or not otp_expiry:
                return {'success': False, 'error': 'No active verification code'}

            # Check expiry
            if datetime.utcnow() > datetime.fromisoformat(otp_expiry):
                return {'success': False, 'error': 'Verification code has expired'}

            # Check attempts
            if attempts >= cls.MAX_FAILED_ATTEMPTS:
                return {'success': False, 'error': 'Too many failed attempts'}

            # Verify OTP
            if not cls.verify_otp_hash(otp, otp_hash, otp_salt):
                # Increment attempts
                prefs['otp_attempts'] = attempts + 1
                prefs['last_failed_attempt'] = datetime.utcnow().isoformat()
                prefs['updated_at'] = datetime.utcnow().isoformat()

                supabase.table('users').update({
                    'notification_preferences': prefs
                }).eq('id', user_id).execute()

                remaining = cls.MAX_FAILED_ATTEMPTS - (attempts + 1)
                return {
                    'success': False,
                    'error': f'Invalid code. {remaining} attempts remaining'
                }

            # Success - clear OTP data and reset attempts
            prefs.pop('otp_hash', None)
            prefs.pop('otp_salt', None)
            prefs.pop('otp_expiry', None)
            prefs['otp_attempts'] = 0
            prefs['updated_at'] = datetime.utcnow().isoformat()

            supabase.table('users').update({
                'notification_preferences': prefs
            }).eq('id', user_id).execute()

            logger.info(f"OTP verified successfully for user {user_id}")
            return {'success': True, 'message': 'Verification successful'}

        except Exception as e:
            logger.error(f"OTP verification failed for user {user_id}: {e}")
            return {'success': False, 'error': 'Verification failed'}

    @classmethod
    async def verify_backup_code(cls, user_id: str, backup_code: str) -> Dict[str, Any]:
        """Verify backup code for 2FA recovery"""
        try:
            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            prefs = user_data.data.get('notification_preferences', {}) or {}

            if not prefs.get('two_factor_enabled'):
                return {'success': False, 'error': '2FA not enabled'}

            backup_codes = prefs.get('backup_codes', [])
            if not backup_codes:
                return {'success': False, 'error': 'No backup codes available'}

            # Check if backup code matches any stored hash
            code_hash = cls.hash_otp(backup_code, user_id)
            if code_hash not in backup_codes:
                return {'success': False, 'error': 'Invalid backup code'}

            # Remove used backup code
            backup_codes.remove(code_hash)
            prefs['backup_codes'] = backup_codes
            prefs['updated_at'] = datetime.utcnow().isoformat()

            supabase.table('users').update({
                'notification_preferences': prefs
            }).eq('id', user_id).execute()

            logger.info(f"Backup code verified for user {user_id}")
            return {'success': True, 'message': 'Backup code accepted'}

        except Exception as e:
            logger.error(f"Backup code verification failed for user {user_id}: {e}")
            return {'success': False, 'error': 'Backup code verification failed'}

    @classmethod
    async def is_2fa_enabled(cls, user_id: str) -> bool:
        """Check if 2FA is enabled for user"""
        try:
            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            prefs = user_data.data.get('notification_preferences', {}) or {}
            return prefs.get('two_factor_enabled', False)
        except Exception:
            return False

    @classmethod
    async def get_2fa_status(cls, user_id: str) -> Dict[str, Any]:
        """Get 2FA status and configuration"""
        try:
            user_data = supabase.table('users').select('notification_preferences').eq('id', user_id).single().execute()
            prefs = user_data.data.get('notification_preferences', {}) or {}

            return {
                'enabled': prefs.get('two_factor_enabled', False),
                'setup_date': prefs.get('two_factor_setup_date'),
                'backup_codes_count': len(prefs.get('backup_codes', [])),
                'failed_attempts': prefs.get('failed_attempts', 0),
                'has_pending_otp': bool(prefs.get('otp_hash'))
            }
        except Exception:
            return {
                'enabled': False,
                'setup_date': None,
                'backup_codes_count': 0,
                'failed_attempts': 0,
                'has_pending_otp': False
            }
