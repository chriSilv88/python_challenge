from .models import DigitArray
from .operations import add

def _multiply_digits(d1, d2):
    """Multiply two single digits (0-9) using only addition."""
    if d1 == 0 or d2 == 0:
        return 0
    
    result = 0
    for _ in range(d2):
        result += d1
    return result

def multiply_by_digit(a, digit):
    """Multiplies a DigitArray by a single digit."""
    if digit == 0 or a.is_zero:
        return DigitArray.from_int(0)
    if digit == 1:
        return a
    
    result = DigitArray.from_int(0)
    for _ in range(digit):
        result = add(result, a)
    return result

def multiply(a, b):
    """Multiplies two DigitArrays using only additions."""
    if a.is_zero or b.is_zero:
        return DigitArray.from_int(0)
    
    a_digits = list(reversed(a.digits))
    b_digits = list(reversed(b.digits))
    
    result = [0] * (len(a_digits) + len(b_digits))
    
    for i, a_digit in enumerate(a_digits):
        carry = 0
        for j, b_digit in enumerate(b_digits):
            product = _multiply_digits(a_digit, b_digit) + result[i + j] + carry
            result[i + j] = product % 10
            carry = product // 10
        
        if carry:
            result[i + len(b_digits)] += carry
    
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    
    return DigitArray(tuple(reversed(result)))