# Log Analysis System - Technical Documentation

# 1. System Purpose and Scope
This document describes a log analysis system developed to process web server access logs and generate statistical reports. The system is designed to handle log files of varying sizes while maintaining efficient memory usage.

# 2. Problem Statement
We need to create a daily report from web server access logs that contains the following information grouped by IP address:

Number of requests from each IP

Percentage of total requests from each IP

Total bytes sent to each IP

Percentage of total bytes sent to each IP

The report must:

Only include entries with "OK" HTTP status

Be sorted by number of requests (highest first)

Be saved as a CSV file

Handle malformed data without crashing

# 3. Technical Requirements
Input Data Format
The system reads from /logfiles/requests.log where each line contains four semicolon-separated values:

TIMESTAMP - Event timestamp (string)

BYTES - Number of bytes sent (integer)

STATUS - HTTP response status (string)

REMOTE_ADDR - Client IP address (string)

Output Requirements
The system writes to /reports/ipaddr.csv with the following columns:

IP Address

Number of requests

Percentage of Total Requests (2 decimal places)

Total Bytes sent

Percentage of total amount of bytes (2 decimal places)

Processing Rules
Filter out all lines where STATUS is not "OK"

Group remaining entries by IP address

Calculate request counts and byte totals per IP

Compute percentages based on filtered data totals

Sort results by request count (descending)

# 4. System Design
Core Architecture
The system follows a modular design with three main components:

Log Parser: Reads and parses log files line by line

Data Processor: Filters, aggregates, and calculates statistics

Report Generator: Formats and writes output in required format

Memory Management Strategy
The system processes files using streaming approach:

Reads one line at a time (never loads entire file into memory)

Maintains minimal in memory data structures

Scales linearly with file size while using constant memory

# Error Handling
Invalid lines are skipped with appropriate logging

Data type conversions are validated

The system continues processing after errors

All errors are logged for debugging