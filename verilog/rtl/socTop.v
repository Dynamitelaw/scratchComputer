//Include dependencies
`include "globalVariables.v"
`include "pipeline.v"
`include "memoryController.v"


module soc(
	input clk,
	input reset,

	//Main memory interface
	input [`DATA_WIDTH-1:0] memDataRead,
	input memReadValid,

	output [`DATA_WIDTH-1:0] memAddress,
	output [`DATA_WIDTH-1:0] memDataWrite,
	output [3:0] memByteSelect,
	output memStore,
	output memLoad,

	//Test bench probes
	output [`DATA_WIDTH-1:0] programCounter
	);

	//Instantiate pipeline
	wire [`DATA_WIDTH-1:0] memoryDataRead_pipeline;

	wire [`DATA_WIDTH-1:0] memoryAddress_pipeline;
	wire [`DATA_WIDTH-1:0] memoryDataWrite_pipeline;
	wire [1:0] memoryLength_pipeline;
	wire store_pipeline;
	wire load_pipeline;
	wire loadUnsigned_pipeline;

	pipeline pipeline (
		.clk(clk),
		.reset(reset),
		.memoryDataRead(memoryDataRead_pipeline),
		.memoryReadValid(dataReadValid_memControl),

		.programCounter_out(programCounter),
		.memoryAddress(memoryAddress_pipeline),
		.memoryDataWrite(memoryDataWrite_pipeline),
		.memoryLength(memoryLength_pipeline),
		.store(store_pipeline),
		.load(load_pipeline),
		.loadUnsigned(loadUnsigned_pipeline)
		);

	//Instantiate memory controller
	wire [`DATA_WIDTH-1:0] dataReadOut_memControl;
	assign memoryDataRead_pipeline = dataReadOut_memControl;

	memoryController memoryController(
		.clk(clk),
		.reset(reset),
		.addressIn(memoryAddress_pipeline),
		.dataWriteIn(memoryDataWrite_pipeline),
		.length(memoryLength_pipeline),
		.storeIn(store_pipeline),
		.loadIn(load_pipeline),
		.loadUnsigned(loadUnsigned_pipeline),
		.dataReadOut(dataReadOut_memControl),
		.dataReadValid(dataReadValid_memControl),

		.ramDataRead(memDataRead),
		.ramReadValid(memReadValid),
		.addressOut(memAddress),
		.ramDataWrite(memDataWrite),
		.byteSelect(memByteSelect),
		.ramStore(memStore),
		.ramLoad(memLoad)
		);

endmodule
