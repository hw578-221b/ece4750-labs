//========================================================================
// Network Router Route Unit
//========================================================================

`ifndef LAB4_SYS_NET_ROUTER_ROUTE_UNIT_V
`define LAB4_SYS_NET_ROUTER_ROUTE_UNIT_V

`include "vc/net-msgs.v"
`include "vc/trace.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab4_sys_NetRouterRouteUnit
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Router id (which router is this in the network?)

  input  logic [1:0]             router_id,

  // Input stream

  input  logic [p_msg_nbits-1:0] istream_msg,
  input  logic                   istream_val,
  output logic                   istream_rdy,

  // Output streams

  output logic [p_msg_nbits-1:0] ostream_msg [3],
  output logic                   ostream_val [3],
  input  logic                   ostream_rdy [3]
);

  net_msg_hdr_t istream_msg_hdr;
  assign istream_msg_hdr = istream_msg[`VC_NET_MSGS_HDR(p_msg_nbits)];

  /* verilator lint_off MULTIDRIVEN */

  // The standard excludes a task's internal reads from always_comb sensitivity. 
  // For example, if the destination stays the same but the selected output becomes ready, 
  // the always_comb block might not rerun to update istream_rdy, in simulation.
  // A function's internal reads are included, so function void solves this.

  // automatic is a useful convention for a combinational helper.
  function automatic void assign_ostream
  (
    input logic [1:0] idx
  );
    ostream_msg[idx] = istream_msg;
    ostream_val[idx] = istream_val;
    istream_rdy = ostream_rdy[idx];
  endfunction

  logic [1:0] target_id;
  assign target_id = istream_msg_hdr.dest;
  
  // rounting based on the shortest path to the desired output router
  always_comb begin
    // default
    ostream_msg = '{default: '0};
    ostream_val = '{default: '0};
    istream_rdy = 1'b0;

    if(target_id > router_id) begin
      if(target_id - router_id <= 2'd2) assign_ostream(1);
      else assign_ostream(2);
    end
    else if(target_id < router_id) begin
      if( router_id - target_id <= 2'd2) assign_ostream(2);
      else assign_ostream(1);
    end
    else
      assign_ostream(0);
  end

  /* verilator lint_off MULTIDRIVEN */

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    if ( istream_val && istream_rdy ) begin
      $sformat( str, "%d", istream_msg_hdr.dest );
      vc_trace.append_str( trace_str, str );
    end
    else
      vc_trace.append_str( trace_str, " " );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* NET_ROUTER_ROUTE_UNIT_V */
