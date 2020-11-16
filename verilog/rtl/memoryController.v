//Include dependencies
`include "globalVariables.v"


module memoryController(
	input clk,
	input reset,

	//CPU interface
	input [`DATA_WIDTH-1:0] addressIn,
	input [`DATA_WIDTH-1:0] dataWriteIn,
	input [1:0] length,
	input storeIn,
	input loadIn,
	input loadUnsigned,
	output wire [`DATA_WIDTH-1:0] dataReadOut,

	//RAM interface
	input [`DATA_WIDTH-1:0] ramDataRead,
	output wire [`DATA_WIDTH-1:0] addressOut,
	output wire [`DATA_WIDTH-1:0] ramDataWrite,
	output wire [3:0] byteSelect,
	output wire ramStore,
	output wire ramLoad
	);

	//Buffer input signals with latches
	reg [`DATA_WIDTH-1:0] addressIn_latch;
	reg [`DATA_WIDTH-1:0] dataWriteIn_latch;
	reg [1:0] length_latch;
	reg loadUnsigned_latch;

	always @(*) begin : inputBuffer_proc
		if (storeIn || loadIn || reset) begin
			addressIn_latch = addressIn;
			dataWriteIn_latch = dataWriteIn;
			length_latch = length;
			loadUnsigned_latch = loadUnsigned;
		end
	end

	assign addressOut = addressIn_latch;
	assign ramStore = storeIn;
	assign ramLoad = loadIn;

	wire [1:0] addressLower;
	assign addressLower = addressIn_latch[1:0];

	//Determine which bytes to write
	reg B0_write;
	reg B1_write;
	reg B2_write;
	reg B3_write;
	assign byteSelect = {B3_write, B2_write, B1_write, B0_write};

	always @(*) begin : byteSelect_proc
		B0_write = (addressLower == 0);
		B1_write = (addressLower == 1) || ((addressLower == 0) && (length_latch > 0));
		B2_write = (addressLower == 2) || ((addressLower == 0) && (length_latch == 3));
		B3_write = (addressLower == 3) || ((addressLower == 2) && (length_latch == 1)) || ((addressLower == 0) && (length_latch == 3));
	end

	//Rearrange data to RAM based on length_latch and address
	wire [7:0] input_byte0;
	assign input_byte0 = dataWriteIn_latch[7:0];
	wire [7:0] input_byte1;
	assign input_byte1 = dataWriteIn_latch[15:8];
	wire [7:0] input_byte2;
	assign input_byte2 = dataWriteIn_latch[23:16];
	wire [7:0] input_byte3;
	assign input_byte3 = dataWriteIn_latch[31:24];

	reg [7:0] ramIn_byte0;
	reg [7:0] ramIn_byte1;
	reg [7:0] ramIn_byte2;
	reg [7:0] ramIn_byte3;
	assign ramDataWrite = {ramIn_byte3, ramIn_byte2, ramIn_byte1, ramIn_byte0};

	reg ri1_B0select;
	reg ri1_B1select;
	reg ri2_B0select;
	reg ri2_B2select;
	reg ri3_B0select;
	reg ri3_B1select;
	reg ri3_B3select;

	always @(*) begin : dataWriteRearrange_proc
		//Byte0
		if (addressLower == 0) ramIn_byte0 = input_byte0;
		else ramIn_byte0 = 0;

		//Byte1
		ri1_B0select = (addressLower == 1);
		ri1_B1select = (addressLower == 0) && (length_latch > 0);

		if (ri1_B0select) ramIn_byte1 = input_byte0;
		else if (ri1_B1select) ramIn_byte1 = input_byte1;
		else ramIn_byte1 = 0;

		//Byte2
		ri2_B0select = (addressLower == 2);
		ri2_B2select = (addressLower == 0) && (length_latch == 3);

		if (ri2_B0select) ramIn_byte2 = input_byte0;
		else if (ri2_B2select) ramIn_byte2 = input_byte2;
		else ramIn_byte2 = 0;

		//Byte 3
		ri3_B0select = (addressLower == 3);
		ri3_B1select = (addressLower == 2) && (length_latch == 1);
		ri3_B3select = (addressLower == 0) && (length_latch == 3);

		if (ri3_B0select) ramIn_byte3 = input_byte0;
		else if (ri3_B1select) ramIn_byte3 = input_byte1;
		else if (ri3_B3select) ramIn_byte3 = input_byte3;
		else ramIn_byte3 = 0;
	end


	//Rearrange and sign extend ram data read based on length_latch
	wire [7:0] ramRead_byte0;
	assign ramRead_byte0 = ramDataRead[7:0];
	wire [7:0] ramRead_byte1;
	assign ramRead_byte1 = ramDataRead[15:8];
	wire [7:0] ramRead_byte2;
	assign ramRead_byte2 = ramDataRead[23:16];
	wire [7:0] ramRead_byte3;
	assign ramRead_byte3 = ramDataRead[31:24];

	reg [7:0] readOut_byte0;
	reg [7:0] readOut_byte1;
	reg [7:0] readOut_byte2;
	reg [7:0] readOut_byte3;
	assign dataReadOut = {readOut_byte3, readOut_byte2, readOut_byte1, readOut_byte0};

	wire [7:0] byte0_extended;
	assign byte0_extended = {8{ramRead_byte0[7] && ~loadUnsigned_latch}};
	wire [7:0] byte1_extended;
	assign byte1_extended = {8{ramRead_byte1[7] && ~loadUnsigned_latch}};
	wire [7:0] byte2_extended;
	assign byte2_extended = {8{ramRead_byte2[7] && ~loadUnsigned_latch}};

	always @(*) begin : signExten_proc
		//Byte0
		case (addressLower)
			0 : readOut_byte0 = ramRead_byte0;
			1 : readOut_byte0 = ramRead_byte1;
			2 : readOut_byte0 = ramRead_byte2;
			3 : readOut_byte0 = ramRead_byte3;
		endcase // addressLower

		//Byte1
		if ((addressLower==0) && (length_latch >= 1)) readOut_byte1 = ramRead_byte1;
		else if ((addressLower==2) && (length_latch==1)) readOut_byte1 = ramRead_byte3;
		else if ((addressLower==2) && (length_latch==0)) readOut_byte1 = byte2_extended;
		else readOut_byte1 = byte0_extended;

		//Byte2
		if ((addressLower==0) && (length_latch==3)) readOut_byte2 = ramRead_byte2;
		else if ((addressLower==0) && (length_latch==1)) readOut_byte2 = byte1_extended;
		else readOut_byte2 = byte0_extended;

		//Byte3
		if ((addressLower==0) && (length_latch==3)) readOut_byte3 = ramRead_byte3;
		else if ((addressLower==0) && (length_latch==1)) readOut_byte3 = byte1_extended;
		else if ((addressLower==2) && (length_latch==1)) readOut_byte3 = byte2_extended;
		else readOut_byte3 = byte0_extended;
	end

endmodule //memoryController