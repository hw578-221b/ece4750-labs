`ifndef BTB_PROC_V
`define BTB_PROC_V

module btb_proc #(
  parameter entry = 4,
  parameter idx_W = $clog2(entry),
  parameter tag_W = 32 - idx_W - 2
)
(
  input  logic        clk,
  input  logic        rst,
  
  // Fetch stage look up
  input  logic [31:0] pc_F,
  output logic        predict_taken,
  output logic [31:0] pc_predict,

  // Resolved jump/branch update (in D/X stage)
  input  logic [31:0] inst_addr,
  input  logic [31:0] target_pc,
  input  logic        btb_wren
);
// suppose hit in btb always assume branch taken (zero direction prediction bits)

// D stage update only when no osquash in X, and not stall in D
// for jal/jalr, if predict not taken (miss), then at D/X stage, update BTB, osquash as usual, if predict taken, not BTB update, no osquash (correct PC already fetched)
// for branch, if predict not taken (miss or FSM predict not taken), then if X stage branch taken, update the BTB, osquash; if not taken, don't update BTB
// for branch, if predict taken, then if X stage branch not taken, update BTB (FSM state), osquash; if taken, no need to update BTB

// update BTB in D stage (jal) and X stage (jalr, bne). If both D and X stage request updating (bne+jal, btb_wren_D == 1, btb_wren_X == 1), only handle X stage request

// don't squash if prediction is correct (predict_taken == pc_redirect)

// BTB memory
logic valid_bits [0:entry-1];
logic [tag_W-1:0] tags [0:entry-1];
logic [31:0] targets [0:entry-1];

// fetch lookup logic
logic [idx_W-1:0] idx;
logic [tag_W-1:0] tag;
logic hit;

assign idx = pc_F[idx_W+1:2];
assign tag = pc_F[31:idx_W+2];

assign hit = valid_bits[idx] && (tag == tags[idx]);
assign pc_predict = targets[idx];
assign predict_taken = hit? 1'b1 : 1'b0;

// resolved jump/branch update logic
logic [idx_W-1:0] idx_wr;
logic [tag_W-1:0] tag_wr;

assign idx_wr = inst_addr[idx_W+1:2];
assign tag_wr = inst_addr[31:idx_W+2];

always_ff @(posedge clk) begin
  if(rst) begin
    for (int i = 0; i < entry; i++)
      valid_bits[i] <= 1'b0;
  end
  else if (btb_wren) begin
    valid_bits[idx_wr] <= 1'b1;
    tags[idx_wr] <= tag_wr;
    targets[idx_wr] <= target_pc;
  end
end

endmodule

`endif