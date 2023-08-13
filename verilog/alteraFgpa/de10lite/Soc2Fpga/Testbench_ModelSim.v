`timescale 10ns/1ps
module testbench();

//Simulate FPGA IO
//////////// CLOCK //////////
reg ADC_CLK_10;
wire MAX10_CLK1_50;
wire MAX10_CLK2_50;

//////////// SDRAM //////////
wire [12:0] DRAM_ADDR;
wire [1:0] DRAM_BA;
wire DRAM_CAS_N;
wire DRAM_CKE;
wire DRAM_CLK;
wire DRAM_CS_N;
wire [15:0] DRAM_DQ;
wire DRAM_LDQM;
wire DRAM_RAS_N;
wire DRAM_UDQM;
wire DRAM_WE_N;

//////////// SEG7 //////////
wire [7:0] HEX0;
wire [7:0] HEX1;
wire [7:0] HEX2;
wire [7:0] HEX3;
wire [7:0] HEX4;
wire [7:0] HEX5;

//////////// KEY //////////
wire [1:0] KEY;

//////////// LED //////////
wire [9:0] LEDR;

//////////// SW //////////
wire [9:0] SW;

//////////// VGA //////////
wire [3:0] VGA_B;
wire [3:0] VGA_G;
wire VGA_HS;
wire [3:0] VGA_R;
wire VGA_VS;

//////////// Accelerometer //////////
wire GSENSOR_CS_N;
wire [2:1] GSENSOR_INT;
wire GSENSOR_SCLK;
wire GSENSOR_SDI;
wire GSENSOR_SDO;

//////////// Arduino //////////
wire [15:0] ARDUINO_IO;
wire ARDUINO_RESET_N;

//////////// GPIO(), GPIO connect to GPIO Default //////////
wire [35:0] GPIO;

//Instantiate model
DE10_LITE_Golden_Top fpgaTop(

	//////////// CLOCK //////////
	.ADC_CLK_10(ADC_CLK_10),
	.MAX10_CLK1_50(MAX10_CLK1_50),
	.MAX10_CLK2_50(MAX10_CLK2_50),

	//////////// SDRAM //////////
	.DRAM_ADDR(DRAM_ADDR),
	.DRAM_BA(DRAM_BA),
	.DRAM_CAS_N(DRAM_CAS_N),
	.DRAM_CKE(DRAM_CKE),
	.DRAM_CLK(DRAM_CLK),
	.DRAM_CS_N(DRAM_CS_N),
	.DRAM_DQ(DRAM_DQ),
	.DRAM_LDQM(DRAM_LDQM),
	.DRAM_RAS_N(DRAM_RAS_N),
	.DRAM_UDQM(DRAM_UDQM),
	.DRAM_WE_N(DRAM_WE_N),

	//////////// SEG7 //////////
	.HEX0(HEX0),
	.HEX1(HEX1),
	.HEX2(HEX2),
	.HEX3(HEX3),
	.HEX4(HEX4),
	.HEX5(HEX5),

	//////////// KEY //////////
	.KEY(KEY),

	//////////// LED //////////
	.LEDR(LEDR),

	//////////// SW //////////
	.SW(SW),

	//////////// VGA //////////
	.VGA_B(VGA_B),
	.VGA_G(VGA_G),
	.VGA_HS(VGA_HS),
	.VGA_R(VGA_R),
	.VGA_VS(VGA_VS),

	//////////// Accelerometer //////////
	.GSENSOR_CS_N(GSENSOR_CS_N),
	.GSENSOR_INT(GSENSOR_INT),
	.GSENSOR_SCLK(GSENSOR_SCLK),
	.GSENSOR_SDI(GSENSOR_SDI),
	.GSENSOR_SDO(GSENSOR_SDO),

	//////////// Arduino //////////
	.ARDUINO_IO(ARDUINO_IO),
	.ARDUINO_RESET_N(ARDUINO_RESET_N),

	//////////// GPIO(), GPIO connect to GPIO Default //////////
	.GPIO(GPIO)
	);


//Run simulation
reg [31:0] cycleCount;
reg clk;
assign MAX10_CLK1_50 = clk;
assign MAX10_CLK2_50 = clk;

reg reset;
assign KEY[0] = ~reset;
assign KEY[1] = ~reset;

initial	begin
	/*
	 Setup
	 */
	cycleCount <= 0;

	//posedge clk
	clk <= 1;
	reset <= 1;

	#8
	//posedge clk
	#4
	//negedge clk
	reset <= 0;
	#4

	/*
	 run program
	 */
	$display("Running program");
	
	while (cycleCount < 100) begin
		//$display("PC=%d", programCounter);
		cycleCount <= cycleCount + 1;
		#8
		reset <= 0;  //dummy write to appease iverilog
	end

	if (cycleCount >= 100) begin
		$display("Max cycle count exceeded. Ending simulation");
	end
	
	//#2500

	/*
	 Ouput stats
	 */
	$display("Done, program terminated");
	$display("cycles=%d", cycleCount);
	$finish;
end

//Clock toggling
always begin
	#4
	clk <= ~clk;
end 
endmodule