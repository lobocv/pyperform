__author__ = 'Calvin'
from pyperform import ComparisonBenchmark


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

with open('report.txt', 'w') as f:
    ComparisonBenchmark.summarize('Group1', f)