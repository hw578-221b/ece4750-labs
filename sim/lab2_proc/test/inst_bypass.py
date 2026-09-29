#=========================================================================
# bypass
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from lab2_proc.test.inst_utils import *

def gen_bypassX_1_test():
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
