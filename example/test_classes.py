__author__ = 'Calvin'
from pyperform import BenchmarkedClass, BenchmarkedFunction, ComparisonBenchmark

def SomeFunc(cls):
    print 'this is {}'.format(cls.__name__)
    return cls


@BenchmarkedClass(cls_args=(1, 2, 3), cls_kwargs={'a': 123})
class MyClass(object):

    def __init__(self, *args, **kwargs):
        self.s = ''

    @ComparisonBenchmark('String Joining', classname="MyClass")
    def do_something1(self, *args, **kwargs):
        s = ''
        self.s = ''
        for i in xrange(100):
            self.s += str(i)
            # s += str(i)

    @ComparisonBenchmark('String Joining', classname="MyClass")
    def do_something2(self, *args, **kwargs):
        self.s = ''.join(map(str, xrange(100)))
        # s = ''.join(map(str, xrange(100)))




MyClass(1,2,3)

MyClass(1,2346436,3)

MyClass(2241,2,3)
