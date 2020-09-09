

module pipelineStateController (
	//Inputs
	input clk,
	input reset,
	input start,

	//Outputs
	output wire fetch_RequestState,
	output wire fetch_ReceiveState,
	output wire decodeState,
	output wire setupState,
	output wire executeState,
	output wire writebackState
	);

	reg [2:0] pipelineState;

	reg [5:0] stateDecoderOutput;
	assign fetch_RequestState = stateDecoderOutput[0];
	assign fetch_ReceiveState = stateDecoderOutput[1];
	assign decodeState = stateDecoderOutput[2];
	assign setupState = stateDecoderOutput[3];
	assign executeState = stateDecoderOutput[4];
	assign writebackState = stateDecoderOutput[5];

	//Logic
	always @ (posedge clk) begin : stateControl
		if (reset) begin
			//reset
			pipelineState <= 0;
		end else begin
			//Increment pipeline from 0 to 5
			if (pipelineState != 5)	pipelineState <= pipelineState + 1;
			else pipelineState <= 0;
		end
	end

	always @(*) begin : stateDecoder_proc
		//Pipeline state decoder
		case (pipelineState)
			0 : stateDecoderOutput = 6'b000001;
			1 : stateDecoderOutput = 6'b000010;
			2 : stateDecoderOutput = 6'b000100;
			3 : stateDecoderOutput = 6'b001000;
			4 : stateDecoderOutput = 6'b010000;
			5 : stateDecoderOutput = 6'b100000;
		endcase // pipelineState
	end

endmodule //pipelineStateController