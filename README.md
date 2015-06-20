PyPerform
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
    - Community-driven library of performance tests to learn from.

Installation
------------
To install:
    
    pip install pyperform
    

Compatibility
-------------
PyPerform was developed in Python 2.7 but has been tested with Python 3.4. Please report any compatibility issues or
send pull requests with your changes!

Usage
-----

To use pyperform to benchmark functions, you need to add one of the following decorators:

```python

@BenchmarkedFunction(setup=None,
                     classname=None,
                     largs=None,
                     kwargs=None,
                     timeit_repeat=3,
                     timeit_number=1000)

@BenchmarkedClass(setup=None,
                  largs=None,
                  kwargs=None,
                  timeit_repeat=3,
                  timeit_number=1000)

@ComparisonBenchmark(group,
                     classname=None,
                     setup=None,
                     largs=None,
                     kwargs=None,
                     validation=False,
                     timeit_repeat=3,
                     timeit_number=1000)

```

where largs is a list of arguments to pass to the function and kwargs is a dictionary of keyword arguments to pass to the 
function. The setup argument is described in the following section. All decorators have timeit_repeat and timeit_number
arguments which are can be used to set the number of trials and repetitions to use with timeit. The ComparisonBenchmark
has a validation flag, which when set to True, will attempt to compare the results of the functions in the group.

Imports and Setup Code
----------------------
Sometimes your decorated function will require some setup code or imported modules. You can easily include any lines of 
code by by appending the tag `#!` to the end of the line. For functions and classes, you only need to tag the `def` or
`class` line and PyPerform will include the entire function/class definition as setup code.


For example:

```python

    from pyperform import BenchmarkedFunction
    
    import math #!
    a = 10  #!
    
    
    def do_calcuation(a, b): #!
        return a * b
    
    
    @BenchmarkedFunction(largs=(5,))
    def call_function(b):
        # We can reference the `a` variable because it is tagged
        result = a * b
        assert result == 50
        # We can call the math module because it is tagged.
        math.log10(100)
        # We can call this function because it is tagged.
        calc_result = do_calcuation(a, b)
        return calc_result

```

Results in:

    call_function 	 6.214 us
    
Alternative, you can set the tag for pyperform to search for by calling `set_import_tag(tag)` with a string argument.
    
The setup argument (Optional)
-----------------------------
All decorators have a setup argument which can be either a function with no arguments, or string of code. If given a
function, the body of the function is executed in the global scope. This means that objects and variables instantiated 
in the body of the function are accessible from within the benchmarked function.
  
Example:

```python

from pyperform import BenchmarkedFunction

def _setup():
    a = 10

@BenchmarkedFunction(setup=_setup, largs=(5,))
def multiply_by_a(b):
    result = a * b
    assert result == 50
    return result

```

Results in:
    
    multiply_by_a 	 3.445 us


Class-method Benchmarking
-------------------------
Pyperform will also work on class methods, but in order to do so, we must instantiate an instance of the class.
This is done in `BenchmarkedClass`. Then once we have decorated the class with `BenchmarkedClass`, we can use
`ComparisonBenchmark` or `BenchmarkedFunction` to performance test the class's methods.

<b>Note that when benchmarking class methods, the `classname` argument to ComparisonBenchmark must be provided.
This argument will hopefully be removed in the future.</b>

In the BenchmarkedClass we instantiate a Person object and then run three benchmarked class-methods.
Two of the class-methods are `ComparisonBenchmarks` and will be compared with one another. To see the result, you must
call the `ComparisonBenchmark.summarize()` function. The third function is a duplicate of calculate_savings_method2 but
it is a BenchmarkedFunction instead. The result of BenchmarkedFunctions is printed when the script is run.

```python

from pyperform import BenchmarkedClass, ComparisonBenchmark, BenchmarkedFunction

@BenchmarkedClass(largs=('Calvin', 24, 1000.,), kwargs={'height': '165 cm'})
class Person(object):

    def __init__(self, name, age, monthly_income, height=None, *args, **kwargs):
        self.name = name
        self.age = age
        self.height = height
        self.monthly_income = monthly_income


    @ComparisonBenchmark('Calculate Savings', classname="Person", timeit_number=100,
                         validation=True, largs=(55,), kwargs={'monthly_spending': 500})
    def calculate_savings_method1(self, retirement_age, monthly_spending=0):
        savings = 0
        for y in range(self.age, retirement_age):
            for m in range(12):
                savings += self.monthly_income - monthly_spending
        return savings

    @ComparisonBenchmark('Calculate Savings', classname="Person", timeit_number=100,
                         validation=True, largs=(55,), kwargs={'monthly_spending': 500})
    def calculate_savings_method2(self, retirement_age, monthly_spending=0):
        yearly_income = 12 * (self.monthly_income - monthly_spending)
        n_years = retirement_age - self.age
        if n_years > 0:
            return yearly_income * n_years

    @BenchmarkedFunction(classname="Person", timeit_number=100,
                         largs=(55,), kwargs={'monthly_spending': 500})
    def same_as_method_2(self, retirement_age, monthly_spending=0):
        yearly_income = 12 * (self.monthly_income - monthly_spending)
        n_years = retirement_age - self.age
        if n_years > 0:
            return yearly_income * n_years

```

You can print the summary to file or if ComparisonBenchmark.summarize() is not given an fs parameter, it will print to
console.

```python

report_file = open('report.txt', 'w')
ComparisonBenchmark.summarize(group='Calculate Savings', fs=report_file)

```

This results in a file `report.txt` that contains the ComparisonBenchmark's results:
    
    Call statement:
    
        instance.calculate_savings_method2(55, monthly_spending=500)
    
    
    Rank     Function Name                       Time         % of Fastest    timeit_repeat   timeit_number 
    ------------------------------------------------------------------------------------------------------------------------
    
    1        Person.calculate_savings_method2    267.093 ns   100.0           3               100           
    2        Person.calculate_savings_method1    35.623 us    0.7             3               100           
    ------------------------------------------------------------------------------------------------------------------------
    
    
    
    Source Code:
    ------------------------------------------------------------------------------------------------------------------------
    
    
    def calculate_savings_method2(self, retirement_age, monthly_spending=0):
        yearly_income = 12 * (self.monthly_income - monthly_spending)
        n_years = retirement_age - self.age
        if n_years > 0:
            return yearly_income * n_years
    ------------------------------------------------------------------------------------------------------------------------
    
    
    def calculate_savings_method1(self, retirement_age, monthly_spending=0):
        savings = 0
        for y in range(self.age, retirement_age):
            for m in range(12):
                savings += self.monthly_income - monthly_spending
        return savings
    ------------------------------------------------------------------------------------------------------------------------

and printed to the screen, the results of the BenchmarkedFunction
    
    same_as_method_2 	 262.827 ns
    
Validation
----------
ComparisonBenchmark has a optional argument `validate`. When `validate=True`, the return value of each 
ComparisonBenchmark in a group is compared. If the results of the function are the not same, a ValidationError is raised.
 
Example:

```python

from pyperform import ComparisonBenchmark
from math import sin  #!


@ComparisonBenchmark('Group1', validation=True, largs=(100,))
def list_append(n, *args, **kwargs):
    l = []
    for i in xrange(1, n):
        l.append(sin(i))
    return l


@ComparisonBenchmark('Group1', validation=True, largs=(100,))
def list_comprehension(n, *args, **kwargs):
    return 1

```

Output:

    pyperform.ValidationError: Results of functions list_append and list_comprehension are not equivalent.
    list_append:	 [0.8414709848078965, 0.9092974268256817, 0.1411200080598672, -0.7568024953079282, -0.9589242746631385, -0.27941549819892586, 0.6569865987187891, 0.9893582466233818, 0.4121184852417566, -0.5440211108893698, -0.9999902065507035, -0.5365729180004349, 0.4201670368266409, 0.9906073556948704, 0.6502878401571168, -0.2879033166650653, -0.9613974918795568, -0.750987246771676, 0.14987720966295234, 0.9129452507276277, 0.8366556385360561, -0.008851309290403876, -0.8462204041751706, -0.9055783620066239, -0.13235175009777303, 0.7625584504796027, 0.956375928404503, 0.27090578830786904, -0.6636338842129675, -0.9880316240928618, -0.404037645323065, 0.5514266812416906, 0.9999118601072672, 0.5290826861200238, -0.428182669496151, -0.9917788534431158, -0.6435381333569995, 0.2963685787093853, 0.9637953862840878, 0.7451131604793488, -0.158622668804709, -0.9165215479156338, -0.8317747426285983, 0.017701925105413577, 0.8509035245341184, 0.9017883476488092, 0.123573122745224, -0.7682546613236668, -0.9537526527594719, -0.26237485370392877, 0.6702291758433747, 0.9866275920404853, 0.39592515018183416, -0.5587890488516163, -0.9997551733586199, -0.5215510020869119, 0.43616475524782494, 0.9928726480845371, 0.6367380071391379, -0.3048106211022167, -0.9661177700083929, -0.7391806966492228, 0.16735570030280691, 0.9200260381967906, 0.8268286794901034, -0.026551154023966794, -0.8555199789753223, -0.8979276806892913, -0.11478481378318722, 0.7738906815578891, 0.9510546532543747, 0.25382336276203626, -0.6767719568873076, -0.9851462604682474, -0.38778163540943045, 0.5661076368981803, 0.9995201585807313, 0.5139784559875352, -0.4441126687075084, -0.9938886539233752, -0.6298879942744539, 0.31322878243308516, 0.9683644611001854, 0.7331903200732922, -0.1760756199485871, -0.9234584470040598, -0.8218178366308225, 0.03539830273366068, 0.8600694058124533, 0.8939966636005579, 0.10598751175115685, -0.7794660696158047, -0.9482821412699473, -0.24525198546765434, 0.683261714736121, 0.9835877454343449, 0.3796077390275217, -0.5733818719904229, -0.9992068341863537]
    list_comprehension:	1
