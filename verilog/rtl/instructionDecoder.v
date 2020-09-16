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
	output reg error,
	output reg pcOverwrite,
	output reg [2:0] branchType,
	output wire jumpInstruction,
	output wire load,
	output reg loadUnsigned,
	output wire store,
	output reg [1:0] memLength
	);

	//Wires to separate instruction fields
	`define OPCODE_WIDTH 7
	`define FUNCT3_WIDTH 3
	`define FUNCT7_WIDTH 7
	`define IMM_WIDTH 12

	//I-type parsing
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

	//B-type parsing
	wire immB_11;
	wire [3:0] imm_4_1;
	wire [5:0] imm_10_5;
	wire imm_12;

	assign immB_11 = instructionIn[7];
	assign imm_4_1 = instructionIn[11:8];
	assign imm_10_5 = instructionIn[30:25];
	assign imm_12 = instructionIn[31];

	//J-type parsing
	wire [7:0] imm_19_12;
	wire immJ_11;
	wire [9:0] imm_10_1;
	wire imm_20;

	assign imm_19_12 = instructionIn[19:12];
	assign immJ_11 = instructionIn[20];
	assign imm_10_1 = instructionIn[30:21];
	assign imm_20 = instructionIn[31];

	//S-type parsing
	wire [4:0] imm_4_0;
	wire [6:0] imm_11_5;

	assign imm_4_0 = instructionIn[11:7];
	assign imm_11_5 = instructionIn[31:25];


	//Hardcoded values of supported opcodes and functions
	
	//Opcodes
	`define OP_IMM 7'h13
	`define OP 7'h33
	`define OP_JAL 7'h6f
	`define OP_BRANCH 7'h63
	`define OP_LOAD 7'h3
	`define OP_STORE 7'h23

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
	`define BEQ_F3 3'h0
	`define BNE_F3 3'h1
	`define BLT_F3 3'h4
	`define BGE_F3 3'h5
	`define BLTU_F3 3'h6
	`define BGEU_F3 3'h7
	`define LW_F3 3'h2
	`define LH_F3 3'h1
	`define LHU_F3 3'h5
	`define LB_F3 3'h0
	`define LBU_F3 3'h4
	`define SW_F3 3'h2
	`define SH_F3 3'h1
	`define SB_F3 3'h0

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
	reg jal_flag;
	assign jumpInstruction = jal_flag;
	reg beq_flag;
	reg bne_flag;
	reg blt_flag;
	reg bge_flag;
	reg bltu_flag;
	reg bgeu_flag;
	reg load_flag;
	assign load = load_flag;
	reg lbu_flag;
	reg lhu_flag;
	reg lb_flag;
	reg lh_flag;
	reg lw_flag;
	reg store_flag;
	assign store = store_flag;
	reg sb_flag;
	reg sh_flag;
	reg sw_flag;

	//Misc vars
	reg bType_flag;
	reg [2:0] bTypeEncode;

	//Decode logic
	`define IMM_EXTEN_WIDTH_I 20
	`define IMM_EXTEN_WIDTH_B 19
	`define IMM_EXTEN_WIDTH_J 11
	`define IMM_EXTEN_WIDTH_S 20
	reg [7:0] resultEncoderInput;
	reg [7:0] branchEncoderInput;

	reg [`DATA_WIDTH-1:0] immediateVal_Itype;
	reg [`DATA_WIDTH-1:0] immediateVal_Btype;
	reg [`DATA_WIDTH-1:0] immediateVal_Jtype;
	reg [`DATA_WIDTH-1:0] immediateVal_Stype;

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
		jal_flag = (opcode == `OP_JAL);
		beq_flag = (opcode == `OP_BRANCH) && (funct3 == `BEQ_F3);
		bne_flag = (opcode == `OP_BRANCH) && (funct3 == `BNE_F3);
		blt_flag = (opcode == `OP_BRANCH) && (funct3 == `BLT_F3);
		bge_flag = (opcode == `OP_BRANCH) && (funct3 == `BGE_F3);
		bltu_flag = (opcode == `OP_BRANCH) && (funct3 == `BLTU_F3);
		bgeu_flag = (opcode == `OP_BRANCH) && (funct3 == `BGEU_F3);

		//Set branch flag
		bType_flag = (opcode == `OP_BRANCH);

		///////////////
		//Determine output control signals
		///////////////
		a_location = rs1;
		b_location = rs2;

		//Determine immediateVal
		immediateSelect = addi_flag || slti_flag || sltiu_flag || jal_flag || bType_flag || load_flag || store_flag;
		immediateVal_Itype = { {`IMM_EXTEN_WIDTH_I{imm[`IMM_WIDTH-1]}}, imm[`IMM_WIDTH-1:0] };  //sign extend immediate value for I-type instructions
		immediateVal_Btype = { {`IMM_EXTEN_WIDTH_B{imm_12}}, imm_12, immB_11, imm_10_5, imm_4_1, 1'b0 };  //contruct and sign extend immediate value for B-type instructions
		immediateVal_Jtype = { {`IMM_EXTEN_WIDTH_J{imm_20}}, imm_20, imm_19_12, immJ_11, imm_10_1, 1'b0 };  //contruct and sign extend immediate value for J-type instructions
		immediateVal_Stype = { {`IMM_EXTEN_WIDTH_S{imm_11_5[6]}}, imm_11_5, imm_4_0,};  //contruct and sign extend immediate value for S-type instructions

		if (jal_flag) immediateVal = immediateVal_Jtype;
		else if (bType_flag) immediateVal = immediateVal_Btype;
		else if (store_flag) immediateVal = immediateVal_Stype;
		else immediateVal = immediateVal_Itype;


		unsignedSelect = divu_flag || remu_flag || sltiu_flag || sltu_flag || bltu_flag || bgeu_flag;
		subtractEnable = sub_flag;
		writeSelect = rd;
		writeEnable = ~(bType_flag || store_flag);

		//result select encoder
		resultEncoderInput = {1'b0, (slti_flag || sltiu_flag ||  slt_flag || sltu_flag), 1'b0, 1'b0, (remu_flag || rem_flag), (div_flag || divu_flag), mul_flag, (addi_flag || add_flag || sub_flag || bType_flag || jal_flag || store_flag || load_flag)};
		case (resultEncoderInput)
			8'b00000001 : resultSelect = 0;
			8'b00000010 : resultSelect = 1;
			8'b00000100 : resultSelect = 2;
			8'b00001000 : resultSelect = 3;
			8'b00010000 : resultSelect = 4;
			8'b00100000 : resultSelect = 5;
			8'b01000000 : resultSelect = 6;
			8'b10000000 : resultSelect = 7;

			default : resultSelect = 0;
		endcase // resultEncoderInput

		pcOverwrite = jal_flag || bType_flag;

		//branch type encoder
		branchEncoderInput = {1'b0, bgeu_flag, bltu_flag, bge_flag, blt_flag, bne_flag, beq_flag, ~(bgeu_flag || bltu_flag || bge_flag || blt_flag || bne_flag || beq_flag)};
		case (branchEncoderInput)
			8'b00000001 : branchType = 0;
			8'b00000010 : branchType = 1;
			8'b00000100 : branchType = 2;
			8'b00001000 : branchType = 3;
			8'b00010000 : branchType = 4;
			8'b00100000 : branchType = 5;
			8'b01000000 : branchType = 6;
			8'b10000000 : branchType = 7;

			default : branchType = 0;
		endcase // branchEncoderInput

		//Load unsigned parsing
		loadUnsigned = lbu_flag || lhu_flag;

		//Determine length of memory access
		if (lhu_flag || lh_flag || sh_flag) memLength = 1;
		else if (lw || sw) memLength = 3;
		else memLength = 0;
	end

endmodule //instructionDecoder