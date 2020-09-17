

module frameWriteController(
	//Inputs
	input fetch_RequestState,
	input fetch_ReceiveState,
	input decodeState,
	input setupState,
	input executeState,
	input memReadState,
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
	output wire jumpInstruction_we,
	output wire load_we,
	output wire store_we,
	output wire memLength_we,
	output wire storeData_we,
	output wire memEnable
	);

	assign aOperand_we = setupState;
	assign aLoc_we = decodeState;
	assign bOperand_we = setupState;
	assign bLoc_we = decodeState;
	assign imm_we = decodeState;
	assign immSlct_we = decodeState;
	assign unsigned_we = decodeState;
	assign subEnable_we = decodeState;
	assign result_we = executeState || memReadState;
	assign resultSlct_we = decodeState;
	assign writeSlct_we = decodeState;
	assign writeEnable_we = decodeState;
	assign cir_writeEnable = fetch_ReceiveState;
	assign pc_writeEnable = executeState;
	assign pcOverwrite_we = decodeState;
	assign branchType_we = decodeState;
	assign jumpInstruction_we = decodeState;
	assign load_we = decodeState;
	assign store_we = decodeState;
	assign memLength_we = decodeState;
	assign storeData_we = setupState;
	assign memEnable = executeState;

endmodule //frameWriteController