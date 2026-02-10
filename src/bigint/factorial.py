import sys
from .models import DigitArray
from .multiply import multiply

def factorial(n):
    """
    Calculate n! and return as string.
    
    Args:
        n: Non-negative integer
        
    Returns:
        n! as string
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    if n == 0 or n == 1:
        return "1"
    
    cache_size = min(n + 1, 101)
    cache = {i: DigitArray.from_int(i) for i in range(1, cache_size)}
    
    result = cache[1] if 1 in cache else DigitArray.from_int(1)
    
    # Multiply by each integer from 2 to n
    for i in range(2, n + 1):
        # Get from cache if available, otherwise create new
        current = cache.get(i)
        if current is None:
            current = DigitArray.from_int(i)
        
        result = multiply(result, current)
        
        if n >= 100 and i % 10 == 0:
            sys.stderr.write(f"\rCalcolo fattoriale... {i}/{n}")
            sys.stderr.flush()
    
    if n >= 100:
        sys.stderr.write("\n")
    
    return str(result)

def calculate_factorial(n):
    """High-level function to calculate factorial and return as string."""
    return factorial(n)

def verify_factorial(n):
    """
    Verify factorial calculation against known values (0-20).
    Returns True if correct or n > 20.
    """
    known_factorials = {
        0: "1",
        1: "1",
        2: "2",
        3: "6",
        4: "24",
        5: "120",
        6: "720",
        7: "5040",
        8: "40320",
        9: "362880",
        10: "3628800",
        11: "39916800",
        12: "479001600",
        13: "6227020800",
        14: "87178291200",
        15: "1307674368000",
        16: "20922789888000",
        17: "355687428096000",
        18: "6402373705728000",
        19: "121645100408832000",
        20: "2432902008176640000",
    }
    
    if n not in known_factorials:
        return True 
    
    calculated = factorial(n)
    expected = known_factorials[n]
    
    return calculated == expected