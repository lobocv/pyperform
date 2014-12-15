pyperform
=========

An easy and convenient way to performance test blocks of python code.
Tired of writing separate scripts for your performance tests? Don't like coding in strings?
Using the pyperform decorators, you can easily implement timeit tests to your functions with just one line!

Features
--------
Features of pyperform include:

    - Quick, easy to implement in-code performance tests that run once when the function is defined
    - Speed comparison of several functions.
    - Validation of results between ComparisonBenchmarks
    - Summary reports.
    - Supports class functions as well as global functions.
    - Performance tests can easily be disabled/enabled globally.
    - Library of performance tests to learn from.


Example
-------
This example demonstrates how pyperform can be used to benchmark class functions. In this example we use
ComparisonBenchmarks to compare the speed of two methods which calculates a person's savings.

** Note that when benchmarking class methods, the `classname` argument to ComparisonBenchmark must be provided.

The class, Person, is initialized with several required parameters (`name`, `age`, `monthly_income`) and some optional
parameters (`height`). The two methods to calculate savings both have a required argument (`retirement_age`) and an optional
argument of monthly spending (`monthly_spending`).


    from pyperform import BenchmarkedClass, ComparisonBenchmark
    
    @BenchmarkedClass(cls_args=('Calvin', 24, 1000.,), cls_kwargs={'height': '165 cm'})
    class Person(object):
    
        def __init__(self, name, age, monthly_income, height=None, *args, **kwargs):
            self.name = name
            self.age = age
            self.height = height
            self.monthly_income = monthly_income
    
    
        @ComparisonBenchmark('Calculate Savings', classname="Person", timeit_number=100, validation=True, largs=(55,), kwargs={'monthly_spending': 500})
        def calculate_savings_method1(self, retirement_age, monthly_spending=0, *args, **kwargs):
            savings = 0
            for y in range(self.age, retirement_age):
                for m in range(12):
                    savings += self.monthly_income - monthly_spending
            return savings
    
        @ComparisonBenchmark('Calculate Savings', classname="Person", timeit_number=100, validation=True, largs=(55,), kwargs={'monthly_spending': 500})
        def calculate_savings_method2(self, retirement_age, monthly_spending=0, *args, **kwargs):
            yearly_income = 12 * (self.monthly_income - monthly_spending)
            n_years = retirement_age - self.age
            if n_years > 0:
                return yearly_income * n_years

You can print the summary to file or if ComparisonBenchmark.summarize() is not given an fs parameter, it will print to
console.

    report_file = open('report.txt', 'w')
    ComparisonBenchmark.summarize(group='Calculate Savings', fs=report_file)

This results in:


    List Arguments: 55
    Keyword Arguments: monthly_spending = 500
    
    
    Function Name                       Time         % of Fastest    timeit_repeat   timeit_number 
    ----------------------------------------------------------------------------------------------------
    Person.calculate_savings_method2    4.147 us     100.0           3               100           
    Person.calculate_savings_method1    66.281 us    6.3             3               100           
    ----------------------------------------------------------------------------------------------------
    
    
    Source Code:
    ----------------------------------------------------------------------------------------------------
    def calculate_savings_method2(self, retirement_age, monthly_spending=0, *args, **kwargs):
        yearly_income = 12 * (self.monthly_income - monthly_spending)
        n_years = retirement_age - self.age
        if n_years > 0:
            return yearly_income * n_years
    
    
    def calculate_savings_method1(self, retirement_age, monthly_spending=0, *args, **kwargs):
        savings = 0
        for y in range(self.age, retirement_age):
            for m in range(12):
                savings += self.monthly_income - monthly_spending
        return savings
    