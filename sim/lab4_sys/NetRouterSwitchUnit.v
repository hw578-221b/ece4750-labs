//========================================================================
// Network Router Switch Unit
//========================================================================

`ifndef LAB4_SYS_NET_ROUTER_SWITCH_UNIT_V
`define LAB4_SYS_NET_ROUTER_SWITCH_UNIT_V

`include "vc/net-msgs.v"
`include "vc/trace.v"

module lab4_sys_NetRouterSwitchUnit
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Input streams

  input  logic [p_msg_nbits-1:0] istream_msg [3],
  input  logic                   istream_val [3],
  output logic                   istream_rdy [3],

  // Output stream

  output logic [p_msg_nbits-1:0] ostream_msg,
  output logic                   ostream_val,
  input  logic                   ostream_rdy
);

  // Arbitration with round robin mechanism
  // Assume istream_msg and istream_val remain unchanged when ostream_rdy = 0

  /* verilator lint_off MULTIDRIVEN */
  function automatic void assign_istream
  (
    input logic [1:0] idx
  );

    ostream_msg = istream_msg[idx];
    ostream_val = istream_val[idx];

  endfunction
  /* verilator lint_off MULTIDRIVEN */

  logic [1:0] rr_ptr, winner;

  // winner selection logic
  always_comb begin
    case(rr_ptr)
      2'd0: begin
        if(istream_val[0])      winner = 2'd1;
        else if(istream_val[1]) winner = 2'd2;
        else if(istream_val[2]) winner = 2'd3;
        else                    winner = 2'd0;
      end
      2'd1: begin
        if(istream_val[1])      winner = 2'd2;
        else if(istream_val[2]) winner = 2'd3;
        else if(istream_val[0]) winner = 2'd1;
        else                    winner = 2'd0;
      end
      2'd2: begin
        if(istream_val[2])      winner = 2'd3;
        else if(istream_val[0]) winner = 2'd1;
        else if(istream_val[1]) winner = 2'd2;
        else                    winner = 2'd0;
      end
      default: winner = 2'd0; // 0 means no winner/ no valid input/ arbiter idle
    endcase
  end

  // istream_rdy depend on istream_val (winner) here in arbiter, otherwise if just broacast ostream_rdy
  // then upstream queue can pop up message even when it's not selected by arbiter when ostream_rdy = 1
  //===============================================================================================
  // ********************Rule: Only the winning input should receive ready*************************
  //===============================================================================================
  assign istream_rdy[0] = ostream_rdy && (winner == 2'd1);
  assign istream_rdy[1] = ostream_rdy && (winner == 2'd2);
  assign istream_rdy[2] = ostream_rdy && (winner == 2'd3);

  // output redirect logic
  always_comb begin
    if(winner != 2'd0)
      assign_istream(winner - 2'd1); // if there is winner, direct the output to that winner port
    else begin
      /* verilator lint_off MULTIDRIVEN */
      ostream_msg = '0;
      ostream_val = '0; // no valid output when no winner
      /* verilator lint_off MULTIDRIVEN */
    end
  end

  // rr_ptr update logic
  always_ff @(posedge clk) begin
    if(reset) begin
      rr_ptr <= 2'd0;
    end
    else begin
      // if current highest prority port (winner) is served (ostream val + rdy)
      if(ostream_val && ostream_rdy)
        // update the rr_ptr according to the winner!!!
        rr_ptr <= ((winner - 2'd1) + 2'd1) % 2'd3;
    end
  end

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  integer num_reqs = 0;

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    num_reqs = istream_val[0] + istream_val[1] + istream_val[2];

    case ( num_reqs )
      0: vc_trace.append_str( trace_str, " " );
      1: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      3: vc_trace.append_str( trace_str, "#" );
    endcase

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* NET_ROUTER_SWITCH_UNIT_V */
