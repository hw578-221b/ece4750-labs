//=========================================================================
// Alt Blocking Cache Datapath
//=========================================================================

`ifndef LAB3_MEM_CACHE_ALT_DPATH_V
`define LAB3_MEM_CACHE_ALT_DPATH_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/srams.v"
`include "vc/mem-msgs.v"

module lab3_mem_CacheAltDpath
#(
  parameter p_num_banks = 1
)
(
  input  logic          clk,
  input  logic          reset,

  // Processor <-> Cache Interface

  input  mem_req_4B_t   proc2cache_reqstream_msg,
  output mem_resp_4B_t  proc2cache_respstream_msg,

  // Cache <-> Memory Interface

  output mem_req_16B_t  cache2mem_reqstream_msg,
  input  mem_resp_16B_t cache2mem_respstream_msg,

  // cache request stream
  output logic [3:0] cachereq_type,
  output logic [31:0] cachereq_addr,
  input  logic cache_req_en,
  input  logic wben_mux_sel,

  // memeory response stream
  input  logic memresp_en,
  input  logic write_data_mux_sel,

  // SRAM control regs
  input  logic tag_array_ren,
  input  logic tag_array_wen0,
  input  logic tag_array_wen1,
  input  logic data_array_ren,
  input  logic data_array_wen,

  // memory request stream
  output logic tag_match0,
  output logic tag_match1,
  input  logic way_sel,
  input  logic evict_addr_reg_en,
  input  logic memreq_addr_mux_sel,
  input  logic [3:0] memreq_type,

  // cache response stream
  input  logic read_data_zero_mux_sel,
  input  logic read_data_reg_en,
  input  logic hit,
  input  logic [3:0] cacheresp_type
);

  //=========================================================================
  // cachereq_msg
  //=========================================================================

  logic [7:0]  cachereq_opaque;
  logic [31:0] cachereq_data;

  vc_EnResetReg#(8) cachereq_opaque_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cache_req_en),
    .d      (proc2cache_reqstream_msg.opaque),
    .q      (cachereq_opaque)
  );

  vc_EnResetReg#(4) cachereq_type_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cache_req_en),
    .d      (proc2cache_reqstream_msg.type_),
    .q      (cachereq_type)
  );

  vc_EnResetReg#(32) cachereq_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cache_req_en),
    .d      (proc2cache_reqstream_msg.addr),
    .q      (cachereq_addr)
  );

  vc_EnResetReg#(32) cachereq_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cache_req_en),
    .d      (proc2cache_reqstream_msg.data),
    .q      (cachereq_data)
  );

  logic [15:0] wb_en, wben_mux_out;

  // wben_dec
  assign wb_en = 16'h000f << word_offset;

  vc_Mux2#(16) wben_mux
  (
    .in0  (wb_en),
    .in1  (16'hffff),
    .sel  (wben_mux_sel),
    .out  (wben_mux_out)
  );

  //=========================================================================
  // address mapping
  //=========================================================================

  logic [3:0] word_offset;
  logic [2:0] index;
  logic [1:0] bank;
  logic [24:0] tag;

  generate
    if (p_num_banks == 1) begin
      assign word_offset = cachereq_addr[3:0];
      assign index = cachereq_addr[6:4];
      assign tag = cachereq_addr[31:7];
    end
    else if (p_num_banks == 4) begin
      assign word_offset = cachereq_addr[3:0];
      assign bank = cachereq_addr[5:4];
      assign index = cachereq_addr[8:6];
      assign tag = {cachereq_addr[31:9], 2'b00};
    end
  endgenerate
  
  //=========================================================================
  // memresp_msg
  //=========================================================================

  logic [127:0] cpu_write_data;
  
  // replicate word that cpu want to write to cache 4 times, so cache line could later where to write the word by wben_mux_out
  assign cpu_write_data = {cachereq_data, cachereq_data, cachereq_data, cachereq_data};

  logic [127:0] memresp_data;

  vc_EnResetReg#(128) memresp_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (memresp_en),
    .d      (cache2mem_respstream_msg.data),
    .q      (memresp_data)
  );
  
  logic [127:0] write_data_mux_out;

  vc_Mux2#(128) write_data_mux
  (
    .in0  (cpu_write_data),
    .in1  (memresp_data),
    .sel  (write_data_mux_sel),
    .out  (write_data_mux_out)
  );

  //=========================================================================
  // Tag Array
  //=========================================================================

  logic [24:0] read_tag_out0, read_tag_out1;

  vc_CombinationalBitSRAM_1rw#(25,8) tag_array_way0
  (
    .clk        (clk),
    .reset      (reset),
    .read_en    (tag_array_ren),
    .read_addr  (index),
    .read_data  (read_tag_out0),
    .write_en   (tag_array_wen0),
    .write_addr (index),
    .write_data (tag)
  );

  vc_CombinationalBitSRAM_1rw#(25,8) tag_array_way1
  (
    .clk        (clk),
    .reset      (reset),
    .read_en    (tag_array_ren),
    .read_addr  (index),
    .read_data  (read_tag_out1),
    .write_en   (tag_array_wen1),
    .write_addr (index),
    .write_data (tag)
  );

  //=========================================================================
  // Data Array
  //=========================================================================
  logic [127:0] read_data_out;

  vc_CombinationalSRAM_1rw#(128,16) data_array
  (
    .clk           (clk),
    .reset         (reset),
    .read_en       (data_array_ren),
    .read_addr     ({way_sel, index}),
    .read_data     (read_data_out),
    .write_byte_en (wben_mux_out),
    .write_en      (data_array_wen),
    .write_addr    ({way_sel, index}),
    .write_data    (write_data_mux_out)
  );

  //=========================================================================
  // cacheresp_msg
  //=========================================================================

  logic [127:0] read_data_zero_mux_out, read_data_reg_q;

  vc_Mux2#(128) read_data_zero_mux
  (
    .in0  (read_data_out),
    .in1  (128'b0),
    .sel  (read_data_zero_mux_sel),
    .out  (read_data_zero_mux_out)
  );

  vc_EnResetReg#(128) read_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (read_data_reg_en),
    .d      (read_data_zero_mux_out),
    .q      (read_data_reg_q)
  );

  logic [1:0] word_select_mux_sel;
  logic [31:0] word_sel_mux_out;

  assign word_select_mux_sel = word_offset >> 2;

  vc_Mux4#(32) word_select_mux
  (
    .in0  (read_data_reg_q[31:0]),
    .in1  (read_data_reg_q[63:32]),
    .in2  (read_data_reg_q[95:64]),
    .in3  (read_data_reg_q[127:96]),
    .sel  (word_select_mux_sel),
    .out  (word_sel_mux_out)
  );

  assign proc2cache_respstream_msg.data = word_sel_mux_out;

  assign proc2cache_respstream_msg.test = {1'b0, hit};

  assign proc2cache_respstream_msg.type_ = cacheresp_type;

  assign proc2cache_respstream_msg.opaque = cachereq_opaque;
  assign proc2cache_respstream_msg.len = 2'b0;

  //=========================================================================
  // memreq_msg
  //=========================================================================

  logic [31:0] mk_addr0, mk_addr1, mk_addr_evict_next, mk_addr_evict, mk_addr_read;
  
  // cmp, compare tag from cachereq to tag from the cache line
  assign tag_match0 = (tag == read_tag_out0);
  assign tag_match1 = (tag == read_tag_out1);
  
  // write back to mem on a read/write miss and a dirty line
  generate
    if(p_num_banks == 1) begin
      assign mk_addr0 = {read_tag_out0, index, 4'b0000};
      assign mk_addr1 = {read_tag_out1, index, 4'b0000};
    end
    else if (p_num_banks == 4) begin
      assign mk_addr0 = {read_tag_out0[23:2], index, bank, 4'b0000};
      assign mk_addr1 = {read_tag_out1[23:2], index, bank, 4'b0000};
    end
  endgenerate

  vc_Mux2#(32) way_evict_mux
  (
    .in0  (mk_addr0),
    .in1  (mk_addr1),
    .sel  (way_sel),
    .out  (mk_addr_evict_next)
  );

  vc_EnResetReg#(32) evict_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (evict_addr_reg_en),
    .d      (mk_addr_evict_next),
    .q      (mk_addr_evict)
  );

  // read from mem on a read/write miss and a clean line
  generate
    if(p_num_banks == 1)
      assign mk_addr_read = {tag, index, 4'b0000};
    else if (p_num_banks == 4)
      assign mk_addr_read = {tag[23:2], index, bank, 4'b0000};
  endgenerate

  logic [31:0] memreq_addr_mux_out;

  vc_Mux2#(32) memreq_addr_mux
  (
    .in0  (mk_addr_evict),
    .in1  (mk_addr_read),
    .sel  (memreq_addr_mux_sel),
    .out  (memreq_addr_mux_out)
  );

  assign cache2mem_reqstream_msg.addr = memreq_addr_mux_out;

  assign cache2mem_reqstream_msg.data = read_data_reg_q;

  assign cache2mem_reqstream_msg.type_ = memreq_type;

  assign cache2mem_reqstream_msg.opaque= 8'b0;
  assign cache2mem_reqstream_msg.len = 4'b0;

endmodule

`endif
