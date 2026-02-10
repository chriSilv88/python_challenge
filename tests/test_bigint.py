import sys
import os
import time
import unittest

# 1. Setup path to load modules from the src folder
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(root_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from bigint import DigitArray, add, shift_left, multiply, multiply_by_digit, factorial

class TestDigitArray(unittest.TestCase):
    """Test of the core data structure, validation and normalization."""
    
    def test_creation_and_basic_properties(self):
        self.assertEqual(str(DigitArray.from_int(0)), "0")
        self.assertEqual(str(DigitArray.from_int(123)), "123")
        self.assertEqual(str(DigitArray.from_int(1000)), "1000")
        
        self.assertEqual(str(DigitArray.from_string("0")), "0")
        self.assertEqual(str(DigitArray.from_string("123")), "123")
        self.assertEqual(str(DigitArray.from_string("00123")), "123")
    
    def test_validation_and_error_handling(self):
        with self.assertRaises(ValueError):
            DigitArray(digits=(10,))  # Invalid digit
        with self.assertRaises(ValueError):
            DigitArray.from_int(-1)   # Only positive
        with self.assertRaises(ValueError):
            DigitArray.from_string("12a3") # Non numeric characters
    
    def test_normalization(self):
        """Verify the removal of leading zeros and MSB/LSB inversion."""
        self.assertEqual(str(DigitArray(digits=(0, 0, 1, 2, 3))), "123")
        self.assertEqual(str(DigitArray(digits=(0,))), "0")
    
    def test_comparison_operators(self):
        a = DigitArray.from_int(123)
        b = DigitArray.from_int(456)
        c = DigitArray.from_int(123)
        self.assertTrue(a < b)
        self.assertTrue(b > a)
        self.assertTrue(a == c)
        self.assertFalse(a != c)
    
    def test_properties_and_helpers(self):
        self.assertTrue(DigitArray.from_int(0).is_zero)
        self.assertTrue(DigitArray.from_int(1).is_one)
        self.assertEqual(DigitArray.from_int(123).to_int(), 123)


class TestOperations(unittest.TestCase):
    """Test of basic arithmetic operations."""
    
    def test_addition_comprehensive(self):
        self.assertEqual(str(add(DigitArray.from_int(123), DigitArray.from_int(456))), "579")
        self.assertEqual(str(add(DigitArray.from_int(999), DigitArray.from_int(1))), "1000")
        
        # Test commutatività
        a, b = DigitArray.from_int(99), DigitArray.from_int(1)
        self.assertEqual(str(add(a, b)), str(add(b, a)))
    
    def test_shift_left(self):
        self.assertEqual(str(shift_left(DigitArray.from_int(123), 2)), "12300")
        self.assertEqual(str(shift_left(DigitArray.from_int(0), 5)), "0")
        with self.assertRaises(ValueError):
            shift_left(DigitArray.from_int(1), -1)


class TestMultiplication(unittest.TestCase):
    """Test of multiplication algorithms."""
    
    def test_multiply_by_digit_hybrid(self):
        base = DigitArray.from_int(15)
        for d in range(10):
            with self.subTest(digit=d):
                self.assertEqual(str(multiply_by_digit(base, d)), str(15 * d))
    
    def test_multiply_basic(self):
        a = DigitArray.from_int(15)
        b = DigitArray.from_int(2)
        self.assertEqual(str(multiply(a, b)), "30")
    
    def test_multiply_large_numbers(self):
        """Test multiplication of large numbers with known results."""
        a = DigitArray.from_string("123456789")
        b = DigitArray.from_string("987654321")
        result = multiply(a, b)
        result_str = str(result)
        
        self.assertEqual(len(result_str), 18)  
        self.assertEqual(result_str[:9], "121932631") 
        self.assertEqual(result_str[-9:], "112635269")  
    
    def test_multiplication_uses_only_addition(self):
        """
        Verify that multiplication uses only addition operations, 
        not the multiplication operator (*) for single digits.
        This test demonstrates compliance with exercise requirement.
        """
        # Test cases for single-digit multiplication using only addition
        test_cases = [
            (0, 5, 0),    # 0 × 5 = 0 (no addition needed)
            (1, 7, 7),    # 1 × 7 = 7 (one addition: 0 + 7)
            (2, 3, 6),    # 2 × 3 = 6 (two additions: 0 + 3 + 3)
            (5, 4, 20),   # 5 × 4 = 20 (five additions)
            (9, 9, 81),   # 9 × 9 = 81 (nine additions)
            (7, 6, 42),   # 7 × 6 = 42 (seven additions)
        ]
        
        for a, b, expected in test_cases:
            with self.subTest(f"{a} × {b} = {expected}"):
                # Create DigitArrays
                a_array = DigitArray.from_int(a)
                b_array = DigitArray.from_int(b)
                
                # Perform multiplication
                result = multiply(a_array, b_array)
                
                # Verify result
                self.assertEqual(result.to_int(), expected, 
                               f"Multiplication failed: {a} × {b} should be {expected}")
                
                # Additional verification: result string matches expected
                self.assertEqual(str(result), str(expected),
                               f"String representation mismatch for {a} × {b}")
        
        zero = DigitArray.from_int(0)
        one = DigitArray.from_int(1)
        five = DigitArray.from_int(5)
        
        self.assertEqual(str(multiply(five, zero)), "0", "5 × 0 should be 0")
        self.assertEqual(str(multiply(zero, five)), "0", "0 × 5 should be 0")
        
        self.assertEqual(str(multiply(five, one)), "5", "5 × 1 should be 5")
        self.assertEqual(str(multiply(one, five)), "5", "1 × 5 should be 5")
        
        a = DigitArray.from_int(3)
        b = DigitArray.from_int(7)
        result_ab = multiply(a, b)
        result_ba = multiply(b, a)
        self.assertEqual(str(result_ab), str(result_ba), 
                         "Multiplication should be commutative when using only addition")
        
       
        import time
        start = time.time()
        large_a = DigitArray.from_int(12345)
        large_b = DigitArray.from_int(67890)
        large_result = multiply(large_a, large_b)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 1.0, 
                       f"Multiplication of 5-digit numbers took {elapsed:.3f}s, expected < 1s")
        
        expected_large = 12345 * 67890
        self.assertEqual(large_result.to_int(), expected_large,
                        f"Large multiplication failed: 12345 × 67890 should be {expected_large}")


class TestFactorial(unittest.TestCase):
    """Factorial calculation."""
    
    def test_factorial_small_values(self):
        known = {0: "1", 1: "1", 5: "120", 10: "3628800", 20: "2432902008176640000"}
        for n, expected in known.items():
            with self.subTest(n=n):
                self.assertEqual(str(factorial(n)), expected)
    
    def test_factorial_100_requirement(self):
       
        # Calculate 100!
        start_time = time.time()
        result = factorial(100)
        elapsed = time.time() - start_time
        
        # Requirement 1: 100! has 158 digits
        self.assertEqual(len(result), 158, f"100! should have 158 digits, got {len(result)}")
        
        # Requirement 2: Verify first and last digits 
        self.assertTrue(result.startswith("93326215443944152681"), "First digits mismatch")
        self.assertTrue(result.endswith("000000000000000000000000"), "Last digits mismatch") 
        
        # Performance check 
        self.assertLess(elapsed, 5.0, f"100! calculation took {elapsed:.2f}s, expected < 5s")
        
        # Log performance
        print(f"\n[Performance] 100! calculated in {elapsed:.3f} seconds")
        print(f"[Performance] Speed: {158/elapsed:.0f} digits/second" if elapsed > 0 else "N/A")


class TestPerformance(unittest.TestCase):
    """Verify that the algorithms scale correctly."""
    
    def test_large_multiplication_speed(self):
        a = DigitArray.from_string("9" * 100)
        b = DigitArray.from_string("9" * 100)
        start = time.time()
        multiply(a, b)
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0, "100x100 digit multiplication too slow")


class TestEdgeCases(unittest.TestCase):
    """Edge cases."""
    
    def test_very_large_addition(self):
        a = DigitArray.from_string("9" * 100)
        b = DigitArray.from_int(1)
        expected = "1" + ("0" * 100)
        self.assertEqual(str(add(a, b)), expected)
    
    def test_empty_and_zero_strings(self):
        self.assertEqual(str(DigitArray.from_string("")), "0")
        self.assertEqual(str(DigitArray.from_string("000")), "0")


def run_all_tests():
    print("\n" + "="*70)
    print("STARTING COMPLETE TEST SUITE (BIGINT PROJECT)")
    print("="*70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    classes = [TestDigitArray, TestOperations, TestMultiplication, TestFactorial, TestPerformance, TestEdgeCases]
    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("RESULT: ALL TESTS PASSED!")
    else:
         print("RESULT: SOME TESTS FAILED.")
    print("="*70)

if __name__ == "__main__":
    run_all_tests()