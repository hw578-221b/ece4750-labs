#=========================================================================
# ProcAlt PyMTL Wrapper
#=========================================================================

import os

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.mem.ifcs    import MemRequesterIfc
from pymtl3.stdlib.mem         import mk_mem_msg

class ProcAlt( VerilogPlaceholder, Component ):
  def construct( s ):

    s.set_metadata( VerilogPlaceholderPass.params, {
          "p_commit": int(os.environ.get("ECE4750_COMMIT_LOG", "0") == "1"),
        } )

    req_class, resp_class = mk_mem_msg( 8, 32, 32 )

    s.mngr2proc   = IStreamIfc( Bits32 )
    s.proc2mngr   = OStreamIfc( Bits32 )
    s.imem        = MemRequesterIfc( req_class, resp_class )
    s.dmem        = MemRequesterIfc( req_class, resp_class )
    s.core_id     = InPort(32)
    s.commit_inst = OutPort()
    s.stats_en    = OutPort()

