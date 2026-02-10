import csv
import json
import sys
from typing import List, TextIO, Optional
from .models import IPReport


class BaseWriter:
    
    def __init__(self, output_stream: TextIO):
        self.output_stream = output_stream
    
    def write(self, reports: List[IPReport]) -> None:
       
        raise NotImplementedError


class CSVWriter(BaseWriter):
    """Writes reports in CSV format."""
    
    def write(self, reports: List[IPReport]) -> None:
       
        if not reports:
            self.output_stream.write("No data to write\n")
            return
        
        writer = csv.writer(self.output_stream)
        
        writer.writerow([
            "IP Address",
            "Number of requests",
            "Percentage of Total Requests",
            "Total Bytes sent",
            "Percentage of the total amount of bytes"
        ])
        
        for report in reports:
            writer.writerow([
                report.ip_address,
                report.request_count,
                f"{report.request_percentage:.2f}",
                report.total_bytes,
                f"{report.bytes_percentage:.2f}"
            ])
    
    def write_with_summary(self, reports: List[IPReport], summary: Optional[dict] = None) -> None:
       
        self.write(reports)
        
        if summary:
            writer = csv.writer(self.output_stream)
            writer.writerow([])  # Empty row
            writer.writerow(["Summary"])
            for key, value in summary.items():
                writer.writerow([key.replace('_', ' ').title(), value])


class JSONWriter(BaseWriter):
    
    def write(self, reports: List[IPReport]) -> None:
       
        if not reports:
            self.output_stream.write("[]\n")
            return
        
        results = []
        
        for report in reports:
            results.append({
                "ip_address": report.ip_address,
                "number_of_requests": report.request_count,
                "percentage_of_total_requests": report.request_percentage,
                "total_bytes_sent": report.total_bytes,
                "percentage_of_total_bytes": report.bytes_percentage
            })
        
        json.dump(results, self.output_stream, indent=2)
    
    def write_with_summary(self, reports: List[IPReport], summary: Optional[dict] = None) -> None:
        
        output = {
            "reports": [],
            "summary": summary or {}
        }
        
        for report in reports:
            output["reports"].append({
                "ip_address": report.ip_address,
                "number_of_requests": report.request_count,
                "percentage_of_total_requests": report.request_percentage,
                "total_bytes_sent": report.total_bytes,
                "percentage_of_total_bytes": report.bytes_percentage
            })
        
        json.dump(output, self.output_stream, indent=2)


def create_writer(format_type: str, output_stream: TextIO) -> BaseWriter:
    
    format_type = format_type.lower().strip()
    
    if format_type == "json":
        return JSONWriter(output_stream)
    elif format_type == "csv":
        return CSVWriter(output_stream)
    else:
        raise ValueError(f"Unsupported format: {format_type}. Use 'csv' or 'json'.")