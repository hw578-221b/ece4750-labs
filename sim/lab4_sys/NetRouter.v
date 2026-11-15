//========================================================================
// Network Router
//========================================================================

`ifndef LAB4_SYS_NET_ROUTER_V
`define LAB4_SYS_NET_ROUTER_V

`include "vc/net-msgs.v"
`include "vc/trace.v"
`include "vc/queues.v"

`include "lab4_sys/NetRouterRouteUnit.v"
`include "lab4_sys/NetRouterSwitchUnit.v"

module lab4_sys_NetRouter
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Router id (which router is this in the network?)

  input  logic     [1:0]         router_id,

  // Input streams

  input  logic [p_msg_nbits-1:0] istream_msg [3],
  input  logic                   istream_val [3],
  output logic                   istream_rdy [3],

  // Output streams

  output logic [p_msg_nbits-1:0] ostream_msg [3],
  output logic                   ostream_val [3],
  input  logic                   ostream_rdy [3]
);

  logic [p_msg_nbits-1:0] deq_msg[3];
  logic [2:0]             free_num[3];
  logic                   deq_val[3];

  logic                   router_istream_rdy[3];

  logic [p_msg_nbits-1:0] router0_ostream_msg[3];
  logic                   router0_ostream_val[3];
  logic                   switch0_istream_rdy[3];

  logic [p_msg_nbits-1:0] router1_ostream_msg[3];
  logic                   router1_ostream_val[3];
  logic                   switch1_istream_rdy[3];

  logic [p_msg_nbits-1:0] router2_ostream_msg[3];
  logic                   router2_ostream_val[3];
  logic                   switch2_istream_rdy[3];

  //==========================================================
  // stream 0
  //==========================================================

  vc_Queue#(`VC_QUEUE_NORMAL, p_msg_nbits, 4) queue_input0
  (
    .clk(clk),            
    .reset(reset),          
    .enq_val(istream_val[0]),        
    .enq_rdy(istream_rdy[0]),        
    .enq_msg(istream_msg[0]),        
    .deq_val(deq_val[0]),        
    .deq_rdy(router_istream_rdy[0]),        
    .deq_msg(deq_msg[0]),        
    .num_free_entries(free_num[0])
  );

  lab4_sys_NetRouterRouteUnit
  #(
    .p_msg_nbits (p_msg_nbits)
  )
  router_u0
  (
    .clk(clk),             
    .reset(reset),           
    .router_id(router_id),       
    .istream_msg(deq_msg[0]),     
    .istream_val(deq_val[0]),     
    .istream_rdy(router_istream_rdy[0]),     
    .ostream_msg(router0_ostream_msg), 
    .ostream_val(router0_ostream_val), 
    .ostream_rdy({switch0_istream_rdy[0], switch1_istream_rdy[0], switch2_istream_rdy[0]})  
  );

  lab4_sys_NetRouterSwitchUnit
  #(
    .p_msg_nbits (p_msg_nbits)
  )
  switch_u0
  (
    .clk(clk),       
    .reset(reset),     
    .istream_msg({router0_ostream_msg[0], router1_ostream_msg[0], router2_ostream_msg[0]}),
    .istream_val({router0_ostream_val[0], router1_ostream_val[0], router2_ostream_val[0]}),
    .istream_rdy(switch0_istream_rdy),
    .ostream_msg(ostream_msg[0]),
    .ostream_val(ostream_val[0]),
    .ostream_rdy(ostream_rdy[0])
  );

  //==========================================================
  // stream 1
  //==========================================================

  vc_Queue#(`VC_QUEUE_NORMAL, p_msg_nbits, 4) queue_input1
  (
    .clk(clk),            
    .reset(reset),          
    .enq_val(istream_val[1]),        
    .enq_rdy(istream_rdy[1]),        
    .enq_msg(istream_msg[1]),        
    .deq_val(deq_val[1]),        
    .deq_rdy(router_istream_rdy[1]),        
    .deq_msg(deq_msg[1]),        
    .num_free_entries(free_num[1])
  );

  lab4_sys_NetRouterRouteUnit
  #(
    .p_msg_nbits (p_msg_nbits)
  )
  router_u1
  (
    .clk(clk),             
    .reset(reset),           
    .router_id(router_id),       
    .istream_msg(deq_msg[1]),     
    .istream_val(deq_val[1]),     
    .istream_rdy(router_istream_rdy[1]),     
    .ostream_msg(router1_ostream_msg), 
    .ostream_val(router1_ostream_val), 
    .ostream_rdy({switch0_istream_rdy[1], switch1_istream_rdy[1], switch2_istream_rdy[1]})  
  );

  lab4_sys_NetRouterSwitchUnit
  #(
    .p_msg_nbits (p_msg_nbits)
  )
  switch_u1
  (
    .clk(clk),       
    .reset(reset),     
    .istream_msg({router0_ostream_msg[1], router1_ostream_msg[1], router2_ostream_msg[1]}),
    .istream_val({router0_ostream_val[1], router1_ostream_val[1], router2_ostream_val[1]}),
    .istream_rdy(switch1_istream_rdy),
    .ostream_msg(ostream_msg[1]),
    .ostream_val(ostream_val[1]),
    .ostream_rdy(ostream_rdy[1])
  );

  //==========================================================
  // stream 2
  //==========================================================

  vc_Queue#(`VC_QUEUE_NORMAL, p_msg_nbits, 4) queue_input2
  (
    .clk(clk),            
    .reset(reset),          
    .enq_val(istream_val[2]),        
    .enq_rdy(istream_rdy[2]),        
    .enq_msg(istream_msg[2]),        
    .deq_val(deq_val[2]),        
    .deq_rdy(router_istream_rdy[2]),        
    .deq_msg(deq_msg[2]),        
    .num_free_entries(free_num[2])
  );

  lab4_sys_NetRouterRouteUnit
  #(
    .p_msg_nbits (p_msg_nbits)
  )
  router_u2
  (
    .clk(clk),             
    .reset(reset),           
    .router_id(router_id),       
    .istream_msg(deq_msg[2]),     
    .istream_val(deq_val[2]),     
    .istream_rdy(router_istream_rdy[2]),     
    .ostream_msg(router2_ostream_msg), 
    .ostream_val(router2_ostream_val), 
    .ostream_rdy({switch0_istream_rdy[2], switch1_istream_rdy[2], switch2_istream_rdy[2]})  
  );

  lab4_sys_NetRouterSwitchUnit
  #(
    .p_msg_nbits (p_msg_nbits)
  )
  switch_u2
  (
    .clk(clk),       
    .reset(reset),     
    .istream_msg({router0_ostream_msg[2], router1_ostream_msg[2], router2_ostream_msg[2]}),
    .istream_val({router0_ostream_val[2], router1_ostream_val[2], router2_ostream_val[2]}),
    .istream_rdy(switch2_istream_rdy),
    .ostream_msg(ostream_msg[2]),
    .ostream_val(ostream_val[2]),
    .ostream_rdy(ostream_rdy[2])
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  vc_NetMsgTrace#(p_msg_nbits) ostream0_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[0]),
    .val   (ostream_val[0]),
    .rdy   (ostream_rdy[0])
  );

  vc_NetMsgTrace#(p_msg_nbits) ostream1_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[1]),
    .val   (ostream_val[1]),
    .rdy   (ostream_rdy[1])
  );

  vc_NetMsgTrace#(p_msg_nbits) ostream2_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[2]),
    .val   (ostream_val[2]),
    .rdy   (ostream_rdy[2])
  );

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    // Line tracing for input queues

    case ( free_num[0] )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    case ( free_num[1] )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    case ( free_num[2] )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    vc_trace.append_str( trace_str, "|" );

    // Line tracing for switch units

    switch_u0.line_trace( trace_str );
    switch_u1.line_trace( trace_str );
    switch_u2.line_trace( trace_str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* NET_ROUTER_V */
