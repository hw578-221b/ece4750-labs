#=========================================================================
# mul
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from lab2_proc.test.inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    csrr x2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mul x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 20
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "mul", 1, 1, 1 ),
    gen_rr_dest_dep_test( 4, "mul", 2, 1, 2 ),
    gen_rr_dest_dep_test( 3, "mul", 3, 1, 3 ),
    gen_rr_dest_dep_test( 2, "mul", 4, 1, 4 ),
    gen_rr_dest_dep_test( 1, "mul", 5, 1, 5 ),
    gen_rr_dest_dep_test( 0, "mul", 6, 1, 6 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "mul",  7, 1,  7 ),
    gen_rr_src0_dep_test( 4, "mul",  8, 1,  8 ),
    gen_rr_src0_dep_test( 3, "mul",  9, 1,  9 ),
    gen_rr_src0_dep_test( 2, "mul", 10, 1, 10 ),
    gen_rr_src0_dep_test( 1, "mul", 11, 1, 11 ),
    gen_rr_src0_dep_test( 0, "mul", 12, 1, 12 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "mul", 1, 13, 13 ),
    gen_rr_src1_dep_test( 4, "mul", 1, 14, 14 ),
    gen_rr_src1_dep_test( 3, "mul", 1, 15, 15 ),
    gen_rr_src1_dep_test( 2, "mul", 1, 16, 16 ),
    gen_rr_src1_dep_test( 1, "mul", 1, 17, 17 ),
    gen_rr_src1_dep_test( 0, "mul", 1, 18, 18 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "mul", 12, 2, 24 ),
    gen_rr_srcs_dep_test( 4, "mul", 13, 3, 39 ),
    gen_rr_srcs_dep_test( 3, "mul", 14, 4, 56 ),
    gen_rr_srcs_dep_test( 2, "mul", 15, 5, 75 ),
    gen_rr_srcs_dep_test( 1, "mul", 16, 6, 96 ),
    gen_rr_srcs_dep_test( 0, "mul", 17, 2, 34 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "mul", 25, 1, 25 ),
    gen_rr_src1_eq_dest_test( "mul", 26, 1, 26 ),
    gen_rr_src0_eq_src1_test( "mul", 4, 16 ),
    gen_rr_srcs_eq_dest_test( "mul", 5, 25 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

# helper function to convert signed integer to 32-bit hex string 
def hex32(x):
  return f"0x{format(x & 0xFFFFFFFF, '08x')}"

def gen_value_test():
  return [
    gen_rr_value_test( "mul", hex32(0), hex32(0), hex32(0)  ),
    gen_rr_value_test( "mul", hex32(1), hex32(1), hex32(1)  ),
    gen_rr_value_test( "mul", hex32(3), hex32(7), hex32(21) ),

    gen_rr_value_test( "mul", hex32(-1), hex32(7), hex32(-7) ),
    gen_rr_value_test( "mul", hex32(2), hex32(-7), hex32(-14) ),
    gen_rr_value_test( "mul", hex32(-7), hex32(-7), hex32(49) ),

    gen_rr_value_test( "mul", hex32(1234), hex32(454), hex32(560236) ),
    gen_rr_value_test( "mul", hex32(1234), hex32(-454), hex32(-560236) ),
    gen_rr_value_test( "mul", hex32(-1234), hex32(454), hex32(-560236) ),
    gen_rr_value_test( "mul", hex32(-1234), hex32(-454), hex32(560236) ),

    gen_rr_value_test( "mul", 0x00000000, 0x7FFFFFFF, 0x00000000 ),
    gen_rr_value_test( "mul", 0x7FFFFFFF, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "mul", 0x7FFFFFFF, 0x7FFFFFFF, 0x00000001 ),
    gen_rr_value_test( "mul", 0x10000000, 0x7FFFFFFF, 0xF0000000 ),
    gen_rr_value_test( "mul", 0x7FFFFFFF, 0x10000000, 0xF0000000 ),
    gen_rr_value_test( "mul", 0xFFFFFFFF, 0xFFFFFFFF, 0x00000001 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32( random.randint(0,0xffffffff) )
    src1 = b32( random.randint(0,0xffffffff) )
    dest = src0 * src1
    # dest.uint() converts the already wrapped result into an unsigned Python integer 
    # not standard python syntax, PyMLT syntax
    asm_code.append( gen_rr_value_test( "mul", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code
