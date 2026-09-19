#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest

from random import randint

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from lab1_imul.IntMulFL import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

# Component is the parent or base class
# This syntax means: Define TestHarness as a specialized kind of PyMTL Component
# A simpler example is:
# class Animal:
#   def breathe(self):
#     print("breathing")

# class Dog(Animal):
#   def bark(self):
#     print("bark")
# Because Dog inherits from Animal:
# dog = Dog()
# dog.breathe()  # Inherited from Animal
# dog.bark()     # Defined in Dog
# That is why the harness instance th can use: th.set_param(...)  th.elaborate()  th.apply(...)
class TestHarness( Component ):

  # construct is a method. src, sink, imul is an instance attribute
  # Component class defines a construct method, but its base implementation does not know what your particular component contains
  # So you have to inherit it and then implement it specifically (overridden the general one in Component)
  def construct( s, imul ):

    # Instantiate models (StreamSourceFL, StreamSinkFL comes from PyMTL Component class)
    # They are assigned into instance atribute belong to testharness object (s) called s.src & s.sink
    # if you use src instead of s.src, then src is only a local variable inside the method, and th=TestHarness(), then th.src will fail
    # The source automatically manages: istream_msg, istream_val, istream_rdy
    # It keeps val and msg stable when the multiplier is not ready.
    s.src  = StreamSourceFL( Bits64 )
    # The sink receives 32-bit output results. It automatically:
    # - Manages ostream_rdy
    # - Waits for ostream_val
    # - Compares each received result against the expected result
    # - Raises a test failure if the result is wrong
    # - Detects missing and extra outputs
    s.sink = StreamSinkFL( Bits32 )
    # s.imul = imul
    # │  │      │
    # │  │      └ local parameter containing the multiplier object
    # │  └ attribute name that will be added to the harness
    # └ current TestHarness object
    # Meaning: Add an attribute named imul to this test-harness object
    # and make that attribute refer to the multiplier passed by the caller
    s.imul = imul
    # In Python, “attribute” is the general term for something reached using dot notation
    # A method (function defined inside class) is a special kind of attribute that is callable
  
    # class Example:
    #   category = "example"
    #   def set_value(s, num):
    #     s.value = num

    # x = Example() # the object x does not have a "value" attribute yet, Trying to read with print(x.value) will fail
    # y = Example()
    # x.set_value(42) # Now x.value = 42
    # y.set_value(21) # Now y.value = 21
    # x.name = "first object" # Python objects generally allow attributes to be added dynamically

    # Instance attributes versus class attributes
    # "value" in the example is an instance attribute because it is defined inside class methods
    # each instance/object (x, y) of the class can have a different "value"
    # A class attribute is assigned directly in the class body (category)
    # Now "category" belongs initially to the class and is shared:
    # print(Example.category)  # example
    # print(x.category)        # example
    # print(y.category)        # example

    # Connect
    # In ordinary Python, //= means floor-division assignment. 
    # PyMTL overloads this operator to mean “connect these interfaces.”
    s.src.ostream  //= s.imul.istream
    s.imul.ostream //= s.sink.istream

  def done( s ):
    # The simulation is finished only when:
    # - The source has sent every input message.
    # - The sink has received every expected result.
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    # This combines traces from all three components: source > multiplier > sink
    return s.src.line_trace() + " > " + s.imul.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.
# concat(): pyMTL function Bit32(x): make the x 32-bit wide 
def mk_imsg( a, b ):
  return concat( Bits32( a, trunc_int=True ), Bits32( b, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.
def mk_omsg( a ):
  return Bits32( a, trunc_int=True )


#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------
# format: input, expected output
small_pos_pos_msgs = [
  mk_imsg(  2,  3 ), mk_omsg(   6 ),
  mk_imsg(  4,  5 ), mk_omsg(  20 ),
  mk_imsg(  3,  4 ), mk_omsg(  12 ),
  mk_imsg( 10, 13 ), mk_omsg( 130 ),
  mk_imsg(  8,  7 ), mk_omsg(  56 ),
]

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional lists of input/output messages to create
# additional directed and random test cases.
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

zero_one_negone_msgs = [
  mk_imsg(0, 0), mk_omsg(0),
  mk_imsg(1, 0), mk_omsg(0),
  mk_imsg(0, 1), mk_omsg(0),
  mk_imsg(1, -1), mk_omsg(-1),
  mk_imsg(-1, 0), mk_omsg(0),
  mk_imsg(0, -1), mk_omsg(0)
]

small_pos_neg_msgs = [
  mk_imsg(-2, 3), mk_omsg(-6),
  mk_imsg(2, -3), mk_omsg(-6),
  mk_imsg(-4, 15), mk_omsg(-60),
  mk_imsg(4, -15), mk_omsg(-60)
]

small_neg_neg_msgs = [
  mk_imsg(-4, -6), mk_omsg(24),
  mk_imsg(-3, -24), mk_omsg(72)
]

large_msgs = [
  mk_imsg(12345, 3456), mk_omsg(42664320),
  mk_imsg(157844, 14567), mk_omsg(2299313548),
  mk_imsg(100000, 80000), mk_omsg(8000000000),   # overflow situation
  mk_imsg(-12345, 3456), mk_omsg(-42664320),
  mk_imsg(12345, -3456), mk_omsg(-42664320),
  mk_imsg(-12345, -3456), mk_omsg(42664320),
  mk_imsg(-100000, 80000), mk_omsg(-8000000000), # overflow situation
  mk_imsg(100000, -80000), mk_omsg(-8000000000), # overflow situation
  mk_imsg(-100000, -80000), mk_omsg(8000000000)  # overflow situation
]

sparse_msgs = [
  mk_imsg(0x00000001, 0x00000100), mk_omsg(0x00000001 * 0x00000100),
  mk_imsg(0x00010001, 0x01000000), mk_omsg(0x00010001 * 0x01000000),
  mk_imsg(0x80000001, 0x00010001),  mk_omsg(0x80000001 * 0x00010001)
]

dense_msgs = [
  mk_imsg(0xffffffff, 0xffffffff), mk_omsg(0xffffffff * 0xffffffff),
  mk_imsg(0xfffffffe, 0xfffffffd), mk_omsg(0xfffffffe * 0xfffffffd),
  mk_imsg(0x7fffffff, 0x7ffffffd), mk_omsg(0x7fffffff * 0x7ffffffd),
]

low_mask = 0xffff0000
low_mask_msgs = []
for i in range(4):
  a = randint(0, 0xffffffff) & low_mask
  b = randint(0, 0xffffffff) & low_mask
  low_mask_msgs.extend([mk_imsg(a, b), mk_omsg(a * b)])

middle_mask = 0xff0000ff
middle_mask_msgs = []
for i in range(4):
  a = randint(0, 0xffffffff) & middle_mask
  b = randint(0, 0xffffffff) & middle_mask
  middle_mask_msgs.extend([mk_imsg(a, b), mk_omsg(a * b)])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

# mk_test_case_table is a function imported from PyMTL (line 10)
# Square brackets create a Python list, containing a header row and one or more test-case rows
# parentheses here do not create a tuple because there is no comma inside them, all the whitespace inside the string is later treated as separators
# equivalent to not having parentheses, python allows strings separated by spaces to be visually aligned 
test_case_table = mk_test_case_table([
  (                     "msgs                   src_delay sink_delay"),
  ["small_pos_pos",     small_pos_pos_msgs,     0,        0          ], # This is another Python list containing four elements
  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to leverage the additional lists
  # of request/response messages defined above, but also to test
  # different source/sink random delays.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  ["zero_one_negone",   zero_one_negone_msgs,   0,        0          ],
  ["small_pos_neg",     small_pos_neg_msgs,     0,        0          ],
  ["small_neg_neg",     small_neg_neg_msgs,     0,        0          ],
  ["large",             large_msgs,             0,        0          ],
  ["sparse",            sparse_msgs,            0,        0          ],
  ["dense",             dense_msgs,             0,        0          ],
  ["low_mask",          low_mask_msgs,          0,        0          ],
  ["middle_mask",       middle_mask_msgs,       0,        0          ],

  ["zero_one_negone_d", zero_one_negone_msgs,   3,        40          ],
  ["small_pos_neg_d",   small_pos_neg_msgs,     3,        40          ],
  ["small_neg_neg_d",   small_neg_neg_msgs,     3,        0          ],
  ["large_d",           large_msgs,             0,        40          ],
])

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness( IntMulFL() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['imul'] )