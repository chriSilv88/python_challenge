import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from log_analyzer.cli import analyze_log_file

input_path = Path("data/sample.log")
output_path = Path("data/report_sample.csv")

print(f"Analyzing sample log: {input_path}...")

try:
    result = analyze_log_file(
        input_path=str(input_path),
        output_path=str(output_path),
        format_type="csv",
    )
except FileNotFoundError:
    print(f"Error: the file {input_path} does not exist!")
    sys.exit(1)

print(f"Done: {result['valid_records']} lines processed")
print(f"Unique IPs: {result['unique_ips']}")
print(f"Report saved to: {output_path}")
