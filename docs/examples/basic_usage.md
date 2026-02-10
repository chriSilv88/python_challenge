# Basic Usage

# Log Analyzer (Exercise #1)

# CLI - Simple Usage

# Process a log file and output CSV
python -m log_analyzer.cli analyze -i access.log -o ipaddr.csv

# Output JSON instead
python -m log_analyzer.cli analyze -i access.log -o report.json -f json

# See what's in a log file
python -m log_analyzer.cli count -i access.log

Programmatic Usage
python
from log_analyzer import LogParser, Aggregator, CSVWriter

parser = LogParser()
aggregator = Aggregator()

for record in parser.parse_file("access.log"):
    if record:
        aggregator.add_record(record)

reports = aggregator.generate_reports(sort_by="requests", descending=True)

with open("ipaddr.csv", "w") as f:
    CSVWriter(f).write(reports)

print(f"Processed {aggregator.total_requests} requests")
BigInt (Exercise #2)
Basic Operations
python
from bigint import factorial, multiply, DigitArray

# 15 × 2 using only addition
a = DigitArray.from_int(15)
b = DigitArray.from_int(2)
result = multiply(a, b)  # DigitArray('30')

# 100! (158 digits)
fact_100 = factorial(100)
print(f"100! has {len(fact_100)} digits")
Large Numbers
python

# Work with very large numbers
big_num = DigitArray.from_string("1234567890" * 10)  # 100 digits
Quick Test
bash
python tests/test_log_analyzer.py
python tests/test_bigint.py
