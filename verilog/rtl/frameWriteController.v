

module frameWriteController(
	//Inputs
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
	output wire result_we
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

endmodule //frameWriteController