//Include dependencies
`include "globalVariables.v"

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

endmodule : instructionDecoder