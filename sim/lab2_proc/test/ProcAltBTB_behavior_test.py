#=========================================================================
# ProcAltBTB_behavior_test.py
#=========================================================================
# It is as simple as inheriting from FL tests and change the ProcType.

from lab2_proc.ProcAltBTB import ProcAltBTB
from lab2_proc.test.ProcFL_BTB_test import Tests as ProcFL_BTB_TestsBaseClass

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

class Tests( ProcFL_BTB_TestsBaseClass ):

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcAltBTB
