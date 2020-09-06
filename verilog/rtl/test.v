module testBench;
	reg clk;
	reg [8] a;
	reg [8] b;
	reg [8] c;

	initial	begin
		clk <= 1;
		a <= 0;
		b <= 0;
		c <= 0;

		#2
		a <= 1;
		
		#2
		b <= 2;

		#2
		c <= a + b;

	end

	//Clock toggling
	always begin
		#1
		clk <= ~clk;
	end 

endmodule