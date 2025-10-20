"""
Simple bot prevention without external services
Uses rate limiting, honeypot fields, and timing checks
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

# In-memory rate limiting storage (IP -> list of timestamps)
# In production, use Redis or similar for distributed rate limiting
_rate_limit_store: Dict[str, list] = defaultdict(list)

# Rate limiting configuration
MAX_REGISTRATIONS_PER_HOUR = 5
MAX_LOGINS_PER_MINUTE = 10
MIN_FORM_SUBMISSION_TIME = 2  # seconds - bots fill forms too fast


def _clean_old_entries(ip_address: str, time_window: timedelta) -> None:
	"""Remove timestamps older than the time window"""
	cutoff = datetime.utcnow() - time_window
	_rate_limit_store[ip_address] = [
		ts for ts in _rate_limit_store[ip_address]
		if ts > cutoff
	]


def check_rate_limit(ip_address: str, action: str = 'register') -> Tuple[bool, str]:
	"""
	Check if IP has exceeded rate limits
	
	Args:
		ip_address: Client IP address
		action: Type of action ('register' or 'login')
	
	Returns:
		Tuple of (allowed: bool, error_message: str)
	"""
	if not ip_address:
		return True, ""
	
	now = datetime.utcnow()
	
	if action == 'register':
		# Clean old entries (older than 1 hour)
		_clean_old_entries(ip_address, timedelta(hours=1))
		
		# Check registration rate limit
		if len(_rate_limit_store[ip_address]) >= MAX_REGISTRATIONS_PER_HOUR:
			logger.warning(f"Rate limit exceeded for IP {ip_address}: {action}")
			return False, "Too many registration attempts. Please try again later."
		
		# Record this attempt
		_rate_limit_store[ip_address].append(now)
		return True, ""
	
	elif action == 'login':
		# Clean old entries (older than 1 minute)
		_clean_old_entries(ip_address, timedelta(minutes=1))
		
		# Check login rate limit
		if len(_rate_limit_store[ip_address]) >= MAX_LOGINS_PER_MINUTE:
			logger.warning(f"Rate limit exceeded for IP {ip_address}: {action}")
			return False, "Too many login attempts. Please try again in a minute."
		
		# Record this attempt
		_rate_limit_store[ip_address].append(now)
		return True, ""
	
	return True, ""


def check_honeypot(data: dict) -> Tuple[bool, str]:
	"""
	Check honeypot field - invisible field that bots typically fill
	
	Args:
		data: Request data dictionary
	
	Returns:
		Tuple of (valid: bool, error_message: str)
	"""
	# Honeypot field should be empty (humans can't see it)
	honeypot_value = data.get('website', '') or data.get('url', '')
	
	if honeypot_value:
		logger.warning(f"Bot detected: honeypot field filled with '{honeypot_value}'")
		return False, "Invalid submission detected."
	
	return True, ""


def check_submission_timing(form_load_time: float) -> Tuple[bool, str]:
	"""
	Check if form was submitted too quickly (bot behavior)
	
	Args:
		form_load_time: Timestamp when form was loaded (from client)
	
	Returns:
		Tuple of (valid: bool, error_message: str)
	"""
	if not form_load_time:
		# If no timing data, allow it (optional field)
		return True, ""
	
	try:
		now = datetime.utcnow()
		form_load = datetime.utcfromtimestamp(form_load_time)
		elapsed = (now - form_load).total_seconds()
		
		if elapsed < MIN_FORM_SUBMISSION_TIME:
			logger.warning(f"Bot detected: form submitted too quickly ({elapsed:.2f}s)")
			return False, "Please take your time filling out the form."
		
		return True, ""
	except Exception as e:
		logger.error(f"Error checking submission timing: {e}")
		# Allow submission if timing check fails
		return True, ""


def validate_bot_prevention(
	ip_address: str,
	data: dict,
	action: str = 'register'
) -> Tuple[bool, str]:
	"""
	Combined bot prevention validation
	
	Args:
		ip_address: Client IP address
		data: Request data dictionary
		action: Type of action ('register' or 'login')
	
	Returns:
		Tuple of (valid: bool, error_message: str)
	"""
	# Check rate limiting
	rate_ok, rate_error = check_rate_limit(ip_address, action)
	if not rate_ok:
		return False, rate_error
	
	# For registration, check honeypot and timing
	if action == 'register':
		honeypot_ok, honeypot_error = check_honeypot(data)
		if not honeypot_ok:
			return False, honeypot_error
		
		timing_ok, timing_error = check_submission_timing(
			data.get('form_load_time')
		)
		if not timing_ok:
			return False, timing_error
	
	return True, ""
