__author__ = 'Calvin'
from pyperform import ComparisonBenchmark, BenchmarkedFunction
import math #!

@ComparisonBenchmark('Group1', largs=(100,))
def mytest(l):
    out = 0.
    for i in range(l):
        out += i
    return out

@ComparisonBenchmark('Group1', largs=(100,))
def mytest2(l):
    out = 0.
    for i in range(l):
        out += i

    return out

@BenchmarkedFunction(largs=(5, 2, 10))
def TripleMultiply(a, b, c):
    result = a * b * c
    return result

with open('report.txt', 'w') as f:
    ComparisonBenchmark.summarize('Group1', f)

