# Some extra sys stuff that is only used for testing
from sys import *
import collections


_int_info_class = collections.namedtuple('sys.int_info', ['bits_per_digit', 'sizeof_digit'])

# MICROPY_LONGINT_IMPL_MPZ
int_info = _int_info_class(
                           bits_per_digit = 16, # MPZ_DIG_SIZE, don't know if they are the same though
                           sizeof_digit = 0  # Don't know
                          )


_float_info_class = collections.namedtuple('sys.float_info', ['max', 'max_exp', 'max_10_exp', 'min', 'min_exp', 'min_10_exp', 'dig', 'mant_dig', 'epsilon', 'radix', 'rounds'])

# MICROPY_PY_BUILTINS_FLOAT
# MICROPY_FLOAT_IMPL == MICROPY_FLOAT_IMPL_FLOAT
# MICROPY_OBJ_REPR == MICROPY_OBJ_REPR_C

#define MP_FLOAT_EXP_BITS (8)
#define MP_FLOAT_FRAC_BITS (23)

#define MP_FLOAT_EXP_BIAS ((1 << (MP_FLOAT_EXP_BITS - 1)) - 1)

#define DEC_VAL_MAX 1e20F
#define SMALL_NORMAL_VAL (1e-37F)
#define SMALL_NORMAL_EXP (-37)

#const int precision = 6;

# This is more or less guess work. I really don't understand floats...
float_info = _float_info_class(max = 3.402823e38,
                               max_exp = 128,
                               max_10_exp = 38,
                               min = 1e-37,
                               min_exp = -128,
                               min_10_exp= -36,
                               dig = 6,
                               mant_dig = 23,
                               epsilon = 0,  # Don't know
                               radix = 2,
                               rounds = 0  # Don't know
                              )
