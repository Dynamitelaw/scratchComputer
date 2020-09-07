

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

	reg [1:0] pipelineState;
	wire notActive;
	assign notActive = 	~active;

	reg [3:0] stateDecoderOutput;
	assign decodeState = stateDecoderOutput[0];
	assign setupState = stateDecoderOutput[1];
	assign executeState = stateDecoderOutput[2];
	assign writebackState = stateDecoderOutput[3];

	wire sleepState;
	assign sleepState = decodeState && notActive;
	wire nextActiveState;
	assign nextActiveState = ((decodeState && active)||setupState||executeState) || ((start&&sleepState) && ~(active&&writebackState));

	//Logic
	always @ (posedge clk) begin : stateControl
		if (reset) begin
			//reset
			pipelineState <= 0;
			active <= 0;
		end else begin
			active <= nextActiveState;

			if (active) begin
				pipelineState <= pipelineState + 1;
			end
		end
	end

	always @(*) begin : stateDecoder_proc
		if (reset) stateDecoderOutput <= 4'b0001;
		else begin
			//Pipeline state decoder
			case (pipelineState)
				0 : stateDecoderOutput <= 4'b0001;
				1 : stateDecoderOutput <= 4'b0010;
				2 : stateDecoderOutput <= 4'b0100;
				3 : stateDecoderOutput <= 4'b1000;
			endcase // pipelineState
		end
	end

endmodule //pipelineStateController