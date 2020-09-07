//Include dependencies
`include "globalVariables.v"
`include "core.v"

module coreTestbench;
	//Program memory
	`define programLength 4
	`define programFilename "simpleTest.hex"
	reg [`INSTRUCTION_WIDTH-1:0] programMem [0:`programLength-1];

	//Instantiate core
	reg clk;
	reg reset;
	reg [`INSTRUCTION_WIDTH-1:0] instructionIn;
	reg start;

	wire busy;

	core core (
		.clk(clk),
		.reset(reset),
		.instructionIn(instructionIn),
		.start(start),

		.busy(busy)
		);

	integer programCounter;

	initial	begin
		/*
		 Setup
		 */
		$dumpfile("coreTestbench.vcd");
		$dumpvars;

		$display("Loading program into memory");
		$readmemh(`programFilename, programMem);
		
		//posedge clk
		clk <= 1;
		reset <= 1;
		programCounter <= 0;

		#2
		//posedge clk
		#1
		//negedge clk
		reset <= 0;

		/*
		 run program
		 */
		while ((programCounter < `programLength-1) || busy) begin
			#2
			if (~busy) programCounter <= programCounter + 1;
		end

		$finish;
	end

	//Clock toggling
	always begin
		#1
		clk <= ~clk;
	end 

	//Instruction passing
	always @(*) begin
		instructionIn = programMem[programCounter];
	end

	//Start sigal
	always @(*) begin
		start = (programCounter <= `programLength) && ~busy;
	end

endmodule
