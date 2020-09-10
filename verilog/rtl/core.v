//Include dependencies
`include "globalVariables.v"
`include "instructionDecoder.v"
`include "frameWriteController.v"
`include "instructionFrame.v"
`include "pipelineStateController.v"
`include "registers.v"
`include "int_ALU.v"
`include "instructionFetchController.v"


module core(
	//Inputs
	input clk,
	input reset,
	input [`DATA_WIDTH-1:0] memoryIn,

	//Outputs
	output wire [`DATA_WIDTH-1:0] programCounter_out
	);

	/////////////////
	//Instruction Fetch controller
	/////////////////

	reg [`DATA_WIDTH-1:0] aluResult;

	wire cir_writeEnable;
	wire [`DATA_WIDTH-1:0] pcOverwrite;
	wire pc_writeEnable;
	wire [2:0] branchType_frame;
	wire jumpInst_frame;
	wire compareGreater;
	wire compareEquals;
	wire compareLess;

	wire [`INSTRUCTION_WIDTH-1:0] instructionOut_ifc;
	wire [`DATA_WIDTH-1:0] programCounter;
	assign programCounter_out = programCounter;
	wire [`DATA_WIDTH-1:0] programCounter_next;

	instructionFetchController instructionFetchController(
		.clk(clk),
		.reset(reset),
		.memoryIn(memoryIn),
		.cir_writeEnable(cir_writeEnable),
		.pcOverwrite(aluResult),
		.pc_writeEnable(pc_writeEnable),
		.branchType(branchType_frame),
		.jumpInst(jumpInst_frame),
		.compareGreater(compareGreater),
		.compareEquals(compareEquals),
		.compareLess(compareLess),

		.instructionOut(instructionOut_ifc),
		.programCounter(programCounter),
		.programCounter_next(programCounter_next)
	);

	/////////////////
	//Instruction decoder
	/////////////////

	wire [`REGADDR_WIDTH-1:0] a_location_decodeOut;
	wire [`REGADDR_WIDTH-1:0] b_location_decodeOut;
	wire immediateSelect_decodeOut;
	wire [`DATA_WIDTH-1:0] immediateVal_decodeOut;
	wire unsignedSelect_decodeOut;
	wire subtractEnable_decodeOut;
	wire [`REGADDR_WIDTH-1:0] writeSelect_decodeOut;
	wire writeEnable_decodeOut;
	wire [`RESLT_SELCT_WIDTH-1:0] resultSelect_decodeOut;
	wire error_decodeOut;
	wire pcOverwrite_decode;
	wire [2:0] branchType_decode;
	wire jumpInst_decode;
	assign jumpInst_frame = jumpInst_decode;

	instructionDecoder instructionDecoder(
		.instructionIn(instructionOut_ifc),

		.a_location(a_location_decodeOut),
		.b_location(b_location_decodeOut),
		.immediateSelect(immediateSelect_decodeOut),
		.immediateVal(immediateVal_decodeOut),
		.unsignedSelect(unsignedSelect_decodeOut),
		.subtractEnable(subtractEnable_decodeOut),
		.writeSelect(writeSelect_decodeOut),
		.writeEnable(writeEnable_decodeOut),
		.resultSelect(resultSelect_decodeOut),
		.error(error_decodeOut),
		.pcOverwrite(pcOverwrite_decode),
		.branchType(branchType_decode),
		.jumpInstruction(jumpInst_decode)
		);

	/////////////////
	//State Controller
	/////////////////

	wire fetch_RequestState;
	wire fetch_ReceiveState;
	wire decodeState;
	wire setupState;
	wire executeState;
	wire writebackState;

	pipelineStateController pipelineStateController(
		.clk(clk),
		.reset(reset),

		.fetch_RequestState(fetch_RequestState),
		.fetch_ReceiveState(fetch_ReceiveState),
		.decodeState(decodeState),
		.setupState(setupState),
		.executeState(executeState),
		.writebackState(writebackState)
		);

	/////////////////
	//Write controller
	/////////////////

	wire aOperand_we;
	wire aLoc_we;
	wire bOperand_we;
	wire bLoc_we;
	wire imm_we;
	wire immSlct_we;
	wire unsigned_we;
	wire subEnable_we;
	wire resultSlct_we;
	wire writeSlct_we;
	wire writeEnable_we;
	wire result_we;
	wire pcOverwrite_we;
	wire branchType_we;
	wire jumpInstruction_we;

	frameWriteController frameWriteController(
		.fetch_RequestState(fetch_RequestState),
		.fetch_ReceiveState(fetch_ReceiveState),
		.decodeState(decodeState),
		.setupState(setupState),
		.executeState(executeState),
		.writebackState(writebackState),

		.aOperand_we(aOperand_we),
		.aLoc_we(aLoc_we),
		.bOperand_we(bOperand_we),
		.bLoc_we(bLoc_we),
		.imm_we(imm_we),
		.immSlct_we(immSlct_we),
		.unsigned_we(unsigned_we),
		.subEnable_we(subEnable_we),
		.resultSlct_we(resultSlct_we),
		.writeSlct_we(writeSlct_we),
		.writeEnable_we(writeEnable_we),
		.result_we(result_we),
		.cir_writeEnable(cir_writeEnable),
		.pc_writeEnable(pc_writeEnable),
		.pcOverwrite_we(pcOverwrite_we),
		.branchType_we(branchType_we),
		.jumpInstruction_we(jumpInstruction_we)
		);

	/////////////////
	//Instruction frame
	/////////////////

	wire [`DATA_WIDTH-1:0] aOperand_frameIn;
	wire [`DATA_WIDTH-1:0] bOperand_frameIn;
	wire [`DATA_WIDTH-1:0] aOpCompare_frameIn;
	wire [`DATA_WIDTH-1:0] bOpCompare_frameIn;

	wire [`DATA_WIDTH-1:0] aOperand_frameOut;
	wire [`REGADDR_WIDTH-1:0] aLoc_frameOut;
	wire [`DATA_WIDTH-1:0] bOperand_frameOut;
	wire [`REGADDR_WIDTH-1:0] bLoc_frameOut;
	wire [`DATA_WIDTH-1:0] immediateVal_frameOut;
	wire immediateSelect_frameOut;
	wire unsignedSelect_frameOut;
	wire subtractEnable_frameOut;
	wire [`RESLT_SELCT_WIDTH-1:0] resultSelect_frameOut;
	wire [`REGADDR_WIDTH-1:0] writeSelect_frameOut;
	wire writeEnable_frameOut;
	wire pcOverwrite_frameOut;
	wire [2:0] branchType_frameOut;
	assign branchType_frame = branchType_frameOut;
	wire jumpInstruction_frameOut;
	wire [`DATA_WIDTH-1:0] aOpCompare_frameOut;
	wire [`DATA_WIDTH-1:0] bOpCompare_frameOut;

	instructionFrame instructionFrame(
		.clk(clk),
		.reset(reset),
		.aOperand_in(aOperand_frameIn),
		.aLoc_in(a_location_decodeOut),
		.bOperand_in(bOperand_frameIn),
		.bLoc_in(b_location_decodeOut),
		.immediateVal_in(immediateVal_decodeOut),
		.immediateSelect_in(immediateSelect_decodeOut),
		.unsignedSelect_in(unsignedSelect_decodeOut),
		.subtractEnable_in(subtractEnable_decodeOut),
		.resultSelect_in(resultSelect_decodeOut),
		.writeSelect_in(writeSelect_decodeOut),
		.writeEnable_in(writeEnable_decodeOut),
		.pcOverwrite_in(pcOverwrite_decode),
		.branchType_in(branchType_decode),
		.jumpInstruction_in(jumpInst_decode),
		.aOpCompare_in(aOpCompare_frameIn),
		.bOpCompare_in(bOpCompare_frameIn),

		.aOperand_we(aOperand_we),
		.aLoc_we(aLoc_we),
		.bOperand_we(bOperand_we),
		.bLoc_we(bLoc_we),
		.imm_we(imm_we),
		.immSlct_we(immSlct_we),
		.unsigned_we(unsigned_we),
		.subEnable_we(subEnable_we),
		.resultSlct_we(resultSlct_we),
		.writeSlct_we(writeSlct_we),
		.writeEnable_we(writeEnable_we),
		.pcOverwrite_we(pcOverwrite_we),
		.branchType_we(branchType_we),
		.jumpInstruction_we(jumpInstruction_we),
		

		.aOperand_out(aOperand_frameOut),
		.aLoc_out(aLoc_frameOut),
		.bOperand_out(bOperand_frameOut),
		.bLoc_out(bLoc_frameOut),
		.immediateVal_out(immediateVal_frameOut),
		.immediateSelect_out(immediateSelect_frameOut),
		.unsignedSelect_out(unsignedSelect_frameOut),
		.subtractEnable_out(subtractEnable_frameOut),
		.resultSelect_out(resultSelect_frameOut),
		.writeSelect_out(writeSelect_frameOut),
		.writeEnable_out(writeEnable_frameOut),
		.pcOverwrite_out(pcOverwrite_frameOut),
		.branchType_out(branchType_frameOut),
		.jumpInstruction_out(jumpInstruction_frameOut),
		.aOpCompare_out(aOpCompare_frameOut),
		.bOpCompare_out(bOpCompare_frameOut)
		);

	/////////////////
	//Registers
	/////////////////

	reg [`DATA_WIDTH-1:0] regDataIn;
	wire [`DATA_WIDTH-1:0] readA_regOut;
	wire [`DATA_WIDTH-1:0] readB_regOut;

	wire writeEnable_reg;
	assign writeEnable_reg = result_we && writeEnable_frameOut;

	registers registers(
		.clk(clk),
		.reset(reset),
		.dataIn(regDataIn),
		.writeSelect(writeSelect_frameOut),
		.writeEnable(writeEnable_reg),
		.readA_select(aLoc_frameOut),
		.readB_select(bLoc_frameOut),

		.readA_out(readA_regOut),
		.readB_out(readB_regOut)
		);

	/////////////////
	//Operand muxes
	/////////////////

	//A_operand mux
	reg [`DATA_WIDTH-1:0] aOperand_muxOut;
	assign aOperand_frameIn = aOperand_muxOut;

	always @(*) begin : aOperandMux_proc
		case (pcOverwrite_frameOut)
			0 : aOperand_muxOut = readA_regOut;
			1 : aOperand_muxOut = programCounter;
		endcase // pcOverwrite_frameOut
	end

	//B_operand mux
	reg [`DATA_WIDTH-1:0] bOperand_muxOut;
	assign bOperand_frameIn = bOperand_muxOut;

	always @(*) begin : bOperandMux_proc
		case (immediateSelect_frameOut)
			0 : bOperand_muxOut = readB_regOut;
			1 : bOperand_muxOut = immediateVal_frameOut;
		endcase // immediateSelect_frameOut
	end

	//A_compareOperand mux
	assign aOpCompare_frameIn = readA_regOut;

	//B_compareOperand mux
	reg [`DATA_WIDTH-1:0] bOpCompare_muxOut;
	assign bOpCompare_frameIn = bOpCompare_muxOut;

	always @(*) begin : bOpCompareMux_proc
		if (immediateSelect_frameOut && ~pcOverwrite_frameOut) bOpCompare_muxOut = immediateVal_frameOut;
		else bOpCompare_muxOut = readB_regOut;
	end

	/////////////////
	//Arithmetic units
	/////////////////

	wire [`DATA_WIDTH-1:0] adderOut;
	adder adder (
		.aOperand(aOperand_frameOut),
		.bOperand(bOperand_frameOut),
		.subtract(subtractEnable_frameOut),

		.result(adderOut)
		);

	wire [`DATA_WIDTH-1:0] mulOut;
	multipler multipler (
		.aOperand(aOperand_frameOut),
		.bOperand(bOperand_frameOut),

		.result(mulOut)
		);

	wire [`DATA_WIDTH-1:0] divideOut;
	wire [`DATA_WIDTH-1:0] remOut;
	divider divider (
		.aOperand(aOperand_frameOut),
		.bOperand(bOperand_frameOut),
		.unsignedEn(unsignedSelect_frameOut),

		.divResult(divideOut),
		.remResult(remOut)
		);
	
	wire [`DATA_WIDTH-1:0] greaterThanOut;
	wire [`DATA_WIDTH-1:0] equalOut;
	wire [`DATA_WIDTH-1:0] lessThanOut;

	assign compareGreater = greaterThanOut[0];
	assign compareEquals = equalOut[0];
	assign compareLess = lessThanOut[0];

	comparator comparator (
		.aOperand(aOpCompare_frameOut),
		.bOperand(bOpCompare_frameOut),
		.unsignedEn(unsignedSelect_frameOut),

		.greater(greaterThanOut),
		.equal(equalOut),
		.less(lessThanOut)
		);

	//Result mux
	always @(*) begin : resultSelect_proc
		case (resultSelect_frameOut)
			0 : aluResult = adderOut;
			1 : aluResult = mulOut;
			2 : aluResult = divideOut;
			3 : aluResult = remOut;
			4 : aluResult = greaterThanOut;
			5 : aluResult = equalOut;
			6 : aluResult = lessThanOut;
			7 : aluResult = 0;
		endcase  //resultSelect_frameOut
	end

	//Register Data in mux
	always @(*) begin : regDataInMux_proc
		case (jumpInstruction_frameOut)
			0 : regDataIn = aluResult;
			1 : regDataIn = programCounter_next;
		endcase // jumpInstruction_frameOut
	end

endmodule //core