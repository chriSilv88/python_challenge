# Technical Decision: Big Integer Representation Strategy

#  Decision Context
During the design of the big integer multiplication system for Exercise #2, we evaluated multiple approaches for representing and manipulating arbitrarily large integers:

Decimal Digit Arrays (LSB first): Arrays of decimal digits (0-9) with least significant-digit first

Binary Representation: Bit arrays or integer chunks in base 2^32 or base 2^64

String Representation: Storing numbers as ASCII character strings

# Decision
We selected the Decimal Digit Arrays (LSB-first) approach.

# Rationale
Primary Reason: Requirement Compliance
The exercise explicitly requires implementing multiplication using only addition operations. The decimal digit array representation:

Directly supports addition only multiplication through repeated addition of digit groups

# Maintains transparency of the multiplication process

Aligns with the pedagogical intent of understanding fundamental arithmetic operations

Secondary Reason: Debuggability and Transparency
Human readable: Decimal digits are familiar and easy to inspect

Step by step traceability: Each addition operation can be traced and verified

Intuitive error identification: Issues are immediately visible in decimal form