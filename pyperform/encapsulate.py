from functools import partial


class Halt(Exception):

    def __init__(self, *args):
        self.return_args = args


class Encapsulate(object):
    """
    Wraps object methods to create pre_ and post_ functions that are called before and after the function.
    Encapsulate automatically looks for pre_<function_name> and post_<function_name> definitions and works
    with overridden functions as well.

    Usage:

        def pre_myfunc():
            print 'Pre Main func'

        @Encapsulate
        def myfunc():
            print 'Main func'

        def post_myfunc():
            print 'Pre Main func'


     myfunc()

     >> 'Pre Main func'
     >> 'Main func'
     >> 'Post Main func'

    """
    encapsulations = {}
    halt = Halt

    def __init__(self, func):
        self._func = func
        self._wrapper = None
        self.overridden = False
        self.objclass = None

    @property
    def func_name(self):
        return self._func.func_name

    def __call__(self, instance, *args, **kwargs):
        if self.overridden:
            # This Encapsulation is overridden so this call is from a super(). Do not execute PRE and POST twice
            return self._func(instance, *args, **kwargs)

        pre_func = getattr(instance, 'pre_%s' % self._func.func_name, None)
        post_func = getattr(instance, 'post_%s' % self._func.func_name, None)

        try:

            if pre_func is not None:
                pre_func(*args, **kwargs)

            ret = self._func(instance, *args, **kwargs)

            if post_func is not None:
                post_ret = post_func(*args, **kwargs)

        except Halt as e:
            return e.return_args

        # return the post function value if it returns something other than None, otherwise return the
        # main functions value
        return post_ret or ret

    def __get__(self, obj, objtype):
        """Support instance methods."""
        if self._wrapper is None:
            self.objclass = obj.__class__
            if obj not in Encapsulate.encapsulations:
                Encapsulate.encapsulations[obj] = {self.func_name: []}

            Encapsulate.encapsulations[obj][self.func_name].append(self)

            # Go through Encapsulations on this objects function and determine which one
            # is overridden. We need to know this so that when the overridden function is called
            # the pre and post functions aren't called again.
            for enc in Encapsulate.encapsulations[obj][self.func_name]:
                # Determine the call order of the functions
                call_order = []
                for ii, cls in enumerate(objtype.__mro__):
                    func = cls.__dict__.get(self.func_name, None)
                    if isinstance(func, Encapsulate):
                        func = func._func

                    call_order.append(func)

                try:
                    idx = call_order.index(enc._func)
                except ValueError:
                    pass
                else:
                    if idx > 0 and any(call_order[:idx]):
                        enc.overridden = True

            self._wrapper = partial(self.__call__, obj)

        return self._wrapper

    def __repr__(self):
        return 'Encapsulation for %s' % self._func.func_name