__author__ = 'Calvin'
try:
    from builtins import range
except ImportError:
    range = xrange
from pyperform import *


class SomeClass(object): #!

    def __init__(self, n):
        self.n = n
        self.count = 0
        if n > 0:
            self.a = SomeClass(n-1)

    def func(self):
        self.count += 1

        return sum(range(10))

@BenchmarkedClass()
class MyClass(object):

    def __init__(self):
        self.obj = SomeClass(5)             # setup an object with some nested lookup
        self.g = self.generator()           # setup the generator in advance

    @ComparisonBenchmark('gen', classname='MyClass', validation=True)
    def call_generator(self):
        for i in self.g:                # Call the generator which calls the function 100 times (like not_generator)
            pass
        return self.obj.a.a.a.a.count

    def generator(self):
        func = self.obj.a.a.a.a.func
        for i in range(100):
            func()
            yield i


    @ComparisonBenchmark('gen', classname='MyClass', validation=True)
    def not_generator(self):
        func = self.obj.a.a.a.a.func
        for i in range(100):
            func()
        return self.obj.a.a.a.a.count


if __name__ == '__main__':

    # c = MyClass()
    # c.call_generator()

    with open('report.txt', 'w') as _f:
        ComparisonBenchmark.summarize('gen', _f, include_source=1)
