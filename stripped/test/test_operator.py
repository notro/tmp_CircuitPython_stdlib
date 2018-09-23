import unittest

from test import support

import operator as py_operator                                                  ###



class OperatorTestCase:
    def test_add(self):
        operator = self.module
        self.assertRaises(TypeError, operator.add)
        self.assertRaises(TypeError, operator.add, None, None)
        self.assertTrue(operator.add(3, 4) == 7)

    def test_mul(self):
        operator = self.module
        self.assertRaises(TypeError, operator.mul)
        self.assertRaises(TypeError, operator.mul, None, None)
        self.assertTrue(operator.mul(5, 2) == 10)

    def test_neg(self):
        operator = self.module
        self.assertRaises(TypeError, operator.neg)
        self.assertRaises(TypeError, operator.neg, None)
        self.assertEqual(operator.neg(5), -5)
        self.assertEqual(operator.neg(-5), 5)
        self.assertEqual(operator.neg(0), 0)
        self.assertEqual(operator.neg(-0), 0)

    def test_pow(self):
        operator = self.module
        self.assertRaises(TypeError, operator.pow)
        self.assertRaises(TypeError, operator.pow, None, None)
        self.assertEqual(operator.pow(3,5), 3**5)
        self.assertRaises(TypeError, operator.pow, 1)
        self.assertRaises(TypeError, operator.pow, 1, 2, 3)


    def test_attrgetter(self):
        operator = self.module
        class A:
            pass
        a = A()
        a.name = 'arthur'
        f = operator.attrgetter('name')
        self.assertEqual(f(a), 'arthur')
        f = operator.attrgetter('rank')
        self.assertRaises(AttributeError, f, a)
        self.assertRaises(TypeError, operator.attrgetter, 2)
        self.assertRaises(TypeError, operator.attrgetter)

        # multiple gets
        record = A()
        record.x = 'X'
        record.y = 'Y'
        record.z = 'Z'
        self.assertEqual(operator.attrgetter('x','z','y')(record), ('X', 'Z', 'Y'))
        self.assertRaises(TypeError, operator.attrgetter, ('x', (), 'y'))

        class C(object):
            def __getattr__(self, name):
                raise SyntaxError
        self.assertRaises(SyntaxError, operator.attrgetter('foo'), C())

        # recursive gets
        a = A()
        a.name = 'arthur'
        a.child = A()
        a.child.name = 'thomas'
        f = operator.attrgetter('child.name')
        self.assertEqual(f(a), 'thomas')
        self.assertRaises(AttributeError, f, a.child)
        f = operator.attrgetter('name', 'child.name')
        self.assertEqual(f(a), ('arthur', 'thomas'))
        f = operator.attrgetter('name', 'child.name', 'child.child.name')
        self.assertRaises(AttributeError, f, a)
        f = operator.attrgetter('child.')
        self.assertRaises(AttributeError, f, a)
        f = operator.attrgetter('.child')
        self.assertRaises(AttributeError, f, a)

        a.child.child = A()
        a.child.child.name = 'johnson'
        f = operator.attrgetter('child.child.name')
        self.assertEqual(f(a), 'johnson')
        f = operator.attrgetter('name', 'child.name', 'child.child.name')
        self.assertEqual(f(a), ('arthur', 'thomas', 'johnson'))


class PyOperatorTestCase(OperatorTestCase, unittest.TestCase):
    module = py_operator

