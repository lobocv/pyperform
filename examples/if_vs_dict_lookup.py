__author__ = 'calvin'
import random #!

from pyperform import ComparisonBenchmark


def _setup():
    l = []
    lookup = {ii: l.append for ii in range(5)}


largs = (random.randint(0, 4),)

@ComparisonBenchmark('group1', setup=_setup, validation=True, timeit_number=10, timeit_repeat=1000)
def do_if():
    ii = random.randint(0, 4)
    if ii == 0:
        l.append(ii)
    elif ii == 1:
        l.append(ii)
    elif ii == 2:
        l.append(ii)
    elif ii == 3:
        l.append(ii)
    elif ii == 4:
        l.append(ii)

@ComparisonBenchmark('group1', setup=_setup, validation=True, timeit_number=10, timeit_repeat=1000)
def do_dict_lookup():
    ii = random.randint(0, 4)
    lookup[ii](ii)


ComparisonBenchmark.summarize('group1')