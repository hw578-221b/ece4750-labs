#=========================================================================
# bypass
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from lab2_proc.test.inst_utils import *

def gen_bypass_1_test():
  return """
    csrr x1, mngr2proc, < 5
    csrr x2, mngr2proc, < 2
    nop
    nop
    nop
    nop
    add  x3, x1, x2
    add  x4, x3, x2
    nop
    nop
    nop
    csrw proc2mngr, x4 > 9
    nop
    nop
    nop
  """

def gen_bypass_2_test():
  return """
    csrr x1, mngr2proc, < 5
    csrr x2, mngr2proc, < 2
    nop
    nop
    add  x3, x1, x2
    add  x4, x3, x2
    nop
    nop
    nop
    csrw proc2mngr, x4 > 9
    nop
    nop
    nop
  """

def gen_bypass_3_test():
  return """
    csrr x1, mngr2proc, < 5
    csrr x2, mngr2proc, < 2
    nop
    add  x3, x1, x2
    add  x4, x3, x2
    nop
    nop
    nop
    csrw proc2mngr, x4 > 9
    nop
    nop
    nop
  """

def gen_bypass_4_test():
  return """
    csrr x1, mngr2proc, < 5
    csrr x2, mngr2proc, < 2
    add  x3, x1, x2
    add  x4, x3, x2
    nop
    nop
    nop
    csrw proc2mngr, x4 > 9
    nop
    nop
    nop
  """

def gen_bypass_5_test():
  return """
    csrr x1, mngr2proc, < 0x2000
    csrr x2, mngr2proc, < 4
    add  x3, x1, x2
    add  x4, x3, x2
    sw   x3, 0(x4)
    sw   x4, 0(x3)
    lw   x5, 0(x4)
    lw   x6, 0(x3)
    addi x7, x6, 1
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x2004
    csrw proc2mngr, x4 > 0x2008
    csrw proc2mngr, x5 > 0x2004
    csrw proc2mngr, x6 > 0x2008
    csrw proc2mngr, x7 > 0x2009
    nop
    nop
    nop
  """

def gen_general_1_test():
  return """
    # Send value 0x00002000 from test source into processor
    csrr x2, mngr2proc < 0x00002000
    csrr x4, mngr2proc < 0x00000200

    # Loop over four elements in array
    addi x1, x0, 4
    loop:
      lw x3, 0(x2)
      addi x3, x3, 1
      sw x3, 0(x4)
      addi x2, x2, 4
      addi x4, x4, 4
      addi x1, x1, -1
      bne x1, x0, loop

    # Read out the four results and send to test sink for verification

    addi x1, x0, 0x200
    lw x2, 0(x1)
    csrw proc2mngr, x2 > 2

    addi x1, x0, 0x204
    lw x2, 0(x1)
    csrw proc2mngr, x2 > 3

    addi x1, x0, 0x208
    lw x2, 0(x1)
    csrw proc2mngr, x2 > 4

    addi x1, x0, 0x20c
    lw x2, 0(x1)
    csrw proc2mngr, x2 > 5

    # Data section
    .data

    # src array
    .word 0x00000001
    .word 0x00000002
    .word 0x00000003
    .word 0x00000004

    # dest array
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
  """
