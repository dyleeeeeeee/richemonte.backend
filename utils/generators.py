"""
Data generation utilities
"""
import random
from core.config import ACCOUNT_NUMBER_LENGTH, CARD_NUMBER_LENGTH, CVV_LENGTH
from .validators import luhn_checksum


def generate_card_number(prefix: str = '4') -> str:
	"""Generate valid card number using Luhn algorithm
	
	Args:
		prefix: Card number prefix (default '4' for Visa)
	
	Returns:
		Valid 16-digit card number as string
	"""
	number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(CARD_NUMBER_LENGTH - len(prefix) - 1)])
	check_digit = (10 - luhn_checksum(int(number))) % 10
	return number + str(check_digit)


def generate_account_number() -> str:
	"""Generate unique 12-digit account number
	
	Returns:
		12-digit account number as string
	"""
	return ''.join([str(random.randint(0, 9)) for _ in range(ACCOUNT_NUMBER_LENGTH)])


def generate_cvv() -> str:
	"""Generate 3-digit CVV code
	
	Returns:
		3-digit CVV as string
	"""
	return ''.join([str(random.randint(0, 9)) for _ in range(CVV_LENGTH)])
