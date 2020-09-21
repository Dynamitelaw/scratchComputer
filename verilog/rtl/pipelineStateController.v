

module pipelineStateController (
	//Inputs
	input clk,
	input reset,

	input loadInst,

	//Outputs
	output wire fetch_RequestState,
	output wire fetch_ReceiveState,
	output wire decodeState,
	output wire setupState,
	output wire executeState,
	output wire memReadState,
	output wire writebackState
	);

	reg [2:0] pipelineState;

	reg [6:0] stateDecoderOutput;
	assign writebackState = stateDecoderOutput[0];
	assign fetch_RequestState = stateDecoderOutput[1];
	assign fetch_ReceiveState = stateDecoderOutput[2];
	assign decodeState = stateDecoderOutput[3];
	assign setupState = stateDecoderOutput[4];
	assign executeState = stateDecoderOutput[5];
	assign memReadState = stateDecoderOutput[6];

	//Logic
	always @ (posedge clk) begin : stateControl
		if (reset) begin
			//reset
			pipelineState <= 0;
		end else begin
			//Increment pipeline from 0 to 6
			if ((memReadState) || (executeState && ~loadInst))	pipelineState <= 0; //skip memRead state if not required
			else pipelineState <= pipelineState + 1;
		end
	end

	always @(*) begin : stateDecoder_proc
		//Pipeline state decoder
		case (pipelineState)
			0 : stateDecoderOutput = 7'b0000001;
			1 : stateDecoderOutput = 7'b0000010;
			2 : stateDecoderOutput = 7'b0000100;
			3 : stateDecoderOutput = 7'b0001000;
			4 : stateDecoderOutput = 7'b0010000;
			5 : stateDecoderOutput = 7'b0100000;
			6 : stateDecoderOutput = 7'b1000000;
		endcase // pipelineState
	end

endmodule //pipelineStateController