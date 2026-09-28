#=========================================================================
# slli
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
    csrr x1, mngr2proc < 0x80008000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 0x03
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
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
    gen_rimm_dest_dep_test( 5, "slli", 1, 1, 2 ),
    gen_rimm_dest_dep_test( 4, "slli", 1, 1, 2 ),
    gen_rimm_dest_dep_test( 3, "slli", 1, 1, 2 ),
    gen_rimm_dest_dep_test( 2, "slli", 1, 1, 2 ),
    gen_rimm_dest_dep_test( 1, "slli", 1, 1, 2 ),
    gen_rimm_dest_dep_test( 0, "slli", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slli", 1, 1, 2 ),
    gen_rimm_src_dep_test( 4, "slli", 1, 1, 2 ),
    gen_rimm_src_dep_test( 3, "slli", 1, 1, 2 ),
    gen_rimm_src_dep_test( 2, "slli", 1, 1, 2 ),
    gen_rimm_src_dep_test( 1, "slli", 1, 1, 2 ),
    gen_rimm_src_dep_test( 0, "slli", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dest_test
#-------------------------------------------------------------------------

def gen_src_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "slli", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rimm_value_test( "slli", 0x00000001, 0, 0x00000001 ),
    gen_rimm_value_test( "slli", 0x00000000, 1, 0x00000000 ),
    gen_rimm_value_test( "slli", 0x00000001, 1, 0x00000002 ),

    gen_rimm_value_test( "slli", 0xffffffff, 0, 0xffffffff ),
    gen_rimm_value_test( "slli", 0xffffffff, 0b11111, 0x80000000 ),
    gen_rimm_value_test( "slli", 0x00000000, 0b11111, 0x00000000 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32( random.randint(0,0xffffffff) )
    src1 = b32( random.randint(0,31) )
    # PyMTL unsigned shift
    dest = src0 << src1
    asm_code.append( gen_rimm_value_test( "slli", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code
