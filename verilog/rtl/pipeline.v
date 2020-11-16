//Include dependencies
`include "globalVariables.v"
`include "instructionDecoder.v"
`include "instructionFrame.v"
`include "pipelineStateController.v"
`include "registers.v"
`include "int_ALU.v"
`include "instructionFetchController.v"


module pipeline(
	//Inputs
	input clk,
	input reset,
	input [`DATA_WIDTH-1:0] memoryDataRead,

	//Outputs
	output wire [`DATA_WIDTH-1:0] programCounter_out,
	output reg [`DATA_WIDTH-1:0] memoryAddress,
	output wire [`DATA_WIDTH-1:0] memoryDataWrite,
	output reg [1:0] memoryLength,
	output reg store,
	output reg load,
	output wire loadUnsigned 
	);

	/////////////////
	//Instruction Fetch controller
	/////////////////

	reg [`DATA_WIDTH-1:0] aluResult;

	wire cir_writeEnable;
	wire [`DATA_WIDTH-1:0] pcOverwrite;
	wire pc_writeEnable;
	wire [2:0] branchType_frame;
	wire jumpInst_ifc;
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
		.memoryIn(memoryDataRead),
		.cir_writeEnable(cir_writeEnable),
		.pcOverwrite(aluResult),
		.pc_writeEnable(pc_writeEnable),
		.branchType(branchType_frame),
		.jumpInst(jumpInst_ifc),
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
	wire branchInst_decode;
	wire [2:0] branchType_decode;
	wire jumpLink_decode;
	wire jumpRegister_decode;
	wire load_decode;
	wire loadUnsigned_decode;
	wire store_decode;
	wire [1:0] memLength_decode;
	wire auipcInst_decode;

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
		.branchInst(branchInst_decode),
		.branchType(branchType_decode),
		.jumpLink(jumpLink_decode),
		.jumpRegister(jumpRegister_decode),
		.load(load_decode),
		.loadUnsigned(loadUnsigned_decode),
		.store(store_decode),
		.memLength(memLength_decode),
		.auipcInst(auipcInst_decode)
		);

	/////////////////
	//State Controller
	/////////////////
	wire loadInst_scIn;

	wire fetch_RequestState;
	wire fetch_ReceiveState;
	assign cir_writeEnable = fetch_ReceiveState;
	wire decodeState;
	wire setupState;
	wire executeState;
	assign pc_writeEnable = executeState;
	wire memReadState;
	wire writebackState;

	pipelineStateController pipelineStateController(
		.clk(clk),
		.reset(reset),
		.loadInst(loadInst_scIn),

		.fetch_RequestState(fetch_RequestState),
		.fetch_ReceiveState(fetch_ReceiveState),
		.decodeState(decodeState),
		.setupState(setupState),
		.executeState(executeState),
		.memReadState(memReadState),
		.writebackState(writebackState)
		);

	/////////////////
	//Instruction frame
	/////////////////

	wire [`DATA_WIDTH-1:0] aOperand_frameIn;
	wire [`DATA_WIDTH-1:0] bOperand_frameIn;
	wire [`DATA_WIDTH-1:0] aOpCompare_frameIn;
	wire [`DATA_WIDTH-1:0] bOpCompare_frameIn;
	wire [`DATA_WIDTH-1:0] storeData_frameIn;

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
	wire branchInst_frameOut;
	wire [2:0] branchType_frameOut;
	assign branchType_frame = branchType_frameOut;
	wire jumpLink_frameOut;
	wire jumpRegister_frameOut;
	assign jumpInst_ifc = jumpLink_frameOut || jumpRegister_frameOut;
	wire [`DATA_WIDTH-1:0] aOpCompare_frameOut;
	wire [`DATA_WIDTH-1:0] bOpCompare_frameOut;
	wire load_frameOut;
	assign loadInst_scIn = load_frameOut;
	wire loadUnsigned_frameOut;
	assign loadUnsigned = loadUnsigned_frameOut;
	wire store_frameOut;
	wire [1:0] memLength_frameOut;
	wire [`DATA_WIDTH-1:0] storeData_frameOut;
	assign memoryDataWrite = storeData_frameOut;
	wire auipc_frameOut;

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
		.branchInst_in(branchInst_decode),
		.branchType_in(branchType_decode),
		.jumpLink_in(jumpLink_decode),
		.jumpRegister_in(jumpRegister_decode),
		.aOpCompare_in(aOpCompare_frameIn),
		.bOpCompare_in(bOpCompare_frameIn),
		.load_in(load_decode),
		.loadUnsigned_in(loadUnsigned_decode),
		.store_in(store_decode),
		.memLength_in(memLength_decode),
		.storeData_in(storeData_frameIn),
		.auipc_in(auipcInst_decode),

		.fetch_RequestState(fetch_RequestState),
		.fetch_ReceiveState(fetch_ReceiveState),
		.decodeState(decodeState),
		.setupState(setupState),
		.executeState(executeState),
		.memReadState(memReadState),
		.writebackState(writebackState),

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
		.branchInst_out(branchInst_frameOut),
		.branchType_out(branchType_frameOut),
		.jumpLink_out(jumpLink_frameOut),
		.jumpRegister_out(jumpRegister_frameOut),
		.aOpCompare_out(aOpCompare_frameOut),
		.bOpCompare_out(bOpCompare_frameOut),
		.load_out(load_frameOut),
		.loadUnsigned_out(loadUnsigned_frameOut),
		.store_out(store_frameOut),
		.memLength_out(memLength_frameOut),
		.storeData_out(storeData_frameOut),
		.auipc_out(auipc_frameOut)
		);

	/////////////////
	//Registers
	/////////////////

	reg [`DATA_WIDTH-1:0] regDataIn;
	wire [`DATA_WIDTH-1:0] readA_regOut;
	wire [`DATA_WIDTH-1:0] readB_regOut;
	assign storeData_frameIn = readB_regOut;

	wire writeEnable_reg;
	assign writeEnable_reg = (executeState || memReadState) && writeEnable_frameOut;

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
		case (branchInst_frameOut || jumpLink_frameOut || auipc_frameOut)
			0 : aOperand_muxOut = readA_regOut;
			1 : aOperand_muxOut = programCounter;
		endcase // branchInst_frameOut
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
		if (immediateSelect_frameOut && ~branchInst_frameOut) bOpCompare_muxOut = immediateVal_frameOut;
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

	/////////////////
	//Register Data in mux
	/////////////////
	
	wire [1:0] regInputSelection;
	assign regInputSelection = {load_frameOut, jumpLink_frameOut || jumpRegister_frameOut};

	always @(*) begin : regDataInMux_proc
		case (regInputSelection)
			0 : regDataIn = aluResult;
			1 : regDataIn = programCounter_next;
			2 : regDataIn = memoryDataRead;
		endcase // jumpInstruction_frameOut
	end

	/////////////////
	//Memory access control
	/////////////////

	always @(*) begin : memAccessControl_proc
		if (writebackState) memoryAddress = programCounter;
		else memoryAddress = aluResult;

		if (writebackState) memoryLength = 3;
		else memoryLength = memLength_frameOut;

		store = store_frameOut && executeState;
		load = (load_frameOut && executeState) || writebackState;
	end

endmodule //core