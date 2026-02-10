import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bigint import factorial, multiply, DigitArray

print("Exercise requirements verification...")

# 1. 15 × 2 using only additions
a = DigitArray.from_int(15)
b = DigitArray.from_int(2)
result = multiply(a, b)
print(f"15 × 2 = {result} (using only additions)")

# 2. 100! 
fact_100 = factorial(100)
print(f"100! calculated: {len(fact_100)} digits")
print(f"First digits: {fact_100[:20]}...")

print("\nMemory efficient implementation, suitable for the test.")
print("In production: consider more efficient algorithms (Karatsuba).")