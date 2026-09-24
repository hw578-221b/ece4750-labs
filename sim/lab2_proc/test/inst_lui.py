#=========================================================================
# lui
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
    lui x1, 0x0001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00001000
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
    gen_imm_dest_dep_test( 5, "lui", 0x00010, 0x00010000 ),
    gen_imm_dest_dep_test( 4, "lui", 0x00200, 0x00200000 ),
    gen_imm_dest_dep_test( 3, "lui", 0x03000, 0x03000000 ),
    gen_imm_dest_dep_test( 2, "lui", 0x40000, 0x40000000 ),
    gen_imm_dest_dep_test( 1, "lui", 0x00050, 0x00050000 ),
    gen_imm_dest_dep_test( 0, "lui", 0x00060, 0x00060000 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_imm_value_test( "lui", 0x00000, 0x00000000 ),
    gen_imm_value_test( "lui", 0x12345, 0x12345000 ),
    gen_imm_value_test( "lui", 0xFFFFF, 0xFFFFF000 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    imm = b32( random.randint(0, 0xFFFFF) )
    dest = (imm << 12)
    asm_code.append( gen_imm_value_test( "lui", imm.int(), dest.int() ) )
  return asm_code