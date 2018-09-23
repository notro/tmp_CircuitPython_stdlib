"""
Define names for built-in types that aren't directly accessible as a builtin.
"""
import sys

# Iterators in Python aren't a matter of type but of protocol.  A large
# and changing number of builtin types implement *some* flavor of
# iterator.  Don't check the type!  Use hasattr to check for both
# "__iter__" and "__next__" attributes instead.

def _f(): pass
FunctionType = type(_f)
LambdaType = type(lambda: None)         # Same as FunctionType

def _g():
    yield 1
GeneratorType = type(_g())

class _C:
    def _m(self): pass
MethodType = type(_C()._m)

BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)     # Same as BuiltinFunctionType

ModuleType = type(sys)


del sys, _f, _g, _C,                              # Not for export



__all__ = [n for n in globals() if n[:1] != '_']
