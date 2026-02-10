from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)  # Immutable for thread-safety and predictability
class LogRecord:
    """
    A single parsed log line.
    
    Attributes:
        timestamp: ISO 8601 formatted timestamp string (UTC)
        bytes_sent: Non-negative integer, bytes sent in response
        status: HTTP status string (e.g., 'OK', 'ERROR')
        remote_addr: IP address of the client (IPv4 or IPv6)
    """
    timestamp: str
    bytes_sent: int
    status: str
    remote_addr: str

    # Class constants – not instance-specific
    STATUS_OK: ClassVar[str] = "OK"
    DELIMITER: ClassVar[str] = ";"

    def __post_init__(self) -> None:
        """Validate the record after initialization."""
        if self.bytes_sent < 0:
            raise ValueError("bytes_sent cannot be negative")


@dataclass
class IPStats:
    
    ip_address: str
    request_count: int = 0
    total_bytes: int = 0

    def add_record(self, record: LogRecord) -> None:
        """Update statistics with a new log record."""
        self.request_count += 1
        self.total_bytes += record.bytes_sent


@dataclass(frozen=True)  # Immutable DTO for reporting
class IPReport:
  
    ip_address: str
    request_count: int
    request_percentage: float
    total_bytes: int
    bytes_percentage: float