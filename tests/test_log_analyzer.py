import unittest
import tempfile
import csv
import json
import os
import sys
import io
from pathlib import Path
from unittest.mock import patch, MagicMock

# Path setup for importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.log_analyzer.parser import LogParser
from src.log_analyzer.aggregator import Aggregator
from src.log_analyzer.models import LogRecord, IPStats, IPReport
from src.log_analyzer.writer import CSVWriter, JSONWriter, create_writer
from src.log_analyzer.cli import analyze_log_file, main
from src.log_analyzer.utils import validate_log_file, create_sample_log

class TestLogRecord(unittest.TestCase):
    """LogRecord class tests."""
    
    def test_record_creation(self):
        """Test basic LogRecord creation."""
        record = LogRecord(
            timestamp="2024-01-01T10:00:00",
            bytes_sent=1024,
            status="OK",
            remote_addr="192.168.1.1"
        )
        
        self.assertEqual(record.timestamp, "2024-01-01T10:00:00")
        self.assertEqual(record.bytes_sent, 1024)
        self.assertEqual(record.status, "OK")
        self.assertEqual(record.remote_addr, "192.168.1.1")
    
    def test_record_negative_bytes_validation(self):
        """Test negative bytes validation."""
        with self.assertRaises(ValueError):
            LogRecord("2024-01-01T10:00:00", -1, "OK", "192.168.1.1")
    
    def test_record_immutability(self):
        """Test that LogRecord is immutable (frozen dataclass)."""
        record = LogRecord("2024-01-01T10:00:00", 1024, "OK", "192.168.1.1")
        
        # Attempting to modify an attribute should fail
        with self.assertRaises(Exception):
            record.bytes_sent = 2048

class TestIPStats(unittest.TestCase):
    """IPStats class tests."""
    
    def test_ipstats_creation(self):
        """Test IPStats creation."""
        stats = IPStats(ip_address="192.168.1.1")
        
        self.assertEqual(stats.ip_address, "192.168.1.1")
        self.assertEqual(stats.request_count, 0)
        self.assertEqual(stats.total_bytes, 0)
    
    def test_ipstats_add_record(self):
        """Test adding a record to IPStats."""
        stats = IPStats(ip_address="192.168.1.1")
        record = LogRecord("2024-01-01T10:00:00", 1024, "OK", "192.168.1.1")
        
        stats.add_record(record)
        
        self.assertEqual(stats.request_count, 1)
        self.assertEqual(stats.total_bytes, 1024)
        
        # Second record
        record2 = LogRecord("2024-01-01T10:00:01", 2048, "OK", "192.168.1.1")
        stats.add_record(record2)
        
        self.assertEqual(stats.request_count, 2)
        self.assertEqual(stats.total_bytes, 3072) 

class TestLogParser(unittest.TestCase):
    """Log parser tests."""
    
    def setUp(self):
        """Setup for each test."""
        self.parser = LogParser(delimiter=";", status_ok="OK")
    
    def test_parse_valid_line(self):
        """Test parsing a valid line."""
        line = "2024-01-01T10:00:00;1024;OK;192.168.1.1"
        record = self.parser._parse_line(line, 1)
        
        self.assertIsNotNone(record)
        self.assertEqual(record.timestamp, "2024-01-01T10:00:00")
        self.assertEqual(record.bytes_sent, 1024)
        self.assertEqual(record.status, "OK")
        self.assertEqual(record.remote_addr, "192.168.1.1")
    
    def test_parse_line_with_whitespace(self):
        """Test parsing with whitespace."""
        line = "  2024-01-01T10:00:00  ;  1024  ;  OK  ;  192.168.1.1  "
        record = self.parser._parse_line(line, 1)
        
        self.assertIsNotNone(record)
        self.assertEqual(record.remote_addr, "192.168.1.1")
    
    def test_parse_invalid_status(self):
        """Test line with status other than OK."""
        line = "2024-01-01T10:00:00;1024;ERROR;192.168.1.1"
        record = self.parser._parse_line(line, 1)
        
        self.assertIsNone(record)
    
    def test_parse_malformed_line(self):
        """Test malformed line."""
        test_cases = [
            "2024-01-01T10:00:00;1024;OK",  # Missing fields
            "only;two;fields",               # Only 2 fields
            "",                              # Empty line
            "   ",                           # Only spaces
        ]
        
        for line in test_cases:
            record = self.parser._parse_line(line, 1)
            self.assertIsNone(record, f"Expected None for line: '{line}'")
    
    def test_parse_negative_bytes(self):
        """Test line with negative bytes."""
        line = "2024-01-01T10:00:00;-100;OK;192.168.1.1"
        record = self.parser._parse_line(line, 1)
        
        self.assertIsNone(record)
    
    def test_parse_invalid_bytes_format(self):
        """Test line with non-numeric bytes."""
        line = "2024-01-01T10:00:00;not_a_number;OK;192.168.1.1"
        record = self.parser._parse_line(line, 1)
        
        self.assertIsNone(record)
    
    def test_parse_file(self):
        """Test complete file parsing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
            f.write("2024-01-01T10:00:01;2048;OK;192.168.1.2\n")
            f.write("2024-01-01T10:00:02;512;ERROR;192.168.1.1\n")
            f.write("2024-01-01T10:00:03;4096;OK;192.168.1.1\n")
            temp_file = f.name
        
        try:
            records = list(self.parser.parse_file(temp_file))
            
            # We should have 4 elements (one is None for ERROR)
            self.assertEqual(len(records), 4)
            
            # Count valid records
            valid_records = [r for r in records if r is not None]
            self.assertEqual(len(valid_records), 3)
            
            # Verify records
            self.assertEqual(valid_records[0].remote_addr, "192.168.1.1")
            self.assertEqual(valid_records[1].remote_addr, "192.168.1.2")
            
        finally:
            os.unlink(temp_file)
    
    def test_count_lines(self):
        """Test line counting."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
            f.write("2024-01-01T10:00:01;2048;ERROR;192.168.1.2\n")
            f.write("2024-01-01T10:00:02;512;OK;192.168.1.3\n")
            temp_file = f.name
        
        try:
            total, valid = self.parser.count_lines(temp_file)
            
            self.assertEqual(total, 3)
            self.assertEqual(valid, 2)  # Only 2 with OK status
            
        finally:
            os.unlink(temp_file)

class TestAggregator(unittest.TestCase):
    """Aggregator tests."""
    
    def setUp(self):
        """Setup for each test."""
        self.aggregator = Aggregator()
        
        # Test records
        self.records = [
            LogRecord("2024-01-01T10:00:00", 1024, "OK", "192.168.1.1"),
            LogRecord("2024-01-01T10:00:01", 2048, "OK", "192.168.1.2"),
            LogRecord("2024-01-01T10:00:02", 4096, "OK", "192.168.1.1"),
            LogRecord("2024-01-01T10:00:03", 0, "OK", "192.168.1.3"),
        ]
        
        for record in self.records:
            self.aggregator.add_record(record)
    
    def test_add_record(self):
        """Test adding a record."""
        aggregator = Aggregator()
        
        self.assertEqual(aggregator.total_requests, 0)
        self.assertEqual(aggregator.total_bytes, 0)
        self.assertEqual(aggregator.unique_ips, 0)
        
        record = LogRecord("2024-01-01T10:00:00", 1024, "OK", "192.168.1.1")
        aggregator.add_record(record)
        
        self.assertEqual(aggregator.total_requests, 1)
        self.assertEqual(aggregator.total_bytes, 1024)
        self.assertEqual(aggregator.unique_ips, 1)
    
    def test_add_record_with_invalid_ip(self):
        """Test adding a record with empty IP (should be filtered by parser)."""
        aggregator = Aggregator()
        
        # Record with empty IP (mock)
        class MockRecord:
            remote_addr = ""
            bytes_sent = 1024
        
        aggregator.add_record(MockRecord())
        
        self.assertEqual(aggregator.error_count, 1)
        self.assertEqual(aggregator.total_requests, 0)
    
    def test_total_statistics(self):
        """Test total statistics."""
        self.assertEqual(self.aggregator.total_requests, 4)
        self.assertEqual(self.aggregator.total_bytes, 1024 + 2048 + 4096 + 0)
        self.assertEqual(self.aggregator.unique_ips, 3)
        self.assertEqual(self.aggregator.error_count, 0)
    
    def test_generate_reports_default(self):
        """Test report generation with default sorting (requests DESC)."""
        reports = self.aggregator.generate_reports()
        
        self.assertEqual(len(reports), 3)
        
        # Verify sorting by requests (descending)
        self.assertEqual(reports[0].ip_address, "192.168.1.1")  # 2 requests
        self.assertEqual(reports[0].request_count, 2)
        self.assertEqual(reports[0].total_bytes, 5120)  # 1024 + 4096
        
        self.assertEqual(reports[1].ip_address, "192.168.1.2")  # 1 request
        self.assertEqual(reports[2].ip_address, "192.168.1.3")  # 1 request, 0 bytes
    
    def test_generate_reports_sort_by_bytes(self):
        """Test report generation sorted by bytes."""
        reports = self.aggregator.generate_reports(sort_by="bytes", descending=True)
        
        # Verify sorting by bytes (descending)
        self.assertEqual(reports[0].ip_address, "192.168.1.1")  # 5120 bytes
        self.assertEqual(reports[0].total_bytes, 5120)
        
        self.assertEqual(reports[1].ip_address, "192.168.1.2")  # 2048 bytes
        self.assertEqual(reports[2].ip_address, "192.168.1.3")  # 0 bytes
    
    def test_generate_reports_ascending(self):
        """Test report generation in ascending order."""
        reports = self.aggregator.generate_reports(sort_by="requests", descending=False)
        
        # Verify there are 3 reports
        self.assertEqual(len(reports), 3)
        
        # Verify first two have 1 request
        self.assertEqual(reports[0].request_count, 1)
        self.assertEqual(reports[1].request_count, 1)
        
        # Verify third has 2 requests
        self.assertEqual(reports[2].request_count, 2)
        self.assertEqual(reports[2].ip_address, "192.168.1.1")
        
        # Verify first two are expected IPs
        expected_ips = {"192.168.1.2", "192.168.1.3"}
        actual_ips = {reports[0].ip_address, reports[1].ip_address}
        self.assertEqual(actual_ips, expected_ips)
    
    def test_generate_reports_percentages(self):
        """Test percentage calculation."""
        reports = self.aggregator.generate_reports()
        
        total_requests = self.aggregator.total_requests  # 4
        total_bytes = self.aggregator.total_bytes        # 7168
        
        for report in reports:
            if report.ip_address == "192.168.1.1":
                # 2/4 = 50%
                self.assertEqual(report.request_percentage, 50.0)
                # 5120/7168 ≈ 71.43%
                self.assertAlmostEqual(report.bytes_percentage, 71.43, places=2)
            
            if report.ip_address == "192.168.1.2":
                # 1/4 = 25%
                self.assertEqual(report.request_percentage, 25.0)
                # 2048/7168 ≈ 28.57%
                self.assertAlmostEqual(report.bytes_percentage, 28.57, places=2)
    
    def test_generate_reports_empty_aggregator(self):
        """Test report generation from empty aggregator."""
        aggregator = Aggregator()
        reports = aggregator.generate_reports()
        
        self.assertEqual(len(reports), 0)
    
    def test_get_summary(self):
        """Test summary statistics."""
        summary = self.aggregator.get_summary()
        
        self.assertIn("total_requests", summary)
        self.assertIn("total_bytes", summary)
        self.assertIn("unique_ips", summary)
        self.assertIn("avg_requests_per_ip", summary)
        self.assertIn("avg_bytes_per_ip", summary)
        self.assertIn("error_count", summary)
        
        self.assertEqual(summary["total_requests"], 4)
        self.assertEqual(summary["unique_ips"], 3)
        self.assertAlmostEqual(summary["avg_requests_per_ip"], 4/3, places=2)
    
    def test_invalid_sort_by(self):
        """Test with invalid sorting criterion."""
        with self.assertRaises(ValueError):
            self.aggregator.generate_reports(sort_by="invalid_field")

class TestWriters(unittest.TestCase):
    """Writer tests (CSV and JSON)."""
    
    def setUp(self):
        """Setup for each test."""
        self.reports = [
            IPReport(
                ip_address="192.168.1.1",
                request_count=2,
                request_percentage=50.0,
                total_bytes=5120,
                bytes_percentage=71.43
            ),
            IPReport(
                ip_address="192.168.1.2",
                request_count=1,
                request_percentage=25.0,
                total_bytes=2048,
                bytes_percentage=28.57
            ),
        ]
    
    def test_csv_writer_basic(self):
        """Test basic CSV writing."""
        output = io.StringIO()
        writer = CSVWriter(output)
        writer.write(self.reports)
        
        output.seek(0)
        reader = csv.reader(output)
        rows = list(reader)
        
        # Verify header
        self.assertEqual(rows[0], [
            "IP Address",
            "Number of requests",
            "Percentage of Total Requests",
            "Total Bytes sent",
            "Percentage of the total amount of bytes"
        ])
        
        # Verify data
        self.assertEqual(rows[1][0], "192.168.1.1")
        self.assertEqual(rows[1][1], "2")
        self.assertEqual(rows[1][2], "50.00")
        self.assertEqual(rows[1][3], "5120")
        self.assertEqual(rows[1][4], "71.43")
        
        self.assertEqual(len(rows), 3) 
    
    def test_csv_writer_empty_reports(self):
        """Test CSV writing with empty list."""
        output = io.StringIO()
        writer = CSVWriter(output)
        writer.write([])
        
        content = output.getvalue()
        self.assertEqual(content, "No data to write\n")
    
    def test_csv_writer_with_summary(self):
        """Test CSV writing with summary."""
        output = io.StringIO()
        writer = CSVWriter(output)
        
        summary = {"total_requests": 10, "unique_ips": 3}
        
        if hasattr(writer, 'write_with_summary'):
            writer.write_with_summary(self.reports, summary)
        else:
            writer.write(self.reports)
        
        content = output.getvalue()
        self.assertIn("192.168.1.1", content)
    
    def test_json_writer_basic(self):
        """Test basic JSON writing."""
        output = io.StringIO()
        writer = JSONWriter(output)
        writer.write(self.reports)
        
        content = output.getvalue()
        data = json.loads(content)
        
        # Verify JSON structure
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        
        # Verify first element
        self.assertEqual(data[0]["ip_address"], "192.168.1.1")
        self.assertEqual(data[0]["number_of_requests"], 2)
        self.assertEqual(data[0]["percentage_of_total_requests"], 50.0)
        self.assertEqual(data[0]["total_bytes_sent"], 5120)
        self.assertEqual(data[0]["percentage_of_total_bytes"], 71.43)
    
    def test_json_writer_empty_reports(self):
        """Test JSON writing with empty list."""
        output = io.StringIO()
        writer = JSONWriter(output)
        writer.write([])
        
        content = output.getvalue()
        data = json.loads(content)
        
        self.assertEqual(data, [])
    
    def test_json_writer_with_summary(self):
        """Test JSON writing with summary."""
        output = io.StringIO()
        writer = JSONWriter(output)
        
        summary = {"total_requests": 10, "unique_ips": 3}
        
        if hasattr(writer, 'write_with_summary'):
            writer.write_with_summary(self.reports, summary)
            content = output.getvalue()
            data = json.loads(content)
            
            self.assertIn("reports", data)
            self.assertIn("summary", data)
            self.assertEqual(data["summary"]["total_requests"], 10)
    
    def test_create_writer_factory(self):
        """Test writer factory creation."""
        # Test CSV writer
        output = io.StringIO()
        csv_writer = create_writer("csv", output)
        self.assertIsInstance(csv_writer, CSVWriter)
        
        # Test JSON writer
        output = io.StringIO()
        json_writer = create_writer("json", output)
        self.assertIsInstance(json_writer, JSONWriter)
        
        # Test invalid format
        output = io.StringIO()
        with self.assertRaises(ValueError):
            create_writer("xml", output)
        
        # Test case insensitive
        output = io.StringIO()
        csv_writer2 = create_writer("CSV", output)
        self.assertIsInstance(csv_writer2, CSVWriter)

class TestCLI(unittest.TestCase):
    """Command-line interface tests."""
    
    def setUp(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_analyze_log_file_basic(self):
        """Test main analysis function."""
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
            f.write("2024-01-01T10:00:01;2048;OK;192.168.1.2\n")
            f.write("2024-01-01T10:00:02;512;ERROR;192.168.1.3\n")
        
        output_file = os.path.join(self.temp_dir, "report.csv")
        
        result = analyze_log_file(
            input_path=log_file,
            output_path=output_file,
            format_type="csv",
            progress_step=0 
        )
        
        # Verifications
        self.assertTrue(result["processing_success"])
        self.assertEqual(result["valid_records"], 2)
        self.assertEqual(result["total_lines"], 3)
        self.assertEqual(result["unique_ips"], 2)
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0][0], "IP Address")
    
    def test_analyze_log_file_stdout(self):
        """Test output to stdout."""
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
        
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            result = analyze_log_file(
                input_path=log_file,
                output_path="-",  # stdout
                format_type="csv"
            )
            
            output = sys.stdout.getvalue()
            
            self.assertEqual(result["output_file"], "stdout")
            self.assertIn("IP Address", output)
            self.assertIn("192.168.1.1", output)
            
        finally:
            sys.stdout = old_stdout
    
    def test_analyze_log_file_json(self):
        """Test output in JSON format."""
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
        
        output_file = os.path.join(self.temp_dir, "report.json")
        
        result = analyze_log_file(
            input_path=log_file,
            output_path=output_file,
            format_type="json"
        )
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, list)
            self.assertEqual(data[0]["ip_address"], "192.168.1.1")
    
    def test_analyze_log_file_file_not_found(self):
        """Test with non-existent input file."""
        with self.assertRaises(FileNotFoundError):
            analyze_log_file(
                input_path="/non/existing/file.log",
                output_path="/tmp/report.csv"
            )
    
    @patch('sys.argv', ['test_cli.py', 'analyze', '--help'])
    def test_cli_help(self):
        """Test that help is displayed correctly."""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            with self.assertRaises(SystemExit) as cm:
                main()
            
            self.assertEqual(cm.exception.code, 0)
            output = sys.stdout.getvalue()
            self.assertIn("usage:", output.lower())
            self.assertIn("analyze", output)
            
        finally:
            sys.stdout = old_stdout

class TestUtils(unittest.TestCase):
    """Utility tests."""
    
    def setUp(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_validate_log_file(self):
        """Test log file validation."""
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
            f.write("malformed_line\n")
        
        result = validate_log_file(log_file)
        
        self.assertIn("total_lines", result)
        self.assertIn("valid_lines", result)
        self.assertGreaterEqual(result["total_lines"], 1)
    
    def test_create_sample_log(self):
        """Test sample log file creation."""
        output_file = os.path.join(self.temp_dir, "sample.log")
        create_sample_log(output_file, num_lines=10)
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 10)

class TestIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_pipeline_csv(self):
        """Test complete pipeline with CSV output."""
        log_file = os.path.join(self.temp_dir, "input.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("2024-01-01T10:00:00;1024;OK;192.168.1.1\n")
            f.write("2024-01-01T10:00:01;2048;OK;192.168.1.2\n")
        
        parser = LogParser()
        aggregator = Aggregator()
        for record in parser.parse_file(log_file):
            if record:
                aggregator.add_record(record)
        
        reports = aggregator.generate_reports()
        output_file = os.path.join(self.temp_dir, "output.csv")
        with open(output_file, 'w', encoding='utf-8') as f:
            writer = CSVWriter(f)
            writer.write(reports)
        
        self.assertTrue(os.path.exists(output_file))
    
    def test_empty_log_file(self):
        """Test with empty log file."""
        log_file = os.path.join(self.temp_dir, "empty.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            pass
        
        parser = LogParser()
        records = list(parser.parse_file(log_file))
        self.assertEqual(len(records), 0)
        
        output_file = os.path.join(self.temp_dir, "output.csv")
        with open(output_file, 'w', encoding='utf-8') as f:
            writer = CSVWriter(f)
            writer.write([])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, "No data to write\n")

def run_all_tests():
    """Function to run all tests."""
    print("\n" + "="*70)
    print("STARTING LOG ANALYZER TEST SUITE (unittest)")
    print("="*70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestLogRecord,
        TestIPStats,
        TestLogParser,
        TestAggregator,
        TestWriters,
        TestCLI,
        TestUtils,
        TestIntegration,
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("LOG ANALYZER TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("\n ALL TESTS PASSED!")
    else:
        print("\n SOME TESTS FAILED:")
        
        for test, traceback in result.failures:
            print(f"\n FAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\n ERROR: {test}")
            print(traceback)
    
    print("="*70)
    
    return result.wasSuccessful()