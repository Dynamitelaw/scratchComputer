`include "../../../rtl/globalVariables.v"
`include "../../../rtl/socTop.v"

//  Nomenclature for the segments on this board is:
//
//          0
//        -----
//       |     |
//      5|     | 1
//       |  6  |
//        -----
//       |     |
//      4|     | 2
//       |     |
//        ----- 
//          3
//
//  The above is used to define the ordering of the bits returned
//  by the function 'segments' below.
//
//  A bit surprisingly, the DE10-Lite's six 7 segment displays are not
//  multiplexed.  Each segment on each LED has its own dedicated FPGA
//  pin.  I guess the board designers thought that they have so many pins 
//  on the FPGA, that it wasn't worth bothering to save pins.  (The 
//  Altera Max 10 on this board does have over 300 pins.)

module DE10_LITE_Golden_Top(

	//////////// CLOCK //////////
	input 		          		ADC_CLK_10,
	input 		          		MAX10_CLK1_50,
	input 		          		MAX10_CLK2_50,

	//////////// SDRAM //////////
	output		    [12:0]		DRAM_ADDR,
	output		     [1:0]		DRAM_BA,
	output		          		DRAM_CAS_N,
	output		          		DRAM_CKE,
	output		          		DRAM_CLK,
	output		          		DRAM_CS_N,
	inout 		    [15:0]		DRAM_DQ,
	output		          		DRAM_LDQM,
	output		          		DRAM_RAS_N,
	output		          		DRAM_UDQM,
	output		          		DRAM_WE_N,

	//////////// SEG7 //////////
	output		     [7:0]		HEX0,
	output		     [7:0]		HEX1,
	output		     [7:0]		HEX2,
	output		     [7:0]		HEX3,
	output		     [7:0]		HEX4,
	output		     [7:0]		HEX5,

	//////////// KEY //////////
	input 		     [1:0]		KEY,

	//////////// LED //////////
	output		     [9:0]		LEDR,

	//////////// SW //////////
	input 		     [9:0]		SW,

	//////////// VGA //////////
	output		     [3:0]		VGA_B,
	output		     [3:0]		VGA_G,
	output		          		VGA_HS,
	output		     [3:0]		VGA_R,
	output		          		VGA_VS,

	//////////// Accelerometer //////////
	output		          		GSENSOR_CS_N,
	input 		     [2:1]		GSENSOR_INT,
	output		          		GSENSOR_SCLK,
	inout 		          		GSENSOR_SDI,
	inout 		          		GSENSOR_SDO,

	//////////// Arduino //////////
	inout 		    [15:0]		ARDUINO_IO,
	inout 		          		ARDUINO_RESET_N,

	//////////// GPIO, GPIO connect to GPIO Default //////////
	inout 		    [35:0]		GPIO
);

//=======================================================
//  Hex outputs
//=======================================================
//Map hex outputs
wire [3:0] segmentValues [5:0];
reg [7:0] segmentOutputs [5:0];


assign segmentValues[0] = 4'h2;
assign segmentValues[1] = 4'h4;
assign segmentValues[2] = 4'h2;
assign segmentValues[3] = 4'h4;
assign segmentValues[4] = 4'h2;
assign segmentValues[5] = 4'h4;


assign HEX0 = segmentOutputs[0];
assign HEX1 = segmentOutputs[1];
assign HEX2 = segmentOutputs[2];
assign HEX3 = segmentOutputs[3];
assign HEX4 = segmentOutputs[4];
assign HEX5 = segmentOutputs[5];

integer i;
always @(*) begin 
	for (i = 0; i < 6; i = i+1) begin
		case (segmentValues[i])         // 654 3210 <----- Bit positions based on
			4'h0   : segmentOutputs[i] = ~7'b011_1111;   //  numbering in comments at
			4'h1   : segmentOutputs[i] = ~7'b000_0110;   //  top of this module.
			4'h2   : segmentOutputs[i] = ~7'b101_1011;
			4'h3   : segmentOutputs[i] = ~7'b100_1111;
			4'h4   : segmentOutputs[i] = ~7'b110_0110;
			4'h5   : segmentOutputs[i] = ~7'b110_1101;
			4'h6   : segmentOutputs[i] = ~7'b111_1101;
			4'h7   : segmentOutputs[i] = ~7'b000_0111;
			4'h8   : segmentOutputs[i] = ~7'b111_1111;
			4'h9   : segmentOutputs[i] = ~7'b110_1111;
			4'hA   : segmentOutputs[i] = ~7'b111_0111;
			4'hB   : segmentOutputs[i] = ~7'b111_1100;
			4'hC   : segmentOutputs[i] = ~7'b011_1001;
			4'hD   : segmentOutputs[i] = ~7'b101_1110;
			4'hE   : segmentOutputs[i] = ~7'b111_1001;
			4'hF   : segmentOutputs[i] = ~7'b111_0001;
			default: segmentOutputs[i] = ~7'b100_0000;
		endcase
	end
end

endmodule
