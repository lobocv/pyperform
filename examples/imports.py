__author__ = 'calvin'


from pyperform import *


@ComparisonBenchmark('imports', timeit_repeat=10)
def import_top_level():
    import os
    import datetime
    import collections
    import json


@ComparisonBenchmark('imports', timeit_repeat=10)
def import_lower_level():
    from os import path
    from datetime import datetime
    from collections import deque
    from json import decoder




ComparisonBenchmark.summarize('imports')
