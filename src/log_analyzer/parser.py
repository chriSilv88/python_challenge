import logging
from typing import Iterator, Optional
from .models import LogRecord

logger = logging.getLogger(__name__)


class LogParser:
    """Parses log files in streaming fashion."""
    
    def __init__(self, delimiter: str = ";", status_ok: str = "OK"):
        
        self.delimiter = delimiter
        self.status_ok = status_ok
    
    def parse_file(self, file_path: str, encoding: str = "utf-8") -> Iterator[Optional[LogRecord]]:
       
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                for line_num, line in enumerate(f, start=1):
                    yield self._parse_line(line, line_num)
        except FileNotFoundError:
            logger.error("File not found: %s", file_path)
            raise
        except UnicodeDecodeError as e:
            logger.error("Encoding error in %s: %s", file_path, e)
            raise
        except OSError as e:
            logger.error("OS error reading %s: %s", file_path, e)
            raise
    
    def _parse_line(self, line: str, line_num: int) -> Optional[LogRecord]:
        
        line = line.rstrip('\n\r')  # Remove trailing newlines
        
        if not line.strip():
            logger.debug("Line %d: Empty line", line_num)
            return None
        
        try:
            parts = line.split(self.delimiter)
            if len(parts) != 4:
                logger.debug("Line %d: Expected 4 fields, got %d", line_num, len(parts))
                return None
            
            timestamp, bytes_str, status, remote_addr = parts
            
            # Remove whitespace
            timestamp = timestamp.strip()
            status = status.strip()
            remote_addr = remote_addr.strip()
            
            # Filter by status
            if status != self.status_ok:
                logger.debug("Line %d: Status not OK: %s", line_num, status)
                return None
            
            # Validate and convert bytes
            bytes_sent = int(bytes_str.strip())
            if bytes_sent < 0:
                logger.debug("Line %d: Negative bytes: %d", line_num, bytes_sent)
                return None
            
            # Validate IP address format 
            if not remote_addr or ' ' in remote_addr:
                logger.debug("Line %d: Invalid IP address: %s", line_num, remote_addr)
                return None
            
            return LogRecord(
                timestamp=timestamp,
                bytes_sent=bytes_sent,
                status=status,
                remote_addr=remote_addr
            )
            
        except (ValueError, IndexError) as e:
            logger.debug("Line %d: Parse error: %s - Line: %s", line_num, e, line[:100])
            return None
    
    def count_lines(self, file_path: str, encoding: str = "utf-8") -> tuple[int, int]:
        
        total = 0
        valid = 0
        
        for record in self.parse_file(file_path, encoding):
            total += 1
            if record is not None:
                valid += 1
        
        return total, valid