#=========================================================================
# extra multicore memory tests
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < {0x00002000,0x00002004,0x00002008,0x0000200c}
    csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}

    .data
    .word 0x01020304
    .word 0x11121314
    .word 0x21222324
    .word 0x31323334
  """

def gen_adja_words_in_line_test():
  return """
  csrr x1, mngr2proc < {0x00002000,0x00002004,0x00002008,0x0000200c}
  csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
  csrr x3, mngr2proc < {0x4a4b4c4d,0x5a5b5c5d,0x6a6b6c6d,0x6a6b6c6d}
  sw   x2, 0(x1)
  sw   x3, 0(x1)
  lw   x4, 0(x1)
  csrw proc2mngr, x4 > {0x4a4b4c4d,0x5a5b5c5d,0x6a6b6c6d,0x6a6b6c6d}
"""

def gen_diff_bank_test():
  return """
  csrr x1, mngr2proc < {0x00002000,0x00002010,0x00002020,0x00002030}
  csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
  sw   x2, 0(x1)
  lw   x3, 0(x1)
  csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
"""

def gen_diff_line_same_bank_test():
  return """
    csrr x1, mngr2proc < {0x00002000,0x00002040,0x00002080,0x000020c0}
    csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
    sw   x2, 0(x1)
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
  """

def gen_same_word_in_line_test(): # dirty eviction
  return """
      csrr x1, mngr2proc < {0x00002000,0x00002200,0x00002400,0x00002600}
      csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
      sw   x2, 0(x1)
      lw   x3, 0(x1)
      csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
    """

def gen_core_bank_rotate_test1():
  return """
    csrr x1, mngr2proc < {0x00002040,0x00002030,0x00002020,0x00002010}
    csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
    sw   x2, 0(x1)
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
  """

def gen_core_bank_rotate_test2():
  return """
    csrr x1, mngr2proc < {0x00002010,0x00002020,0x00002030,0x00002000}
    csrr x2, mngr2proc < {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
    sw   x2, 0(x1)
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0x0a0b0c0d,0x1a1b1c1d,0x2a2b2c2d,0x3a3b3c3d}
  """

def gen_read_miss_test():
  return """
    csrr x1, mngr2proc < {0x00002000,0x00002004,0x00002008,0x0000200c}
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > {0x01020304,0x11121314,0x21222324,0x31323334}

    .data
    .word 0x01020304
    .word 0x11121314
    .word 0x21222324
    .word 0x31323334
  """

# Convert four Python values into the harness's {a,b,c,d} syntax.
def group(values):
  return "{" + ",".join(f"0x{x:08x}" for x in values) + "}"

def gen_random_access_test():
  asm = []
  # four test memory using python dictionary
  # they track the latest value at each address, which is exactly what the final check needs.
  # the dictionaries might contain different numbers of initialized words in the end
  mem_arrays = [{} for _ in range(4)]

  # write into memory and check results
  for _ in range(80):
    # give each core permanent ownership of one word position in every line to prevent R/W racing
    # random tag for testing eviction behavior
    tag = random.getrandbits(3)
    idx = random.getrandbits(3)
    bank = random.getrandbits(2)

    addrs = [0x2000 + (tag << 9) + (idx << 6) + (bank << 4) + core_id*4 for core_id in range(4)]

    values = [random.randint(0, 0xffffffff) for _ in range(4)]

    asm.append(f"csrr x1, mngr2proc < {group(addrs)}")
    asm.append(f"csrr x2, mngr2proc < {group(values)}")
    asm.append("sw x2, 0(x1)")
    asm.append("lw x3, 0(x1)")
    asm.append(f"csrw proc2mngr, x3 > {group(values)}")

    # update the test memory
    # zip() pairs up elements from multiple lists by matching their positions
    for core_mem, addr, value in zip(mem_arrays, addrs, values):
      core_mem[addr] = value

  # final sweep, check memory result by reading every initalized word back
  # apply to 4 dictionaries have same # of entries
  # This catches corruption of a word that later random operations never happened to read.
  for addr0 in mem_arrays[0]:         # Iterating over a dictionary gives its keys!

    addrs = [addr0 + 4*core_id for core_id in range(4)]
    values = [core_mem[addr] for core_mem, addr in zip(mem_arrays, addrs)]
    # Alternative:
    # values = [mem_arrays[core][addrs[core]] for core in range(4)]

    asm.append(f"csrr x4, mngr2proc < {group(addrs)}")
    asm.append("lw x5, 0(x4)")
    asm.append(f"csrw proc2mngr, x5 > {group(values)}")

  # # Another way of final sweep: (4 dictionaries need to have same # of entries)

  # # mem.items() list to every (key, value) pair in the dictionary
  # # Without *: (mem.items() for mem in mem_arrays) produces a single generator/box/list containing 4 dictionary views
  # # Python unpacks that generator so zip() receives 4 separate arguments
  # # unpack + zip effectively transposing the data
  # for pairs in zip(*(mem.items() for mem in mem_arrays)):
  #   # use * unpack pairs tuples feeds the 4 (addr, val) tuples into zip() as 4 separate arguments
  #   # zip() pairs up all the first elements together and all the second elements together
  #   # also effectively transposing the data
  #   addrs, values = zip(*pairs)

  #   asm.append(f"csrr x4, mngr2proc < {group(addrs)}")
  #   asm.append("lw x5, 0(x4)")
  #   asm.append(f"csrw proc2mngr, x5 > {group(values)}")

  return '\n'.join(asm)