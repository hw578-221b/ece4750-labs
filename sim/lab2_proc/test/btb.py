#=========================================================================
# btb test cases
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from lab2_proc.test.inst_utils import *

def gen_btb_taken_test():
  return """
    csrr x1, mngr2proc, < 4  # 0x0200
    csrr x2, mngr2proc, < 0  # 0x0204      
    csrr x3, mngr2proc, < 0  # 0x0208
                             # 
  loop:                      # 
    addi x2, x2, 1           # 0x020c
    addi x3, x3, 1           # 0x0210
    addi x1, x1, -1          # 0x0214
    bne  x1, x0, loop        # 0x0218
                             # 
    csrw proc2mngr, x2 > 4   # 0x021c      
    csrw proc2mngr, x3 > 4   # 0x0220
  """                        

def gen_btb_not_taken_test():
  return """
    csrr x1, mngr2proc, < 1
    csrr x2, mngr2proc, < 2
    csrr x4, mngr2proc, < 3
    csrr x3, mngr2proc, < 0
                          
  loop1:                          
    addi x3, x3, 1                
    bge  x1, x2, loop1 

  loop2:                          
    addi x3, x3, 2                
    blt  x4, x2, loop2

  loop3:                          
    addi x3, x3, 3                
    bne  x2, x2, loop3
  
    csrw proc2mngr, x3 > 6
  """

def gen_btb_branch_jump_test():
  return """
    csrr x1, mngr2proc, < 4  
    csrr x2, mngr2proc, < 0  
    csrr x3, mngr2proc, < 0  
                             
  loop:                      
    addi x2, x2, 1           
    addi x3, x3, 1           
    addi x1, x1, -1
    jal  x4, foo1       # simulate function call 
    bne  x1, x0, loop
    jal  x0, foo2       # btb shouldn't update with this tag until bne not taken
  
  foo1:
    addi x2, x2, 1
    jalr x0, x4, 0

  foo2:
    addi x3, x3, 1     
                             
    csrw proc2mngr, x2 > 8  
    csrw proc2mngr, x3 > 5   
  """ 

def gen_btb_branch_jump2_test():
  return """
    csrr x1, mngr2proc, < 4  
    csrr x2, mngr2proc, < 0  
    csrr x3, mngr2proc, < 0  
                             
  loop:                      
    addi x2, x2, 1           
    addi x3, x3, 1           
    addi x1, x1, -1
    jal  x4, foo1       # simulate function call 
    bne  x1, x0, loop
    jal  x0, foo2       # btb shouldn't update with this tag until bne not taken
  
  foo1:
    addi x2, x2, 1
    nop                 # make jalr occupy different BTB entry with previous jal and bne
    nop
    nop
    jalr x0, x4, 0

  foo2:
    addi x3, x3, 1     
                             
    csrw proc2mngr, x2 > 8  
    csrw proc2mngr, x3 > 5   
  """  

def gen_btb_two_level_branch_test():
  return """
    csrr x1, mngr2proc, < 4  
    csrr x2, mngr2proc, < 2   
    csrr x3, mngr2proc, < 0  
                             
  loop:                               
    addi x3, x3, 1           
    addi x1, x1, -1          
    bne  x1, x0, loop
    addi x2, x2, -1
    addi x1, x0, 4
    bne  x2, x0, loop
                                
    csrw proc2mngr, x3 > 8   
  """     