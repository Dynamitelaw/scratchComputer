//Include dependencies
`include "globalVariables.v"
`include "core.v"

module coreTestbench;
	reg clk;
	reg [8] a;
	reg [8] b;
	reg [8] c;

	//Instantiate core
	reg reset;
	reg [`INSTRUCTION_WIDTH] instructionIn;
	reg start;

	wire busy;

	core core (
		.clk(clk),
		.reset(reset),
		.instructionIn(instructionIn),
		.start(start),

		.busy(busy)
		);


	initial	begin
		/*
		 Setup
		 */
		$dumpfile("coreTestbench.vcd");
		$dumpvars;
		
		//posedge clk
		clk <= 1;
		reset <= 1;
		start <= 0;

		#2
		//posedge clk
		#1
		//negedge clk
		reset <= 0;

		/*
		 program
		 */
		instructionIn <= 32'h1200293;  //addi t0, zero, 18
		start <= 1;
		#1
		//posedge clk
		#1
		//negedge clk
		start <= 0;

		#40 //20 cycles

		//negedge clk

		instructionIn <= 32'h1800313;  //addi t1, zero, 24
		start <= 1;
		#1
		//posedge clk
		#1
		//negedge clk
		start <= 0;

		#40 //20 cycles

		//negedge clk

		instructionIn <= 32'h530e33;  //add t3, t1, t0 
		start <= 1;
		#1
		//posedge clk
		#1
		//negedge clk
		start <= 0;

		#40 //20 cycles

		//negedge clk

		instructionIn <= 32'he0fb3;  //mv t6,t3
		start <= 1;
		#1
		//posedge clk
		#1
		//negedge clk
		start <= 0;

		#40 //20 cycles

		//negedge clk


		/*
		 exit
		 */
		$display("hello world!");
		$finish;

	end

	//Clock toggling
	always begin
		#1
		clk <= ~clk;
	end 

endmodule
