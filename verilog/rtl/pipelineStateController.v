

module pipelineStateController (
	//Inputs
	input clk,
	input reset,
	input start,

	//Outputs
	output reg active,
	output wire decodeState,
	output wire setupState,
	output wire executeState,
	output wire writebackState
	);

	reg [2] pipelineState;
	wire notActive;
	assign notActive = 	~active;

	reg [4] 2bDecoderOuput;
	assign decodeState = 2bDecoderOuput[0];
	assign setupState = 2bDecoderOuput[1];
	assign executeState = 2bDecoderOuput[2];
	assign writebackState = 2bDecoderOuput[3];

	wire sleepState;
	assign sleepState = decodeState && notActive;
	wire nextActiveState;
	assign nextActiveState = ((decodeState && active)||setupState||executeState) || ((start&&sleepState) && ~(active&&writebackState))

	//Logic
	always @ (posedge clk) begin : stateControl
		if (reset) begin
			//reset
			pipelineState <= 0;
			active <= 0;

			2bDecoderOuput <= 4'b0001;
		end else begin
			active <= nextActiveState;

			if (active) begin
				pipelineState <= pipelineState + 1;
			end

			//Pipeline state decoder
			case (pipelineState)
				0 : 2bDecoderOuput <= 4'b0001;
				1 : 2bDecoderOuput <= 4'b0010;
				2 : 2bDecoderOuput <= 4'b0100;
				3 : 2bDecoderOuput <= 4'b1000;
			endcase // pipelineState
		end
	end

endmodule : pipelineStateController