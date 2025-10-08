"""
Validation utilities
"""
from typing import List


def digits_of(n: int) -> List[int]:
	"""Convert number to list of digits
	
	Args:
		n: Integer to convert
	
	Returns:
		List of individual digits
	"""
	return [int(d) for d in str(n)]


def luhn_checksum(card_number: int) -> int:
	"""Calculate Luhn checksum for card number validation
	
	Args:
		card_number: Card number without check digit
	
	Returns:
		Checksum value (0-9)
	"""
	digits = digits_of(card_number)
	odd_digits = digits[-1::-2]
	even_digits = digits[-2::-2]
	checksum = sum(odd_digits)
	for d in even_digits:
		checksum += sum(digits_of(d * 2))
	return checksum % 10
