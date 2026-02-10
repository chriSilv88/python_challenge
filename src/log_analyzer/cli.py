import argparse
import sys
import logging
from pathlib import Path
from typing import Optional
from .parser import LogParser
from .aggregator import Aggregator
from .writer import create_writer

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_log_file(
    input_path: str,
    output_path: Optional[str] = None,
    format_type: str = "csv",
    encoding: str = "utf-8",
    delimiter: str = ";",
    status_ok: str = "OK",
    sort_by: str = "requests",
    descending: bool = True,
    show_summary: bool = False,
    progress_step: int = 10000
) -> dict:
   
    # Validate input file
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Validate progress_step
    if progress_step < 0:
        raise ValueError("progress_step must be non-negative")
    
    # Create components
    parser = LogParser(delimiter=delimiter, status_ok=status_ok)
    aggregator = Aggregator()
    
    # Process file
    logger.info("Processing file: %s", input_path)
    processed_count = 0
    valid_count = 0
    
    for record in parser.parse_file(input_path, encoding):
        processed_count += 1
        if record is not None:
            aggregator.add_record(record)
            valid_count += 1
        
        if progress_step > 0 and processed_count % progress_step == 0:
            logger.info("Processed %d lines (valid: %d)...", 
                       processed_count, valid_count)
    
    logger.info("Processing complete. Valid records: %d/%d", 
                valid_count, processed_count)
    
    # Generate reports
    reports = aggregator.generate_reports(sort_by=sort_by, descending=descending)
    
    # Prepare output stream
    if output_path is None or output_path == "-":
        output_stream = sys.stdout
        close_stream = False
    else:
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_stream = open(output_path, 'w', encoding=encoding)
        close_stream = True
    
    try:
        # Write output
        writer = create_writer(format_type, output_stream)
        
        if show_summary:
            if hasattr(writer, 'write_with_summary'):
                writer.write_with_summary(reports, aggregator.get_summary())
            else:
                writer.write(reports)
                if format_type == "csv":
                    output_stream.write("\n\nSummary:\n")
                    for key, value in aggregator.get_summary().items():
                        output_stream.write(f"{key}: {value}\n")
        else:
            writer.write(reports)
            
    finally:
        if close_stream:
            output_stream.close()
    
    return {
        "input_file": str(input_path),
        "output_file": output_path if output_path != "-" else "stdout",
        "format": format_type,
        "total_lines": processed_count,
        "valid_records": valid_count,
        "unique_ips": aggregator.unique_ips,
        "total_requests": aggregator.total_requests,
        "total_bytes": aggregator.total_bytes,
        "error_count": aggregator.error_count,
        "processing_success": True
    }


def main(args=None):
    """
    Main CLI entry point.
    
    Args:
        args: Command-line arguments (for testing)
    """
    parser = argparse.ArgumentParser(
        description="Log Analyzer - Exercise #1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.log_analyzer.cli analyze -i data/sample.log
  python -m src.log_analyzer.cli analyze -i data/sample.log -f json -o report.json
  python -m src.log_analyzer.cli analyze -i data/sample.log -o - --summary
        """
    )
    
    subparsers = parser.add_subparsers(
        dest="command", 
        required=True, 
        help="Command to execute"
    )
    
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze log file and generate report"
    )
    
    analyze_parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input log file path"
    )
    
    analyze_parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="Output file (use '-' for stdout, default: -)"
    )
    
    analyze_parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)"
    )
    
    analyze_parser.add_argument(
        "--encoding",
        "-e",
        default="utf-8",
        help="File encoding (default: utf-8)"
    )
    
    analyze_parser.add_argument(
        "--delimiter",
        "-d",
        default=";",
        help="Field delimiter in log file (default: ;)"
    )
    
    analyze_parser.add_argument(
        "--status-ok",
        "-s",
        default="OK",
        help='Status value to accept (default: "OK")'
    )
    
    analyze_parser.add_argument(
        "--sort-by",
        choices=["requests", "bytes"],
        default="requests",
        help="Sort reports by (default: requests)"
    )
    
    sort_group = analyze_parser.add_mutually_exclusive_group()
    sort_group.add_argument(
        "--descending",
        action="store_true",
        default=True,
        help="Sort in descending order (default)"
    )
    sort_group.add_argument(
        "--ascending",
        action="store_true",
        help="Sort in ascending order"
    )
    
    analyze_parser.add_argument(
        "--summary",
        action="store_true",
        help="Include summary statistics in output"
    )
    
    analyze_parser.add_argument(
        "--progress-step",
        type=int,
        default=10000,
        help="Log progress every N lines (0 to disable, default: 10000)"
    )
    
    analyze_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    analyze_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress all non-error output"
    )
    
    count_parser = subparsers.add_parser(
        "count",
        help="Count lines in log file"
    )
    
    count_parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input log file path"
    )
    
    count_parser.add_argument(
        "--encoding",
        "-e",
        default="utf-8",
        help="File encoding (default: utf-8)"
    )
    
    count_parser.add_argument(
        "--delimiter",
        "-d",
        default=";",
        help="Field delimiter in log file (default: ;)"
    )
    
    count_parser.add_argument(
        "--status-ok",
        "-s",
        default="OK",
        help='Status value to accept (default: "OK")'
    )
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif parsed_args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
   
    try:
        if parsed_args.command == "analyze":
            if parsed_args.ascending:
                descending = False
            else:
                descending = True  
            
            result = analyze_log_file(
                input_path=parsed_args.input,
                output_path=parsed_args.output,
                format_type=parsed_args.format,
                encoding=parsed_args.encoding,
                delimiter=parsed_args.delimiter,
                status_ok=parsed_args.status_ok,
                sort_by=parsed_args.sort_by,
                descending=descending, 
                show_summary=parsed_args.summary,
                progress_step=parsed_args.progress_step
            )
            
            if not parsed_args.quiet:
                print(f"\n Analysis complete!", file=sys.stderr)
                print(f"   Input: {result['input_file']}", file=sys.stderr)
                print(f"   Output: {result['output_file']}", file=sys.stderr)
                print(f"   Valid records: {result['valid_records']}/{result['total_lines']}", file=sys.stderr)
                print(f"   Unique IPs: {result['unique_ips']}", file=sys.stderr)
                print(f"   Total requests: {result['total_requests']}", file=sys.stderr)
                print(f"   Total bytes: {result['total_bytes']:,}", file=sys.stderr)
        
        elif parsed_args.command == "count":
            parser = LogParser(
                delimiter=parsed_args.delimiter,
                status_ok=parsed_args.status_ok
            )
            total, valid = parser.count_lines(parsed_args.input, parsed_args.encoding)
            invalid = total - valid
            
            print(f"Total lines: {total}")
            print(f"Valid lines (status={parsed_args.status_ok}): {valid}")
            print(f"Invalid/skipped lines: {invalid}")
            if total > 0:
                print(f"Valid percentage: {(valid/total*100):.1f}%")
        
        else:
            parser.print_help()
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if parsed_args.verbose:
            logger.exception("Unexpected error occurred during execution")
        else:
            error_msg = str(e)
            if not error_msg:
                error_msg = type(e).__name__
            print(f"Error: {error_msg}", file=sys.stderr)
        
        sys.exit(1)


if __name__ == "__main__":
    main()