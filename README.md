pyperform
=========

An easy and convenient way to performance test blocks python code.
Tired of writing separate scripts for your performance tests? Don't like coding in strings?
Using the pyperform decorators, you can easily implement timeit tests to your functions with just one line!

Example:

'''
@BenchmarkedFunction(largs=(5, 2, 10))
def TripleMultiply(a, b, c):
    result = a * b * c
    return result
'''

This result:
'''
TripleMultiply 	 1.344 ms
'''

Features of pyperform include:

    - Quick, easy to implement in-code performance tests.
    - Speed comparison of several functions.
    - Summary reports.
    - Supports class functions as well as global functions.
    - Performance tests can easily be disabled/enabled globally.
    - Library of performance tests to learn from.

To do / Potential Features:
    - Logging of system information (operating system, CPU frequency etc.)
    - Disassembled code
    - Code revision / performance history

