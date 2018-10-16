import unittest

funcattrs_dict = {}                                                             ###
def funcattrs(**kwds):
    def decorate(func):
        funcattrs_dict.setdefault(func.__name__, {})                            ###
        funcattrs_dict[func.__name__].update(kwds)                              ###
        return func
    return decorate

MiscDecorators_dict = {}                                                        ###
class MiscDecorators (object):
    @staticmethod
    def author(name):
        def decorate(func):
            MiscDecorators_dict[func.__name__] = name                           ###
            return func
        return decorate

# -----------------------------------------------


# -----------------------------------------------

def countcalls(counts):
    "Decorator to count calls to a function"
    def decorate(func):
        func_name = func.__name__
        counts[func_name] = 0
        def call(*args, **kwds):
            counts[func_name] += 1
            return func(*args, **kwds)
        return call
    return decorate

# -----------------------------------------------

def memoize(func):
    saved = {}
    def call(*args):
        try:
            return saved[args]
        except KeyError:
            res = func(*args)
            saved[args] = res
            return res
        except TypeError:
            # Unhashable argument
            return func(*args)
    return call

# -----------------------------------------------

class TestDecorators(unittest.TestCase):

    def test_single(self):
        class C(object):
            @staticmethod
            def foo(): return 42
        self.assertEqual(C.foo(), 42)
        self.assertEqual(C().foo(), 42)

    def test_staticmethod_function(self):
        @staticmethod
        def notamethod(x):
            return x
        self.assertRaises(TypeError, notamethod, 1)

    def test_dotted(self):
        decorators = MiscDecorators()
        @decorators.author('Cleese')
        def foo(): return 42
        self.assertEqual(foo(), 42)
        self.assertEqual(MiscDecorators_dict['foo'], 'Cleese')                  ###

    def test_memoize(self):
        counts = {}

        @memoize
        @countcalls(counts)
        def double(x):
            return x * 2

        self.assertEqual(counts, dict(double=0))

        # Only the first call with a given argument bumps the call count:
        #
        self.assertEqual(double(2), 4)
        self.assertEqual(counts['double'], 1)
        self.assertEqual(double(2), 4)
        self.assertEqual(counts['double'], 1)
        self.assertEqual(double(3), 6)
        self.assertEqual(counts['double'], 2)

        # Unhashable arguments do not get memoized:
        #
        self.assertEqual(double([10]), [10, 10])
        self.assertEqual(counts['double'], 3)
        self.assertEqual(double([10]), [10, 10])
        self.assertEqual(counts['double'], 4)

    def test_double(self):
        class C(object):
            @funcattrs(abc=1, xyz="haha")
            @funcattrs(booh=42)
            def foo(self): return 42
        self.assertEqual(C().foo(), 42)
        self.assertEqual(funcattrs_dict['foo']['abc'], 1)                       ###
        self.assertEqual(funcattrs_dict['foo']['xyz'], "haha")                  ###
        self.assertEqual(funcattrs_dict['foo']['booh'], 42)                     ###

    def test_order(self):
        # Test that decorators are applied in the proper order to the function
        # they are decorating.
        def callnum(num):
            """Decorator factory that returns a decorator that replaces the
            passed-in function with one that returns the value of 'num'"""
            def deco(func):
                return lambda: num
            return deco
        @callnum(2)
        @callnum(1)
        def foo(): return 42
        self.assertEqual(foo(), 2,
                            "Application order of decorators is incorrect")

    def test_eval_order(self):
        # Evaluating a decorated function involves four steps for each
        # decorator-maker (the function that returns a decorator):
        #
        #    1: Evaluate the decorator-maker name
        #    2: Evaluate the decorator-maker arguments (if any)
        #    3: Call the decorator-maker to make a decorator
        #    4: Call the decorator
        #
        # When there are multiple decorators, these steps should be
        # performed in the above order for each decorator, but we should
        # iterate through the decorators in the reverse of the order they
        # appear in the source.

        actions = []

        def make_decorator(tag):
            actions.append('makedec' + tag)
            def decorate(func):
                actions.append('calldec' + tag)
                return func
            return decorate

        class NameLookupTracer (object):
            def __init__(self, index):
                self.index = index

            def __getattr__(self, fname):
                if fname == 'make_decorator':
                    opname, res = ('evalname', make_decorator)
                elif fname == 'arg':
                    opname, res = ('evalargs', str(self.index))
                else:
                    assert False, "Unknown attrname %s" % fname
                actions.append('%s%d' % (opname, self.index))
                return res

        c1, c2, c3 = map(NameLookupTracer, [ 1, 2, 3 ])

        expected_actions = [ 'evalname1', 'evalargs1', 'makedec1',
                             'evalname2', 'evalargs2', 'makedec2',
                             'evalname3', 'evalargs3', 'makedec3',
                             'calldec3', 'calldec2', 'calldec1' ]

        actions = []
        @c1.make_decorator(c1.arg)
        @c2.make_decorator(c2.arg)
        @c3.make_decorator(c3.arg)
        def foo(): return 42
        self.assertEqual(foo(), 42)

        self.assertEqual(actions, expected_actions)

        # Test the equivalence claim in chapter 7 of the reference manual.
        #
        actions = []
        def bar(): return 42
        bar = c1.make_decorator(c1.arg)(c2.make_decorator(c2.arg)(c3.make_decorator(c3.arg)(bar)))
        self.assertEqual(bar(), 42)
        self.assertEqual(actions, expected_actions)

class TestClassDecorators(unittest.TestCase):

    def test_simple(self):
        def plain(x):
            x.extra = 'Hello'
            return x
        @plain
        class C(object): pass
        self.assertEqual(C.extra, 'Hello')

    def test_double(self):
        def ten(x):
            x.extra = 10
            return x
        def add_five(x):
            x.extra += 5
            return x

        @add_five
        @ten
        class C(object): pass
        self.assertEqual(C.extra, 15)

    def test_order(self):
        def applied_first(x):
            x.extra = 'first'
            return x
        def applied_second(x):
            x.extra = 'second'
            return x
        @applied_second
        @applied_first
        class C(object): pass
        self.assertEqual(C.extra, 'second')

