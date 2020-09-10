//Include dependencies
`include "globalVariables.v"


module instructionFetchController(
	//Inputs
	input clk,
	input reset,
	input [`INSTRUCTION_WIDTH-1:0] memoryIn,
	input cir_writeEnable,
	input [`DATA_WIDTH-1:0] pcOverwrite,
	input pc_writeEnable,
	input [2:0] branchType,
	input jumpInst,
	input compareGreater,
	input compareEquals,
	input compareLess,

	//Outputs
	output reg [`INSTRUCTION_WIDTH-1:0] instructionOut,
	output reg [`DATA_WIDTH-1:0] programCounter,
	output wire [`DATA_WIDTH-1:0] programCounter_next
	);

	reg pcOverwriteEnable;
	assign programCounter_next = programCounter + 4;

	//Branch type flags
	reg [7:0] bTypeDecode_out;

	wire beqFlag;
	wire bneFlag;
	wire bltFlag;
	wire bgeFlag;
	wire bltuFlag;
	wire bgeuFlag;

	assign beqFlag = bTypeDecode_out[1];
	assign bneFlag = bTypeDecode_out[2];
	assign bltFlag = bTypeDecode_out[3];
	assign bgeFlag = bTypeDecode_out[4];
	assign bltuFlag = bTypeDecode_out[5];
	assign bgeuFlag = bTypeDecode_out[6];

	always @(*) begin : ifcCombinational_proc
		//Decode branchType
		case (branchType)
			0 : bTypeDecode_out = 8'b00000001;
			1 : bTypeDecode_out = 8'b00000010;
			2 : bTypeDecode_out = 8'b00000100;
			3 : bTypeDecode_out = 8'b00001000;
			4 : bTypeDecode_out = 8'b00010000;
			5 : bTypeDecode_out = 8'b00100000;
			6 : bTypeDecode_out = 8'b01000000;
			7 : bTypeDecode_out = 8'b10000000;
		endcase // branchType

		//Overwrite PC on jump instruction or true branch condition
		pcOverwriteEnable = jumpInst || (compareEquals && beqFlag) || (~compareEquals && bneFlag) || (compareLess && bltFlag) || (compareGreater && bgeFlag) || (compareLess && bltuFlag) || (compareGreater && bgeuFlag);
	end

	always @ (posedge clk) begin : ifcSeq_proc
		if (reset) begin
			//reset
			programCounter <= 0;
			instructionOut <= 0;
		end else begin
			if (cir_writeEnable) instructionOut <= memoryIn;
			
			if (pc_writeEnable) begin
				if (pcOverwriteEnable) programCounter <= pcOverwrite;
				else programCounter <= programCounter_next;
			end
		end
	end


endmodule  //instructionFetchController