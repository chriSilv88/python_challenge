import argparse
import sys
import time
from .models import DigitArray
from .factorial import calculate_factorial, verify_factorial
from .multiply import multiply


def handle_factorial(args):
    """Handle factorial command."""
    start_time = time.time()
    
    try:
        result = calculate_factorial(args.n, use_fast=False)
        elapsed = time.time() - start_time
        
        if args.verify and args.n <= 20:
            is_correct = verify_factorial(args.n)
            print(f"Verification: {'✓' if is_correct else '✗'}")
        
        if args.stats:
            print(f"\nStatistics:")
            print(f"  Input: {args.n}")
            print(f"  Result digits: {len(result)}")
            print(f"  Time: {elapsed:.3f} seconds")
            print(f"  Speed: {len(result)/elapsed:.0f} digits/second" if elapsed > 0 else "  Speed: N/A")
        
        if not args.stats_only:
            if args.full:
                print(f"{args.n}! = {result}")
            else:
                if len(result) > 100:
                    print(f"{args.n}! =")
                    print(f"  First 50 digits: {result[:50]}")
                    print(f"  Last 50 digits:  ...{result[-50:]}")
                    print(f"  Total digits: {len(result)}")
                else:
                    print(f"{args.n}! = {result}")
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_multiply(args):
    """Handle multiply command."""
    try:
        a = DigitArray.from_string(args.a)
        b = DigitArray.from_string(args.b)
        
        start_time = time.time()
        result = multiply(a, b)
        elapsed = time.time() - start_time
        
        if args.stats:
            print(f"\nStatistics:")
            print(f"  A digits: {len(a)}")
            print(f"  B digits: {len(b)}")
            print(f"  Result digits: {len(result)}")
            print(f"  Time: {elapsed:.3f} seconds")
        
        print(f"Result: {result}")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main(args=None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Big Integer Operations - Exercise #2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.bigint.cli factorial 10
  python -m src.bigint.cli factorial 100 --stats
  python -m src.bigint.cli multiply 123456789 987654321
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")
    
    # Factorial command 
    factorial_parser = subparsers.add_parser("factorial", help="Calculate factorial")
    factorial_parser.add_argument("n", type=int, help="Number to calculate factorial for")
    factorial_parser.add_argument("--verify", action="store_true", help="Verify result for n ≤ 20")
    factorial_parser.add_argument("--stats", action="store_true", help="Show statistics")
    factorial_parser.add_argument("--stats-only", action="store_true", help="Show only statistics")
    factorial_parser.add_argument("--full", action="store_true", help="Show full result (caution for large n!)")
    factorial_parser.set_defaults(func=handle_factorial)
    
    # Multiply command 
    multiply_parser = subparsers.add_parser("multiply", help="Multiply two numbers")
    multiply_parser.add_argument("a", type=str, help="First number")
    multiply_parser.add_argument("b", type=str, help="Second number")
    multiply_parser.add_argument("--stats", action="store_true", help="Show statistics")
    multiply_parser.set_defaults(func=handle_multiply)
    
    # Parse and execute
    parsed_args = parser.parse_args(args)
    parsed_args.func(parsed_args)


if __name__ == "__main__":
    main()