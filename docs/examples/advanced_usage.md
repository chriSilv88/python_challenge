# **examples/advanced_usage.md**

```markdown
# Advanced Patterns

## Log Analyzer - Production Extensions

### Custom Parsing Rules
```python
class SecurityParser(LogParser):
    def _parse_line(self, line: str, line_num: int):
        record = super()._parse_line(line, line_num)
        if record and self._is_suspicious(record):
            return None
        return record
Real-time Monitoring
python
import time
from collections import deque

class LiveMonitor:
    def __init__(self, window=60):
        self.window = window
        self.recent = deque(maxlen=10000)
    
    def process_stream(self, log_file):
        last_pos = 0
        while True:
            with open(log_file, 'r') as f:
                f.seek(last_pos)
                for line in f:
                    self._process_line(line)
                last_pos = f.tell()
            time.sleep(1)
BigInt - Optimized Algorithms
Karatsuba Multiplication (Faster for large numbers)
python
def karatsuba(x: DigitArray, y: DigitArray) -> DigitArray:
    # Base case
    if len(x.digits) < 10 or len(y.digits) < 10:
        return multiply(x, y)
    
    # Split and recursive calls
    m = min(len(x.digits), len(y.digits))
    m2 = m // 2
    
    high1, low1 = split_at(x, m2)
    high2, low2 = split_at(y, m2)
    
    z0 = karatsuba(low1, low2)
    z1 = karatsuba(add(low1, high1), add(low2, high2))
    z2 = karatsuba(high1, high2)
    
    # Combine results
    return add(shift_left(z2, 2*m2), 
               add(shift_left(subtract(subtract(z1, z2), z0), m2), z0))
Integration Examples
FastAPI Web Service
python
from fastapi import FastAPI, UploadFile
import tempfile
from log_analyzer.cli import analyze_log_file

app = FastAPI()

@app.post("/analyze")
async def analyze_log(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
    
    result = analyze_log_file(tmp.name, "output.json", format_type="json")
    return {"unique_ips": result["unique_ips"], 
            "total_requests": result["total_requests"]}