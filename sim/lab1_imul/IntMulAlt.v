//=======================================================================
// Integer Multiplier Variable-Latency Implementation
//=======================================================================
`ifndef LAB1_IMUL_INT_MUL_ALT_V
`define LAB1_IMUL_INT_MUL_ALT_V

`include "vc/trace.v"
`include "vc/regs.v"
`include "vc/counters.v"
`include "vc/arithmetic.v"
`include "vc/muxes.v"

// ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Define datapath and control unit here.
//'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
module TrailingZeroCounter32 (
  input logic [31:0] in,
  output logic [4:0] count,
  output logic all_zero
);

  integer i;

  always_comb begin
    // Default: assume all zeros; change to false when a 1 is found.
    // when all bits are 0, all_zero = 1, count = 0
    count = 5'd0;
    all_zero = 1'd1;
    // priority encoder logic !!!
    for ( i = 0; i < 32; i = i + 1 ) begin
      if ( all_zero && in[i] ) begin
        count = i;
        all_zero = 1'b0;
      end
    end
  end

endmodule

module dpath (
  input logic [63:0] istream_msg,
  input logic b_mux_sel, // 1 when reset/idle
  input logic a_mux_sel, // 1 when reset/idle
  input logic result_mux_sel, // 1 when reset/idle
  input logic reset,
  input logic clk,
  output logic [31:0] ostream_msg,
  output logic all_zero
);

  localparam result_en = 1;

  logic [31:0] a, b, b_mux_out, a_mux_out;
  logic [31:0] b_reg_q, a_reg_q, b_shift_out, a_shift_out,
               result_mux_out, result_reg_q, adder_out,
               add_mux_out;
  logic b_lsb, overflow_flag;
  logic [4:0] count;
  logic [5:0] shift_num;

  // Don't use logic a = istream[31:0] For a logic variable, this is
  // initialization, not a continuously updated connection. It may only
  // evaluate once at time zero.
  assign a = istream_msg[63:32];
  assign b = istream_msg[31:0];

  TrailingZeroCounter32 trailing_zero_counter
  (
    .in       (b_reg_q),
    .count    (count),
    .all_zero (all_zero)
  );

  assign shift_num = (count == 5'd0) ? 5'd1 : count;

  vc_Mux2
  #(
    .p_nbits (32)
  )
  b_mux
  (
    .in0 (b_shift_out),
    .in1 (b),
    .sel (b_mux_sel),
    .out (b_mux_out)
  );

  vc_Mux2
  #(
    .p_nbits (32)
  )
  a_mux
  (
    .in0 (a_shift_out),
    .in1 (a),
    .sel (a_mux_sel),
    .out (a_mux_out)
  );

  vc_Reg
  #(
    .p_nbits (32)
  )
  b_reg
  (
    .clk (clk),
    .d   (b_mux_out),
    .q   (b_reg_q)
  );

  vc_Reg
  #(
    .p_nbits (32)
  )
  a_reg
  (
    .clk (clk),
    .d   (a_mux_out),
    .q   (a_reg_q)
  );

  assign b_lsb = b_reg_q[0];

  vc_RightLogicalShifter
  #(
    .p_nbits       (32),
    .p_shamt_nbits (6)
  )
  b_shift
  (
    .in    (b_reg_q),
    .shamt (shift_num),
    .out   (b_shift_out)
  );

  vc_LeftLogicalShifter
  #(
    .p_nbits       (32),
    .p_shamt_nbits (6)
  )
  a_shift
  (
    .in    (a_reg_q),
    .shamt (shift_num),
    .out   (a_shift_out)
  );

  vc_Mux2
  #(
    .p_nbits (32)
  )
  result_mux
  (
    .in0 (add_mux_out),
    .in1 (0),
    .sel (result_mux_sel),
    .out (result_mux_out)
  );

  vc_EnReg
  #(
    .p_nbits (32)
  )
  result_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (result_mux_out),
    .q     (result_reg_q),
    .en    (result_en)
  );

  vc_Adder
  #(
    .p_nbits (32)
  )
  adder
  (
    .in0  (a_reg_q),
    .in1  (result_reg_q),
    .cin  (0),
    .out  (adder_out),
    .cout (overflow_flag)
  );
  
  // When b_lbs is 0, just shift, no add (in0), if b_lsb is 1, perform add (in1)
  vc_Mux2
  #(
    .p_nbits (32)
  )
  add_mux
  (
    .in0 (result_reg_q),
    .in1 (adder_out),
    .sel (b_lsb),
    .out (add_mux_out)
  );

  assign ostream_msg = result_reg_q;

endmodule


module FSMctl (
  input logic all_zero,
  input logic istream_val,
  input logic ostream_rdy,
  input logic clk,
  input logic rst_p,
  output logic b_mux_sel,
  output logic a_mux_sel,
  output logic result_mux_sel,
  output logic istream_rdy,
  output logic ostream_val
);

  localparam [1:0] IDLE = 2'b00,
                  CALC = 2'b01,
                  DONE = 2'b10;

  logic [1:0] state, next_state;

  // present state logic
  always_ff @(posedge clk) begin
    if ( rst_p )
      state <= IDLE;
    else
      state <= next_state;
  end

  // next state logic
  always_comb begin
    next_state = state;
    case ( state )
      IDLE: begin
        if ( istream_val && istream_rdy )
          next_state = CALC;
      end
      CALC: begin
        if ( all_zero )
          next_state = DONE;
      end
      DONE: begin
        if ( ostream_val && ostream_rdy )
          next_state = IDLE;
      end
      default: begin
        next_state = IDLE;
      end
    endcase
  end

  // FSM output logic (combinational, for control signals)
  always_comb begin
    // default
    b_mux_sel = 1;
    a_mux_sel = 1;
    result_mux_sel = 1;
    istream_rdy = 0;
    ostream_val = 0;

    case ( state )
      IDLE: begin
        istream_rdy = 1;
      end
      CALC: begin
        istream_rdy = 0;
        b_mux_sel = 0;
        a_mux_sel = 0;
        result_mux_sel = 0;
      end
      DONE: begin
        ostream_val = 1;
      end
      default: begin
        istream_rdy = 0;
        ostream_val = 0;
      end
    endcase

  end

endmodule


//=======================================================================
// Integer Multiplier Variable-Latency Implementation
//=======================================================================
module lab1_imul_IntMulAlt
(
  input  logic        clk,
  input  logic        reset,

  input  logic        istream_val,
  output logic        istream_rdy,
  input  logic [63:0] istream_msg,

  output logic        ostream_val,
  input  logic        ostream_rdy,
  output logic [31:0] ostream_msg
);

  logic b_mux_sel_t, a_mux_sel_t, result_mux_sel_t, b_all_zero;

  FSMctl control
  (
    .all_zero       (b_all_zero),
    .istream_val    (istream_val),
    .ostream_rdy    (ostream_rdy),
    .clk            (clk),
    .rst_p          (reset),
    .b_mux_sel      (b_mux_sel_t),
    .a_mux_sel      (a_mux_sel_t),
    .result_mux_sel (result_mux_sel_t),
    .istream_rdy    (istream_rdy),
    .ostream_val    (ostream_val)
  );

  dpath datapath
  (
    .istream_msg    (istream_msg),
    .b_mux_sel      (b_mux_sel_t),
    .a_mux_sel      (a_mux_sel_t),
    .result_mux_sel (result_mux_sel_t),
    .clk            (clk),
    .reset          (reset),
    .ostream_msg    (ostream_msg),
    .all_zero       (b_all_zero)
  );

  //---------------------------------------------------------------------
  // Line Tracing
  //---------------------------------------------------------------------
  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", istream_msg );
    vc_trace.append_val_rdy_str(
      trace_str, istream_val, istream_rdy, str
    );

    vc_trace.append_str( trace_str, "(" );

    case ( control.state )
      2'b00: begin
        vc_trace.append_str(trace_str, "I ");
      end
      2'b01: begin
        $sformat(str, "C ");
        vc_trace.append_str(trace_str, str);
      end
      2'b10: begin
        vc_trace.append_str(trace_str, "D ");
      end
      default: begin
        vc_trace.append_str(trace_str, "? ");
      end
    endcase

    $sformat(
      str, "a=%d b=%d out=%d",
      datapath.a_reg_q, datapath.b_reg_q, datapath.result_reg_q
    );
    vc_trace.append_str(trace_str, str);

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", ostream_msg );
    vc_trace.append_val_rdy_str(
      trace_str, ostream_val, ostream_rdy, str
    );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_ALT_V */
