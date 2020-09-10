//Include dependencies
`include "globalVariables.v"
`include "core.v"
`include "coreTestbench_programInputs.v"

module coreTestbench;
	//Program memory
	reg [`INSTRUCTION_WIDTH-1:0] programMem [0:`programLength-1];

	//Instantiate core
	reg clk;
	reg reset;
	reg [`INSTRUCTION_WIDTH-1:0] memoryIn;

	wire [`DATA_WIDTH-1:0] programCounter;

	core core (
		.clk(clk),
		.reset(reset),
		.memoryIn(memoryIn),

		.programCounter_out(programCounter)
		);


	initial	begin
		/*
		 Setup
		 */
		$dumpvars;

		$display("Loading program into memory");
		$readmemh(`programFilename, programMem);
		
		//posedge clk
		clk <= 1;
		reset <= 1;

		#2
		//posedge clk
		#1
		//negedge clk
		reset <= 0;

		/*
		 run program
		 */
		$display("Running program");
		
		while (programCounter <= (`programLength)*4) begin
			//$display("PC=%d", programCounter);
			#2
			reset <= 0;  //dummy write to appease iverilog
		end
		
		//#2500

		/*
		 Ouput stats
		 */
		$display("Done, program terminated");
		$display("cycles=%0t", ($time-14)/2);
		$finish;
	end

	//Clock toggling
	always begin
		#1
		clk <= ~clk;
	end 

	//Instruction passing
	always @(*) begin
		memoryIn = programMem[programCounter/4];
	end
endmodule
