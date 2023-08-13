`include "../../../rtl/globalVariables.v"

module memoryInterface (
	input clk, // Clock
	input reset, 
	
	//========================
	// Consumter Interfaces
	//========================
	//Port 0
	input [`DATA_WIDTH-1:0] port0_address,
	input [`DATA_WIDTH-1:0] port0_writeData,
	input port0_writeEnable,
	output reg port0_writeReady,

	input port0_readEnable,
	output reg port0_readReady,
	output reg [`DATA_WIDTH-1:0] port0_readData,
	output reg [`DATA_WIDTH-1:0] port0_readDataAddress,
	output reg [`DATA_WIDTH-1:0] port0_readDataValid,

	output reg port0_error,

	//Port 1
	input [`DATA_WIDTH-1:0] port1_address,
	input [`DATA_WIDTH-1:0] port1_writeData,
	input port1_writeEnable,
	output reg port1_writeReady,

	input port1_readEnable,
	output reg port1_readReady,
	output reg [`DATA_WIDTH-1:0] port1_readData,
	output reg [`DATA_WIDTH-1:0] port1_readDataAddress,
	output reg [`DATA_WIDTH-1:0] port1_readDataValid,

	output reg port1_error,

	//=============================
	// SDRAM Controller Interface
	//=============================
	// 	FIFO Write Side 1
	output reg [`DSIZE-1:0] sdram_WR_DATA, //Controller data output reg
	output reg sdram_WR, 	//Write Request
	output reg [`ASIZE-1:0] 	 sdram_WR_ADDR, 	//Write start address
	output reg [`ASIZE-1:0] 	 sdram_WR_MAX_ADDR, 	//Write max address
	output reg [8:0] 	 sdram_WR_LENGTH, 	//Write length
	input sdram_WR_FULL, 	//Write fifo full
	input [15:0] sdram_WR_USE, 	//Write fifo usedw

	// 	FIFO Read Side 1
	input [`DSIZE-1:0] sdram_RD_DATA, //Controller data input
	output reg sdram_RD, //Read Request
	output reg [`ASIZE-1:0] sdram_RD_ADDR, 	//Read start address
	output reg [`ASIZE-1:0] sdram_RD_MAX_ADDR, 	//Read max address
	output reg [8:0] sdram_RD_LENGTH, 	//Read length
	input sdram_RD_EMPTY, 	//Read fifo empty
	input [15:0] sdram_RD_USE 	//Read fifo usedw
);

//Port 0 input flops
reg [`DATA_WIDTH-1:0] port0_address_ff;
reg [`DATA_WIDTH-1:0] port0_writeData_ff;
reg port0_readRequest;
reg port0_writeRequest;
wire port0_valid;
assign port0_valid = port0_readEnable | port0_writeEnable;
reg port0_requestValid_ff;

always @(posedge clk) begin
	if(reset) begin
		port0_requestValid_ff <= 0;
		port0_error <= 0;
	end 
	else begin
		if (port0_valid) begin
			port0_requestValid_ff <= 1;
			port0_address_ff <= port0_address;
			port0_writeData_ff <= port0_writeData;
			port0_readRequest <= port0_readEnable;
			port0_writeRequest <= port0_writeEnable;
			port0_error <= port0_readEnable & port0_writeEnable;
		end
	end
end

//Port 1 input flops
reg [`DATA_WIDTH-1:0] port1_address_ff;
reg [`DATA_WIDTH-1:0] port1_writeData_ff;
reg port1_readRequest;
reg port1_writeRequest;
wire port1_valid;
assign port1_valid = port1_readEnable | port1_writeEnable;
reg port1_requestValid_ff;

always @(posedge clk) begin
	if (reset) begin
		port1_requestValid_ff <= 0;
		port1_error <= 0;
	end 
	else begin
		if (port1_valid) begin
			port1_requestValid_ff <= 1;
			port1_address_ff <= port1_address;
			port1_writeData_ff <= port1_writeData;
			port1_readRequest <= port1_readEnable;
			port1_writeRequest <= port1_writeEnable;
			port1_error <= port1_readEnable & port1_writeEnable;
		end
	end
end

//Mem pipeline arbitration
reg portSelect;
always @(posedge clk) begin
	if (reset) begin
		portSelect <= 0;
	end
	else begin
		//Round robin port arbitration
		case ({portSelect, port0_valid, port1_valid})
			3'b?10 : portSelect <= 0;
			3'b?01 : portSelect <= 1;
			default : portSelect <= ~portSelect;
		endcase
	end
end

reg [`DATA_WIDTH-1:0] nextRequest_address;
reg [`DATA_WIDTH-1:0] nextRequest_wrData;
reg nextRequest_isRead;
reg nextRequest_isWrite;
reg nextRequest_isValid;
reg nextRequest_portId;
always @(*) begin
	//Next request mux
	case ({portSelect, port0_requestValid_ff, port1_requestValid_ff})
		3'b01? : begin
			nextRequest_address = port0_address_ff;
			nextRequest_isRead = port0_readRequest;
			nextRequest_isWrite = port0_writeRequest;
			nextRequest_wrData = port0_writeData_ff & {`DATA_WIDTH{port0_writeRequest}};
			nextRequest_isValid = 1;
			nextRequest_portId = 0;
		end
		3'b1?1 : begin
			nextRequest_address = port1_address_ff;
			nextRequest_isRead = port1_readRequest;
			nextRequest_isWrite = port1_writeRequest;
			nextRequest_wrData = port1_writeData_ff & {`DATA_WIDTH{port0_writeRequest}};
			nextRequest_isValid = 1;
			nextRequest_portId = 1;
		end
		default begin
			nextRequest_address = 0;
			nextRequest_isRead = 0;
			nextRequest_isWrite = 0;
			nextRequest_wrData = 0;
			nextRequest_isValid = 0;
			nextRequest_portId = 0;
		end
	endcase
end

wire [`ASIZE-1:0] sdramRequest_address;
wire [`DATA_WIDTH-1:0] sdramRequest_wrData;
wire sdramRequest_isRead;
wire sdramRequest_isWrite;
wire sdramRequest_isValid;
wire sdramRequest_portId;
reg [15:0] sdram_readData_lower;
reg [15:0] sdram_readData_upper;
wire [31:0] sdram_readData;
assign sdram_readData = {sdram_readData_upper, sdram_readData_lower};
reg sdramRequest_handled;

assign sdramRequest_address = nextRequest_address[`ASIZE:1];
assign sdramRequest_wrData = nextRequest_wrData;
assign sdramRequest_isRead = nextRequest_isRead;
assign sdramRequest_isWrite = nextRequest_isWrite;
assign sdramRequest_isValid = nextRequest_isValid;
assign sdramRequest_portId = nextRequest_portId;

//Output request timers
parameter READ_TIMER_CYCLES = 12030;
parameter WRITE_TIMER_CYCLES = 70;
parameter SDRAM_INIT_CYCLES = 1000;

reg [3:0] sdramHandlerState;
`define RESET_STATE 0
`define IDLE_STATE 1
`define WRITE_WORD_LOWER 2
`define WRITE_WORD_UPPER 3
`define READ_WORD_LOWER 4
`define READ_WORD_UPPER 5
`define REQUEST_DONE 6

reg [16:0] waitTimer;
reg writeSettled;
always @(posedge clk) begin
	if (reset) begin
		sdramHandlerState <= `RESET_STATE;
		waitTimer <= 0;
		writeSettled <= 1;
		sdram_RD <= 0;
		sdram_WR <= 0;
		sdramRequest_handled <= 0;
	end
	else begin
		case (sdramHandlerState)
			`RESET_STATE : begin
				waitTimer <= waitTimer + 1;
				writeSettled <= 1;
				sdram_RD <= 0;
				sdram_WR <= 0;
				if (waitTimer == `SDRAM_INIT_CYCLES) sdramHandlerState <= `IDLE_STATE;
			end
			`IDLE_STATE : begin
				sdram_RD <= 0;
				sdram_WR <= 0;
				sdramRequest_handled <= 0;

				if (writeSettled) begin
					waitTimer <= 0;
				end
				else begin
					waitTimer <= waitTimer + 1;
					if (waitTimer == READ_TIMER_CYCLES) writeSettled <= 1;
				end

				if (sdramRequest_isValid) begin
					if (sdramRequest_isRead && writeSettled) sdramHandlerState <= `READ_WORD_LOWER;
					else if (sdramRequest_isWrite) sdramHandlerState <= `WRITE_WORD_LOWER;
				end
			end
			`WRITE_WORD_LOWER : begin
				sdram_WR_DATA <= sdramRequest_wrData[15:0];
				sdram_WR_ADDR <= sdramRequest_address;
				sdram_WR <= 1;
				if (waitTimer == `WRITE_TIMER_CYCLES) sdramHandlerState <= `WRITE_WORD_UPPER;
				waitTimer <= waitTimer + 1;
			end
			`WRITE_WORD_UPPER : begin
				sdram_WR_DATA <= sdramRequest_wrData[31:16];
				sdram_WR_ADDR <= sdramRequest_address+1;
				if (waitTimer == `WRITE_TIMER_CYCLES*2) begin
					sdram_WR <= 0;
					writeSettled <= 0;
					sdramHandlerState <= `REQUEST_DONE;
				end
				waitTimer <= waitTimer + 1;
			end
			`READ_WORD_LOWER : begin
				sdram_RD_ADDR <= sdramRequest_address;
				sdram_RD <= 1;
				if (waitTimer == 1) begin 
					sdram_readData_lower <= sdram_RD_DATA;
					sdramHandlerState <= `READ_WORD_UPPER;
				end
				waitTimer <= waitTimer + 1;
			end
			`READ_WORD_UPPER : begin
				sdram_RD_ADDR <= sdramRequest_address+1;
				sdram_RD <= 1;
				if (waitTimer == 3) begin 
					sdram_readData_upper <= sdram_RD_DATA;
					sdramHandlerState <= `REQUEST_DONE;
				end
				waitTimer <= waitTimer + 1;
			end
			`REQUEST_DONE : begin
				sdramRequest_handled <= 1;
				waitTimer <= 0;
				sdramHandlerState <= `IDLE_STATE;
			end
		endcase
	end
end

//Read output control
always @(posedge clk) begin
	if (reset) begin
		port0_readData <= 0;
		port0_readDataAddress <= 0;
		port0_readDataValid <= 0;

		port1_readData <= 0;
		port1_readDataAddress <= 0;
		port1_readDataValid <= 0;
	end
	else begin
		if (sdramRequest_handled) begin
			if (sdramRequest_portId == 0) begin
				port0_readData <= sdram_readData;
				port0_readDataAddress <= sdramRequest_address;
				port0_readDataValid <= sdramRequest_isRead;
			end
			else if (sdramRequest_portId == 1) begin
				port1_readData <= sdram_readData;
				port1_readDataAddress <= sdramRequest_address;
				port1_readDataValid <= sdramRequest_isRead;
			end
		end
		else begin
			port0_readDataValid <= 0;
			port1_readDataValid <= 0;
		end
	end
end

endmodule