//Include dependencies
`include "globalVariables.v"


module flipSign (
	input [`DATA_WIDTH-1:0] operand,
	input flip,

	output reg [`DATA_WIDTH-1:0] result
	);

	wire [`DATA_WIDTH-1:0] flipExtended;
	assign flipExtended = {`DATA_WIDTH{flip}};

	always @(*) begin : adder_proc
		if (flip) result = (operand ^ flipExtended) + 1;
		else if (~flip) result = operand;
	end
endmodule


module absoluteValue (
	input [`DATA_WIDTH-1:0] operand,
	input unsignedEn,

	output wire [`DATA_WIDTH-1:0] result,
	output wire isNegative
	);

	wire msb;
	assign msb = operand[`DATA_WIDTH-1];

	assign isNegative = msb && ~unsignedEn;

	flipSign flipSign(
		.operand(operand),
		.flip(isNegative),

		.result(result)
		);
endmodule


module adder (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,
	input subtract,

	output reg [`DATA_WIDTH-1:0] result
	);

	always @(*) begin : adder_proc
		if (~subtract) result = aOperand + bOperand;
		else if (subtract) result = aOperand - bOperand;
	end

endmodule


module multipler (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,

	output reg [`DATA_WIDTH-1:0] result
	);

	always @(*) begin : mul_proc
		result = aOperand * bOperand;
	end

endmodule


module divider (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,
	input unsignedEn,

	output wire [`DATA_WIDTH-1:0] divResult,
	output wire [`DATA_WIDTH-1:0] remResult
	);

	//Get absolute val of A
	wire [`DATA_WIDTH-1:0] aOp_abs;
	wire a_isNegative;
	absoluteValue absoluteValue_A(
		.operand(aOperand),
		.unsignedEn(unsignedEn),

		.result(aOp_abs),
		.isNegative(a_isNegative)
		);

	//Get absolute val of B
	wire [`DATA_WIDTH-1:0] bOp_abs;
	wire b_isNegative;
	absoluteValue absoluteValue_B(
		.operand(bOperand),
		.unsignedEn(unsignedEn),

		.result(bOp_abs),
		.isNegative(b_isNegative)
		);

	//Unisgned divider outputs
	reg [`DATA_WIDTH-1:0] divuResult;
	reg [`DATA_WIDTH-1:0] remuResult;

	//Flip sign of div outputs
	wire divFlip;
	assign divFlip = a_isNegative ^ b_isNegative;

	flipSign flipSign_div(
		.operand(divuResult),
		.flip(divFlip),

		.result(divResult)
		);

	//Flip sign of rem outputs	
	flipSign flipSign_rem(
		.operand(remuResult),
		.flip(a_isNegative),

		.result(remResult)
		);

	always @(*) begin : divider_proc
		divuResult = aOp_abs / bOp_abs;
		remuResult = aOp_abs % bOp_abs;
	end

endmodule


module comparator (
	input [`DATA_WIDTH-1:0] aOperand,
	input [`DATA_WIDTH-1:0] bOperand,
	input unsignedEn,

	output reg [`DATA_WIDTH-1:0] greater,
	output reg [`DATA_WIDTH-1:0] equal,
	output reg [`DATA_WIDTH-1:0] less
	);
	
	//<TODO> properly handle the signs of the operands. Right now it only does unsigned comparisons

	always @(*) begin : comparator_proc
		greater = aOperand > bOperand;
		equal = aOperand == bOperand;
		less = aOperand < bOperand;
	end

endmodule