//=======================================================================
// Integer Multiplier Fixed-Latency Implementation
//=======================================================================
`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/trace.v"
`include "vc/regs.v"
`include "vc/counters.v"
`include "vc/arithmetic.v"
`include "vc/muxes.v"

module dpath (
  input logic [63:0] istream_msg,
  input logic b_mux_sel, // 1 when reset/idle
  input logic a_mux_sel, // 1 when reset/idle
  input logic result_en, // 0 when in DONE state, 1 when in CALC and IDLE state
  input logic result_mux_sel, // 1 when reset/idle
  input logic reset,
  input logic clk,
  output logic [31:0] ostream_msg
);

  logic [31:0] a, b, b_mux_out, a_mux_out;
  logic [31:0] b_reg_q, a_reg_q, b_shift_out, a_shift_out,
               result_mux_out, result_reg_q, adder_out,
               add_mux_out;

  logic b_lsb, overflow_flag;

  // Don't use logic a = istream[31:0] For a logic variable, this is
  // initialization, not a continuously updated connection. It may only
  // evaluate once at time zero.
  assign a = istream_msg[63:32];
  assign b = istream_msg[31:0];

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
    .p_nbits (32)
  )
  b_shift
  (
    .in    (b_reg_q),
    .shamt (1),
    .out   (b_shift_out)
  );

  vc_LeftLogicalShifter
  #(
    .p_nbits (32)
  )
  a_shift
  (
    .in    (a_reg_q),
    .shamt (1),
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
  input logic istream_val,
  input logic ostream_rdy,
  input logic clk,
  input logic rst_p,
  output logic b_mux_sel,
  output logic a_mux_sel,
  output logic result_mux_sel,
  output logic result_en,
  output logic istream_rdy,
  output logic ostream_val
);

  localparam [1:0] IDLE = 2'b00,
                  CALC = 2'b01,
                  DONE = 2'b10;

  logic [1:0] state, next_state;
  logic [4:0] counter;

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
        if ( &counter ) // counter == 31
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
    result_en = 1;
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
        // will be 0 only during the first cycle of done! then go to 1 (default) afterwards
        // can't hold data if consumer is not ready! consider give result_en a real enable that deasserted in DONE
        result_mux_sel = 0;
      end
      DONE: begin
        ostream_val = 1;
        result_en = 0; // need to disable reg so that it can keep the current result until consumer accept it (switch to IDLE)
      end
      default: begin
        istream_rdy = 0;
        ostream_val = 0;
      end
    endcase
  end

  // FSM output logic (sequential, for counter register)
  always_ff @(posedge clk) begin
    if ( rst_p )
      counter <= 5'd0;
    else if ( state == IDLE )
      counter <= 5'd0;
    else if ( state == CALC )
      counter <= counter + 5'd1;
    else
      counter <= 5'd0;
  end

endmodule


//=======================================================================
// Integer Multiplier Fixed-Latency Implementation
//=======================================================================
module lab1_imul_IntMulBase
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

  logic b_mux_sel_t, a_mux_sel_t, result_mux_sel_t, result_en_t;

  FSMctl control
  (
    .istream_val    (istream_val),
    .ostream_rdy    (ostream_rdy),
    .clk            (clk),
    .rst_p          (reset),
    .b_mux_sel      (b_mux_sel_t),
    .a_mux_sel      (a_mux_sel_t),
    .result_mux_sel (result_mux_sel_t),
    .result_en      (result_en_t),
    .istream_rdy    (istream_rdy),
    .ostream_val    (ostream_val)
  );

  dpath datapath
  (
    .istream_msg    (istream_msg),
    .b_mux_sel      (b_mux_sel_t),
    .a_mux_sel      (a_mux_sel_t),
    .result_mux_sel (result_mux_sel_t),
    .result_en      (result_en_t),
    .clk            (clk),
    .reset          (reset),
    .ostream_msg    (ostream_msg)
  );

  //---------------------------------------------------------------------
  // Line Tracing
  //---------------------------------------------------------------------
  // Compile the following code only if the macro SYNTHESIS is not defined.
  // During hardware synthesis, the tool normally defines SYNTHESIS, so this block is removed.
  // During simulation, SYNTHESIS is normally not defined, so tracing is included
  // SYNTHESIS is not a Verilog signal. It is a compile-time macro.
  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    // Syntax: $sformat(destination, format_string, values...); %x means hexadecimal
    // $sformat does not print anything. It creates a formatted string
    // This differs from $display, which prints immediately
    $sformat( str, "%x", istream_msg );
    // Append the input according to valid/ready
    // trace_str    complete trace buffer to modify
    // istream_val  whether the input message is valid
    // istream_rdy  whether the multiplier is ready
    // str          formatted input-message text
    // The helper chooses what to append (messge text in
    // str/spaces/#/./x) based on the handshake signals
    vc_trace.append_val_rdy_str(
      trace_str, istream_val, istream_rdy, str
    );

    // This appends a literal opening parenthesis to the full trace
    // Syntax: append_str(destination_trace, string_to_append)
    vc_trace.append_str( trace_str, "(" );

    case ( control.state )
      2'b00: begin
        vc_trace.append_str(trace_str, "I ");
      end
      2'b01: begin
        $sformat(str, "C%02d ", control.counter);
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

`endif /* LAB1_IMUL_INT_MUL_BASE_V */


// Don't use registered ouput for control signals such as istream_rdy, ostream_val, and the mux selects
// If that's the case, the datapath samples the previous cycle’s mux
// selections, initialization and calculation become offset by a cycle
// always_ff @(posedge clk) begin
//   if(rst_p || state == IDLE) begin
//     counter <= 5'd0;
//     istream_rdy <= 1;
//     ostream_val <= 0;
//     b_mux_sel <= 1;
//     a_mux_sel <= 1;
//     result_mux_sel <= 1;
//   end
//   else begin
//     b_mux_sel <= 0;
//     a_mux_sel <= 0;
//     result_mux_sel <= 0;

//     case ( state )
//       CALC: begin
//         istream_rdy <= 0;
//         counter <= counter + 5'd1;
//       end
//       DONE: begin
//         ostream_val <= 1;
//       end
//     endcase
//   end
// end
