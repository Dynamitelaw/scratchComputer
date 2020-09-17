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
	input pcOverwrite_in,
	input [2:0] branchType_in,
	input jumpInstruction_in,
	input [`DATA_WIDTH-1:0] aOpCompare_in,
	input [`DATA_WIDTH-1:0] bOpCompare_in,
	input load_in,
	input loadUnsigned_in,
	input store_in,
	input [1:0] memLength_in,
	input [`DATA_WIDTH-1:0] storeData_in,

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
	input pcOverwrite_we,
	input branchType_we,
	input jumpInstruction_we,
	input load_we,
	input store_we,
	input memLength_we,
	input storeData_we,

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
	output reg writeEnable_out,
	output reg pcOverwrite_out,
	output reg [2:0] branchType_out,
	output reg jumpInstruction_out,
	output reg [`DATA_WIDTH-1:0] aOpCompare_out,
	output reg [`DATA_WIDTH-1:0] bOpCompare_out,
	output reg load_out,
	output reg loadUnsigned_out,
	output reg store_out,
	output reg [1:0] memLength_out,
	output reg [`DATA_WIDTH-1:0] storeData_out
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
			pcOverwrite_out <= 0;
			branchType_out <= 0;
			jumpInstruction_out <= 0;
			aOpCompare_out <= 0;
			bOperand_out <= 0;
			load_out <= 0;
			loadUnsigned_out <= 0;
			store_out <= 0;
			memLength_out <= 0;
			storeData_out <= 0;
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
			if (pcOverwrite_we) pcOverwrite_out <= pcOverwrite_in;
			if (branchType_we) branchType_out <= branchType_in;
			if (jumpInstruction_we) jumpInstruction_out <= jumpInstruction_in;
			if (aOperand_we) aOpCompare_out <= aOpCompare_in;
			if (bOperand_we) bOpCompare_out <= bOpCompare_in;
			if (load_we) load_out <= load_in;
			if (load_we) loadUnsigned_out <= loadUnsigned_in;
			if (store_we) store_out <= store_in;
			if (memLength_we) memLength_out <= memLength_in;
			if (storeData_we) storeData_out <= storeData_in;
		end
	end

endmodule //instructionFrame