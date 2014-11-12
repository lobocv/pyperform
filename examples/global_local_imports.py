__author__ = 'calvin'
from pyperform import PerformanceComparison
import dis

@PerformanceComparison('Group1')
def local_import(*args, **kwargs):
    from math import log10

    for i in xrange(1, 10000):
        a = log10(i)
dis.dis(local_import)


from math import log10

@PerformanceComparison('Group1', setup='from math import log10')
def global_import(*args, **kwargs):
    for i in xrange(1, 10000):
        a = log10(i)

dis.dis(global_import)