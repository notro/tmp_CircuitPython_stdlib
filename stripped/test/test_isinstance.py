# Tests some corner cases with isinstance() and issubclass().  While these
# tests use new style classes and properties, they actually do whitebox
# testing of error conditions uncovered when using extension types.

import unittest



# normal classes
class Super:
    pass

class Child(Super):
    pass

# new-style classes
class NewSuper(object):
    pass

class NewChild(NewSuper):
    pass



class TestIsInstanceIsSubclass(unittest.TestCase):
    # Tests to ensure that isinstance and issubclass work on abstract
    # classes and instances.  Before the 2.2 release, TypeErrors were
    # raised when boolean values should have been returned.  The bug was
    # triggered by mixing 'normal' classes and instances were with
    # 'abstract' classes and instances.  This case tries to test all
    # combinations.

    def test_isinstance_normal(self):
        # normal instances
        self.assertEqual(True, isinstance(Super(), Super))
        self.assertEqual(False, isinstance(Super(), Child))

        self.assertEqual(True, isinstance(Child(), Super))

    def test_subclass_normal(self):
        # normal classes
        self.assertEqual(True, issubclass(Super, Super))
        self.assertEqual(False, issubclass(Super, Child))

        self.assertEqual(True, issubclass(Child, Child))
        self.assertEqual(True, issubclass(Child, Super))

    def test_subclass_tuple(self):
        # test with a tuple as the second argument classes
        self.assertEqual(True, issubclass(Child, (Child,)))
        self.assertEqual(True, issubclass(Child, (Super,)))
        self.assertEqual(False, issubclass(Super, (Child,)))
        self.assertEqual(True, issubclass(Super, (Child, Super)))
        self.assertEqual(False, issubclass(Child, ()))

        self.assertEqual(True, issubclass(NewChild, (NewChild,)))
        self.assertEqual(True, issubclass(NewChild, (NewSuper,)))
        self.assertEqual(False, issubclass(NewSuper, (NewChild,)))
        self.assertEqual(True, issubclass(NewSuper, (NewChild, NewSuper)))
        self.assertEqual(False, issubclass(NewChild, ()))

        self.assertEqual(True, issubclass(int, (int, (float, int))))
        self.assertEqual(True, issubclass(str, (str, (Child, NewChild, str))))

