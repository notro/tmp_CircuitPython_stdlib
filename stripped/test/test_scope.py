import unittest



class ScopeTests(unittest.TestCase):

    def testSimpleNesting(self):

        def make_adder(x):
            def adder(y):
                return x + y
            return adder

        inc = make_adder(1)
        plus10 = make_adder(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testExtraNesting(self):

        def make_adder2(x):
            def extra(): # check freevars passing through non-use scopes
                def adder(y):
                    return x + y
                return adder
            return extra()

        inc = make_adder2(1)
        plus10 = make_adder2(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testSimpleAndRebinding(self):

        def make_adder3(x):
            def adder(y):
                return x + y
            x = x + 1 # check tracking of assignment to x in defining scope
            return adder

        inc = make_adder3(0)
        plus10 = make_adder3(9)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testNestingGlobalNoFree(self):

        def make_adder4(): # XXX add exta level of indirection
            def nest():
                def nest():
                    def adder(y):
                        return global_x + y # check that plain old globals work
                    return adder
                return nest()
            return nest()

        global_x = 1
        adder = make_adder4()
        self.assertEqual(adder(1), 2)

        global_x = 10
        self.assertEqual(adder(-2), 8)

    def testNestingThroughClass(self):

        def make_adder5(x):
            class Adder:
                def __call__(self, y):
                    return x + y
            return Adder()

        inc = make_adder5(1)
        plus10 = make_adder5(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    def testNestingPlusFreeRefToGlobal(self):

        def make_adder6(x):
            global global_nest_x
            def adder(y):
                return global_nest_x + y
            global_nest_x = x
            return adder

        inc = make_adder6(1)
        plus10 = make_adder6(10)

        self.assertEqual(inc(1), 11) # there's only one global
        self.assertEqual(plus10(-2), 8)

    def testNearestEnclosingScope(self):

        def f(x):
            def g(y):
                x = 42 # check that this masks binding in f()
                def h(z):
                    return x + z
                return h
            return g(2)

        test_func = f(10)
        self.assertEqual(test_func(5), 47)

    def testMixedFreevarsAndCellvars(self):

        def identity(x):
            return x

        def f(x, y, z):
            def g(a, b, c):
                a = a + x # 3
                def h():
                    # z * (4 + 9)
                    # 3 * 13
                    return identity(z * (b + y))
                y = c + z # 9
                return h
            return g

        g = f(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 39)

    def testCellIsKwonlyArg(self):
        # Issue 1409: Initialisation of a cell value,
        # when it comes from a keyword-only parameter
        def foo(*, a=17):
            def bar():
                return a + 5
            return bar() + 3

        self.assertEqual(foo(a=42), 50)
        self.assertEqual(foo(), 25)

    def testRecursion(self):

        def f(x):
            def fact(n):
                if n == 0:
                    return 1
                else:
                    return n * fact(n - 1)
            if x >= 0:
                return fact(x)
            else:
                raise ValueError("x must be >= 0")

        self.assertEqual(f(6), 720)


    def testLambdas(self):

        f1 = lambda x: lambda y: x + y
        inc = f1(1)
        plus10 = f1(10)
        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(5), 15)

        f2 = lambda x: (lambda : lambda y: x + y)()
        inc = f2(1)
        plus10 = f2(10)
        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(5), 15)

        f3 = lambda x: lambda y: global_x + y
        global_x = 1
        inc = f3(None)
        self.assertEqual(inc(2), 3)

        f8 = lambda x, y, z: lambda a, b, c: lambda : z * (b + y)
        g = f8(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 18)

    def testComplexDefinitions(self):

        def makeReturner(*lst):
            def returner():
                return lst
            return returner

        self.assertEqual(makeReturner(1,2,3)(), (1,2,3))

        def makeReturner2(**kwargs):
            def returner():
                return kwargs
            return returner

        self.assertEqual(makeReturner2(a=11)()['a'], 11)

    def testLocalsClass(self):
        # This test verifies that calling locals() does not pollute
        # the local namespace of the class with free variables.  Old
        # versions of Python had a bug, where a free variable being
        # passed through a class namespace would be inserted into
        # locals() by locals() or exec or a trace function.
        #
        # The real bug lies in frame code that copies variables
        # between fast locals and the locals dict, e.g. when executing
        # a trace function.

        def f(x):
            class C:
                x = 12
                def m(self):
                    return x
                locals()
            return C

        self.assertEqual(f(1).x, 12)

        def f(x):
            class C:
                y = x
                def m(self):
                    return x
                z = list(locals())
            return C

        varnames = f(1).z
        self.assertNotIn("x", varnames)
        self.assertIn("y", varnames)

    def testBoundAndFree(self):
        # var is bound and free in class

        def f(x):
            class C:
                def m(self):
                    return x
                a = x
            return C

        inst = f(3)()
        self.assertEqual(inst.a, inst.m())

    def testListCompLocalVars(self):

        try:
            print(bad)
        except NameError:
            pass
        else:
            print("bad should not be defined")

        def x():
            [bad for s in 'a b' for bad in s.split()]

        x()
        try:
            print(bad)
        except NameError:
            pass

    def testFreeingCell(self):
        # Test what happens when a finalizer accesses
        # the cell where the object was stored.
        class Special:
            def __del__(self):
                nestedcell_get()

    def testNonLocalFunction(self):

        def f(x):
            def inc():
                nonlocal x
                x += 1
                return x
            def dec():
                nonlocal x
                x -= 1
                return x
            return inc, dec

        inc, dec = f(0)
        self.assertEqual(inc(), 1)
        self.assertEqual(inc(), 2)
        self.assertEqual(dec(), 1)
        self.assertEqual(dec(), 0)

    def testNonLocalMethod(self):
        def f(x):
            class c:
                def inc(self):
                    nonlocal x
                    x += 1
                    return x
                def dec(self):
                    nonlocal x
                    x -= 1
                    return x
            return c()
        c = f(0)
        self.assertEqual(c.inc(), 1)
        self.assertEqual(c.inc(), 2)
        self.assertEqual(c.dec(), 1)
        self.assertEqual(c.dec(), 0)

    def testGlobalInParallelNestedFunctions(self):
        # A symbol table bug leaked the global statement from one
        # function to other nested functions in the same block.
        # This test verifies that a global statement in the first
        # function does not affect the second function.
        local_ns = {}
        global_ns = {}
        exec("""if 1:
            def f():
                y = 1
                def g():
                    global y
                    return y
                def h():
                    return y + 1
                return g, h
            y = 9
            g, h = f()
            result9 = g()
            result2 = h()
            """, local_ns, global_ns)
        self.assertEqual(2, global_ns["result2"])
        self.assertEqual(9, global_ns["result9"])

    def testNonLocalClass(self):

        def f(x):
            class c:
                nonlocal x
                x += 1
                def get(self):
                    return x
            return c()

        c = f(0)
        self.assertEqual(c.get(), 1)


    def testNonLocalGenerator(self):

        def f(x):
            def g(y):
                nonlocal x
                for i in range(y):
                    x += 1
                    yield x
            return g

        g = f(0)
        self.assertEqual(list(g(5)), [1, 2, 3, 4, 5])

    def testNestedNonLocal(self):

        def f(x):
            def g():
                nonlocal x
                x -= 2
                def h():
                    nonlocal x
                    x += 4
                    return x
                return h
            return g

        g = f(1)
        h = g()
        self.assertEqual(h(), 3)

    def testTopIsNotSignificant(self):
        # See #9997.
        def top(a):
            pass
        def b():
            global a

