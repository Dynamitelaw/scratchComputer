//Include dependencies
`define INSTRUCTION_WIDTH 32
`define REGADDR_WIDTH 5
`define DATA_WIDTH 32

`define RESLT_SELCT_WIDTH 3
//Include dependencies

module instructionDecoder (
	//Inputs
	input [`INSTRUCTION_WIDTH-1:0] instructionIn,

	//Outputs
	output reg [`REGADDR_WIDTH-1:0] a_location,
	output reg [`REGADDR_WIDTH-1:0] b_location,
	output reg immediateSelect,
	output reg [`DATA_WIDTH-1:0] immediateVal,
	output reg unsignedSelect,
	output reg subtractEnable,
	output reg [`REGADDR_WIDTH-1:0] writeSelect,
	output reg writeEnable,
	output reg [`RESLT_SELCT_WIDTH-1:0] resultSelect,
	output reg error
	);

	//Wires to separate instruction fields
	`define OPCODE_WIDTH 7
	`define FUNCT3_WIDTH 3
	`define FUNCT7_WIDTH 7
	`define IMM_WIDTH 12

	wire [`OPCODE_WIDTH-1:0] opcode;
	wire [`REGADDR_WIDTH-1:0] rd;
	wire [`FUNCT3_WIDTH-1:0] funct3;
	wire [`REGADDR_WIDTH-1:0] rs1;
	wire [`REGADDR_WIDTH-1:0] rs2;
	wire [`FUNCT7_WIDTH-1:0] funct7;
	wire [`IMM_WIDTH-1:0] imm;

	assign opcode = instructionIn[6:0];
	assign rd = instructionIn[11:7];
	assign funct3 = instructionIn[14:12];
	assign rs1 = instructionIn[19:15];
	assign rs2 = instructionIn[24:20];
	assign funct7 = instructionIn[31:25];
	assign imm = instructionIn[31:20];


	//Hardcoded values of supported opcodes and functions
	
	//Opcodes
	`define OP_IMM 7'h13
	`define OP 7'h33

	//funct3
	`define ADDI_F3 3'h0
	`define ADD_F3 3'h0
	`define SLT_F3 3'h2
	`define SLTU_F3 3'h3
	`define SUB_F3 3'h0
	`define MUL_F3 3'h0
	`define DIV_F3 3'h4
	`define DIVU_F3 3'h5
	`define REM_F3 3'h6
	`define REMU_F3 3'h7

	//funct7
	`define ADD_SLT_F7 7'h0
	`define SUB_F7 7'h20
	`define MULDIV_F7 7'h1

	//Flag bits for decoded instructions
	reg addi_flag;
	reg add_flag;
	reg sub_flag;
	reg mul_flag;
	reg div_flag;
	reg divu_flag;
	reg rem_flag;
	reg remu_flag;
	reg slti_flag;
	reg sltiu_flag;
	reg slt_flag;
	reg sltu_flag;

	//Decode logic
	`define IMM_EXTEN_WIDTH 20
	reg [7:0] encoderInput;

	always @(*) begin : instructionDecode
		//Check for supported instructions and set decode flags
		addi_flag = (opcode == `OP_IMM) && (funct3 == `ADDI_F3);
		add_flag = (opcode == `OP) && (funct3 == `ADD_F3) && (funct7 == `ADD_SLT_F7);
		sub_flag = (opcode == `OP) && (funct3 == `SUB_F3) && (funct7 == `SUB_F7);
		mul_flag = (opcode == `OP) && (funct3 == `MUL_F3) && (funct7 == `MULDIV_F7);
		div_flag = (opcode == `OP) && (funct3 == `DIV_F3) && (funct7 == `MULDIV_F7);
		divu_flag = (opcode == `OP) && (funct3 == `DIVU_F3) && (funct7 == `MULDIV_F7);
		rem_flag = (opcode == `OP) && (funct3 == `REM_F3) && (funct7 == `MULDIV_F7);
		remu_flag = (opcode == `OP) && (funct3 == `REMU_F3) && (funct7 == `MULDIV_F7);
		slti_flag = (opcode == `OP_IMM) && (funct3 == `SLT_F3);
		sltiu_flag = (opcode == `OP_IMM) && (funct3 == `SLTU_F3);
		slt_flag = (opcode == `OP) && (funct3 == `SLT_F3) && (funct7 == `ADD_SLT_F7);
		sltu_flag = (opcode == `OP) && (funct3 == `SLTU_F3) && (funct7 == `ADD_SLT_F7);

		//Determine output control signals
		a_location = rs1;
		b_location = rs2;

		immediateSelect = addi_flag || slti_flag || sltiu_flag;
		immediateVal = { {`IMM_EXTEN_WIDTH{imm[`IMM_WIDTH-1]}}, imm[`IMM_WIDTH-1:0] };  //sign extend immediate value

		unsignedSelect = divu_flag || remu_flag || sltiu_flag || sltu_flag;
		subtractEnable = sub_flag;
		writeSelect = rd;
		writeEnable = 1;

		//result select encoder
		encoderInput = {1'b0, (slti_flag || sltiu_flag ||  slt_flag || sltu_flag), 1'b0, 1'b0, (remu_flag || rem_flag), (div_flag || divu_flag), mul_flag, (addi_flag || add_flag || sub_flag)};
		case (encoderInput)
			8'b00000001 : resultSelect = 0;
			8'b00000010 : resultSelect = 1;
			8'b00000100 : resultSelect = 2;
			8'b00001000 : resultSelect = 3;
			8'b00010000 : resultSelect = 4;
			8'b00100000 : resultSelect = 5;
			8'b01000000 : resultSelect = 6;
			8'b10000000 : resultSelect = 7;

			default : resultSelect = 0;
		endcase // encoderInput
	end

endmodule //instructionDecoder


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
//Include dependencies


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

endmodule //instructionFrame


module pipelineStateController (
	//Inputs
	input clk,
	input reset,
	input start,

	//Outputs
	output reg active,
	output wire decodeState,
	output wire setupState,
	output wire executeState,
	output wire writebackState
	);

	reg [1:0] pipelineState;
	wire notActive;
	assign notActive = 	~active;

	reg [3:0] stateDecoderOutput;
	assign decodeState = stateDecoderOutput[0];
	assign setupState = stateDecoderOutput[1];
	assign executeState = stateDecoderOutput[2];
	assign writebackState = stateDecoderOutput[3];

	wire sleepState;
	assign sleepState = decodeState && notActive;
	wire nextActiveState;
	assign nextActiveState = ((decodeState && active)||setupState||executeState) || ((start&&sleepState) && ~(active&&writebackState));

	//Logic
	always @ (posedge clk) begin : stateControl
		if (reset) begin
			//reset
			pipelineState <= 0;
			active <= 0;
		end else begin
			active <= nextActiveState;

			if (active) begin
				pipelineState <= pipelineState + 1;
			end
		end
	end

	always @(*) begin : stateDecoder_proc
		if (reset) stateDecoderOutput <= 4'b0001;
		else begin
			//Pipeline state decoder
			case (pipelineState)
				0 : stateDecoderOutput <= 4'b0001;
				1 : stateDecoderOutput <= 4'b0010;
				2 : stateDecoderOutput <= 4'b0100;
				3 : stateDecoderOutput <= 4'b1000;
			endcase // pipelineState
		end
	end

endmodule //pipelineStateController
//Include dependencies


module registers (
	//Inputs
	input clk,
	input reset,
	
	input [`DATA_WIDTH-1:0] dataIn,
	input [`REGADDR_WIDTH-1:0] writeSelect,
	input writeEnable,
	input [`REGADDR_WIDTH-1:0] readA_select,
	input [`REGADDR_WIDTH-1:0] readB_select,

	//Outputs
	output reg [`DATA_WIDTH-1:0] readA_out,
	output reg [`DATA_WIDTH-1:0] readB_out
	);

	//General purpose registers
	wire [`DATA_WIDTH-1:0] r0;
	assign r0 = 0;
	reg [`DATA_WIDTH-1:0] r1;
	reg [`DATA_WIDTH-1:0] r2;
	reg [`DATA_WIDTH-1:0] r3;
	reg [`DATA_WIDTH-1:0] r4;
	reg [`DATA_WIDTH-1:0] r5;
	reg [`DATA_WIDTH-1:0] r6;
	reg [`DATA_WIDTH-1:0] r7;
	reg [`DATA_WIDTH-1:0] r8;
	reg [`DATA_WIDTH-1:0] r9;
	reg [`DATA_WIDTH-1:0] r10;
	reg [`DATA_WIDTH-1:0] r11;
	reg [`DATA_WIDTH-1:0] r12;
	reg [`DATA_WIDTH-1:0] r13;
	reg [`DATA_WIDTH-1:0] r14;
	reg [`DATA_WIDTH-1:0] r15;
	reg [`DATA_WIDTH-1:0] r16;
	reg [`DATA_WIDTH-1:0] r17;
	reg [`DATA_WIDTH-1:0] r18;
	reg [`DATA_WIDTH-1:0] r19;
	reg [`DATA_WIDTH-1:0] r20;
	reg [`DATA_WIDTH-1:0] r21;
	reg [`DATA_WIDTH-1:0] r22;
	reg [`DATA_WIDTH-1:0] r23;
	reg [`DATA_WIDTH-1:0] r24;
	reg [`DATA_WIDTH-1:0] r25;
	reg [`DATA_WIDTH-1:0] r26;
	reg [`DATA_WIDTH-1:0] r27;
	reg [`DATA_WIDTH-1:0] r28;
	reg [`DATA_WIDTH-1:0] r29;
	reg [`DATA_WIDTH-1:0] r30;
	reg [`DATA_WIDTH-1:0] r31;

	//Register alias probes (for easier simulation debug)
	wire [`DATA_WIDTH-1:0] ra;
	assign ra = r1;
	wire [`DATA_WIDTH-1:0] sp;
	assign sp = r2;
	wire [`DATA_WIDTH-1:0] gp;
	assign gp = r3;
	wire [`DATA_WIDTH-1:0] tp;
	assign tp = r4;
	wire [`DATA_WIDTH-1:0] t0;
	assign t0 = r5;
	wire [`DATA_WIDTH-1:0] t1;
	assign t1 = r6;
	wire [`DATA_WIDTH-1:0] t2;
	assign t2 = r7;
	wire [`DATA_WIDTH-1:0] s0;
	assign s0 = r8;
	wire [`DATA_WIDTH-1:0] fp;
	assign fp = r8;
	wire [`DATA_WIDTH-1:0] s1;
	assign s1 = r9;
	wire [`DATA_WIDTH-1:0] a0;
	assign a0 = r10;
	wire [`DATA_WIDTH-1:0] a1;
	assign a1 = r11;
	wire [`DATA_WIDTH-1:0] a2;
	assign a2 = r12;
	wire [`DATA_WIDTH-1:0] a3;
	assign a3 = r13;
	wire [`DATA_WIDTH-1:0] a4;
	assign a4 = r14;
	wire [`DATA_WIDTH-1:0] a5;
	assign a5 = r15;
	wire [`DATA_WIDTH-1:0] a6;
	assign a6 = r16;
	wire [`DATA_WIDTH-1:0] a7;
	assign a7 = r17;
	wire [`DATA_WIDTH-1:0] s2;
	assign s2 = r18;
	wire [`DATA_WIDTH-1:0] s3;
	assign s3 = r19;
	wire [`DATA_WIDTH-1:0] s4;
	assign s4 = r20;
	wire [`DATA_WIDTH-1:0] s5;
	assign s5 = r21;
	wire [`DATA_WIDTH-1:0] s6;
	assign s6 = r22;
	wire [`DATA_WIDTH-1:0] s7;
	assign s7 = r23;
	wire [`DATA_WIDTH-1:0] s8;
	assign s8 = r24;
	wire [`DATA_WIDTH-1:0] s9;
	assign s9 = r25;
	wire [`DATA_WIDTH-1:0] s10;
	assign s10 = r26;
	wire [`DATA_WIDTH-1:0] s11;
	assign s11 = r27;
	wire [`DATA_WIDTH-1:0] t3;
	assign t3 = r28;
	wire [`DATA_WIDTH-1:0] t4;
	assign t4 = r29;
	wire [`DATA_WIDTH-1:0] t5;
	assign t5 = r30;
	wire [`DATA_WIDTH-1:0] t6;
	assign t6 = r31;

	//Read output logic
	always @(*) begin : outputMux_proc
		case (readA_select)
			0 : readA_out = r0;
			1 : readA_out = r1;
			2 : readA_out = r2;
			3 : readA_out = r3;
			4 : readA_out = r4;
			5 : readA_out = r5;
			6 : readA_out = r6;
			7 : readA_out = r7;
			8 : readA_out = r8;
			9 : readA_out = r9;
			10 : readA_out = r10;
			11 : readA_out = r11;
			12 : readA_out = r12;
			13 : readA_out = r13;
			14 : readA_out = r14;
			15 : readA_out = r15;
			16 : readA_out = r16;
			17 : readA_out = r17;
			18 : readA_out = r18;
			19 : readA_out = r19;
			20 : readA_out = r20;
			21 : readA_out = r21;
			22 : readA_out = r22;
			23 : readA_out = r23;
			24 : readA_out = r24;
			25 : readA_out = r25;
			26 : readA_out = r26;
			27 : readA_out = r27;
			28 : readA_out = r28;
			29 : readA_out = r29;
			30 : readA_out = r30;
			31 : readA_out = r31;
		endcase // readA_select

		case (readB_select)
			0 : readB_out = r0;
			1 : readB_out = r1;
			2 : readB_out = r2;
			3 : readB_out = r3;
			4 : readB_out = r4;
			5 : readB_out = r5;
			6 : readB_out = r6;
			7 : readB_out = r7;
			8 : readB_out = r8;
			9 : readB_out = r9;
			10 : readB_out = r10;
			11 : readB_out = r11;
			12 : readB_out = r12;
			13 : readB_out = r13;
			14 : readB_out = r14;
			15 : readB_out = r15;
			16 : readB_out = r16;
			17 : readB_out = r17;
			18 : readB_out = r18;
			19 : readB_out = r19;
			20 : readB_out = r20;
			21 : readB_out = r21;
			22 : readB_out = r22;
			23 : readB_out = r23;
			24 : readB_out = r24;
			25 : readB_out = r25;
			26 : readB_out = r26;
			27 : readB_out = r27;
			28 : readB_out = r28;
			29 : readB_out = r29;
			30 : readB_out = r30;
			31 : readB_out = r31;
		endcase // readA_select
	end

	//Register write logic
	always @(posedge clk) begin : registerWrite_proc
		if (reset) begin
			r1 <= 0;
			r2 <= 0;
			r3 <= 0;
			r4 <= 0;
			r5 <= 0;
			r6 <= 0;
			r7 <= 0;
			r8 <= 0;
			r9 <= 0;
			r10 <= 0;
			r11 <= 0;
			r12 <= 0;
			r13 <= 0;
			r14 <= 0;
			r15 <= 0;
			r16 <= 0;
			r17 <= 0;
			r18 <= 0;
			r19 <= 0;
			r20 <= 0;
			r21 <= 0;
			r22 <= 0;
			r23 <= 0;
			r24 <= 0;
			r25 <= 0;
			r26 <= 0;
			r27 <= 0;
			r28 <= 0;
			r29 <= 0;
			r30 <= 0;
			r31 <= 0;
		end else begin
			if (writeEnable && (writeSelect==1)) r1 <= dataIn;
			if (writeEnable && (writeSelect==2)) r2 <= dataIn;
			if (writeEnable && (writeSelect==3)) r3 <= dataIn;
			if (writeEnable && (writeSelect==4)) r4 <= dataIn;
			if (writeEnable && (writeSelect==5)) r5 <= dataIn;
			if (writeEnable && (writeSelect==6)) r6 <= dataIn;
			if (writeEnable && (writeSelect==7)) r7 <= dataIn;
			if (writeEnable && (writeSelect==8)) r8 <= dataIn;
			if (writeEnable && (writeSelect==9)) r9 <= dataIn;
			if (writeEnable && (writeSelect==10)) r10 <= dataIn;
			if (writeEnable && (writeSelect==11)) r11 <= dataIn;
			if (writeEnable && (writeSelect==12)) r12 <= dataIn;
			if (writeEnable && (writeSelect==13)) r13 <= dataIn;
			if (writeEnable && (writeSelect==14)) r14 <= dataIn;
			if (writeEnable && (writeSelect==15)) r15 <= dataIn;
			if (writeEnable && (writeSelect==16)) r16 <= dataIn;
			if (writeEnable && (writeSelect==17)) r17 <= dataIn;
			if (writeEnable && (writeSelect==18)) r18 <= dataIn;
			if (writeEnable && (writeSelect==19)) r19 <= dataIn;
			if (writeEnable && (writeSelect==20)) r20 <= dataIn;
			if (writeEnable && (writeSelect==21)) r21 <= dataIn;
			if (writeEnable && (writeSelect==22)) r22 <= dataIn;
			if (writeEnable && (writeSelect==23)) r23 <= dataIn;
			if (writeEnable && (writeSelect==24)) r24 <= dataIn;
			if (writeEnable && (writeSelect==25)) r25 <= dataIn;
			if (writeEnable && (writeSelect==26)) r26 <= dataIn;
			if (writeEnable && (writeSelect==27)) r27 <= dataIn;
			if (writeEnable && (writeSelect==28)) r28 <= dataIn;
			if (writeEnable && (writeSelect==29)) r29 <= dataIn;
			if (writeEnable && (writeSelect==30)) r30 <= dataIn;
			if (writeEnable && (writeSelect==31)) r31 <= dataIn;
		end
	end

endmodule
//Include dependencies


module flipSign (
	input [`DATA_WIDTH-1:0] operand,
	input flip,

	output reg [`DATA_WIDTH-1:0] result
	);

	wire [`DATA_WIDTH-1:0] flipExtended;
	assign flipExtended = {`DATA_WIDTH{flip}};

	always @(*) begin : adder_proc
		if (flip) result = (operand ^ flipExtended) + 1;
		else  result = operand;
	end
endmodule


module absoluteValue (
	input [`DATA_WIDTH-1:0] operand,
	input unsignedEn,

	output wire [`DATA_WIDTH-1:0] result,
	output wire isNegative
	);

	wire msb;
	assign msb = operand[`DATA_WIDTH-1];

	assign isNegative = msb && ~unsignedEn;

	flipSign flipSign(
		.operand(operand),
		.flip(isNegative),

		.result(result)
		);
endmodule


module adder (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,
	input subtract,

	output reg [`DATA_WIDTH-1:0] result
	);

	always @(*) begin : adder_proc
		if (~subtract) result = aOperand + bOperand;
		else result = aOperand - bOperand;
	end

endmodule


module multipler (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,

	output reg [`DATA_WIDTH-1:0] result
	);

	always @(*) begin : mul_proc
		result = aOperand * bOperand;
	end

endmodule


module divider (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,
	input unsignedEn,

	output wire [`DATA_WIDTH-1:0] divResult,
	output wire [`DATA_WIDTH-1:0] remResult
	);

	//Get absolute val of A
	wire [`DATA_WIDTH-1:0] aOp_abs;
	wire a_isNegative;
	absoluteValue absoluteValue_A(
		.operand(aOperand),
		.unsignedEn(unsignedEn),

		.result(aOp_abs),
		.isNegative(a_isNegative)
		);

	//Get absolute val of B
	wire [`DATA_WIDTH-1:0] bOp_abs;
	wire b_isNegative;
	absoluteValue absoluteValue_B(
		.operand(bOperand),
		.unsignedEn(unsignedEn),

		.result(bOp_abs),
		.isNegative(b_isNegative)
		);

	//Unisgned divider outputs
	reg [`DATA_WIDTH-1:0] divuResult;
	reg [`DATA_WIDTH-1:0] remuResult;

	//Flip sign of div outputs
	wire divFlip;
	assign divFlip = a_isNegative ^ b_isNegative;

	flipSign flipSign_div(
		.operand(divuResult),
		.flip(divFlip),

		.result(divResult)
		);

	//Flip sign of rem outputs	
	flipSign flipSign_rem(
		.operand(remuResult),
		.flip(a_isNegative),

		.result(remResult)
		);

	always @(*) begin : divider_proc
		divuResult = aOp_abs / bOp_abs;
		remuResult = aOp_abs % bOp_abs;
	end

endmodule


module comparator (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,
	input unsignedEn,

	output reg [`DATA_WIDTH-1:0] greater,
	output reg [`DATA_WIDTH-1:0] equal,
	output reg [`DATA_WIDTH-1:0] less
	);
	
	//<TODO> properly handle the signs of the operands. Right now it only does unsigned comparisons

	always @(*) begin : comparator_proc
		greater = aOperand > bOperand;
		equal = aOperand == bOperand;
		less = aOperand < bOperand;
	end

endmodule


module core(
	//Inputs
	input clk,
	input reset,
	input [`INSTRUCTION_WIDTH-1:0] instructionIn,
	input start,

	//Outputs
	output wire busy,
	output wire [`DATA_WIDTH-1:0] tempRegOut
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

	assign tempRegOut = readA_regOut;

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
