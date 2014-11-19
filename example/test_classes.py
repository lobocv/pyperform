__author__ = 'Calvin'
from pyperform import BenchmarkedClass, BenchmarkedFunction, ComparisonBenchmark

def SomeFunc(cls):
    print 'this is {}'.format(cls.__name__)
    return cls


@BenchmarkedClass(cls_args=(1, 2, 3), cls_kwargs={'a': 123})
class MyClass(object):

    def __init__(self, *args, **kwargs):
        self.s = ''

    @ComparisonBenchmark('String Joining', classname="MyClass", largs=(100,))
    def do_something1(self, n, *args, **kwargs):
        self.s = ''
        for i in xrange(n):
            self.s += str(i)

    @ComparisonBenchmark('String Joining', classname="MyClass", largs=(100,), kwargs={'kwarg1': 'k', 'kwarg2': 5000, 'extra_kwarg': 'Extra kwarg'})
    def do_something2(self, n, kwarg1='a', kwarg2=123, *args, **kwargs):
        # print kwarg1, kwarg2, kwargs
        self.s = ''.join(map(str, xrange(n)))





MyClass(1,2,3)

MyClass(1,2346436,3)

MyClass(2241,2,3)
