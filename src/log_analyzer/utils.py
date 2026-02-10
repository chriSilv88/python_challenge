import sys
from pathlib import Path
from typing import Optional, Dict, Any
from .cli import analyze_log_file


def analyze_directory(
    input_dir: str,
    output_dir: Optional[str] = None,
    pattern: str = "*.log",
    format_type: str = "csv",
    **kwargs
) -> Dict[str, Any]:
    
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path / "reports"
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for log_file in input_path.glob(pattern):
        if log_file.is_file():
            output_file = output_path / f"{log_file.stem}_report.{format_type}"
            
            try:
                result = analyze_log_file(
                    input_path=str(log_file),
                    output_path=str(output_file),
                    format_type=format_type,
                    **kwargs
                )
                results[log_file.name] = result
                print(f"Processed: {log_file.name}")
                
            except Exception as e:
                results[log_file.name] = {
                    "error": str(e),
                    "processing_success": False
                }
                print(f"Failed: {log_file.name} - {e}")
    
    # Print summary
    if results:
        total_files = len(results)
        successful = sum(1 for r in results.values() if r.get("processing_success", False))
        
        print(f"\n Directory analysis summary:")
        print(f"   Total files: {total_files}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {total_files - successful}")
        print(f"   Reports saved to: {output_path}")
    
    return results


def validate_log_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
 
    from .parser import LogParser
    
    parser = LogParser()
    stats = {
        "total_lines": 0,
        "valid_lines": 0,
        "invalid_lines": 0,
        "sample_records": [],
        "issues": []
    }
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f, 1):
                stats["total_lines"] += 1
                
                if line_num <= 5:  # Sample first 5 records
                    record = parser._parse_line(line, line_num)
                    if record:
                        stats["sample_records"].append({
                            "line": line_num,
                            "timestamp": record.timestamp,
                            "bytes": record.bytes_sent,
                            "status": record.status,
                            "ip": record.remote_addr
                        })
                
                if line_num >= 100:  # Only check first 100 lines
                    break
        
        # Quick count of valid lines
        total, valid = parser.count_lines(file_path, encoding)
        stats["valid_lines"] = valid
        stats["invalid_lines"] = total - valid
        
        if valid == 0:
            stats["issues"].append("No valid records found")
        
        return stats
        
    except Exception as e:
        return {
            "error": str(e),
            "total_lines": stats["total_lines"],
            "valid_lines": 0,
            "issues": [f"Validation error: {e}"]
        }


def create_sample_log(output_path: str, num_lines: int = 20) -> None:

    import random
    from datetime import datetime, timedelta
    
    ip_pool = [
        "192.168.1.1", "192.168.1.2", "192.168.1.3",
        "10.0.0.1", "10.0.0.2", "172.16.0.1",
        "203.0.113.1", "198.51.100.1"
    ]
    
    statuses = ["OK", "ERROR", "OK", "OK", "FORBIDDEN"]
    
    start_time = datetime(2024, 1, 1, 10, 0, 0)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(num_lines):
            timestamp = start_time + timedelta(seconds=i)
            bytes_sent = random.choice([0, 512, 1024, 2048, 4096, 8192])
            status = random.choice(statuses)
            ip = random.choice(ip_pool)
            
            f.write(f"{timestamp};{bytes_sent};{status};{ip}\n")
    
    print(f"Sample log created: {output_path} ({num_lines} lines)")


def benchmark_performance(
    input_path: str,
    runs: int = 3,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    
    import time
    from .parser import LogParser
    from .aggregator import Aggregator
    
    parser = LogParser()
    results = []
    
    print(f"Benchmarking performance ({runs} runs)...")
    
    for run in range(1, runs + 1):
        print(f"  Run {run}/{runs}...", end=" ")
        sys.stdout.flush()
        
        start_time = time.time()
        
        aggregator = Aggregator()
        processed = 0
        valid = 0
        
        for record in parser.parse_file(input_path, encoding):
            processed += 1
            if record is not None:
                aggregator.add_record(record)
                valid += 1
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        results.append({
            "run": run,
            "elapsed_seconds": elapsed,
            "processed_lines": processed,
            "valid_lines": valid,
            "lines_per_second": processed / elapsed if elapsed > 0 else 0,
            "unique_ips": aggregator.unique_ips
        })
        
        print(f"{elapsed:.2f}s")
    
    # Calculate statistics
    if results:
        avg_elapsed = sum(r["elapsed_seconds"] for r in results) / len(results)
        avg_lps = sum(r["lines_per_second"] for r in results) / len(results)
        
        return {
            "file": input_path,
            "runs": runs,
            "average_elapsed_seconds": avg_elapsed,
            "average_lines_per_second": avg_lps,
            "results": results
        }
    
    return {"error": "No benchmark results"}
