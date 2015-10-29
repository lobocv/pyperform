__author__ = 'clobo'

from collections import namedtuple  #!
from pyperform import ComparisonBenchmark

MyNamedTuple = namedtuple('ButtonStatus', ('name', 'age', 'gender'))  #!


class MyClass(object):  #!
    __slots__ = ('name', 'age', 'gender')

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                     Creation Speed Tests
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


@ComparisonBenchmark('class')
def create_class():
    for i in xrange(1000):
        c = MyClass('calvin', 25, 'male')


@ComparisonBenchmark('class')
def create_namedtuple():
    for i in xrange(1000):
        c = MyNamedTuple('calvin', 25, 'male')


@ComparisonBenchmark('class')
def create_dict():
    for i in xrange(1000):
        c = {'name': 'calvin', 'age': 25, 'gender': 'male'}


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    Lookup Speed Tests
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


@ComparisonBenchmark('lookup')
def class_attr_lookup():
    c = MyClass('calvin', 25, 'male')
    for i in xrange(10000):
        name, age, gender = c.name, c.age, c.gender


@ComparisonBenchmark('lookup')
def namedtuple_attr_lookup():
    c = MyNamedTuple('calvin', 25, 'male')
    for i in xrange(10000):
        name, age, gender = c.name, c.age, c.gender


@ComparisonBenchmark('lookup')
def dict_attr_lookup():
    c = {'name': 'calvin', 'age': 25, 'gender': 'male'}
    for i in xrange(10000):
        name, age, gender = c['name'], c['age'], c['gender']


ComparisonBenchmark.summarize('class')
ComparisonBenchmark.summarize('lookup')
