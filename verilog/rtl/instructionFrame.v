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
	input branchInst_in,
	input [2:0] branchType_in,
	input jumpLink_in,
	input jumpRegister_in,
	input [`DATA_WIDTH-1:0] aOpCompare_in,
	input [`DATA_WIDTH-1:0] bOpCompare_in,
	input load_in,
	input loadUnsigned_in,
	input store_in,
	input [1:0] memLength_in,
	input [`DATA_WIDTH-1:0] storeData_in,
	input auipc_in,

	//Pipeline state inputs
	input fetch_RequestState,
	input fetch_ReceiveState,
	input decodeState,
	input setupState,
	input executeState,
	input memReadState,
	input writebackState,

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
	output reg branchInst_out,
	output reg [2:0] branchType_out,
	output reg jumpLink_out,
	output reg jumpRegister_out,
	output reg [`DATA_WIDTH-1:0] aOpCompare_out,
	output reg [`DATA_WIDTH-1:0] bOpCompare_out,
	output reg load_out,
	output reg loadUnsigned_out,
	output reg store_out,
	output reg [1:0] memLength_out,
	output reg [`DATA_WIDTH-1:0] storeData_out,
	output reg auipc_out
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
			branchInst_out <= 0;
			branchType_out <= 0;
			jumpLink_out <= 0;
			jumpRegister_out <= 0;
			aOpCompare_out <= 0;
			bOperand_out <= 0;
			load_out <= 0;
			loadUnsigned_out <= 0;
			store_out <= 0;
			memLength_out <= 0;
			storeData_out <= 0;
			auipc_out <= 0;
		end else begin
			if (setupState) aOperand_out <= aOperand_in;
			if (decodeState) aLoc_out <= aLoc_in;
			if (setupState) bOperand_out <= bOperand_in;
			if (decodeState) bLoc_out <= bLoc_in;
			if (decodeState) immediateVal_out <= immediateVal_in;
			if (decodeState) immediateSelect_out <= immediateSelect_in;
			if (decodeState) unsignedSelect_out <= unsignedSelect_in;
			if (decodeState) subtractEnable_out <= subtractEnable_in;
			if (decodeState) resultSelect_out <= resultSelect_in;
			if (decodeState) writeSelect_out <= writeSelect_in;
			if (decodeState) writeEnable_out <= writeEnable_in;
			if (decodeState) branchInst_out <= branchInst_in;
			if (decodeState) branchType_out <= branchType_in;
			if (decodeState) jumpLink_out <= jumpLink_in;
			if (decodeState) jumpRegister_out <= jumpRegister_in;
			if (setupState) aOpCompare_out <= aOpCompare_in;
			if (setupState) bOpCompare_out <= bOpCompare_in;
			if (decodeState) load_out <= load_in;
			if (decodeState) loadUnsigned_out <= loadUnsigned_in;
			if (decodeState) store_out <= store_in;
			if (decodeState) memLength_out <= memLength_in;
			if (setupState) storeData_out <= storeData_in;
			if (decodeState) auipc_out <= auipc_in;
		end
	end

endmodule //instructionFrame