#=========================================================================
# ProcAltBTB_jump_test.py
#=========================================================================
# It is as simple as inheriting from FL tests and change the ProcType.

from lab2_proc.ProcAltBTB import ProcAltBTB
from lab2_proc.test.ProcFL_jump_test import Tests as ProcFL_jump_TestsBaseClass

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

class Tests( ProcFL_jump_TestsBaseClass ):

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcAltBTB

