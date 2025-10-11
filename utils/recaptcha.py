"""
reCAPTCHA verification utility
Anti-bot protection for registration and sensitive operations
"""
import logging
import os
import httpx
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
RECAPTCHA_THRESHOLD = 0.5  # Score threshold (0.0 = bot, 1.0 = human)


async def verify_recaptcha(token: str, action: str = 'register') -> Tuple[bool, float, Optional[str]]:
    """
    Verify reCAPTCHA v3 token
    
    Args:
        token: reCAPTCHA token from frontend
        action: Expected action name (register, login, etc.)
    
    Returns:
        Tuple of (success: bool, score: float, error: Optional[str])
    """
    if not RECAPTCHA_SECRET_KEY:
        logger.warning("RECAPTCHA_SECRET_KEY not configured, skipping verification")
        return True, 1.0, None  # Allow in development
    
    if not token:
        return False, 0.0, "No reCAPTCHA token provided"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    'secret': RECAPTCHA_SECRET_KEY,
                    'response': token
                },
                timeout=5.0
            )
            
            result = response.json()
            
            if not result.get('success'):
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                return False, 0.0, f"Verification failed: {', '.join(error_codes)}"
            
            score = result.get('score', 0.0)
            received_action = result.get('action', '')
            
            # Verify action matches
            if received_action != action:
                logger.warning(f"Action mismatch: expected {action}, got {received_action}")
                return False, score, "Action mismatch"
            
            # Check score threshold
            if score < RECAPTCHA_THRESHOLD:
                logger.warning(f"Low reCAPTCHA score: {score} (threshold: {RECAPTCHA_THRESHOLD})")
                return False, score, f"Bot detected (score: {score})"
            
            logger.info(f"reCAPTCHA verification successful: score={score}, action={action}")
            return True, score, None
            
    except httpx.TimeoutException:
        logger.error("reCAPTCHA verification timeout")
        return False, 0.0, "Verification timeout"
    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {str(e)}")
        return False, 0.0, f"Verification error: {str(e)}"
