//=========================================================================
// Base Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_CACHE_BASE_CTRL_V
`define LAB3_MEM_CACHE_BASE_CTRL_V

`include "vc/mem-msgs.v"
`include "vc/regfiles.v"

module lab3_mem_CacheBaseCtrl
#(
  parameter p_num_banks = 1
)
(
  input  logic        clk,
  input  logic        reset,

  // Processor <-> Cache Interface

  input  logic        proc2cache_reqstream_val,
  output logic        proc2cache_reqstream_rdy,

  output logic        proc2cache_respstream_val,
  input  logic        proc2cache_respstream_rdy,

  // Cache <-> Memory Interface

  output logic        cache2mem_reqstream_val,
  input  logic        cache2mem_reqstream_rdy,

  input  logic        cache2mem_respstream_val,
  output logic        cache2mem_respstream_rdy,

  // cache request stream
  input  logic [3:0]  cachereq_type,
  input  logic [31:0] cachereq_addr,
  output logic        cache_req_en,
  output logic        wben_mux_sel,

  // memeory response stream
  output logic        memresp_en,
  output logic        write_data_mux_sel,

  // SRAM control regs
  output logic        tag_array_ren,
  output logic        tag_array_wen,
  output logic        data_array_ren,
  output logic        data_array_wen,

  // memory request stream
  input  logic        tag_match,
  output logic        evict_addr_reg_en,
  output logic        memreq_addr_mux_sel,
  output logic [3:0]  memreq_type,

  // cache response stream
  output logic        read_data_zero_mux_sel,
  output logic        read_data_reg_en,
  output logic        hit,
  output logic [3:0]  cacheresp_type
);

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE              = 5'd0;
  localparam STATE_TAG_CHECK         = 5'd1;
  localparam STATE_INIT_DATA_ACCESS  = 5'd2;
  localparam STATE_READ_DATA_ACCESS  = 5'd3;
  localparam STATE_WRITE_DATA_ACCESS = 5'd4;
  localparam STATE_REFILL_REQUEST    = 5'd5;
  localparam STATE_REFILL_WAIT       = 5'd6;
  localparam STATE_REFILL_UPDATE     = 5'd7;
  localparam STATE_EVICT_PREPARE     = 5'd8;
  localparam STATE_EVICT_REQUEST     = 5'd9;
  localparam STATE_EVICT_WAIT        = 5'd10;
  localparam STATE_WAIT              = 5'd11;

  //----------------------------------------------------------------------
  // valid & dirty bits implementation
  //----------------------------------------------------------------------
  logic [3:0] word_offset, index;
  logic [23:0] tag;

  assign word_offset = cachereq_addr[3:0];

  generate
    if (p_num_banks == 1) begin
      assign index = cachereq_addr[7:4];
      assign tag = cachereq_addr[31:8];
    end
    else if (p_num_banks == 4) begin // address mapping for four banks
      assign index = cachereq_addr[9:6];
      assign tag = {cachereq_addr[31:10], 2'b00};
    end
  endgenerate

  logic valid_bit_in, dirty_bit_in;
  logic valid_bits_write_en, dirty_bits_write_en;
  logic is_valid, is_dirty;

  vc_ResetRegfile_1r1w#(1,16) valid_bits
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_valid),
    .write_en   (valid_bits_write_en),
    .write_addr (index),
    .write_data (valid_bit_in)
  );

  vc_ResetRegfile_1r1w#(1,16) dirty_bits
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_dirty),
    .write_en   (dirty_bits_write_en),
    .write_addr (index),
    .write_data (dirty_bit_in)
  );

  //----------------------------------------------------------------------
  // reset and present state logic
  //----------------------------------------------------------------------
  logic [4:0] state, next_state;

  always_ff @(posedge clk) begin
    if(reset) begin
      state <= STATE_IDLE;
    end
    else
      state <= next_state;
  end

  //----------------------------------------------------------------------
  // state transition logic
  //----------------------------------------------------------------------

  logic is_read, is_write, is_init;

  assign is_read  = (cachereq_type == `VC_MEM_REQ_MSG_TYPE_READ);
  assign is_write = (cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE);
  assign is_init  = (cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE_INIT);

  logic lookup_hit;
  // Use inside TAG CHECK state to determine next_state transition
  assign lookup_hit = is_init? 1'b0 : (is_valid && tag_match);

  always_comb begin
    next_state = state; // default assignment
    case(state)
      STATE_IDLE: begin
        if(proc2cache_reqstream_val && proc2cache_reqstream_rdy)
          next_state = STATE_TAG_CHECK;
      end
      STATE_TAG_CHECK: begin
        if(is_init)
          next_state = STATE_INIT_DATA_ACCESS;
        else if(lookup_hit && is_read)
          next_state = STATE_READ_DATA_ACCESS;
        else if(lookup_hit && is_write)
          next_state = STATE_WRITE_DATA_ACCESS;
        else if(!lookup_hit && !is_dirty)
          next_state = STATE_REFILL_REQUEST;
        else if(!lookup_hit && is_dirty && is_valid)
          next_state = STATE_EVICT_PREPARE;
      end
      STATE_EVICT_PREPARE: next_state = STATE_EVICT_REQUEST;
      STATE_EVICT_REQUEST: begin
        if(cache2mem_reqstream_val && cache2mem_reqstream_rdy)
          next_state = STATE_EVICT_WAIT;
      end
      STATE_EVICT_WAIT: begin
        if(cache2mem_respstream_val && cache2mem_respstream_rdy)
          next_state = STATE_REFILL_REQUEST;
      end
      STATE_REFILL_REQUEST: begin
        if(cache2mem_reqstream_val && cache2mem_reqstream_rdy)
          next_state = STATE_REFILL_WAIT;
      end
      STATE_REFILL_WAIT: begin
        if(cache2mem_respstream_val && cache2mem_respstream_rdy)
          next_state = STATE_REFILL_UPDATE;
      end
      STATE_REFILL_UPDATE: begin
        if(is_read) next_state = STATE_READ_DATA_ACCESS;
        else if(is_write) next_state = STATE_WRITE_DATA_ACCESS;
      end
      STATE_READ_DATA_ACCESS: next_state = STATE_WAIT;
      STATE_WRITE_DATA_ACCESS: next_state = STATE_WAIT;
      STATE_INIT_DATA_ACCESS: next_state = STATE_WAIT;
      STATE_WAIT: begin
        if(proc2cache_respstream_val && proc2cache_respstream_rdy)
          next_state = STATE_IDLE;
      end
      default:
        next_state = STATE_IDLE;
    endcase
  end

  //----------------------------------------------------------------------
  // FSM output logic (combinational, for control signals)
  //----------------------------------------------------------------------

  task cs
  (
    input logic       cs_cachereq_rdy,
    input logic       cs_cacheresp_val,
    input logic       cs_memreq_val,
    input logic       cs_memresq_rdy,
    input logic       cs_cache_req_en,
    input logic       cs_wben_mux_sel,
    input logic       cs_memresp_en,
    input logic       cs_write_data_mux_sel,
    input logic       cs_tag_array_ren,
    input logic       cs_tag_array_wen,
    input logic       cs_data_array_ren,
    input logic       cs_data_array_wen,
    input logic       cs_evict_addr_reg_en,
    input logic       cs_memreq_addr_mux_sel,
    input logic       cs_read_data_zero_mux_sel,
    input logic       cs_read_data_reg_en,
    input logic       cs_valid_bit_in,
    input logic       cs_valid_bits_write_en,
    input logic       cs_dirty_bit_in,
    input logic       cs_dirty_bits_write_en
  );
  begin
    proc2cache_reqstream_rdy  = cs_cachereq_rdy;
    proc2cache_respstream_val = cs_cacheresp_val;
    cache2mem_reqstream_val   = cs_memreq_val;
    cache2mem_respstream_rdy  = cs_memresq_rdy;
    cache_req_en              = cs_cache_req_en;
    wben_mux_sel              = cs_wben_mux_sel;
    memresp_en                = cs_memresp_en;
    write_data_mux_sel        = cs_write_data_mux_sel;
    tag_array_ren             = cs_tag_array_ren;
    tag_array_wen             = cs_tag_array_wen;
    data_array_ren            = cs_data_array_ren;
    data_array_wen            = cs_data_array_wen;
    evict_addr_reg_en         = cs_evict_addr_reg_en;
    memreq_addr_mux_sel       = cs_memreq_addr_mux_sel;
    read_data_zero_mux_sel    = cs_read_data_zero_mux_sel;
    read_data_reg_en          = cs_read_data_reg_en;
    valid_bit_in              = cs_valid_bit_in;
    valid_bits_write_en       = cs_valid_bits_write_en;
    dirty_bit_in              = cs_dirty_bit_in;
    dirty_bits_write_en       = cs_dirty_bits_write_en;
  end
  endtask
   
  // cacheresp_type logic
  assign cacheresp_type = cachereq_type;

  // memreq_type!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  assign memreq_type = (state == STATE_EVICT_REQUEST)? `VC_MEM_REQ_MSG_TYPE_WRITE : 
      ((state == STATE_REFILL_REQUEST)? `VC_MEM_REQ_MSG_TYPE_READ : `VC_MEM_RESP_MSG_TYPE_X);
  //assign memreq_type = (state == STATE_REFILL_REQUEST) ? `VC_MEM_REQ_MSG_TYPE_READ : `VC_MEM_RESP_MSG_TYPE_X;

  always_comb begin
    case(state)
      //                          cache cache mem mem  cache wben mem  wdata tag   tag   data  data  evict memreq rdata rdata valid valid dirty dirty
      //                          req   resp  req resp req   mux  resp mux   array array array array addr  addr   zero  reg   bit   write bit   write
      //                          rdy   val   val rdy  en    sel  en   sel   ren   wen   ren   wen   en    sel    sel   en    in    en    in    en
      STATE_IDLE:              cs( 1,   0,    0,  0,   1,    'x,  1,   'x,   0,    0,    0,    0,    1,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_TAG_CHECK:         cs( 0,   0,    0,  0,   0,    'x,  1,   'x,   1,    0,    1,    0,    1,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_EVICT_PREPARE:     cs( 0,   0,    0,  0,   0,    'x,  1,   'x,   1,    0,    1,    0,    1,    'x,     0,   1,    0,    0,    0,    0    );
      STATE_EVICT_REQUEST:     cs( 0,   0,    1,  0,   0,    'x,  1,   'x,   1,    0,    1,    0,    0,     0,     1,   0,    0,    0,    0,    0    );
      STATE_EVICT_WAIT:        cs( 0,   0,    0,  1,   0,    'x,  1,   'x,   1,    0,    1,    0,    1,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_REFILL_REQUEST:    cs( 0,   0,    1,  0,   0,    'x,  1,   'x,   1,    0,    1,    0,    1,     1,     1,   1,    0,    0,    0,    0    );
      STATE_REFILL_WAIT:       cs( 0,   0,    0,  1,   0,    'x,  1,   'x,   1,    0,    1,    0,    1,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_REFILL_UPDATE:     cs( 0,   0,    0,  0,   0,     1,  0,    1,   0,    1,    0,    1,    1,    'x,     1,   1,    1,    1,    0,    1    );
      STATE_READ_DATA_ACCESS:  cs( 0,   0,    0,  0,   0,    'x,  1,   'x,   1,    0,    1,    0,    1,    'x,     0,   1,    0,    0,    0,    0    );
      STATE_WRITE_DATA_ACCESS: cs( 0,   0,    0,  0,   0,     0,  1,    0,   0,    1,    0,    1,    1,    'x,     1,   1,    0,    0,    1,    1    );
      STATE_INIT_DATA_ACCESS:  cs( 0,   0,    0,  0,   0,     0,  1,    0,   0,    1,    0,    1,    1,    'x,     1,   1,    1,    1,    0,    1    );
      STATE_WAIT:              cs( 0,   1,    0,  0,   0,     0,  1,    0,   1,    0,    1,    0,    1,    'x,     1,   0,    0,    0,    0,    0    );
      
      default:                 cs( 0,   0,    0,  0,   0,    'x,  0,   'x,   0,    0,    0,    0,    0,    'x,    'x,   0,    0,    0,    0,    0    );        
    endcase
  end

  //----------------------------------------------------------------------
  // FSM output logic (sequential, for hit signal)
  //----------------------------------------------------------------------

  always_ff @(posedge clk) begin
    if(reset)
      hit <= 1'b0;
    else if(is_init)
      hit <= 1'b0;
    else if(state == STATE_TAG_CHECK)
      hit <= lookup_hit;
  end

endmodule

`endif


// Don't use this style as FSM output table, not clean!!!

// always_comb begin
//   // default assignment
//   proc2cache_reqstream_rdy = 0;
//   proc2cache_respstream_val = 0;
//   cache2mem_reqstream_val = 0;
//   cache2mem_respstream_rdy = 0;

//   cacheresp_type = !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

//   cache_req_en = 1;
//   wben_mux_sel = 1'bx;
//   write_data_mux_sel =1'bx;

//   tag_array_ren = 0;
//   tag_array_wen = 0;
//   data_array_ren = 0;
//   data_array_wen = 0;

//   read_data_reg_en = 1;
//   read_data_zero_mux_sel = 1'bx;
//   hit = 2'bx;

//   case(state)
//     STATE_IDLE: begin
//       //proc2cache_respstream_val = 0; // already set in default
//       proc2cache_reqstream_rdy = 1;
//     end
//     STATE_TAG_CHECK: begin
//       tag_array_ren = 1;
//     end
//     STATE_INIT_DATA_ACCESS: begin
//       tag_array_wen = 1;
//       data_array_wen = 1;
//       wben_mux_sel = 1; // write to all words in that cache line
//       write_data_mux_sel = 0; // get data from cache req stream

//       hit = 2'd0;
//       read_data_zero_mux_sel = 1; // set data to 0 when cache write resp
//     end
//     STATE_WAIT: begin
//       proc2cache_respstream_val = 1;
//     end
//     default: begin
//       proc2cache_reqstream_rdy = 0;
//       proc2cache_respstream_val = 0;
//       cache2mem_reqstream_val = 0;
//       cache2mem_respstream_rdy = 0;
//     end
//   endcase
// end
