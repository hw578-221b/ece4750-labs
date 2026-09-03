#=========================================================================
# IntMulBase_test
#=========================================================================

# The old ad-hoc script was executed directly with Python and did not use pytest
# Pytest is the testing framework. It:
# - Discovers functions whose names begin with test
# - Runs each test
# - Reports pass/failure results
# - Supplies fixtures such as cmdline_opts
# - Supports parameterized tests
import pytest

# run_sim is a PyMTL test utility that performs most of the simulation setup automatically.
from pymtl3.stdlib.test_utils import run_sim

from lab1_imul.test.IntMulFL_test import TestHarness, test_case_table

# This imports the PyMTL Verilog-placeholder wrapper
from lab1_imul.IntMulBase import IntMulBase

# A decorator @ modifies the function behavior immediately below it. Here, it's equivalent to:
# def test(test_params, cmdline_opts):
#   ...
# decorator = pytest.mark.parametrize(**test_case_table) # creates/configures an object named decorator
# test = decorator(test) # pass test into decorator and save the returned result in test

# pytest.mark.parametrize(...) creates a decorator configured with a list of test parameters.
# It tells pytest: Run this test function once for every row in test_case_table
# ** is dictionary unpacking, test_case_table is a dictionary produced by mk_test_case_table()
# This differs from a single *, which unpacks a list or tuple into positional arguments
@pytest.mark.parametrize( **test_case_table )
# Pytest recognizes this function because its name is test.
# You do not call it directly. Pytest calls it and supplies both arguments.
# test_params comes from the parameterization table. It has fields:
# test_params.msgs, test_params.src_delay, test_params.sink_delay
# For the current row: msgs = small_pos_pos_msgs, src_delay = 0, sink_delay = 0
# cmdline_opts is a pytest fixtureIt contains command-line simulation options such as:
# --dump-vcd, --dump-textwave, --max-cycles, --test-verilog
def test( test_params, cmdline_opts ):

  # IntMulBase() creates the multiplier wrapper (One multiplier object)
  # TestHarness(...) take that object (multiplier) as parameter and put it into construct()'s imul parameter
  # Work approximately like:
  # multiplier = IntMulBase()
  # th = TestHarness()
  # th._saved_construct_args = [multiplier] # this will be passed to construct's imul later during elaborate()
  # Python automatically supplies th as s
  th = TestHarness( IntMulBase() )
  # Set & save source/sink construction parameters
  # This string supplies arguments that PyMTL will use when it later calls the source’s construct method.
  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2], # going through all the input
    initial_delay=test_params.src_delay+3, # This delays the source before sending its first message
    interval_delay=test_params.src_delay ) # This inserts a delay between successive input messages

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  # duts=['imul']: identifies th.imul as the design under test
  run_sim( th, cmdline_opts, duts=['imul'] )

