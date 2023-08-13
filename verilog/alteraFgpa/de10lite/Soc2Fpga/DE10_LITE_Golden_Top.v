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

/*
//Use button 0 as reset
wire reset;
assign reset = ~KEY[0];

//Use button 1 as write enable
wire writeButton;
assign writeButton = ~KEY[1];

//Slow down clock

reg [8:0] clockCounter;
wire slowerClock;
assign slowerClock = clockCounter[8];
always @(posedge MAX10_CLK1_50) begin
	clockCounter <= clockCounter + 1;
end
*/
/*
wire slowerClock;
assign slowerClock = MAX10_CLK1_50;
*/
/*
reg slowerClock;
always @(posedge MAX10_CLK1_50) begin
	slowerClock <= ~slowerClock;
end
*/

//Instantate 32 bit RAM module
/*
wire [7:0]  ram_address;
wire [31:0] ram_data_in;
wire	  ram_wren;
wire	[31:0]  ram_data_out;
reg processingRead;

sdram32 RAM(
	.address(ram_address),
	.clock(MAX10_CLK1_50),
	.data(ram_data_in),
	.wren(ram_wren),
	.q(ram_data_out));

//Instantiate soc
wire [`DATA_WIDTH-1:0] ramDataRead;
wire [`DATA_WIDTH-1:0] ramAddress;
assign ram_address = ramAddress[9:2];
wire [`DATA_WIDTH-1:0] ramDataWrite;
wire [3:0] ramByteSelect;
wire ramStore;
wire ramLoad;
reg ramReadValid;

wire [`DATA_WIDTH-1:0] programCounter;

soc soc(
	.clk(slowerClock),
	.reset(reset),

	//Main memory interface
	.memDataRead(ram_data_out),
	.memReadValid(1'b1),
	.memAddress(ramAddress),
	.memDataWrite(ram_data_in),
	.memByteSelect(ramByteSelect),
	.memStore(ram_wren),
	.memLoad(ramLoad),

	//Test bench probes
	.programCounter(programCounter)
	);

//Wait for 32 cycles before ramRead is marked as valid
reg [4:0] readCycleCounter;
always @(posedge slowerClock) begin
	if (reset) begin
		processingRead <= 0;
		readCycleCounter <= 0;
		ramReadValid <= 0;
	end
	else begin
		if (ramLoad && ~processingRead) begin
			processingRead <= 1;
			readCycleCounter <= 0;
			ramReadValid <= 0;
		end
		else if (processingRead && (readCycleCounter == 31)) begin
				readCycleCounter <= 0;
				ramReadValid <= 1;
				processingRead <= 0;
		end
		else if (processingRead) begin
				readCycleCounter <= readCycleCounter +1;
		end
	end
end

//Capture write data coming from the SOC
reg [`DATA_WIDTH-1:0] coreDataWrite;
always @(posedge slowerClock) begin
	if (reset) coreDataWrite <= 0;
	else if (ram_wren) coreDataWrite <= ram_data_in;
end
*/
//=======================================================
//  Memory Interface
//=======================================================


//=======================================================
//  REG/WIRE declarations
//=======================================================

wire reset;
assign reset = ~KEY[0];
reg reset_n;
reg  [15:0]  writedata;
wire  [15:0]  readdata;
reg          write;
reg          read;
wire          clk_test;

reg [24:0] readAddress;
reg [24:0] writeAddress;

//=======================================================
//  Structural coding
//=======================================================

//	SDRAM frame buffer
Sdram_Control	u1	(	//	HOST Side
						   .REF_CLK(MAX10_CLK1_50),
					      .RESET_N(reset_n),
							//	FIFO Write Side 
						   .WR_DATA(writedata),
							.WR(write),
							.WR_ADDR(writeAddress),//.WR_ADDR(0),
							.WR_MAX_ADDR(25'h1ffffff),		//	
							.WR_LENGTH(9'h80),
							.WR_LOAD(!reset_n),
							.WR_CLK(clk_test),
							//	FIFO Read Side 
						   .RD_DATA(readdata),
				        	.RD(read),
				        	.RD_ADDR(readAddress), //.RD_ADDR(0),			//	Read odd field and bypess blanking
							.RD_MAX_ADDR(25'h1ffffff),
							.RD_LENGTH(9'h80),
				        	.RD_LOAD(!reset_n),
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


pll_test u2(
	.areset(),
	.inclk0(MAX10_CLK2_50),
	.c0(clk_test),
	.locked());


//=======================================================
//  Read/Write Test V2
//=======================================================
reg [31:0] clockCounter2;

always @(posedge MAX10_CLK1_50) begin
	if (reset) begin
		clockCounter2 <= 0;
	end
	else begin
		clockCounter2 <= clockCounter2 + 1;
	end
end

reg [3:0] testState;
`define RESET_STATE 0
`define IDLE_STATE 1
`define WRITE_LAUNCH 2
`define WRITE_WAIT 3
`define READ_LAUNCH 4
`define READ_WAIT 5
`define READ_DONE 6

reg [23:0] readStartCounter;
reg [23:0] readEndCounter;
reg [23:0] counterDifference;
always @(posedge MAX10_CLK1_50) begin
	if (reset) begin
		testState <= `RESET_STATE;
		counterDifference <= 24'h00dead;
		reset_n <= 0;
		
		writedata <= 16'hdead;
		writeAddress <= 25'hdead;
		write <= 0;

		readAddress <= 25'hdead;
		read <= 0;
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

				if (clockCounter2 == 10) testState <= `IDLE_STATE;
			end
			`IDLE_STATE : begin
				reset_n <= 1;

				writedata <= 0;
				writeAddress <= 0;
				write <= 0;

				readAddress <= 0;
				read <= 0;

				if (clockCounter2 == 1000) testState <= `WRITE_LAUNCH;
			end
			`WRITE_LAUNCH : begin
				reset_n <= 1;

				writedata <= 16'h4242;
				writeAddress <= 25'h1234;
				write <= 1;

				readAddress <= 0;
				read <= 0;

				if (clockCounter2 == 1065) testState <= `WRITE_WAIT;
			end
			`WRITE_WAIT : begin
				reset_n <= 1;

				writedata <= 16'h4242;
				writeAddress <= 25'h1234;
				write <= 0;

				readAddress <= 0;
				read <= 0;

				if (clockCounter2 == 1066) testState <= `READ_LAUNCH;
			end
			`READ_LAUNCH : begin
				reset_n <= 1;

				writedata <= 16'h4242;
				writeAddress <= 25'h1234;
				write <= 0;

				readAddress <= 25'h1234;
				read <= 1;
				readStartCounter <= clockCounter2;

				testState <= `READ_WAIT;
			end
			`READ_WAIT : begin
				reset_n <= 1;

				writedata <= 16'h4242;
				writeAddress <= 25'h1234;
				write <= 0;

				readAddress <= 25'h1234;
				read <= 1;

				if (readdata == 16'h4242) begin
					testState <= `READ_DONE;
					readEndCounter <= clockCounter2;
				end
			end
			`READ_DONE : begin
				counterDifference <= readEndCounter - readStartCounter;
			end
		endcase
	end
end

//=======================================================
//  Hex output
//=======================================================

wire [15:0] clockCounter2_upper;
assign clockCounter2_upper = clockCounter2[31:16];
wire [19:0] counterDifference_lower;
assign counterDifference_lower = counterDifference[19:0];

//Split ram data out into nibbles for hex displays
wire [3:0] hexNibbles [7:0];
genvar nibbleId;
generate
	for(nibbleId = 0;nibbleId < 5; nibbleId = nibbleId + 1) begin : genNibbleOuts
		//assign hexNibbles[nibbleId] = coreDataWrite[(nibbleId*4)+3:nibbleId*4];
		//assign hexNibbles[nibbleId] = ramAddress[(nibbleId*4)+3:nibbleId*4];
		//assign hexNibbles[nibbleId] = readdata[(nibbleId*4)+3:nibbleId*4];
		assign hexNibbles[nibbleId] = counterDifference_lower[(nibbleId*4)+3:nibbleId*4];
		//assign hexNibbles[nibbleId] = programCounter[(nibbleId*4)+3:nibbleId*4];
	end
endgenerate

//Map hex outputs
wire [3:0] segmentValues [5:0];
reg [7:0] segmentOutputs [5:0];


assign segmentValues[0] = hexNibbles[0];
assign segmentValues[1] = hexNibbles[1];
assign segmentValues[2] = hexNibbles[2];
assign segmentValues[3] = hexNibbles[3];
assign segmentValues[4] = 4'hf;
assign segmentValues[5] = testState;


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
