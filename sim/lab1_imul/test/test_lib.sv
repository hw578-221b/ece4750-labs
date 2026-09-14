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

int cycles;
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
  input  string case_name;
);

endtask

//----------------------------------------------------------------------
// test_bench_end
//----------------------------------------------------------------------
task test_bench_end();
  $display("");
  
  
endtask

endmodule