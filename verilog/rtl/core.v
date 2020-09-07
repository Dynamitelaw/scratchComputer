//Include dependencies
`include "globalVariables.v"
`include "instructionDecoder.v"
`include "frameWriteController.v"
`include "instructionFrame.v"
`include "pipelineStateController.v"
`include "registers.v"
`include "int_ALU.v"


module core(
	//Inputs
	input clk,
	input reset,
	input [`INSTRUCTION_WIDTH-1:0] instructionIn,
	input start,

	//Outputs
	output wire busy
	);

	//Instruction decoder
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

	instructionDecoder instructionDecoder(
		.instructionIn(instructionIn),

		.a_location(a_location_decodeOut),
		.b_location(b_location_decodeOut),
		.immediateSelect(immediateSelect_decodeOut),
		.immediateVal(immediateVal_decodeOut),
		.unsignedSelect(unsignedSelect_decodeOut),
		.subtractEnable(subtractEnable_decodeOut),
		.writeSelect(writeSelect_decodeOut),
		.writeEnable(writeEnable_decodeOut),
		.resultSelect(resultSelect_decodeOut),
		.error(error_decodeOut)
		);

	//State Controller
	wire active;
	assign busy = active;
	wire decodeState;
	wire setupState;
	wire executeState;
	wire writebackState;

	pipelineStateController pipelineStateController(
		.clk(clk),
		.reset(reset),
		.start(start),

		.active(active),
		.decodeState(decodeState),
		.setupState(setupState),
		.executeState(executeState),
		.writebackState(writebackState)
		);

	//Write controller
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

	frameWriteController frameWriteController(
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
		.result_we(result_we)
		);

	//Instruction frame
	wire [`DATA_WIDTH-1:0] aOperand_frameIn;
	wire [`DATA_WIDTH-1:0] bOperand_frameIn;

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
		.writeEnable_out(writeEnable_frameOut)
		);

	//Registers
	reg [`DATA_WIDTH-1:0] reg_dataIn;

	wire [`DATA_WIDTH-1:0] readA_regOut;
	wire [`DATA_WIDTH-1:0] readB_regOut;
	assign aOperand_frameIn = readA_regOut;

	wire writeEnable_reg;
	assign writeEnable_reg = result_we && writeEnable_frameOut;

	registers registers(
		.clk(clk),
		.reset(reset),
		.dataIn(reg_dataIn),
		.writeSelect(writeSelect_frameOut),
		.writeEnable(writeEnable_reg),
		.readA_select(aLoc_frameOut),
		.readB_select(bLoc_frameOut),

		.readA_out(readA_regOut),
		.readB_out(readB_regOut)
		);

	//B_operand mux
	reg [`DATA_WIDTH-1:0] bOperand_muxOut;
	assign bOperand_frameIn = bOperand_muxOut;

	always @(*) begin : bOperandMux_proc
		case (immediateSelect_frameOut)
			0 : bOperand_muxOut = readB_regOut;
			1 : bOperand_muxOut = immediateVal_frameOut;
		endcase // immediateSelect_frameOut
	end

	//Arithmetic units
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
	comparator comparator (
		.aOperand(aOperand_frameOut),
		.bOperand(bOperand_frameOut),
		.unsignedEn(unsignedSelect_frameOut),

		.greater(greaterThanOut),
		.equal(equalOut),
		.less(lessThanOut)
		);

	//Result mux
	always @(*) begin : resultSelect_proc
		case (resultSelect_frameOut)
			0 : reg_dataIn = adderOut;
			1 : reg_dataIn = mulOut;
			2 : reg_dataIn = divideOut;
			3 : reg_dataIn = remOut;
			4 : reg_dataIn = greaterThanOut;
			5 : reg_dataIn = equalOut;
			6 : reg_dataIn = lessThanOut;
			7 : reg_dataIn = 0;
		endcase  //resultSelect_frameOut
	end

endmodule //core