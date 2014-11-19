__author__ = 'Calvin'
from pyperform import ComparisonBenchmark, BenchmarkedFunction


@ComparisonBenchmark('Group1', largs=(100,))
def mytest(l):
    out = 0.
    for i in xrange(l):
        out += i
    return out

@ComparisonBenchmark('Group1', largs=(100,))
def mytest2(l):
    out = 0.
    for i in range(l):
        out += i

    return out

def test3_setup():
    a = 5
    b = 12

@BenchmarkedFunction(setup=test3_setup, largs=(5, ))
def mytest3(multiplier):
    return a * b * multiplier

with open('report.txt', 'w') as f:
    ComparisonBenchmark.summarize('Group1', f)

mytest3(463)