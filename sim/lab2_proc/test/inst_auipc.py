#=========================================================================
# auipc
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
    auipc x1, 0x00010                       # PC=0x200
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw  proc2mngr, x1 > 0x00010200
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
    gen_imm_dest_dep_test( 5, "auipc", 0x00010, 0x00010200 ),
    gen_imm_dest_dep_test( 4, "auipc", 0x00200, 0x0020021c ),
    gen_imm_dest_dep_test( 3, "auipc", 0x03000, 0x03000234 ),
    gen_imm_dest_dep_test( 2, "auipc", 0x40000, 0x40000248 ),
    gen_imm_dest_dep_test( 1, "auipc", 0x00050, 0x00050258 ),
    gen_imm_dest_dep_test( 0, "auipc", 0x00060, 0x00060264 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_imm_value_test( "auipc", 0x00000, 0x00000200 ),
    gen_imm_value_test( "auipc", 0x12345, 0x12345208 ),
    gen_imm_value_test( "auipc", 0xFFFFF, 0xFFFFF210 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    imm = b32( random.randint(0, 0xFFFFF) )
    dest = (imm << 12) + 0x200 + 0x8 * i
    asm_code.append( gen_imm_value_test( "auipc", imm.int(), dest.int() ) )
  return asm_code