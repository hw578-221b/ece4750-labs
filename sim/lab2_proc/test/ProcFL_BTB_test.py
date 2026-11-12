#=========================================================================
# ProcFL_BTB_test.py
#=========================================================================
# We group all our test cases into a class so that we can easily reuse
# these test cases in our RTL tests. We can simply inherit from this test
# class, overload the setup_class method, and set the ProcType
# appropriately.

import pytest

from pymtl3 import *
from lab2_proc.test.harness import asm_test, run_test
from lab2_proc.ProcFL import ProcFL

from lab2_proc.test import btb

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcFL

  @pytest.mark.parametrize( "name,test", [
    asm_test( btb.gen_btb_taken_test ),
    asm_test( btb.gen_btb_not_taken_test ),
    asm_test( btb.gen_btb_branch_jump_test ),
    asm_test( btb.gen_btb_branch_jump2_test ),
    asm_test( btb.gen_btb_two_level_branch_test ),
  ])

  def test_btb( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  # def test_add_delays( s ):
  #   run_test( s.ProcType, inst_add.gen_random_test, delays=True,
  #             cmdline_opts=s.__class__.cmdline_opts )