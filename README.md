# Python Challenge

Author: Christian Silvestri<br>
Date: 2026-02-07

# Overview

This repository contains solutions developed specifically for a technical assessment consisting of two independent exercises:

# Log Analyzer — generation of daily traffic reports from raw HTTP logs

# BigInt arithmetic — integer multiplication using addition only, including factorial computation

The focus of this project is correctness, clarity, and reasonable engineering practices, rather than enterprise-level completeness or production hardening.

The structure and abstractions are intentionally kept clean but lightweight, to reflect how a senior developer would approach a technical test.

# Project Structure

```text
python-challenge/
│
├─ data/                # Sample input logs and generated example reports
├─ docs/                # Technical notes and design decisions
│   ├─ api/
│   └─ decisions/
├─ examples/            # Executable scripts demonstrating full solutions
├─ src/                 # Source code for both exercises
│   ├─ log_analyzer/
│   └─ bigint/
├─ tests/               # Unit tests
└─ .gitignore```

Requirements

Python 3.11+

Standard library only (no external frameworks or dependencies)

Unix-like shell (bash / zsh)

Exercise 1 — Log Analyzer

The log analyzer processes HTTP access logs and produces a daily report with:

IP Address

Number of requests

Percentage of total requests

Total bytes sent

Percentage of total bytes

Only records with HTTP status OK are considered, as required by the specification.

The implementation is streaming-based, allowing large files to be processed with constant memory usage.

#  Run Example

From the project root:

python3 examples/run_exercise1.py


This will:

Read a sample log from data/sample.log

Generate a CSV report

Print a short execution summary to stdout

# Exercise 2 — BigInt Arithmetic

This exercise implements multiplication of arbitrarily large integers using addition only, while storing numbers as arrays of digits.

The solution includes:

Addition based multiplication

Factorial computation

A simple internal digit representation

The implementation prioritizes clarity and correctness, not advanced multiplication algorithms.

# Run Example
python3 examples/run_exercise2.py

# Unit Tests

Basic unit tests are provided to validate correctness and edge cases.

# Run all tests from the project root:

python3 -m unittest discover -s tests

# Documentation

docs/api/ — brief API notes for main components

docs/decisions/ — short design rationale documents (ADRs)

These documents explain why certain design choices were made, without overengineering the solution.

# Notes

This project is intentionally scoped to a technical test, not a production system

No frameworks or unnecessary abstractions were introduced

The goal is to demonstrate problem solving, code quality, and engineering judgment
