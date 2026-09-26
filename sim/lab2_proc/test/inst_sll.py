#=========================================================================
# sll
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
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sll x3, x1, x2
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
    gen_rr_dest_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 4, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 3, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 2, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 1, "sll", 1, 1, 2 ),
    gen_rr_dest_dep_test( 0, "sll", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_src0_dep_test( 4, "sll", 1, 1, 2 ),
    gen_rr_src0_dep_test( 3, "sll", 1, 1, 2 ),
    gen_rr_src0_dep_test( 2, "sll", 1, 1, 2 ),
    gen_rr_src0_dep_test( 1, "sll", 1, 1, 2 ),
    gen_rr_src0_dep_test( 0, "sll", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_src1_dep_test( 4, "sll", 1, 1, 2 ),
    gen_rr_src1_dep_test( 3, "sll", 1, 1, 2 ),
    gen_rr_src1_dep_test( 2, "sll", 1, 1, 2 ),
    gen_rr_src1_dep_test( 1, "sll", 1, 1, 2 ),
    gen_rr_src1_dep_test( 0, "sll", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sll", 1, 1, 2 ),
    gen_rr_srcs_dep_test( 4, "sll", 1, 1, 2 ),
    gen_rr_srcs_dep_test( 3, "sll", 1, 1, 2 ),
    gen_rr_srcs_dep_test( 2, "sll", 1, 1, 2 ),
    gen_rr_srcs_dep_test( 1, "sll", 1, 1, 2 ),
    gen_rr_srcs_dep_test( 0, "sll", 1, 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sll", 1, 1, 2 ),
    gen_rr_src1_eq_dest_test( "sll", 1, 1, 2 ),
    gen_rr_src0_eq_src1_test( "sll", 2, 8 ),
    gen_rr_srcs_eq_dest_test( "sll", 2, 8 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sll", 0x00000001, 0x00000000, 0x00000001 ),
    gen_rr_value_test( "sll", 0x00000000, 0x00000001, 0x00000000 ),
    gen_rr_value_test( "sll", 0x00000001, 0x00000001, 0x00000002 ),

    gen_rr_value_test( "sll", 0xffffffff, 0x00000000, 0xffffffff ),
    gen_rr_value_test( "sll", 0xffffffff, 0xffffffff, 0x80000000 ),
    gen_rr_value_test( "sll", 0x00000000, 0xffffffff, 0x00000000 ),
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
    # dest.uint() converts the already wrapped result into an unsigned Python integer 
    asm_code.append( gen_rr_value_test( "sll", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

