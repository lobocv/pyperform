__author__ = 'Calvin'
from pyperform import ComparisonBenchmark


def setup_func():
    from test_classes import MyClass

    self = MyClass()
    self.a = 12
    self.b = 123

@ComparisonBenchmark('Group1', setup=setup_func, largs=(100,))
def mytest(l):
    out = 0.
    for i in xrange(l):
        out += i
    print self.a
    return out

@ComparisonBenchmark('Group1', setup=setup_func, largs=(100,))
def mytest2(l):
    out = 0.
    for i in range(l):
        out += i

    return out

with open('report.txt', 'w') as f:
    ComparisonBenchmark.summarize('Group1', f)