`timescale 1ns/1ps

`define RED    "\033[31m"
`define GREEN  "\033[32m"
`define YELLOW "\033[33m"
`define RESET  "\033[0m"

// assume DUT operates under posedge clk
module TestLib (
  input  logic rst_type, // 0: active low rst, 1: active high rst
  output logic clk,
  output logic rst 
);

logic passed, failed;
int num_checks, num_test_case_passed, num_test_case_failed;

int cycles, seed;
int all_cases, case_num;
string vcd_name;

// ------------------------------------------------------------
// clock generator
// ------------------------------------------------------------
initial begin
  clk = 1'b0;
  always #5 clk = ~clk;
end

// ------------------------------------------------------------
// Global cycle counter
// ------------------------------------------------------------
always @(posedge clk) begin
  if(rst_type == 1'd0) begin
    if(!rst)
      cycles <= 0;
    else
      cycles <= cycles + 1;
  end
  else begin
    if(rst)
      cycles <= 0;
    else
      cycles <= cycles + 1;
  end
end

//----------------------------------------------------------------------
// CLI argument parsing
//----------------------------------------------------------------------
initial begin
  all_cases = 0;
  case_num = -1;

  if(!$value$plusargs("test-case=%d", case_num))
    all_cases = 1;

  if($value$plusargs("vcd-name=%s", vcd_name)) begin
    $dumpfile(vcd_name);
    $dumpvars();
  end
end

// ------------------------------------------------------------
// active low reset helper
// ------------------------------------------------------------
task reset_dut_n()
  // reset DUT
  rst = 1'd0;
  repeat (3) @(posedge clk);

  // release rst_n at negedge to aviod conflict with DUT logic
  @(negedge clk)
  rst = 1'd1;
endtask

// ------------------------------------------------------------
// active high reset helper
// ------------------------------------------------------------
task reset_dut_p()
  // reset DUT
  rst = 1'd1;
  repeat (3) @(posedge clk);

  // release rst_n at negedge to aviod conflict with DUT logic
  @(negedge clk)
  rst = 1'd0;
endtask

//----------------------------------------------------------------------
// test_bench_begin
//----------------------------------------------------------------------
task test_bench_begin();
  $display("");
  num_test_case_passed = 0;
  num_test_case_failed = 0;
  #1; // keep test activity away from clock-edge scheduling to avoid data racing
endtask

//----------------------------------------------------------------------
// test_case_begin
//----------------------------------------------------------------------
task test_case_begin(
  input string case_name;
);

  $write("%-40s", case_name);

  if(!all_cases)
    $write("");

  passed = 1'd0;
  failed = 1'd0;
  num_checks = 0;
  seed = 32'hdeadbeef;
  
  if(rst_type == 1'd0)
    reset_dut_n();
  else
    reset_dut_p();
endtask

//----------------------------------------------------------------------
// test_case_end
//----------------------------------------------------------------------
task test_case_end();

  if(!failed && passed)
    num_test_case_passed += 1;
  else
    num_test_case_failed += 1;
  
  // print brief results when testing all cases
  if(all_cases) begin
    if(!failed && passed)
      $write(`GREEN, "passed", `RESET);
    else
      $write(`RED, "failed", `RESET);
    
    $write(" (%0d checked)\n", num_checks);
  end

endtask

//----------------------------------------------------------------------
// test_bench_end
//----------------------------------------------------------------------
task test_bench_end();
  $display("");
  
  if(all_cases) begin
    $display("num_test_case_passed = %0d", num_test_case_passed);
    $display("num_test_case_failed = %0d", num_test_case_failed);
  end
  else begin
    $write("\n");
    if(!failed && passed)
      $write(`GREEN, "passed", `RESET);
    else
      $write(`RED, "failed", `RESET);
    $write(" (%0d checked)\n", num_checks);
  end

endtask

endmodule

// "display" is a string type variable
// We use the !== operator so that Xs must also match exactly (support unknown-propagation tests)
// The trailing if (1) allows the usual semicolon after the macro invocation to serve as an empty statement
`define CHECK_EQUAL(inst_name, actual, expected, display)                             \
  if(actual !== expected) begin                                                       \
    inst_name.failed = 1;                                                             \
    if(!inst_name.all_cases) begin                                                    \
      if(display == "b")                                                              \
        $display(`RED, "Error: ", `RESET, "In cycle: %0d, actual: %b, expected: %b",  \
        inst_name.cycles, actual, expected);                                          \
      else if(display == "h")                                                         \
        $display(`RED, "Error: ", `RESET, "In cycle: %0d, actual: %h, expected: %h",  \
        inst_name.cycles, actual, expected);                                          \
      else if(display == "s")                                                         \
        $display(`RED, "Error: ", `RESET, "In cycle: %0d, actual: %s, expected: %s",  \
        inst_name.cycles, actual, expected);                                          \
    end                                                                               \
  end                                                                                 \
  else begin                                                                          \
    inst_name.passed = 1;                                                             \
  end                                                                                 \
  if (1)                                                                              \