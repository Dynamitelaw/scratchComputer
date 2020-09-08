module main;
	reg clk;
	reg [7:0] a;
	reg [8] b;
	reg [8] c;

	initial	begin
		$dumpfile("test.vcd");
		$dumpvars;
		
		clk <= 1;
		a <= 8'b0110111;
		b <= 0;
		c <= 0;

		#2
		a <= 8'b0110111;;
		
		#2
		b <= 2;

		#2
		c <= a + b;

		#2
		$display("a = %b", a);
		$display("a = %b", a[3:0]);
		$finish;

	end

	//Clock toggling
	always begin
		#1
		clk <= ~clk;
	end 

endmodule
