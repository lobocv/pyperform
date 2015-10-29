__author__ = 'Calvin'
import weakref  # !

from pyperform import ComparisonBenchmark


class A(object):  # !
    def __init__(self):
        self.count = 0


a = A()  # !
ar = weakref.ref(a)  # !


@ComparisonBenchmark('Group1', largs=())
def without_weakref():
    a = A()
    for i in range(1000):
        a.count += 1
    return a.count


@ComparisonBenchmark('Group1', largs=())
def with_weakref():
    for i in range(1000):
        ar().count += 1
    return ar().count


ComparisonBenchmark.summarize('Group1')
