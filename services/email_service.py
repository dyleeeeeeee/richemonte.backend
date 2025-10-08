"""
Email service using Resend API
"""
import logging
from typing import Optional, List, Dict, Any
import resend
from core.config import EMAIL_FROM, RESEND_API_KEY

logger = logging.getLogger(__name__)

# Initialize Resend
resend.api_key = RESEND_API_KEY


async def send_email(to: str, subject: str, html: str, attachments: Optional[List] = None) -> Dict[str, Any]:
	"""Send email via Resend API
	
	Args:
		to: Recipient email address
		subject: Email subject
		html: HTML email content
		attachments: Optional list of attachments
	
	Returns:
		Dict with success status and message ID or error
	"""
	try:
		params = {
			'from': EMAIL_FROM,
			'to': [to],
			'subject': subject,
			'html': html
		}
		
		if attachments:
			params['attachments'] = attachments
		
		response = resend.Emails.send(params)
		logger.info(f"Email sent successfully to {to}: {response.get('id')}")
		return {'success': True, 'id': response.get('id')}
	except Exception as e:
		logger.error(f"Failed to send email to {to}: {str(e)}")
		return {'success': False, 'error': str(e)}
