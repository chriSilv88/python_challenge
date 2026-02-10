__version__ = "1.0.0"

# Importiamo le classi e le funzioni principali dai vari moduli
from .models import DigitArray
from .operations import add, shift_left
from .multiply import multiply, multiply_by_digit
from .factorial import factorial, calculate_factorial

# Definiamo cosa esportare ufficialmente quando si usa "from bigint import *"
__all__ = [
    'DigitArray',
    'add',
    'shift_left',
    'multiply',
    'multiply_by_digit',
    'factorial',
    'calculate_factorial'
]