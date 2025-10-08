"""
Email HTML templates for Concierge Bank
"""
from core.config import LUXURY_GOLD_COLOR


def welcome_email(full_name: str) -> str:
	"""Generate welcome email HTML
	
	Args:
		full_name: User's full name
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto;">
		<h1 style="color: {LUXURY_GOLD_COLOR};">Welcome to Concierge Bank</h1>
		<p>Dear {full_name or 'Valued Client'},</p>
		<p>Your account has been successfully created. Experience the pinnacle of luxury banking.</p>
		<p style="font-style: italic;">À votre service éternel!</p>
	</div>
	"""


def account_created_email(account_type: str, account_number: str, initial_deposit: float) -> str:
	"""Generate account creation confirmation email
	
	Args:
		account_type: Type of account (Checking, Savings, Investment)
		account_number: Account number
		initial_deposit: Initial deposit amount
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif;">
		<h2 style="color: {LUXURY_GOLD_COLOR};">New Account Opened</h2>
		<p>Your {account_type} account has been successfully created.</p>
		<p><strong>Account Number:</strong> {account_number}</p>
		<p><strong>Initial Balance:</strong> ${initial_deposit:,.2f}</p>
	</div>
	"""


def card_approved_email(card_brand: str, card_type: str, card_last_four: str, credit_limit: float) -> str:
	"""Generate card approval email
	
	Args:
		card_brand: Card brand (Cartier, Van Cleef & Arpels, etc.)
		card_type: Card type (Credit, Debit)
		card_last_four: Last 4 digits of card number
		credit_limit: Credit limit amount
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif;">
		<h2 style="color: {LUXURY_GOLD_COLOR};">Card Application Approved!</h2>
		<p>Congratulations! Your {card_brand} {card_type} card has been approved.</p>
		<p><strong>Card Number:</strong> •••• •••• •••• {card_last_four}</p>
		<p><strong>Credit Limit:</strong> ${credit_limit:,.2f}</p>
		<p>Your card will arrive within 5-7 business days.</p>
	</div>
	"""


def transfer_confirmation_email(amount: float, new_balance: float) -> str:
	"""Generate transfer confirmation email
	
	Args:
		amount: Transfer amount
		new_balance: New account balance
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif;">
		<h2 style="color: {LUXURY_GOLD_COLOR};">Transfer Confirmation</h2>
		<p>Your transfer of ${amount:,.2f} has been completed successfully.</p>
		<p><strong>New Balance:</strong> ${new_balance:,.2f}</p>
	</div>
	"""


def bill_payment_email(payee_name: str, amount: float, payment_date: str) -> str:
	"""Generate bill payment confirmation email
	
	Args:
		payee_name: Name of payee
		amount: Payment amount
		payment_date: Date of payment
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif;">
		<h2 style="color: {LUXURY_GOLD_COLOR};">Bill Payment Confirmation</h2>
		<p>Your payment to {payee_name} has been processed successfully.</p>
		<p><strong>Amount:</strong> ${amount:,.2f}</p>
		<p><strong>Payment Date:</strong> {payment_date}</p>
	</div>
	"""


def check_deposit_email(amount: float, check_number: str) -> str:
	"""Generate check deposit confirmation email
	
	Args:
		amount: Check amount
		check_number: Check number
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif;">
		<h2 style="color: {LUXURY_GOLD_COLOR};">Check Deposit Confirmation</h2>
		<p>Your check deposit has been received and is being processed.</p>
		<p><strong>Amount:</strong> ${amount:,.2f}</p>
		<p><strong>Check Number:</strong> {check_number}</p>
		<p>Funds will be available within 1-5 business days.</p>
	</div>
	"""


def check_order_email(design: str, quantity: int, price: float) -> str:
	"""Generate check order confirmation email
	
	Args:
		design: Check design name
		quantity: Number of checks ordered
		price: Total price
	
	Returns:
		HTML email content
	"""
	return f"""
	<div style="font-family: Georgia, serif;">
		<h2 style="color: {LUXURY_GOLD_COLOR};">Check Order Confirmation</h2>
		<p>Your check order has been received.</p>
		<p><strong>Design:</strong> {design}</p>
		<p><strong>Quantity:</strong> {quantity} checks</p>
		<p><strong>Total:</strong> ${price:.2f}</p>
		<p>Your checks will arrive within 7-10 business days.</p>
	</div>
	"""
