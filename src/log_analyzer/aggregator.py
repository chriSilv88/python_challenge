import logging
from typing import Dict, List
from .models import LogRecord, IPStats, IPReport

logger = logging.getLogger(__name__)


class Aggregator:
    """Aggregates statistics per IP address and produces reports."""
    
    def __init__(self):
        """Initialize empty aggregator."""
        self._stats: Dict[str, IPStats] = {}
        self._total_requests = 0
        self._total_bytes = 0
        self._error_count = 0
    
    def add_record(self, record: LogRecord) -> None:
        ip = record.remote_addr
        
        # Skip invalid IPs 
        if not ip:
            self._error_count += 1
            return
        
        # Get or create IPStats for this IP
        if ip not in self._stats:
            self._stats[ip] = IPStats(ip_address=ip)
        
        # Update statistics
        self._stats[ip].add_record(record)
        self._total_requests += 1
        self._total_bytes += record.bytes_sent
    
    def generate_reports(self, sort_by: str = "requests", descending: bool = True) -> List[IPReport]:
       
        if sort_by not in ("requests", "bytes"):
            raise ValueError(f"sort_by must be 'requests' or 'bytes', got: {sort_by}")
        
        reports = []
        
        for stats in self._stats.values():
            # Calculate percentages (0 if no totals)
            request_pct = 0.0
            bytes_pct = 0.0
            
            if self._total_requests > 0:
                request_pct = (stats.request_count / self._total_requests) * 100
            
            if self._total_bytes > 0:
                bytes_pct = (stats.total_bytes / self._total_bytes) * 100
            
            reports.append(IPReport(
                ip_address=stats.ip_address,
                request_count=stats.request_count,
                request_percentage=round(request_pct, 2),
                total_bytes=stats.total_bytes,
                bytes_percentage=round(bytes_pct, 2)
            ))
        
        # Sort reports
        if sort_by == "bytes":
            key_func = lambda x: x.total_bytes
        else:  # "requests"
            key_func = lambda x: x.request_count
        
        return sorted(reports, key=key_func, reverse=descending)
    
    @property
    def total_requests(self) -> int:
        """Total number of requests across all IPs."""
        return self._total_requests
    
    @property
    def total_bytes(self) -> int:
        """Total bytes sent across all IPs."""
        return self._total_bytes
    
    @property
    def unique_ips(self) -> int:
        """Number of unique IP addresses."""
        return len(self._stats)
    
    @property
    def error_count(self) -> int:
        """Number of records that couldn't be aggregated."""
        return self._error_count
    
    def get_summary(self) -> Dict[str, any]:
        
        return {
            "total_requests": self._total_requests,
            "total_bytes": self._total_bytes,
            "unique_ips": self.unique_ips,
            "error_count": self._error_count,
            "avg_requests_per_ip": (
                self._total_requests / self.unique_ips 
                if self.unique_ips > 0 else 0
            ),
            "avg_bytes_per_ip": (
                self._total_bytes / self.unique_ips 
                if self.unique_ips > 0 else 0
            ),
        }