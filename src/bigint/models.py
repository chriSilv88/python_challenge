from functools import total_ordering

@total_ordering
class DigitArray:
    
    def __init__(self, digits):
        if not digits:
            digits = (0,)
        
        # Validate digits
        for d in digits:
            if not isinstance(d, int) or d < 0 or d > 9:
                raise ValueError(f"Invalid digit: {d}")
        
        i = 0
        while i < len(digits) - 1 and digits[i] == 0:
            i += 1
        
        self._digits = digits[i:]
        self._str = None  
    
    @classmethod
    def from_int(cls, n):
        """Create a DigitArray from an integer."""
        if n < 0:
            raise ValueError("Negative numbers not supported")
        if n == 0:
            return cls((0,))
        
        digits = []
        while n > 0:
            digits.insert(0, n % 10)  # prepend
            n //= 10
        
        return cls(tuple(digits))
    
    @classmethod
    def from_string(cls, s):
        """Create a DigitArray from a string."""
        if not s:
            return cls((0,))
        
        # Remove leading zeros from string
        s = s.lstrip('0')
        if not s:
            return cls((0,))
        
        digits = tuple(int(ch) for ch in s)
        return cls(digits)
    
    @property
    def digits(self):
        """Return the digits as a tuple."""
        return self._digits
    
    @property
    def is_zero(self):
        """Return True if this number is zero."""
        return len(self._digits) == 1 and self._digits[0] == 0
    
    @property
    def is_one(self):
        """Return True if this number is one."""
        return len(self._digits) == 1 and self._digits[0] == 1
    
    def __str__(self):
        """Return string representation."""
        if self._str is None:
            self._str = ''.join(str(d) for d in self._digits)
        return self._str
    
    def __repr__(self):
        """Return detailed representation."""
        return f"DigitArray({self._digits})"
    
    def __eq__(self, other):
        """Equality comparison."""
        if not isinstance(other, DigitArray):
            return False
        return self._digits == other._digits
    
    def __lt__(self, other):
        """Less than comparison."""
        if not isinstance(other, DigitArray):
            return NotImplemented
        
        # Compare lengths first
        if len(self._digits) != len(other._digits):
            return len(self._digits) < len(other._digits)
        
        # Same length, compare digit by digit
        for d1, d2 in zip(self._digits, other._digits):
            if d1 != d2:
                return d1 < d2
        
        return False  
    
    def to_int(self):
        result = 0
        for d in self._digits:
            result = result * 10 + d
        return result
    
    def __hash__(self):
        return hash(self._digits)