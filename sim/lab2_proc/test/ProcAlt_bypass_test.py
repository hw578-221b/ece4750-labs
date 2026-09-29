#=========================================================================
# ProcAlt_bypass_test.py
#=========================================================================
# It is as simple as inheriting from FL tests and change the ProcType.

from lab2_proc.ProcAlt import ProcAlt
from lab2_proc.test.ProcFL_bypass_test import Tests as ProcFL_bypass_TestsBaseClass

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

class Tests( ProcFL_bypass_TestsBaseClass ):

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcAlt

