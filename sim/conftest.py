#=========================================================================
# conftest
#=========================================================================

import pytest
import random

def pytest_addoption(parser):

  parser.addoption( "--dump-asm", action="store_true",
                    help="dump asm file for each test" )

  parser.addoption( "--dump-bin", action="store_true",
                    help="dump binary file for each test" )

  parser.addoption("--commit", action="store_true",
                  help="show retirement monitor output")

@pytest.fixture(autouse=True)
def fix_randseed():
  """Set the random seed prior to each test case."""
  random.seed(0xdeadbeef)

@pytest.fixture()
def dump_asm(request):
  """Dump Assembly File for each test."""
  return request.config.getoption("--dump-asm")

# This fixture runs automatically before each test
@pytest.fixture(autouse=True)
def configure_commit_log(request, monkeypatch):
  # ProcBase reads this when constructing its Verilog placeholder.
  monkeypatch.setenv("ECE4750_COMMIT_LOG",
                     "1" if request.config.getoption("--commit") else "0")

# Report hook, retrieve commit message output while keeping other output captured
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
  outcome = yield
  report = outcome.get_result()
  if report.when == "call" and item.config.getoption("--commit"):
    # Keep normal output captured; show only retirement lines, even on pass.
    lines = [line for line in report.capstdout.splitlines()
             if line.startswith("[Commit ")]
    terminal = item.config.pluginmanager.getplugin("terminalreporter")
    if lines and terminal is not None:
      terminal.write_line("")
      terminal.write_line("Commit log: " + item.nodeid)
      for line in lines:
        terminal.write_line(line)
