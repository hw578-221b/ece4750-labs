//=========================================================================
// Alt Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_CACHE_ALT_CTRL_OP1_V
`define LAB3_MEM_CACHE_ALT_CTRL_OP1_V

`include "vc/mem-msgs.v"
`include "vc/regfiles.v"

module lab3_mem_CacheAltCtrlOp1
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
  output logic        tag_array_wen0,
  output logic        tag_array_wen1,
  output logic        data_array_ren,
  output logic        data_array_wen0,
  output logic        data_array_wen1,

  // memory request stream
  input  logic        tag_match0,
  input  logic        tag_match1,
  output logic        way_sel,
  output logic        read_way_mux_sel,
  output logic [1:0]  parallel_rd_sel,
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
  localparam STATE_TAG_CHECK_RD      = 5'd1;
  localparam STATE_INIT_DATA_ACCESS  = 5'd2;
  //localparam STATE_READ_DATA_ACCESS  = 5'd3;
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
  logic [3:0] word_offset;
  logic [2:0] index;
  logic [24:0] tag;

  assign word_offset = cachereq_addr[3:0];

  generate
    if (p_num_banks == 1) begin
      assign index = cachereq_addr[6:4];
      assign tag = cachereq_addr[31:7];
    end
    else if (p_num_banks == 4) begin // address mapping for four banks
      assign index = cachereq_addr[8:6];
      assign tag = {cachereq_addr[31:9], 2'b00};
    end
  endgenerate

  logic valid_bit_in, dirty_bit_in, use_bit_in;
  logic valid_bits_write_en0, valid_bits_write_en1, dirty_bits_write_en0, dirty_bits_write_en1, use_bits_write_en;
  logic is_valid_way0, is_valid_way1, is_dirty_way0, is_dirty_way1, use_bit;

  vc_ResetRegfile_1r1w#(1,8) valid_bits_way0
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_valid_way0),
    .write_en   (valid_bits_write_en0),
    .write_addr (index),
    .write_data (valid_bit_in)
  );

  vc_ResetRegfile_1r1w#(1,8) valid_bits_way1
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_valid_way1),
    .write_en   (valid_bits_write_en1),
    .write_addr (index),
    .write_data (valid_bit_in)
  );

  vc_ResetRegfile_1r1w#(1,8) dirty_bits_way0
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_dirty_way0),
    .write_en   (dirty_bits_write_en0),
    .write_addr (index),
    .write_data (dirty_bit_in)
  );

  vc_ResetRegfile_1r1w#(1,8) dirty_bits_way1
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (is_dirty_way1),
    .write_en   (dirty_bits_write_en1),
    .write_addr (index),
    .write_data (dirty_bit_in)
  );

  // 1 use bit (track two ways) for each set (8 set in total)
  vc_ResetRegfile_1r1w#(1,8) use_bits
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (index),
    .read_data  (use_bit),
    .write_en   (use_bits_write_en),
    .write_addr (index),
    .write_data (use_bit_in)
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

  logic is_read, is_write, is_init, is_valid, is_dirty;

  assign is_read  = (cachereq_type == `VC_MEM_REQ_MSG_TYPE_READ);
  assign is_write = (cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE);
  assign is_init  = (cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE_INIT);

  // Use inside TAG CHECK READ state to determine next_state transition
  logic lookup_hit;
  assign lookup_hit = is_init? 1'b0 : ((is_valid_way0 && tag_match0) || (is_valid_way1 && tag_match1));

  // next use bit logic, determined in TAG CHECK state
  // when hit, use = way number that hit, when miss, use (the way need to replace) = the other way that's not recently used (LRU)
  always_comb begin
    if(is_valid_way0 && tag_match0)
      use_bit_in = 0;
    else if(is_valid_way1 && tag_match1)
      use_bit_in = 1;
    else
      use_bit_in = ~use_bit; // LRU policy
  end

  // Use inside TAG CHECK state to determine next_state transition
  logic lookup_way_sel;
  assign lookup_way_sel = use_bit_in;

  assign is_valid = (lookup_way_sel == 0)? is_valid_way0 : is_valid_way1;
  assign is_dirty = (lookup_way_sel == 0)? is_dirty_way0 : is_dirty_way1;

  always_comb begin
    next_state = state; // default assignment
    case(state)
      STATE_IDLE: begin
        if(proc2cache_reqstream_val && proc2cache_reqstream_rdy)
          next_state = STATE_TAG_CHECK_RD;
      end
      // can appear 2 cycles, 1 cycle handle read from cache refill, another cycle handle a new read request
      STATE_TAG_CHECK_RD: begin
        if(is_init)
          next_state = STATE_INIT_DATA_ACCESS;
        else if(lookup_hit && is_read) // on a read hit (could be wither first lookup hit, or hit after cache line refill)
          if(!proc2cache_respstream_rdy)
            next_state = STATE_WAIT;
          else begin
            if(!proc2cache_reqstream_val)
              next_state = STATE_IDLE;
            else
              next_state = STATE_TAG_CHECK_RD;
          end
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
        if(is_read) next_state = STATE_TAG_CHECK_RD;
        else if(is_write) next_state = STATE_WRITE_DATA_ACCESS;
      end
      //STATE_READ_DATA_ACCESS: next_state = STATE_WAIT;
      STATE_WRITE_DATA_ACCESS: next_state = STATE_WAIT;
      STATE_INIT_DATA_ACCESS: next_state = STATE_WAIT;
      STATE_WAIT: begin
        if(proc2cache_respstream_val && proc2cache_respstream_rdy) begin
          if(proc2cache_reqstream_val)
            next_state = STATE_TAG_CHECK_RD;
          else
            next_state = STATE_IDLE;
        end
      end

      default: next_state = STATE_IDLE;
    endcase
  end

  //----------------------------------------------------------------------
  // FSM output logic (combinational, for control signals)
  //----------------------------------------------------------------------

  logic tag_array_wen, data_array_wen, valid_bits_write_en, dirty_bits_write_en;
  
  task cs
  (
    input logic       cs_memreq_val,
    input logic       cs_memresq_rdy,
    input logic       cs_wben_mux_sel,
    input logic       cs_write_data_mux_sel,
    input logic       cs_tag_array_ren,
    input logic       cs_tag_array_wen,
    input logic       cs_data_array_ren,
    input logic       cs_data_array_wen,
    input logic       cs_memreq_addr_mux_sel,
    input logic       cs_read_data_zero_mux_sel,
    input logic       cs_read_data_reg_en,
    input logic       cs_valid_bit_in,
    input logic       cs_valid_bits_write_en,
    input logic       cs_dirty_bit_in,
    input logic       cs_dirty_bits_write_en
  );
  begin
    cache2mem_reqstream_val   = cs_memreq_val;
    cache2mem_respstream_rdy  = cs_memresq_rdy;
    wben_mux_sel              = cs_wben_mux_sel;
    write_data_mux_sel        = cs_write_data_mux_sel;
    tag_array_ren             = cs_tag_array_ren;
    tag_array_wen             = cs_tag_array_wen;
    data_array_ren            = cs_data_array_ren;
    data_array_wen            = cs_data_array_wen;
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

  // memreq_type
  assign memreq_type = (state == STATE_EVICT_REQUEST)? `VC_MEM_REQ_MSG_TYPE_WRITE : 
      ((state == STATE_REFILL_REQUEST)? `VC_MEM_REQ_MSG_TYPE_READ : `VC_MEM_RESP_MSG_TYPE_X);

  // cache req_rdy, resp_val logic
  // set resp_val to high in read lookup hit/ wait state, so data can get get into resp stream in 1 cycle
  // set req_rdy and req_en to high when in read lookup hit/ wait state, and next state is TCR state, so req data can come through in the next cycle
  always_comb begin
    // default assignment
    proc2cache_reqstream_rdy = 0;
    proc2cache_respstream_val = 0;

    if(state == STATE_IDLE) begin
      proc2cache_reqstream_rdy = 1;
    end
    // use lookup_hit so reads completing after refill can also return their data
    else if(state == STATE_WAIT || ((state == STATE_TAG_CHECK_RD) && is_read && lookup_hit)) begin
      // has valid data to send to resp stream
      proc2cache_respstream_val = 1;
      // ready to take another request only when current response can be accpeted
      proc2cache_reqstream_rdy = proc2cache_respstream_rdy;
    end
  end

  // ****************Capture a request only when it is accepted!**********************
  assign cache_req_en = proc2cache_reqstream_val && proc2cache_reqstream_rdy;

  // same for memresp_en
  assign memresp_en = cache2mem_respstream_val && cache2mem_respstream_rdy;

  // select the way that's currently using (determined by LRU policy)
  //logic way_sel;
  assign way_sel = use_bit;
  
  // determine which way to write tag into by way_sel
  assign tag_array_wen0 = tag_array_wen && (way_sel == 0);
  assign tag_array_wen1 = tag_array_wen && (way_sel == 1);

  // determine which way to write data into by way_sel
  assign data_array_wen0 = data_array_wen && (way_sel == 0);
  assign data_array_wen1 = data_array_wen && (way_sel == 1);

  // determine which way to write valid/dirty bit into by way_sel
  assign valid_bits_write_en0 = valid_bits_write_en && (way_sel == 0);
  assign valid_bits_write_en1 = valid_bits_write_en && (way_sel == 1);

  assign dirty_bits_write_en0 = dirty_bits_write_en && (way_sel == 0);
  assign dirty_bits_write_en1 = dirty_bits_write_en && (way_sel == 1);

  // parallel_rd_sel logic
  always_comb begin
    if((state == STATE_TAG_CHECK_RD) && is_read)
      parallel_rd_sel = {1'b0, lookup_way_sel};
    else
      parallel_rd_sel = 2'd2;
  end

  // ************Match the immediate response's way when read bypassing******************
  // so that when proc stall, value inside the reg doesn't come from the wrong way!
  // otherwise, use the registered way selection for operations such as eviction
  assign read_way_mux_sel = (parallel_rd_sel == 2'd0) ? 1'b0 :
                            (parallel_rd_sel == 2'd1) ? 1'b1 : way_sel;
  
  // only update use bits at TAG CHECK stage
  assign use_bits_write_en = (state == STATE_TAG_CHECK_RD)? 1 : 0;

  assign evict_addr_reg_en = (state == STATE_EVICT_PREPARE);

  always_comb begin
    case(state)
      //                           mem mem  wben wdata tag   tag   data  data  memreq rdata rdata valid valid dirty dirty
      //                           req resp mux  mux   array array array array addr   zero  reg   bit   write bit   write
      //                           val rdy  sel  sel   ren   wen   ren   wen   sel    sel   en    in    en    in    en
      STATE_IDLE:              cs( 0,  0,   'x,  'x,   0,    0,    0,    0,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_TAG_CHECK_RD:      cs( 0,  0,   'x,  'x,   1,    0,    1,    0,    'x,     0,   1,    0,    0,    0,    0    );
      STATE_EVICT_PREPARE:     cs( 0,  0,   'x,  'x,   1,    0,    1,    0,    'x,     0,   1,    0,    0,    0,    0    );
      STATE_EVICT_REQUEST:     cs( 1,  0,   'x,  'x,   1,    0,    1,    0,     0,     1,   0,    0,    0,    0,    0    );
      STATE_EVICT_WAIT:        cs( 0,  1,   'x,  'x,   1,    0,    1,    0,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_REFILL_REQUEST:    cs( 1,  0,   'x,  'x,   1,    0,    1,    0,     1,     1,   1,    0,    0,    0,    0    );
      STATE_REFILL_WAIT:       cs( 0,  1,   'x,  'x,   1,    0,    1,    0,    'x,     1,   1,    0,    0,    0,    0    );
      STATE_REFILL_UPDATE:     cs( 0,  0,    1,   1,   0,    1,    0,    1,    'x,     1,   1,    1,    1,    0,    1    );
      STATE_WRITE_DATA_ACCESS: cs( 0,  0,    0,   0,   0,    1,    0,    1,    'x,     1,   1,    0,    0,    1,    1    );
      STATE_INIT_DATA_ACCESS:  cs( 0,  0,    0,   0,   0,    1,    0,    1,    'x,     1,   1,    1,    1,    0,    1    );
      STATE_WAIT:              cs( 0,  0,    0,   0,   1,    0,    1,    0,    'x,     1,   0,    0,    0,    0,    0    );
      
      default:                 cs( 0,  0,   'x,  'x,   0,    0,    0,    0,    'x,    'x,   0,    0,    0,    0,    0    );        
    endcase
  end

  //----------------------------------------------------------------------
  // FSM output logic (sequential, for hit signal)
  //----------------------------------------------------------------------
  logic hit_reg, first_check, checked;

  assign first_check = (state == STATE_TAG_CHECK_RD) && !checked;

  // checked logic
  always_ff @(posedge clk) begin
    if(reset)
      checked <= 1'b0;
    else if(proc2cache_reqstream_val && proc2cache_reqstream_rdy) // new cache request
      checked <= 1'b0;
    // feedback loop via checked, once checked, won't enter this branch again until new request
    else if(first_check)
      checked <= 1'b1;
  end

  // hit_reg logic
  always_ff @(posedge clk) begin
    if(reset) begin
      hit_reg <= 1'b0;
    end
    else if(is_init)
      hit_reg <= 1'b0;
    // Don't use state == TCR! After refill, lookup_hit will be 1 (false hit), if processor stall and cache enter W stage 
    // this will overwrite the saved miss in hit_reg with hit, cause proc receive wrong response when it's ready
    else if(first_check) begin
      hit_reg <= lookup_hit;
    end
  end

  // if first check, selecting the combinational hit in case need to output resp at TCR stage (resp_rdy) 
  // as registered version has old data 1 cycle earlier at this time
  // if not first check, like when read miss: go from refill_update to TCR, use the registered version
  assign hit = first_check? lookup_hit : hit_reg;

endmodule

`endif