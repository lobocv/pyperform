__author__ = 'Calvin'
from pyperform import PerformanceComparison


@PerformanceComparison('Group1', l=range(10))
def iter_reversed(l):
    out = 0.
    for i in reversed(l):
        out += i

    return out

@PerformanceComparison('Group1', l=range(10))
def iter_forward(l):
    out = 0.
    for i in l:
        out += i

    return out

with open('report.txt', 'w') as f:
    PerformanceComparison.summarize('Group1', f)