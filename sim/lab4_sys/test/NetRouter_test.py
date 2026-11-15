#=========================================================================
# NetRouter_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from lab4_sys.NetMsg import mk_net_msg
from lab4_sys.NetRouter import NetRouter

import random
random.seed(0xdeadbeef)

#-------------------------------------------------------------------------
# Message Types
#-------------------------------------------------------------------------

NetMsgType = mk_net_msg( 32 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, router_id=0 ):

    # Instantiate models

    s.srcs   = [ StreamSourceFL( NetMsgType ) for _ in range(3) ]
    s.router = NetRouter( p_msg_nbits=44 )
    s.sinks  = [ StreamSinkFL( NetMsgType ) for _ in range(3) ]

    # Connect

    s.router.router_id //= router_id
    for i in range(3):
      s.srcs[i].ostream   //= s.router.istream[i]
      s.router.ostream[i] //= s.sinks[i].istream

  def done( s ):
    for i in range(3):
      if not s.srcs[i].done() or not s.sinks[i].done():
        return False
    return True

  def line_trace( s ):
    srcs_str  = "|".join([ src.line_trace()  for src  in s.srcs  ])
    sinks_str = "|".join([ sink.line_trace() for sink in s.sinks ])
    return f"{srcs_str} > ({s.router.line_trace()}) > {sinks_str}"

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------
# These is an example of a basic test. This tests may not be valid
# depending on your routing and arbitration algorithms. You are free to
# change this test. We will not test your router since its functionality
# depends on the chosen routing and arbitration algorithms.

def test_basic( cmdline_opts ):

  th = TestHarness( router_id=0 )

  msgs = [
    #           src  dest opaq  payload
    NetMsgType( 0,   2,   0x12, 0x12121212 ),
    NetMsgType( 1,   0,   0x10, 0x10101010 ),
    NetMsgType( 2,   1,   0x11, 0x11111111 ),
  ]

  th.set_param("top.srcs[0].construct",  msgs=[ m for m in msgs if m.src  == 0 ] )
  th.set_param("top.srcs[1].construct",  msgs=[ m for m in msgs if m.src  == 1 ] )
  th.set_param("top.srcs[2].construct",  msgs=[ m for m in msgs if m.src  == 2 ] )
  th.set_param("top.sinks[0].construct", msgs=[ m for m in msgs if m.dest == 0 ] )
  th.set_param("top.sinks[1].construct", msgs=[ m for m in msgs if m.dest in (1,2) ] )
  th.set_param("top.sinks[2].construct", msgs=[ m for m in msgs if m.dest == 3 ] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['router'] )


one = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
]

rotate0 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   0,   0x10, 0x10101010 ),
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
  NetMsgType( 2,   1,   0x11, 0x11111111 ),
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
]

rotate1 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   3,   0x13, 0x13131313 ),
  NetMsgType( 2,   0,   0x10, 0x10101010 ),
  NetMsgType( 0,   1,   0x11, 0x11111111 ),
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
]

rotate2 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   2,   0x12, 0x12121212 ),
  NetMsgType( 2,   3,   0x13, 0x13131313 ),
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
  NetMsgType( 0,   1,   0x11, 0x11111111 ),
]

rotate3 = [
  #           src  dest opaq  payload
  NetMsgType( 1,   1,   0x11, 0x11111111 ),
  NetMsgType( 2,   2,   0x12, 0x12121212 ),
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
]

all_to_dest0 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x12, 0x12121212 ),
  NetMsgType( 1,   0,   0x10, 0x10101010 ),
  NetMsgType( 2,   0,   0x11, 0x11111111 ),
]

all_to_dest1 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   1,   0x12, 0x12121212 ),
  NetMsgType( 1,   1,   0x10, 0x10101010 ),
  NetMsgType( 2,   1,   0x11, 0x11111111 ),
]

all_to_dest2 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
  NetMsgType( 1,   2,   0x10, 0x10101010 ),
  NetMsgType( 2,   2,   0x11, 0x11111111 ),
]

all_to_dest3 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   3,   0x12, 0x12121212 ),
  NetMsgType( 1,   3,   0x10, 0x10101010 ),
  NetMsgType( 2,   3,   0x11, 0x11111111 ),
]

loaded_to_dest0 = [
  NetMsgType( 0,   0,   0x10, 0x12121212 ),
  NetMsgType( 1,   0,   0x11, 0x10101010 ),
  NetMsgType( 2,   0,   0x12, 0x11111111 ),
  NetMsgType( 0,   0,   0x13, 0x12121212 ),
  NetMsgType( 1,   0,   0x14, 0x10101010 ),
  NetMsgType( 2,   0,   0x15, 0x11111111 ),
  NetMsgType( 0,   0,   0x16, 0x12121212 ),
  NetMsgType( 1,   0,   0x17, 0x10101010 ),
  NetMsgType( 2,   0,   0x18, 0x11111111 ),
]

loadded_to_output1 = [
  NetMsgType( 0,   1,   0x10, 0x12121212 ),
  NetMsgType( 1,   2,   0x11, 0x10101010 ),
  NetMsgType( 2,   1,   0x12, 0x11111111 ),
  NetMsgType( 0,   2,   0x13, 0x12121212 ),
  NetMsgType( 1,   1,   0x14, 0x10101010 ),
  NetMsgType( 2,   2,   0x15, 0x11111111 ),
]

random_msg = []

# generate random messages
for i in range(60):
  src = random.randint(0,2)
  dest = random.randint(0,3)
  rand_payload = random.randint(0,0xffffffff)
  random_msg.append( NetMsgType( src, dest, i, rand_payload ) )


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                                  "msgs    src_delay sink_delay delay_mode ordered"),
  [ "one",                            one,                 0,  0,  'fixed',   True  ],
  [ "rotate0",                        rotate0,             0,  0,  'fixed',   True  ],
  [ "rotate1",                        rotate1,             0,  0,  'fixed',   True  ],
  [ "rotate2",                        rotate2,             0,  0,  'fixed',   True  ],
  [ "rotate3",                        rotate3,             0,  0,  'fixed',   True  ],
  [ "all_to_dest0",                   all_to_dest0,        0,  0,  'fixed',   True  ],
  [ "all_to_dest1",                   all_to_dest1,        0,  0,  'fixed',   True  ],
  [ "all_to_dest2",                   all_to_dest2,        0,  0,  'fixed',   True  ],
  [ "all_to_dest3",                   all_to_dest3,        0,  0,  'fixed',   True  ],
  [ "loaded_to_dest0",                loaded_to_dest0,     0,  0,  'fixed',   True  ],
  [ "loadded_to_output1",             loadded_to_output1,  0,  0,  'fixed',   True  ],
  [ "random",                         random_msg,          0,  0,  'fixed',   False ],
  [ "random_src_stall",               random_msg,          5,  0,  'random',  False ],
  [ "random_dst_stall",               random_msg,          0,  5,  'random',  False ],
  [ "random_both_stall",              random_msg,          5,  5,  'random',  False ],
])

#-------------------------------------------------------------------------
# test w/ router id = 0
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_router_id_0( test_params, cmdline_opts ):

  th = TestHarness( router_id=0 )

  th.set_param("top.srcs[0].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 0 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[1].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 1 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[2].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 2 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 0 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay,
    ordered             = test_params.ordered )

  th.set_param("top.sinks[1].construct",
    msgs                = [ m for m in test_params.msgs if m.dest in (1,2) ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay,
    ordered             = test_params.ordered )

  th.set_param("top.sinks[2].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 3 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay,
    ordered             = test_params.ordered )
  
  th.elaborate()

  run_sim( th, cmdline_opts, duts=['router'] )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

