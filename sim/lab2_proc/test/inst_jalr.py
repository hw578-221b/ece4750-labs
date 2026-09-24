#=========================================================================
# jalr
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

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0           # 0x0200
                              #
    lui  x1,     %hi[label_a] # 0x0204
    addi x1, x1, %lo[label_a] # 0x0208
                              #
    nop                       # 0x020c
    nop                       # 0x0210
    nop                       # 0x0214
    nop                       # 0x0218
    nop                       # 0x021c
    nop                       # 0x0220
    nop                       # 0x0224
    nop                       # 0x0228
                              #
    jalr  x31, x1, 0          # 0x022c
    addi  x3, x3, 0b01        # 0x0230

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addi  x3, x3, 0b10

    # Check the link address
    csrw  proc2mngr, x31 > 0x0230

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3  > 0b10

  """

#-------------------------------------------------------------------------
# gen_directed_test
#-------------------------------------------------------------------------

def gen_jump_squash_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3,  x0,  0              # 0x00000200
    lui   x31,      %hi[label_2]   # 0x00000204
    addi  x31, x31, %lo[label_2]   # 0x00000208
    jalr  x1,  x31, 0              # 0x0000020c
    addi  x3,  x3,  0b00000000001  # 0x00000210
    addi  x3,  x3,  0b00000000010  # 0x00000214
                                   #
  label_2:                         #
    addi  x3,  x3,  0b00000000100  # 0x00000218
    addi  x4,  x1,  0              # 0x0000021c

    csrw  proc2mngr, x3 > 0b00000000100

    # Check the link addresses         
    csrw  proc2mngr, x4 > 0x00000210                        
  """

def gen_fulljump_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3,  x0,  0              # 0x00000200
    lui   x31,      %hi[label_2]   # 0x00000204
    addi  x31, x31, %lo[label_2]   # 0x00000208
    jalr  x1,  x31, 0              # 0x0000020c
    addi  x3,  x3,  0b00000000001  # 0x00000210
                                   #
  label_1:                         #
    addi  x3,  x3,  0b00000000010  # 0x00000214
    addi  x2,  x1,  0              # 0x00000218
    lui   x31,      %hi[label_4]   # 0x0000021c
    addi  x31, x31, %lo[label_4]   # 0x00000220
    jalr  x1,  x31, 0              # 0x00000224
    addi  x1,  x3,  0b00000000100  # 0x00000228
                                   #
  label_2:                         #
    addi  x3,  x3,  0b00000001000  # 0x0000022c
    addi  x4,  x1,  0              # 0x00000230
    lui   x31,      %hi[label_1]   # 0x00000234
    addi  x31, x31, %lo[label_1]   # 0x00000238
    jalr  x1,  x31, 0              # 0x0000023c
    addi  x3,  x3,  0b00000010000  # 0x00000240
                                   #
  label_3:                         #
    addi  x3,  x3,  0b00000100000  # 0x00000244
    addi  x5,  x1,  0              # 0x00000248
    lui   x31,      %hi[label_5]   # 0x0000024c
    addi  x31, x31, %lo[label_5]   # 0x00000250
    jalr  x1,  x31, 0              # 0x00000254
    addi  x1,  x3,  0b00001000000  # 0x00000258
                                   #
  label_4:                         #
    addi  x3,  x3,  0b00010000000  # 0x0000025c
    addi  x6,  x1,  0              # 0x00000260
    lui   x31,      %hi[label_3]   # 0x00000264
    addi  x31, x31, %lo[label_3]   # 0x00000268
    jalr  x1,  x31, 0              # 0x0000026c
    addi  x1,  x3,  0b00100000000  # 0x00000270
                                   #
  label_5:                         #
    addi  x3,  x3,  0b01000000000  # 0x00000274
    addi  x7,  x1,  0              # 0x00000278

    csrw  proc2mngr, x3 > 0b01010101010

    # Check the link addresses
    csrw  proc2mngr, x2 > 0x00000240             
    csrw  proc2mngr, x4 > 0x00000210             
    csrw  proc2mngr, x5 > 0x00000270             
    csrw  proc2mngr, x6 > 0x00000228             
    csrw  proc2mngr, x7 > 0x00000258             
  """

def gen_bne_with_jalr_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0          
    # Use x5 to track if jal happens
    addi  x5, x0, 0

    csrr  x2, mngr2proc < 1  
    csrr  x4, mngr2proc < 2
    lui   x31,      %hi[label_b]
    addi  x31, x31, %lo[label_b]

    # label_c branch should be taken, not label_b
    bne   x2, x4, label_c    
    jalr  x1, x31, 0        
    addi  x3, x3, 0b000001   
                             
  label_b:                   
    addi  x3, x3, 0b000010   
    addi  x5, x1, 0          
                             
  label_c:                   
    addi  x3, x3, 0b100000   

    csrw  proc2mngr, x3 > 0b100000

    # Check the link addresses
    csrw  proc2mngr, x5 > 0 
  """

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

# Generate a permutation in which no value stays in its original position.
def gen_rand_derangement():
  original = [1, 2, 3, 4, 5]

  while True:
    # Shuffle a fresh copy so each destination label still appears once.
    seq = original.copy()
    random.shuffle(seq)

    if all(seq[i-1] != i for i in range(1,6)):
      return seq

def gen_randjump_test():

  seq = gen_rand_derangement()

  # Match the assembly's initial register values. x3 tracks visited labels;
  # the other registers capture link addresses and stay zero if unvisited.
  x2 = x3= x4 = x5 = x6 = x7 = 0

  # Map each destination label to its expected saved link value:
  # labels 1, 2, 3, 4, 5 copy x1 into x2, x4, x5, x6, x7, respectively.
  label_to_regs = {
      1: x2,
      2: x4,
      3: x5,
      4: x6,
      5: x7
  }

  # Map each jump source to the link address written by jalr (its PC + 4).
  # Source 0 is the entry jump; sources 1..4 are the labeled blocks.
  # These addresses assume this program starts at 0x200.
  label_to_pcs = {
      0: 0x00000224,
      1: 0x0000023c,
      2: 0x00000254,
      3: 0x0000026c,
      4: 0x00000284
  }

  # Model the entry jump and the link value saved at its destination.
  next_num = seq[0]
  curr_num = 0
  label_to_regs[next_num] = label_to_pcs[curr_num]

  # Follow the same jumps as the assembly. Since each destination appears
  # once in seq, the path from entry 0 reaches label 5 without revisiting
  # a label, so at most five label visits need to be modeled.
  for i in range(0,5):
      if next_num == 5:
          # The terminal block sets bit 9, saves x1 into x7, and falls
          # through to the checks. Its saved link was recorded on arrival.
          x3 += (1 << 9)
          break
      else:
          curr_num = next_num
          # Label k adds bit (2*k - 1) to the control-flow marker in x3.
          x3 += (1 << (2*curr_num-1))
          # Follow this block's jalr and record the link its destination
          # will copy from x1 into the corresponding saved-link register.
          next_num=seq[next_num]
          label_to_regs[next_num] = label_to_pcs[curr_num]

  # Extract the expected register values for the proc2mngr checks below.
  x2 = label_to_regs[1]
  x4 = label_to_regs[2]
  x5 = label_to_regs[3]
  x6 = label_to_regs[4]
  x7 = label_to_regs[5]
  
  return f"""

    # Use x3 to track the control flow pattern
    addi  x3,  x0,  0                       # 0x00000200
    # Initalize all Xregs used to 0 for verification reference (if not jumped to, stay 0)
    addi  x2,  x0,  0                       # 0x00000204
    addi  x4,  x0,  0                       # 0x00000208
    addi  x5,  x0,  0                       # 0x0000020c
    addi  x6,  x0,  0                       # 0x00000210
    addi  x7,  x0,  0                       # 0x00000214

    lui   x31,      %hi[label_{seq[0]}]     # 0x00000218
    addi  x31, x31, %lo[label_{seq[0]}]     # 0x0000021c
    jalr  x1,  x31, 0                       # 0x00000220
    addi  x3,  x3,  0b00000000001           # 0x00000224
                                            #
  label_1:                                  #
    addi  x3,  x3,  0b00000000010           # 0x00000228
    addi  x2,  x1,  0                       # 0x0000022c
    lui   x31,      %hi[label_{seq[1]}]     # 0x00000230
    addi  x31, x31, %lo[label_{seq[1]}]     # 0x00000234
    jalr  x1,  x31, 0                       # 0x00000238
    addi  x1,  x3,  0b00000000100           # 0x0000023c
                                            #
  label_2:                                  #
    addi  x3,  x3,  0b00000001000           # 0x00000240
    addi  x4,  x1,  0                       # 0x00000244
    lui   x31,      %hi[label_{seq[2]}]     # 0x00000248
    addi  x31, x31, %lo[label_{seq[2]}]     # 0x0000024c
    jalr  x1,  x31, 0                       # 0x00000250
    addi  x3,  x3,  0b00000010000           # 0x00000254
                                            #
  label_3:                                  #
    addi  x3,  x3,  0b00000100000           # 0x00000258
    addi  x5,  x1,  0                       # 0x0000025c
    lui   x31,      %hi[label_{seq[3]}]     # 0x00000260
    addi  x31, x31, %lo[label_{seq[3]}]     # 0x00000264
    jalr  x1,  x31, 0                       # 0x00000268
    addi  x1,  x3,  0b00001000000           # 0x0000026c
                                            #
  label_4:                                  #
    addi  x3,  x3,  0b00010000000           # 0x00000270
    addi  x6,  x1,  0                       # 0x00000274
    lui   x31,      %hi[label_{seq[4]}]     # 0x00000278
    addi  x31, x31, %lo[label_{seq[4]}]     # 0x0000027c
    jalr  x1,  x31, 0                       # 0x00000280
    addi  x1,  x3,  0b00100000000           # 0x00000284
                                            #
  label_5:                                  #
    addi  x3,  x3,  0b01000000000           # 0x00000288
    addi  x7,  x1,  0                       # 0x0000028c

    csrw  proc2mngr, x3 > {x3:#011b}        

    # Check the link addresses
    csrw  proc2mngr, x2 > {x2:#08x}         
    csrw  proc2mngr, x4 > {x4:#08x}         
    csrw  proc2mngr, x5 > {x5:#08x}         
    csrw  proc2mngr, x6 > {x6:#08x}         
    csrw  proc2mngr, x7 > {x7:#08x}         
  """