#=========================================================================
# sra
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
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sra x3, x1, x2
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
    gen_rr_dest_dep_test( 5, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 4, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 3, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 2, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 1, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 0, "sra", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sra", 1, 1, 0 ),
    gen_rr_src0_dep_test( 4, "sra", 1, 1, 0 ),
    gen_rr_src0_dep_test( 3, "sra", 1, 1, 0 ),
    gen_rr_src0_dep_test( 2, "sra", 1, 1, 0 ),
    gen_rr_src0_dep_test( 1, "sra", 1, 1, 0 ),
    gen_rr_src0_dep_test( 0, "sra", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sra", 1, 1, 0 ),
    gen_rr_src1_dep_test( 4, "sra", 1, 1, 0 ),
    gen_rr_src1_dep_test( 3, "sra", 1, 1, 0 ),
    gen_rr_src1_dep_test( 2, "sra", 1, 1, 0 ),
    gen_rr_src1_dep_test( 1, "sra", 1, 1, 0 ),
    gen_rr_src1_dep_test( 0, "sra", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sra", 1, 1, 0 ),
    gen_rr_srcs_dep_test( 4, "sra", 1, 1, 0 ),
    gen_rr_srcs_dep_test( 3, "sra", 1, 1, 0 ),
    gen_rr_srcs_dep_test( 2, "sra", 1, 1, 0 ),
    gen_rr_srcs_dep_test( 1, "sra", 1, 1, 0 ),
    gen_rr_srcs_dep_test( 0, "sra", 1, 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sra", 1, 1, 0 ),
    gen_rr_src1_eq_dest_test( "sra", 1, 1, 0 ),
    gen_rr_src0_eq_src1_test( "sra", 2, 0 ),
    gen_rr_srcs_eq_dest_test( "sra", 2, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sra", 0x00000001, 0x00000000, 0x00000001 ),
    gen_rr_value_test( "sra", 0x00000000, 0x00000001, 0x00000000 ),
    gen_rr_value_test( "sra", 0x00000001, 0x00000001, 0x00000000 ),

    gen_rr_value_test( "sra", 0xffffffff, 0x00000001, 0xffffffff ),
    gen_rr_value_test( "sra", 0x00000001, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "sra", 0xffffffff, 0xffffffff, 0xffffffff ),

    gen_rr_value_test( "sra", 16, 2, 4 ),
    gen_rr_value_test( "sra", 17, 2, 4 ),
    gen_rr_value_test( "sra", 19, 2, 4 ),
    gen_rr_value_test( "sra", 20, 2, 5 ),

    gen_rr_value_test( "sra", -16, 2, -4 ),
    gen_rr_value_test( "sra", -17, 2, -5 ),
    gen_rr_value_test( "sra", -19, 2, -5 ),
    gen_rr_value_test( "sra", -20, 2, -5 ),
    gen_rr_value_test( "sra", -16, 0xffffffe2, -4 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32( random.randint(0,0xffffffff) )
    src1 = b32( random.randint(0,31) )
    # Shift the signed Python integer to preserve the sign bit for sra.
    dest = b32( src0.int() >> src1.uint() )
    # dest.uint() converts the already wrapped result into an unsigned Python integer 
    asm_code.append( gen_rr_value_test( "sra", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code
