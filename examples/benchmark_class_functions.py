__author__ = 'Calvin'
"""
This example demonstrates how pyperform can be used to benchmark class functions. In this example we use
ComparisonBenchmarks to compare the speed of two methods which calculates a person's savings.

** Note that when benchmarking class methods, the classname argument to ComparisonBenchmark must be provided.

The class, Person, is initialized with several required parameters (name, age, monthly_income) and some optional
parameters (height). The two methods to calculate savings both have a required argument (retirement_age) and an optional
argument of monthly spending (monthly_spending).

"""

from pyperform import BenchmarkedClass, ComparisonBenchmark, BenchmarkedFunction

@BenchmarkedClass(largs=('Calvin', 24, 1000.,), kwargs={'height': '165 cm'})
class Person(object):

    def __init__(self, name, age, monthly_income, height=None, *args, **kwargs):
        self.name = name
        self.age = age
        self.height = height
        self.monthly_income = monthly_income

    @ComparisonBenchmark('Calculate Savings', classname="Person", timeit_number=100, validation=True, largs=(55,),
                         kwargs={'monthly_spending': 500})
    def calculate_savings_method1(self, retirement_age, monthly_spending=0):
        savings = 0
        for y in range(self.age, retirement_age):
            for m in range(12):
                savings += self.monthly_income - monthly_spending
        return savings

    @ComparisonBenchmark('Calculate Savings', classname="Person", timeit_number=100, validation=True, largs=(55,),
                         kwargs={'monthly_spending': 500})
    def calculate_savings_method2(self, retirement_age, monthly_spending=0):
        yearly_income = 12 * (self.monthly_income - monthly_spending)
        n_years = retirement_age - self.age
        if n_years > 0:
            return yearly_income * n_years

    @BenchmarkedFunction(classname="Person", timeit_number=100, largs=(55,), kwargs={'monthly_spending': 500})
    def same_as_method_2(self, retirement_age, monthly_spending=0):
        yearly_income = 12 * (self.monthly_income - monthly_spending)
        n_years = retirement_age - self.age
        if n_years > 0:
            return yearly_income * n_years


# Can print the summary to file or if ComparisonBenchmark.summarize() is not given an fs parameter, it will print to
# console.
report_file = open('report.txt', 'w')
ComparisonBenchmark.summarize(group='Calculate Savings', fs=report_file)