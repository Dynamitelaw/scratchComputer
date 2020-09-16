//Include dependencies
`include "globalVariables.v"


module memoryController(
	input clk,

	//CPU interface
	input [`DATA_WIDTH-1:0] addressIn,
	input [`DATA_WIDTH-1:0] dataWriteIn,
	input [`DATA_WIDTH-1:0] length,
	input storeIn,
	input loadIn,
	input loadUnsighed,
	output [`DATA_WIDTH-1:0] dataReadOut,

	//RAM interface
	input [`DATA_WIDTH-1:0] ramDataRead,
	output [`DATA_WIDTH-1:0] addressOut,
	output [`DATA_WIDTH-1:0] ramDataWrite,
	output [3:0] byteSelect,
	output ramStore,
	output ramLoad
	);

endmodule //memoryController