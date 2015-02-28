__author__ = 'Calvin'
try:
    from builtins import range
except ImportError:
    range = xrange
from pyperform import *


def _setup():
    class SomeClass(object):

        def __init__(self, n):
            self.n = n
            self.count = 0
            if n > 0:
                self.a = SomeClass(n-1)

        def func(self):
            self.count +=1

            return sum(range(10))

class SomeClass(object):

    def __init__(self, n):
        self.n = n
        self.count = 0
        if n > 0:
            self.a = SomeClass(n-1)

    def func(self):
        self.count += 1
        return sum(range(10))

@BenchmarkedClass(setup=_setup)
class MyClass(object):

    def __init__(self):
        self.obj = SomeClass(5)
        self.g = self.generator()

    @ComparisonBenchmark('gen', classname='MyClass', setup=_setup, validation=True)
    def call_generator(self):
        # self.g = self.generator()
        for i in self.g:
            pass
        return self.obj.a.a.a.a.count

    def generator(self):
        func = self.obj.a.a.a.a.func
        for i in range(100):
            func()
            yield i


    @ComparisonBenchmark('gen', classname='MyClass', setup=_setup, validation=True)
    def not_generator(self):
        for i in range(100):
            self.obj.a.a.a.a.func()
        return self.obj.a.a.a.a.count


if __name__ == '__main__':

    # c = MyClass()
    # c.call_generator()

    with open('report.txt', 'w') as _f:
        ComparisonBenchmark.summarize('gen', _f, include_source=1)
