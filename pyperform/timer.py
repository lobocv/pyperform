__author__ = 'calvin'



def timer(func):
    def _timed_function(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(func.__name__, ':\t', convert_time_units(t2-t1))
        return result

    _timed_function.__name__ = "_timed_{}".format(func.__name__)
    return _timed_function
