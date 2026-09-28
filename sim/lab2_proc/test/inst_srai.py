#=========================================================================
# srai
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
    csrr x1, mngr2proc < 0x00008000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srai x3, x1, 0x03
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00001000
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
    gen_rimm_dest_dep_test( 5, "srai", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 4, "srai", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 3, "srai", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 2, "srai", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 1, "srai", 1, 1, 0 ),
    gen_rimm_dest_dep_test( 0, "srai", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srai", 1, 1, 0 ),
    gen_rimm_src_dep_test( 4, "srai", 1, 1, 0 ),
    gen_rimm_src_dep_test( 3, "srai", 1, 1, 0 ),
    gen_rimm_src_dep_test( 2, "srai", 1, 1, 0 ),
    gen_rimm_src_dep_test( 1, "srai", 1, 1, 0 ),
    gen_rimm_src_dep_test( 0, "srai", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dest_test
#-------------------------------------------------------------------------

def gen_src_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "srai", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "srai", 0x00000001, 0, 0x00000001 ),
    gen_rimm_value_test( "srai", 0x00000000, 1, 0x00000000 ),
    gen_rimm_value_test( "srai", 0x00000001, 1, 0x00000000 ),

    gen_rimm_value_test( "srai", 0xffffffff, 1,   0xffffffff ),
    gen_rimm_value_test( "srai", 0x00000001, 0b11111, 0x00000000 ),
    gen_rimm_value_test( "srai", 0xffffffff, 0b11111, 0xffffffff ),

    gen_rimm_value_test( "srai", 16, 2, 4 ),
    gen_rimm_value_test( "srai", 17, 2, 4 ),
    gen_rimm_value_test( "srai", 19, 2, 4 ),
    gen_rimm_value_test( "srai", 20, 2, 5 ),

    gen_rimm_value_test( "srai", -16, 2, -4 ),
    gen_rimm_value_test( "srai", -17, 2, -5 ),
    gen_rimm_value_test( "srai", -19, 2, -5 ),
    gen_rimm_value_test( "srai", -20, 2, -5 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32( random.randint(0,0xffffffff) )
    src1 = b32( random.randint(0,31) )
    dest = b32( src0.int() >> src1.uint() )
    asm_code.append( gen_rimm_value_test( "srai", src0.int(), src1.uint(), dest.int() ) )
  return asm_code