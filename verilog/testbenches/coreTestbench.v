//Include dependencies
`include "globalVariables.v"
`include "core.v"
`include "memoryController.v"
`include "coreTestbench_programInputs.v"


module RAM(
	input clk,
	input reset,

	//Inputs
	input [`DATA_WIDTH-1:0] addressIn,
	input [`DATA_WIDTH-1:0] dataWriteIn,
	input [3:0] byteSelect,
	input store,
	input load,

	//Ouptuts
	output reg [`DATA_WIDTH-1:0] dataReadOut,
	output reg addressOutOfRange
	);

	reg [`DATA_WIDTH-1:0] memory [0:`memorySize/4];

	reg [`DATA_WIDTH-1:0] memDataCurrent;
	wire [7:0] memDataCurrent_byte0;
	assign memDataCurrent_byte0 = memDataCurrent[7:0];
	wire [7:0] memDataCurrent_byte1;
	assign memDataCurrent_byte1 = memDataCurrent[15:8];
	wire [7:0] memDataCurrent_byte2;
	assign memDataCurrent_byte2 = memDataCurrent[23:16];
	wire [7:0] memDataCurrent_byte3;
	assign memDataCurrent_byte3 = memDataCurrent[31:24];

	reg [7:0] memoryIn_byte0;
	reg [7:0] memoryIn_byte1;
	reg [7:0] memoryIn_byte2;
	reg [7:0] memoryIn_byte3;
	wire [`DATA_WIDTH-1:0] memoryIn;
	assign memoryIn = {memoryIn_byte3, memoryIn_byte2, memoryIn_byte1, memoryIn_byte0};

	wire B0_write;
	assign B0_write = byteSelect[0];
	wire B1_write;
	assign B1_write = byteSelect[1];
	wire B2_write;
	assign B2_write = byteSelect[2];
	wire B3_write;
	assign B3_write = byteSelect[3];

	wire [7:0] dataWriteIn_byte0;
	assign dataWriteIn_byte0 = dataWriteIn[7:0];
	wire [7:0] dataWriteIn_byte1;
	assign dataWriteIn_byte1 = dataWriteIn[15:8];
	wire [7:0] dataWriteIn_byte2;
	assign dataWriteIn_byte2 = dataWriteIn[23:16];
	wire [7:0] dataWriteIn_byte3;
	assign dataWriteIn_byte3 = dataWriteIn[31:24];

	`ifdef FRAME_BUFFER_ENABLE
	integer frameBufferFile;
	wire [`frameBufferSize*8-1:0]frameBufferArray;
	genvar i;
	for (i=0; i<`frameBufferSize/4; i=i+1) assign frameBufferArray[32*i+31:32*i] = memory[`frameBufferStart/4 + i];
	`endif

	`ifdef INPUT_BUFFER_ENABLE
	reg [`DATA_WIDTH-1:0] inputBuffer [0:(`inputBufferSize/4)-1];
	`endif

	always @(posedge clk) begin : ram_proc
		if (store) memory[addressIn/4] <= memoryIn;

		`ifdef FRAME_BUFFER_ENABLE
		if (store) begin
			if ((addressIn >= `frameBufferStart) && (addressIn <= `frameBufferStart+`frameBufferSize)) begin
				//We have written to the frame buffer. Update output binary file
				frameBufferFile = $fopen("simulation/coreTestbench/frameBuffer.b","wb"); // open in binary mode
				$fwrite(frameBufferFile, "%u", frameBufferArray);
				$fclose(frameBufferFile);
			end
		end
		`endif

		`ifdef INPUT_BUFFER_ENABLE
		if (load) begin
			if ((addressIn >= `inputBufferStart) && (addressIn <= `inputBufferStart+`inputBufferSize)) begin
				//We have accessed the GIO buffer. Update memory from hex buffer file
				$readmemh(`inputBufferPath, inputBuffer);
				dataReadOut <= inputBuffer[(addressIn-`inputBufferStart)/4];
			end
			else dataReadOut <= memory[addressIn/4];
		end
		`else
		if (load) dataReadOut <= memory[addressIn/4];
		`endif
	end
	
	always @(*) begin
		memDataCurrent = memory[addressIn/4];

		if (B0_write) memoryIn_byte0 = dataWriteIn_byte0;
		else memoryIn_byte0 = memDataCurrent_byte0;

		if (B1_write) memoryIn_byte1 = dataWriteIn_byte1;
		else memoryIn_byte1 = memDataCurrent_byte1;

		if (B2_write) memoryIn_byte2 = dataWriteIn_byte2;
		else memoryIn_byte2 = memDataCurrent_byte2;

		if (B3_write) memoryIn_byte3 = dataWriteIn_byte3;
		else memoryIn_byte3 = memDataCurrent_byte3;
	end

	always @(*) begin : proc_ 
		addressOutOfRange = (addressIn >= `memorySize) && (store || load);
	end

	initial begin
		$display("Loading program into memory");
		$readmemh(`programFilename, memory);
	end

endmodule //RAM


module coreTestbench;
	int cycleCount;

	//Instantiate core
	reg clk;
	reg reset;
	wire [`DATA_WIDTH-1:0] memoryDataRead_core;

	wire [`DATA_WIDTH-1:0] programCounter;
	wire [`DATA_WIDTH-1:0] memoryAddress_core;
	wire [`DATA_WIDTH-1:0] memoryDataWrite_core;
	wire [1:0] memoryLength_core;
	wire store_core;
	wire load_core;
	wire loadUnsigned_core;

	core core (
		.clk(clk),
		.reset(reset),
		.memoryDataRead(memoryDataRead_core),

		.programCounter_out(programCounter),
		.memoryAddress(memoryAddress_core),
		.memoryDataWrite(memoryDataWrite_core),
		.memoryLength(memoryLength_core),
		.store(store_core),
		.load(load_core),
		.loadUnsigned(loadUnsigned_core)
		);

	//Instantiate memory controller
	wire [`DATA_WIDTH-1:0] dataReadOut_memControl;
	assign memoryDataRead_core = dataReadOut_memControl;

	wire [`DATA_WIDTH-1:0] ramDataRead;
	wire [`DATA_WIDTH-1:0] addressOut_memControl;
	wire [`DATA_WIDTH-1:0] ramDataWrite;
	wire [3:0] byteSelect;
	wire ramStore;
	wire ramLoad;

	memoryController memoryController(
		.clk(clk),
		.reset(reset),
		.addressIn(memoryAddress_core),
		.dataWriteIn(memoryDataWrite_core),
		.length(memoryLength_core),
		.storeIn(store_core),
		.loadIn(load_core),
		.loadUnsigned(loadUnsigned_core),
		.dataReadOut(dataReadOut_memControl),

		.ramDataRead(ramDataRead),
		.addressOut(addressOut_memControl),
		.ramDataWrite(ramDataWrite),
		.byteSelect(byteSelect),
		.ramStore(ramStore),
		.ramLoad(ramLoad)
		);

	//Instantiate main memory
	wire addressOutOfRange;

	RAM RAM(
		.clk(clk),
		.reset(reset),
		.addressIn(addressOut_memControl),
		.dataWriteIn(ramDataWrite),
		.byteSelect(byteSelect),
		.store(ramStore),
		.load(ramLoad),

		.dataReadOut(ramDataRead),
		.addressOutOfRange(addressOutOfRange)
		);


	initial	begin
		/*
		 Setup
		 */
		$dumpvars;
		cycleCount <= 0;

		//posedge clk
		clk <= 1;
		reset <= 1;

		#2
		//posedge clk
		#1
		//negedge clk
		reset <= 0;
		#1

		/*
		 run program
		 */
		$display("Running program");
		
		`ifdef MAX_CYLCLES
			while ((programCounter <= (`programLength)*4) && (cycleCount < `MAX_CYLCLES)) begin
				//$display("PC=%d", programCounter);
				cycleCount <= cycleCount + 1;
				#2
				reset <= 0;  //dummy write to appease iverilog
			end

			if (cycleCount >= `MAX_CYLCLES) begin
				$display("Max cycle count exceeded. Ending simulation");
			end
		`else
			while (programCounter <= (`programLength)*4) begin
				//$display("PC=%d", programCounter);
				#2
				reset <= 0;  //dummy write to appease iverilog
				cycleCount <= cycleCount + 1;
			end
		`endif
		
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
		#1
		clk <= ~clk;
	end 
endmodule
