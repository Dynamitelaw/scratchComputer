

module frameWriteController(
	//Inputs
	input fetch_RequestState,
	input fetch_ReceiveState,
	input decodeState,
	input setupState,
	input executeState,
	input writebackState,

	//Outputs
	output wire aOperand_we,
	output wire aLoc_we,
	output wire bOperand_we,
	output wire bLoc_we,
	output wire imm_we,
	output wire immSlct_we,
	output wire unsigned_we,
	output wire subEnable_we,
	output wire resultSlct_we,
	output wire writeSlct_we,
	output wire writeEnable_we,
	output wire result_we,
	output wire cir_writeEnable,
	output wire pc_writeEnable,
	output wire pcOverwrite_we,
	output wire branchType_we,
	output wire jumpInstruction_we
	);

	assign aOperand_we = setupState;
	assign aLoc_we = decodeState;
	assign bOperand_we = setupState;
	assign bLoc_we = decodeState;
	assign imm_we = decodeState;
	assign immSlct_we = decodeState;
	assign unsigned_we = decodeState;
	assign subEnable_we = decodeState;
	assign result_we = executeState || writebackState;
	assign resultSlct_we = decodeState;
	assign writeSlct_we = decodeState;
	assign writeEnable_we = decodeState;
	assign cir_writeEnable = fetch_ReceiveState;
	assign pcOverwrite_we = decodeState;
	assign branchType_we = decodeState;
	assign jumpInstruction_we = decodeState;

endmodule //frameWriteController