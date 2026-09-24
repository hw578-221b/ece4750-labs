#=========================================================================
# jal
#=========================================================================

from pymtl3 import *
from lab2_proc.test.inst_utils import *
import random

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addi  x3, x0, 0     # 0x0200
                        #
    nop                 # 0x0204
    nop                 # 0x0208
    nop                 # 0x020c
    nop                 # 0x0210
    nop                 # 0x0214
    nop                 # 0x0218
    nop                 # 0x021c
    nop                 # 0x0220
                        #
    jal   x1, label_a   # 0x0224
    addi  x3, x3, 0b01  # 0x0228

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
    csrw  proc2mngr, x1 > 0x0228

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3 > 0b10

  """

#-------------------------------------------------------------------------
# gen_directed_test
#-------------------------------------------------------------------------

def gen_multijump_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0          # 0x00000200

    jal   x1, label_a        # 0x00000204
    addi  x3, x3, 0b000001   # 0x00000208
                             #
  label_b:                   #
    addi  x3, x3, 0b000010   # 0x0000020c
    addi  x5, x1, 0          # 0x00000210
    jal   x1, label_c        # 0x00000214
    addi  x3, x3, 0b000100   # 0x00000218
                             #
  label_a:                   #
    addi  x3, x3, 0b001000   # 0x0000021c
    addi  x4, x1, 0          # 0x00000220
    jal   x1, label_b        # 0x00000224
    addi  x3, x3, 0b010000   # 0x00000228
                             #
  label_c:                   #
    addi  x3, x3, 0b100000   # 0x0000022c
    addi  x6, x1, 0          # 0x00000230

    # Carefully determine which bits are expected
    # to be set if jump operates correctly.
    csrw  proc2mngr, x3 > 0b101010

    # Check the link addresses
    csrw  proc2mngr, x4 > 0x00000208
    csrw  proc2mngr, x5 > 0x00000228
    csrw  proc2mngr, x6 > 0x00000218
  """

def gen_fulljump_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0               # 0x00000200
                                  #
    jal   x1, label_2             # 0x00000204
    addi  x3, x3, 0b00000000001   # 0x00000208
                                  #
  label_1:                        #
    addi  x3, x3, 0b00000000010   # 0x0000020c
    addi  x2, x1, 0               # 0x00000210
    jal   x1, label_4             # 0x00000214
    addi  x3, x3, 0b00000000100   # 0x00000218
                                  #
  label_2:                        #
    addi  x3, x3, 0b00000001000   # 0x0000021c
    addi  x4, x1, 0               # 0x00000220
    jal   x1, label_1             # 0x00000224
    addi  x3, x3, 0b00000010000   # 0x00000228
                                  #
  label_3:                        #
    addi  x3, x3, 0b00000100000   # 0x0000022c
    addi  x5, x1, 0               # 0x00000230
    jal   x1, label_5             # 0x00000234
    addi  x3, x3, 0b00001000000   # 0x00000238
                                  #
  label_4:                        #
    addi  x3, x3, 0b00010000000   # 0x0000023c
    addi  x6, x1, 0               # 0x00000240
    jal   x1, label_3             # 0x00000244
    addi  x3, x3, 0b00100000000   # 0x00000248
                                  #
  label_5:                        #
    addi  x3, x3, 0b01000000000   # 0x0000024c
    addi  x7, x1, 0               # 0x00000250
  
    csrw  proc2mngr, x3 > 0b01010101010

    # Check the link addresses
    csrw  proc2mngr, x2 > 0x00000228
    csrw  proc2mngr, x4 > 0x00000208
    csrw  proc2mngr, x5 > 0x00000248
    csrw  proc2mngr, x6 > 0x00000218
    csrw  proc2mngr, x7 > 0x00000238
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

    # seq[i-1] != i for i in range(1, 6)
    # This is a generator expression. It acts like a high-speed, memory-efficient for loop that 
    # evaluates a condition for every iteration and spits out a stream of True or False values one by one
    # The all() function is a built-in Python function that takes an iterable (like our stream of booleans)
    # and checks if every single item is True

    # can also use Python's any() function, which returns True if at least one condition is met:
    # if not any(seq[i-1] == i for i in range(1, 6)):
    #   return seq

    # Rrevent self-jumps: the assembly below uses
    # seq[0] for the entry jump and seq[k] for the jump from label_k.
    if all(seq[i-1] != i for i in range(1,6)):
      return seq

def gen_randjump_test():

  # seq[0] is the entry destination; seq[1] through seq[4] are the
  # destinations of jumps from labels 1 through 4. Label 5 ends the path.
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

  # Map each jump source to the link address written by jal (its PC + 4).
  # Source 0 is the entry jump; sources 1..4 are the labeled blocks.
  # These addresses assume this program starts at 0x200.
  label_to_pcs = {
      0: 0x0000021c,
      1: 0x0000022c,
      2: 0x0000023c,
      3: 0x0000024c,
      4: 0x0000025c
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
          # Follow this block's jal and record the link its destination
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
    addi  x3, x0, 0               # 0x00000200
    # Initalize all Xregs used to 0 for verification reference (if not jumped to, stay 0)
    addi  x2, x0, 0               # 0x00000204
    addi  x4, x0, 0               # 0x00000208
    addi  x5, x0, 0               # 0x0000020c
    addi  x6, x0, 0               # 0x00000210
    addi  x7, x0, 0               # 0x00000214
                                  #
    jal   x1, label_{seq[0]}      # 0x00000218
    addi  x3, x3, 0b00000000001   # 0x0000021c
                                  #
  label_1:                        #
    addi  x3, x3, 0b00000000010   # 0x00000220
    addi  x2, x1, 0               # 0x00000224
    jal   x1, label_{seq[1]}      # 0x00000228
    addi  x1, x3, 0b00000000100   # 0x0000022c
                                  #
  label_2:                        #
    addi  x3, x3, 0b00000001000   # 0x00000230
    addi  x4, x1, 0               # 0x00000234
    jal   x1, label_{seq[2]}      # 0x00000238
    addi  x3, x3, 0b00000010000   # 0x0000023c
                                  #
  label_3:                        #
    addi  x3, x3, 0b00000100000   # 0x00000240
    addi  x5, x1, 0               # 0x00000244
    jal   x1, label_{seq[3]}      # 0x00000248
    addi  x1, x3, 0b00001000000   # 0x0000024c
                                  #
  label_4:                        #
    addi  x3, x3, 0b00010000000   # 0x00000250
    addi  x6, x1, 0               # 0x00000254
    jal   x1, label_{seq[4]}      # 0x00000258
    addi  x1, x3, 0b00100000000   # 0x0000025c
                                  #
  label_5:                        #
    addi  x3, x3, 0b01000000000   # 0x00000260
    addi  x7, x1, 0               # 0x00000264
  
    csrw  proc2mngr, x3 > {x3:#011b}   # use # to include the 0b/0x prefix

    # Check the link addresses
    csrw  proc2mngr, x2 > {x2:#08x}
    csrw  proc2mngr, x4 > {x4:#08x}
    csrw  proc2mngr, x5 > {x5:#08x}
    csrw  proc2mngr, x6 > {x6:#08x}
    csrw  proc2mngr, x7 > {x7:#08x}
  """
