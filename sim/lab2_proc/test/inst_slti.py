#=========================================================================
# slti
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 6
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rimm_dest_dep_test( 5, "slti", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 4, "slti", 2, 1, 0 ),
    gen_rimm_dest_dep_test( 3, "slti", 3, 1, 0 ),
    gen_rimm_dest_dep_test( 2, "slti", 4, 1, 0 ),
    gen_rimm_dest_dep_test( 1, "slti", 5, 1, 0 ),
    gen_rimm_dest_dep_test( 0, "slti", 6, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slti", 1, 1, 0 ),
    gen_rimm_src_dep_test( 4, "slti", 2, 1, 0 ),
    gen_rimm_src_dep_test( 3, "slti", 3, 1, 0 ),
    gen_rimm_src_dep_test( 2, "slti", 4, 1, 0 ),
    gen_rimm_src_dep_test( 1, "slti", 5, 1, 0 ),
    gen_rimm_src_dep_test( 0, "slti", 6, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dest_test
#-------------------------------------------------------------------------

def gen_src_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "slti", 28, 30, 1 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "slti", 0x00000000, 0x000, 0 ),
    gen_rimm_value_test( "slti", 0x00000000, 0x001, 1 ),
    gen_rimm_value_test( "slti", 0x00000003, 0x001, 0 ),

    gen_rimm_value_test( "slti", 0x7fffffff, 0x7ff, 0 ),
    gen_rimm_value_test( "slti", 0xffffffff, 0x7ff, 1 ),
    gen_rimm_value_test( "slti", 0x7fffffff, 0xfff, 0 ),
    gen_rimm_value_test( "slti", 0xffffffff, 0xfff, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32( random.randint(0,0xffffffff))
    src1 = b32( random.randint(-2048,2047))
    if src0.int() < src1.int():
      dest = 1
    else:
      dest = 0

    asm_code.append( gen_rimm_value_test( "slti", src0.int(), src1.int(), dest ) )
  return asm_code