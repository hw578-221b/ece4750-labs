#=========================================================================
# ProcFL_lab4_test.py
#=========================================================================
# Tests for the instructions that the lab4 programs use and that lab2
# does not include. ProcAlt_lab4_test.py runs these tests on ProcAlt.

import pytest

from pymtl3 import *
from lab2_proc.test.harness import asm_test, run_test
from lab2_proc.ProcFL import ProcFL

from lab2_proc.test import inst_andi
from lab2_proc.test import inst_bge
from lab2_proc.test import inst_bgeu
from lab2_proc.test import inst_sltiu
from lab2_proc.test import inst_sltu
from lab2_proc.test import inst_srli
from lab2_proc.test import inst_xori

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcFL

  #-----------------------------------------------------------------------
  # andi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_andi.gen_basic_test     ),
    asm_test( inst_andi.gen_dest_dep_test  ),
    asm_test( inst_andi.gen_src_dep_test   ),
    asm_test( inst_andi.gen_srcs_dest_test ),
    asm_test( inst_andi.gen_value_test     ),
    asm_test( inst_andi.gen_random_test    ),
  ])
  def test_andi( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_andi_delays( s ):
    run_test( s.ProcType, inst_andi.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bge
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bge.gen_basic_test             ),
    asm_test( inst_bge.gen_src0_dep_taken_test    ),
    asm_test( inst_bge.gen_src0_dep_nottaken_test ),
    asm_test( inst_bge.gen_src1_dep_taken_test    ),
    asm_test( inst_bge.gen_src1_dep_nottaken_test ),
    asm_test( inst_bge.gen_srcs_dep_taken_test    ),
    asm_test( inst_bge.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bge.gen_src0_eq_src1_test      ),
    asm_test( inst_bge.gen_value_test             ),
    asm_test( inst_bge.gen_random_test            ),
    asm_test( inst_bge.gen_back_to_back_test      ),
  ])
  def test_bge( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_bge_delays( s ):
    run_test( s.ProcType, inst_bge.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bgeu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bgeu.gen_basic_test             ),
    asm_test( inst_bgeu.gen_src0_dep_taken_test    ),
    asm_test( inst_bgeu.gen_src0_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_src1_dep_taken_test    ),
    asm_test( inst_bgeu.gen_src1_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_srcs_dep_taken_test    ),
    asm_test( inst_bgeu.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_src0_eq_src1_test      ),
    asm_test( inst_bgeu.gen_value_test             ),
    asm_test( inst_bgeu.gen_random_test            ),
    asm_test( inst_bgeu.gen_back_to_back_test      ),
  ])
  def test_bgeu( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_bgeu_delays( s ):
    run_test( s.ProcType, inst_bgeu.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sltiu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sltiu.gen_basic_test     ),
    asm_test( inst_sltiu.gen_dest_dep_test  ),
    asm_test( inst_sltiu.gen_src_dep_test   ),
    asm_test( inst_sltiu.gen_srcs_dest_test ),
    asm_test( inst_sltiu.gen_value_test     ),
    asm_test( inst_sltiu.gen_random_test    ),
  ])
  def test_sltiu( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_sltiu_delays( s ):
    run_test( s.ProcType, inst_sltiu.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sltu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sltu.gen_basic_test     ),
    asm_test( inst_sltu.gen_dest_dep_test  ),
    asm_test( inst_sltu.gen_src0_dep_test  ),
    asm_test( inst_sltu.gen_src1_dep_test  ),
    asm_test( inst_sltu.gen_srcs_dep_test  ),
    asm_test( inst_sltu.gen_srcs_dest_test ),
    asm_test( inst_sltu.gen_value_test     ),
    asm_test( inst_sltu.gen_random_test    ),
  ])
  def test_sltu( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_sltu_delays( s ):
    run_test( s.ProcType, inst_sltu.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # srli
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srli.gen_basic_test     ),
    asm_test( inst_srli.gen_dest_dep_test  ),
    asm_test( inst_srli.gen_src_dep_test   ),
    asm_test( inst_srli.gen_srcs_dest_test ),
    asm_test( inst_srli.gen_value_test     ),
    asm_test( inst_srli.gen_random_test    ),
  ])
  def test_srli( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_srli_delays( s ):
    run_test( s.ProcType, inst_srli.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # xori
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xori.gen_basic_test     ),
    asm_test( inst_xori.gen_dest_dep_test  ),
    asm_test( inst_xori.gen_src_dep_test   ),
    asm_test( inst_xori.gen_srcs_dest_test ),
    asm_test( inst_xori.gen_value_test     ),
    asm_test( inst_xori.gen_random_test    ),
  ])
  def test_xori( s, name, test ):
    run_test( s.ProcType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_xori_delays( s ):
    run_test( s.ProcType, inst_xori.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
