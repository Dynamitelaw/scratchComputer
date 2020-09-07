//Include dependencies
`include "globalVariables.v"


module instructionFrame(
	input clk,
	input reset,

	//Data inputs
	input [`DATA_WIDTH-1:0] aOperand_in,
	input [`REGADDR_WIDTH-1:0] aLoc_in,
	input [`DATA_WIDTH-1:0] bOperand_in,
	input [`REGADDR_WIDTH-1:0] bLoc_in,
	input [`DATA_WIDTH-1:0] immediateVal_in,
	input immediateSelect_in,
	input unsignedSelect_in,
	input subtractEnable_in,
	input [`RESLT_SELCT_WIDTH-1:0] resultSelect_in,
	input [`REGADDR_WIDTH-1:0] writeSelect_in,
	input writeEnable_in,

	//Write enable inputs
	input aOperand_we,
	input aLoc_we,
	input bOperand_we,
	input bLoc_we,
	input imm_we,
	input immSlct_we,
	input unsigned_we,
	input subEnable_we,
	input resultSlct_we,
	input writeSlct_we,
	input writeEnable_we,

	//Data outputs
	output reg [`DATA_WIDTH-1:0] aOperand_out,
	output reg [`REGADDR_WIDTH-1:0] aLoc_out,
	output reg [`DATA_WIDTH-1:0] bOperand_out,
	output reg [`REGADDR_WIDTH-1:0] bLoc_out,
	output reg [`DATA_WIDTH-1:0] immediateVal_out,
	output reg immediateSelect_out,
	output reg unsignedSelect_out,
	output reg subtractEnable_out,
	output reg [`RESLT_SELCT_WIDTH-1:0] resultSelect_out,
	output reg [`REGADDR_WIDTH-1:0] writeSelect_out,
	output reg writeEnable_out
	);

	always @(posedge clk) begin : instructionFrame_proc
		if(reset) begin
			aOperand_out <= 0;
			aLoc_out <= 0;
			bOperand_out <= 0;
			bLoc_out <= 0;
			immediateVal_out <= 0;
			immediateSelect_out <= 0;
			unsignedSelect_out <= 0;
			subtractEnable_out <= 0;
			resultSelect_out <= 0;
			writeSelect_out <= 0;
			writeEnable_out <= 0;
		end else begin
			if (aOperand_we) aOperand_out <= aOperand_in;
			if (aLoc_we) aLoc_out <= aLoc_in;
			if (bOperand_we) bOperand_out <= bOperand_in;
			if (bLoc_we) bLoc_out <= bLoc_in;
			if (imm_we) immediateVal_out <= immediateVal_in;
			if (immSlct_we) immediateSelect_out <= immediateSelect_in;
			if (unsigned_we) unsignedSelect_out <= unsignedSelect_in;
			if (subEnable_we) subtractEnable_out <= subtractEnable_in;
			if (resultSlct_we) resultSelect_out <= resultSelect_in;
			if (writeSlct_we) writeSelect_out <= writeSelect_in;
			if (writeEnable_we) writeEnable_out <= writeEnable_in;
		end
	end

endmodule : instructionFrame