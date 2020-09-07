//Include dependencies
`include "globalVariables.v"


module registers (
	//Inputs
	input clk,
	input reset,
	
	input [`DATA_WIDTH-1:0] dataIn,
	input [`REGADDR_WIDTH-1:0] writeSelect,
	input writeEnable,
	input [`REGADDR_WIDTH-1:0] readA_select,
	input [`REGADDR_WIDTH-1:0] readB_select,

	//Outputs
	output reg [`DATA_WIDTH-1:0] readA_out,
	output reg [`DATA_WIDTH-1:0] readB_out
	);

	//General purpose registers
	wire [`DATA_WIDTH-1:0] r0;
	assign r0 = 0;
	reg [`DATA_WIDTH-1:0] r1;
	reg [`DATA_WIDTH-1:0] r2;
	reg [`DATA_WIDTH-1:0] r3;
	reg [`DATA_WIDTH-1:0] r4;
	reg [`DATA_WIDTH-1:0] r5;
	reg [`DATA_WIDTH-1:0] r6;
	reg [`DATA_WIDTH-1:0] r7;
	reg [`DATA_WIDTH-1:0] r8;
	reg [`DATA_WIDTH-1:0] r9;
	reg [`DATA_WIDTH-1:0] r10;
	reg [`DATA_WIDTH-1:0] r11;
	reg [`DATA_WIDTH-1:0] r12;
	reg [`DATA_WIDTH-1:0] r13;
	reg [`DATA_WIDTH-1:0] r14;
	reg [`DATA_WIDTH-1:0] r15;
	reg [`DATA_WIDTH-1:0] r16;
	reg [`DATA_WIDTH-1:0] r17;
	reg [`DATA_WIDTH-1:0] r18;
	reg [`DATA_WIDTH-1:0] r19;
	reg [`DATA_WIDTH-1:0] r20;
	reg [`DATA_WIDTH-1:0] r21;
	reg [`DATA_WIDTH-1:0] r22;
	reg [`DATA_WIDTH-1:0] r23;
	reg [`DATA_WIDTH-1:0] r24;
	reg [`DATA_WIDTH-1:0] r25;
	reg [`DATA_WIDTH-1:0] r26;
	reg [`DATA_WIDTH-1:0] r27;
	reg [`DATA_WIDTH-1:0] r28;
	reg [`DATA_WIDTH-1:0] r29;
	reg [`DATA_WIDTH-1:0] r30;
	reg [`DATA_WIDTH-1:0] r31;

	//Register alias probes (for easier simulation debug)
	wire [`DATA_WIDTH-1:0] ra;
	assign ra = r1;
	wire [`DATA_WIDTH-1:0] sp;
	assign sp = r2;
	wire [`DATA_WIDTH-1:0] gp;
	assign gp = r3;
	wire [`DATA_WIDTH-1:0] tp;
	assign tp = r4;
	wire [`DATA_WIDTH-1:0] t0;
	assign t0 = r5;
	wire [`DATA_WIDTH-1:0] t1;
	assign t1 = r6;
	wire [`DATA_WIDTH-1:0] t2;
	assign t2 = r7;
	wire [`DATA_WIDTH-1:0] s0;
	assign s0 = r8;
	wire [`DATA_WIDTH-1:0] fp;
	assign fp = r8;
	wire [`DATA_WIDTH-1:0] s1;
	assign s1 = r9;
	wire [`DATA_WIDTH-1:0] a0;
	assign a0 = r10;
	wire [`DATA_WIDTH-1:0] a1;
	assign a1 = r11;
	wire [`DATA_WIDTH-1:0] a2;
	assign a2 = r12;
	wire [`DATA_WIDTH-1:0] a3;
	assign a3 = r13;
	wire [`DATA_WIDTH-1:0] a4;
	assign a4 = r14;
	wire [`DATA_WIDTH-1:0] a5;
	assign a5 = r15;
	wire [`DATA_WIDTH-1:0] a6;
	assign a6 = r16;
	wire [`DATA_WIDTH-1:0] a7;
	assign a7 = r17;
	wire [`DATA_WIDTH-1:0] s2;
	assign s2 = r18;
	wire [`DATA_WIDTH-1:0] s3;
	assign s3 = r19;
	wire [`DATA_WIDTH-1:0] s4;
	assign s4 = r20;
	wire [`DATA_WIDTH-1:0] s5;
	assign s5 = r21;
	wire [`DATA_WIDTH-1:0] s6;
	assign s6 = r22;
	wire [`DATA_WIDTH-1:0] s7;
	assign s7 = r23;
	wire [`DATA_WIDTH-1:0] s8;
	assign s8 = r24;
	wire [`DATA_WIDTH-1:0] s9;
	assign s9 = r25;
	wire [`DATA_WIDTH-1:0] s10;
	assign s10 = r26;
	wire [`DATA_WIDTH-1:0] s11;
	assign s11 = r27;
	wire [`DATA_WIDTH-1:0] t3;
	assign t3 = r28;
	wire [`DATA_WIDTH-1:0] t4;
	assign t4 = r29;
	wire [`DATA_WIDTH-1:0] t5;
	assign t5 = r30;
	wire [`DATA_WIDTH-1:0] t6;
	assign t6 = r31;

	//Read output logic
	always @(*) begin : outputMux_proc
		case (readA_select)
			0 : readA_out = r0;
			1 : readA_out = r1;
			2 : readA_out = r2;
			3 : readA_out = r3;
			4 : readA_out = r4;
			5 : readA_out = r5;
			6 : readA_out = r6;
			7 : readA_out = r7;
			8 : readA_out = r8;
			9 : readA_out = r9;
			10 : readA_out = r10;
			11 : readA_out = r11;
			12 : readA_out = r12;
			13 : readA_out = r13;
			14 : readA_out = r14;
			15 : readA_out = r15;
			16 : readA_out = r16;
			17 : readA_out = r17;
			18 : readA_out = r18;
			19 : readA_out = r19;
			20 : readA_out = r20;
			21 : readA_out = r21;
			22 : readA_out = r22;
			23 : readA_out = r23;
			24 : readA_out = r24;
			25 : readA_out = r25;
			26 : readA_out = r26;
			27 : readA_out = r27;
			28 : readA_out = r28;
			29 : readA_out = r29;
			30 : readA_out = r30;
			31 : readA_out = r31;
		endcase // readA_select

		case (readB_select)
			0 : readB_out = r0;
			1 : readB_out = r1;
			2 : readB_out = r2;
			3 : readB_out = r3;
			4 : readB_out = r4;
			5 : readB_out = r5;
			6 : readB_out = r6;
			7 : readB_out = r7;
			8 : readB_out = r8;
			9 : readB_out = r9;
			10 : readB_out = r10;
			11 : readB_out = r11;
			12 : readB_out = r12;
			13 : readB_out = r13;
			14 : readB_out = r14;
			15 : readB_out = r15;
			16 : readB_out = r16;
			17 : readB_out = r17;
			18 : readB_out = r18;
			19 : readB_out = r19;
			20 : readB_out = r20;
			21 : readB_out = r21;
			22 : readB_out = r22;
			23 : readB_out = r23;
			24 : readB_out = r24;
			25 : readB_out = r25;
			26 : readB_out = r26;
			27 : readB_out = r27;
			28 : readB_out = r28;
			29 : readB_out = r29;
			30 : readB_out = r30;
			31 : readB_out = r31;
		endcase // readA_select
	end

	//Register write logic
	always @(posedge clk) begin : registerWrite_proc
		if (reset) begin
			r1 <= 0;
			r2 <= 0;
			r3 <= 0;
			r4 <= 0;
			r5 <= 0;
			r6 <= 0;
			r7 <= 0;
			r8 <= 0;
			r9 <= 0;
			r10 <= 0;
			r11 <= 0;
			r12 <= 0;
			r13 <= 0;
			r14 <= 0;
			r15 <= 0;
			r16 <= 0;
			r17 <= 0;
			r18 <= 0;
			r19 <= 0;
			r20 <= 0;
			r21 <= 0;
			r22 <= 0;
			r23 <= 0;
			r24 <= 0;
			r25 <= 0;
			r26 <= 0;
			r27 <= 0;
			r28 <= 0;
			r29 <= 0;
			r30 <= 0;
			r31 <= 0;
		end else begin
			if (writeEnable && (writeSelect==1)) r1 <= dataIn;
			if (writeEnable && (writeSelect==2)) r2 <= dataIn;
			if (writeEnable && (writeSelect==3)) r3 <= dataIn;
			if (writeEnable && (writeSelect==4)) r4 <= dataIn;
			if (writeEnable && (writeSelect==5)) r5 <= dataIn;
			if (writeEnable && (writeSelect==6)) r6 <= dataIn;
			if (writeEnable && (writeSelect==7)) r7 <= dataIn;
			if (writeEnable && (writeSelect==8)) r8 <= dataIn;
			if (writeEnable && (writeSelect==9)) r9 <= dataIn;
			if (writeEnable && (writeSelect==10)) r10 <= dataIn;
			if (writeEnable && (writeSelect==11)) r11 <= dataIn;
			if (writeEnable && (writeSelect==12)) r12 <= dataIn;
			if (writeEnable && (writeSelect==13)) r13 <= dataIn;
			if (writeEnable && (writeSelect==14)) r14 <= dataIn;
			if (writeEnable && (writeSelect==15)) r15 <= dataIn;
			if (writeEnable && (writeSelect==16)) r16 <= dataIn;
			if (writeEnable && (writeSelect==17)) r17 <= dataIn;
			if (writeEnable && (writeSelect==18)) r18 <= dataIn;
			if (writeEnable && (writeSelect==19)) r19 <= dataIn;
			if (writeEnable && (writeSelect==20)) r20 <= dataIn;
			if (writeEnable && (writeSelect==21)) r21 <= dataIn;
			if (writeEnable && (writeSelect==22)) r22 <= dataIn;
			if (writeEnable && (writeSelect==23)) r23 <= dataIn;
			if (writeEnable && (writeSelect==24)) r24 <= dataIn;
			if (writeEnable && (writeSelect==25)) r25 <= dataIn;
			if (writeEnable && (writeSelect==26)) r26 <= dataIn;
			if (writeEnable && (writeSelect==27)) r27 <= dataIn;
			if (writeEnable && (writeSelect==28)) r28 <= dataIn;
			if (writeEnable && (writeSelect==29)) r29 <= dataIn;
			if (writeEnable && (writeSelect==30)) r30 <= dataIn;
			if (writeEnable && (writeSelect==31)) r31 <= dataIn;
		end
	end

endmodule