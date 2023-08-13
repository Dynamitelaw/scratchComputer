
//=======================================================
//  This code is generated by Terasic System Builder
//=======================================================

module DE10_LITE_SDRAM_RTL_Test(

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
	inout 		          		ARDUINO_RESET_N
);



//=======================================================
//  REG/WIRE declarations
//=======================================================

reg  [15:0]  writedata;
wire  [15:0]  readdata;
reg          write;
reg          read;
wire          clk_test;
assign clk_test = MAX10_CLK1_50;
reg [24:0] readAddress;
reg [24:0] writeAddress;


//=======================================================
//  Structural coding
//=======================================================

//	SDRAM frame buffer
reg reset_n;
Sdram_Control	u1	(	//	HOST Side
						   .REF_CLK(MAX10_CLK1_50),
					      .RESET_N(reset_n),
							//	FIFO Write Side 
						   .WR_DATA(writedata),
							.WR(write),
							.WR_ADDR(0),
							.WR_MAX_ADDR(25'h1ffffff),		//	
							.WR_LENGTH(9'h80),
							.WR_LOAD(0),
							.WR_CLK(clk_test),
							//	FIFO Read Side 
						   .RD_DATA(readdata),
				        	.RD(read),
				        	.RD_ADDR(readAddress),			//	Read odd field and bypess blanking
							.RD_MAX_ADDR(25'h1ffffff),
							.RD_LENGTH(9'h80),
				        	.RD_LOAD(0),
							.RD_CLK(clk_test),
                     //	SDRAM Side
						   .SA(DRAM_ADDR),
						   .BA(DRAM_BA),
						   .CS_N(DRAM_CS_N),
						   .CKE(DRAM_CKE),
						   .RAS_N(DRAM_RAS_N),
				         .CAS_N(DRAM_CAS_N),
				         .WE_N(DRAM_WE_N),
						   .DQ(DRAM_DQ),
				         .DQM({DRAM_UDQM,DRAM_LDQM}),
							.SDR_CLK(DRAM_CLK)	);

/*
pll_test u2(
	.areset(),
	.inclk0(MAX10_CLK2_50),
	.c0(clk_test),
	.locked());	
*/
	
//====================================================================================
wire reset;
assign reset = KEY[0];

wire writeButton;
assign writeButton = ~KEY[1];

/*
always @(posedge clk_test) begin
	if (~reset_n) begin
		writedata <= 0;
		write <= 0;
	end
	else begin
		if (writeButton) begin
			writedata <= 16'h4242;
			write <= 1;
		end
		else begin
			write <= 0;
			read <= 1;
		end
	end
end
*/
reg [32:0] clockCounter;

always @(posedge MAX10_CLK1_50) begin
	if (reset) begin
		clockCounter <= 0;
	end
	else begin
		clockCounter <= clockCounter + 1;
	end
end

reg [4:0] testState;
`define RESET_STATE 0
`define WRITE_LAUNCH 1
`define WRITE_WAIT 2
`define READ_LAUNCH 3
`define READ_WAIT 4
`define READ_DONE 5

reg [23:0] readStartCounter;
reg [23:0] readEndCounter;
reg [23:0] counterDifference;
always @(posedge MAX10_CLK1_50) begin
	if (reset) begin
		testState <= `RESET_STATE;
		counterDifference <= 24'h00dead;
	end
	else begin
		case (testState)
			`RESET_STATE : begin
				reset_n <= 0;

				writedata <= 0;
				writeAddress <= 0;
				write <= 0;

				readAddress <= 0;
				read <= 0;

				if (clockCounter == 2) testState <= `WRITE_LAUNCH;
			end
			`WRITE_LAUNCH : begin
				reset_n <= 1;

				writedata <= 16'h4242;
				writeAddress <= 25'h1234;
				write <= 1;

				readAddress <= 0;
				read <= 0;

				testState <= `WRITE_WAIT;
			end
			`WRITE_WAIT : begin
				reset_n <= 1;

				writedata <= 16'h4242;
				writeAddress <= 25'h1234;
				write <= 0;

				readAddress <= 0;
				read <= 0;

				if (clockCounter == 20) testState <= `READ_LAUNCH;
			end
			`READ_LAUNCH : begin
				reset_n <= 1;

				writedata <= 0;
				writeAddress <= 0;
				write <= 0;

				readAddress <= 25'h1234;
				read <= 1;
				readStartCounter <= clockCounter;

				testState <= `READ_WAIT;
			end
			`READ_WAIT : begin
				reset_n <= 1;

				writedata <= 0;
				writeAddress <= 0;
				write <= 0;

				readAddress <= 25'h1234;
				read <= 0;

				if (readdata == 16'h4242) begin
					testState <= `READ_DONE;
					readEndCounter <= clockCounter;
				end
			end
			`READ_DONE : begin
				counterDifference <= readEndCounter - readStartCounter;
			end
		endcase
	end
end

wire [3:0] hexNibbles [3:0];
genvar nibbleId;
generate
	for(nibbleId = 0;nibbleId < 4; nibbleId = nibbleId + 1) begin : genNibbleOuts
		assign hexNibbles[nibbleId] = counterDifference[(nibbleId*4)+3:nibbleId*4];
	end
endgenerate

//Map hex outputs
wire [3:0] segmentValues [5:0];
reg [7:0] segmentOutputs [5:0];


//assign segmentValues[0] = hexNibbles[0];
//assign segmentValues[1] = hexNibbles[1];
//assign segmentValues[2] = hexNibbles[2];
//assign segmentValues[3] = hexNibbles[3];
//assign segmentValues[4] = 4'h0;
//assign segmentValues[5] = 4'h0;

wire [3:0] hexValues [15:0];
assign hexValues[0] = 4'h0;
assign hexValues[1] = 4'h1;
assign hexValues[2] = 4'h2;
assign hexValues[3] = 4'h3;
assign hexValues[4] = 4'h4;
assign hexValues[5] = 4'h5;
assign hexValues[6] = 4'h6;
assign hexValues[7] = 4'h7;
assign hexValues[8] = 4'h8;
assign hexValues[9] = 4'h9;
assign hexValues[10] = 4'hA;
assign hexValues[11] = 4'hB;
assign hexValues[12] = 4'hC;
assign hexValues[13] = 4'hD;
assign hexValues[14] = 4'hE;
assign hexValues[15] = 4'hF;

wire [6:0] segmentOptions [15:0];
assign segmentOptions[0] = ~7'b1000000;
assign segmentOptions[1] = ~7'b01000000;
assign segmentOptions[2] = ~7'b0010000;
assign segmentOptions[3] = ~7'b0001000;
assign segmentOptions[4] = ~7'b0000100;
assign segmentOptions[5] = ~7'b0000010;
assign segmentOptions[6] = ~7'b0000001;
assign segmentOptions[7] = ~7'b0000000;
assign segmentOptions[8] = ~7'b1000000;
assign segmentOptions[9] = ~7'b01000000;
assign segmentOptions[10] = ~7'b0010000;
assign segmentOptions[11] = ~7'b0001000;
assign segmentOptions[12] = ~7'b0000100;
assign segmentOptions[13] = ~7'b0000010;
assign segmentOptions[14] = ~7'b0000001;
assign segmentOptions[15] = ~7'b0000000;

reg [26:0] clockCounter2;
wire superSlowClock;
assign superSlowClock = clockCounter2[26];
always @(posedge MAX10_CLK1_50) begin
	clockCounter2 <= clockCounter2 + 1;
end

reg [3:0] selectedValue;
always @(posedge superSlowClock) begin
	selectedValue <= selectedValue + 1;
end

assign segmentValues[0] = hexValues[selectedValue];
assign segmentValues[1] = hexValues[selectedValue];
assign segmentValues[2] = hexValues[selectedValue];
assign segmentValues[3] = hexValues[selectedValue];
assign segmentValues[4] = hexValues[selectedValue];
assign segmentValues[5] = hexValues[selectedValue];


//assign HEX0 = segmentOutputs[0];
//assign HEX1 = segmentOutputs[1];
//assign HEX2 = segmentOutputs[2];
//assign HEX3 = ~7'b1001111;
//assign HEX4 = ~7'b1001111;
//assign HEX5 = segmentOutputs[5];

assign HEX0 = segmentOptions[selectedValue];
assign HEX1 = segmentOptions[selectedValue];
assign HEX2 = segmentOptions[selectedValue];
assign HEX3 = segmentOptions[selectedValue];
assign HEX4 = segmentOptions[selectedValue];
assign HEX5 = segmentOptions[selectedValue];

integer i;
always @(*) begin 
	for (i = 0; i < 6; i = i+1) begin
		case (segmentValues[i])         // 654 3210 <----- Bit positions based on
			4'h0   : segmentOutputs[i] = ~7'b0111111;   //  numbering in comments at
			4'h1   : segmentOutputs[i] = ~7'b0000110;   //  top of this module.
			4'h2   : segmentOutputs[i] = ~7'b1011011;
			4'h3   : segmentOutputs[i] = ~7'b1001111;
			4'h4   : segmentOutputs[i] = ~7'b1100110;
			4'h5   : segmentOutputs[i] = ~7'b1101101;
			4'h6   : segmentOutputs[i] = ~7'b1111101;
			4'h7   : segmentOutputs[i] = ~7'b0000111;
			4'h8   : segmentOutputs[i] = ~7'b1111111;
			4'h9   : segmentOutputs[i] = ~7'b1101111;
			4'hA   : segmentOutputs[i] = ~7'b1110111;
			4'hB   : segmentOutputs[i] = ~7'b1111100;
			4'hC   : segmentOutputs[i] = ~7'b0111001;
			4'hD   : segmentOutputs[i] = ~7'b1011110;
			4'hE   : segmentOutputs[i] = ~7'b1111001;
			4'hF   : segmentOutputs[i] = ~7'b1110001;
			default: segmentOutputs[i] = ~7'b1000000;
		endcase
	end
end

endmodule
