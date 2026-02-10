from .models import DigitArray

def add(a, b):
    """Adds two DigitArrays."""
    a_digits = list(reversed(a.digits))
    b_digits = list(reversed(b.digits))
    
    max_len = max(len(a_digits), len(b_digits))
    a_digits += [0] * (max_len - len(a_digits))
    b_digits += [0] * (max_len - len(b_digits))
    
    result = []
    carry = 0
    
    for i in range(max_len):
        total = a_digits[i] + b_digits[i] + carry
        result.append(total % 10)
        carry = total // 10
    
    if carry:
        result.append(carry)
    
    return DigitArray(tuple(reversed(result)))

def shift_left(a, n):
    if n < 0:
        raise ValueError("Shift amount must be non-negative")
    if n == 0:
        return a
    if a.is_zero:
        return a
    return DigitArray(a.digits + (0,) * n)