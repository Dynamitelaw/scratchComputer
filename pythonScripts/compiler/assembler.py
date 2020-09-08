import argparse
import sys
import math
import pandas as pd
from enum import Enum, unique


#Enum for supported instruction keys
@unique
class INST(Enum):
    #Integer arithmetic instructions
    ADDI = 0
    ADD = 1
    MOVE = 2
    SUB = 3
    MUL = 4
    DIV = 5
    DIVU = 6
    REM = 7
    REMU = 8
    SLTI = 9
    SLTIU = 10
    SLT = 11
    SLTU = 12
    JAL = 13
    J = 14


#Mapping of each register ABI name to their hardware address
registerNameMaping = {
	"x0":0,
	"zero":0,
	"x1":1,
	"ra":1,
	"x2":2,
	"sp":2,
	"x3":3,
	"gp":3,
	"x4":4,
	"tp":4,
	"x5":5,
	"t0":5,
	"x6":6,
	"t1":6,
	"x7":7,
	"t2":7,
	"x8":8,
	"s0":8,
	"fp":8,
	"x9":9,
	"s1":9,
	"x10":10,
	"a0":10,
	"x11":11,
	"a1":11,
	"x12":12,
	"a2":12,
	"x13":13,
	"a3":13,
	"x14":14,
	"a4":14,
	"x15":15,
	"a5":15,
	"x16":16,
	"a6":16,
	"x17":17,
	"a7":17,
	"x18":18,
	"s2":18,
	"x19":19,
	"s3":19,
	"x20":20,
	"s4":20,
	"x21":21,
	"s5":21,
	"x22":22,
	"s6":22,
	"x23":23,
	"s7":23,
	"x24":24,
	"s8":24,
	"x25":25,
	"s9":25,
	"x26":26,
	"s10":26,
	"x27":27,
	"s11":27,
	"x28":28,
	"t3":28,
	"x29":29,
	"t4":29,
	"x30":30,
	"t5":30,
	"x31":31,
	"t6":31
}


def parseInstruction(asmLine):
	'''
	Parses a single line of assembly code
	'''
	instructionName = asmLine.split(" ")[0]

	#Identify instruction type
	instructionEnum = -1
	if (instructionName == "addi"):
		instructionEnum = INST.ADDI
	elif (instructionName == "add"):
		instructionEnum = INST.ADD
	elif (instructionName == "mv"):
		instructionEnum = INST.MOVE
	elif (instructionName == "move"):
		instructionEnum = INST.MOVE
	elif (instructionName == "sub"):
		instructionEnum = INST.SUB
	elif (instructionName == "mul"):
		instructionEnum = INST.MUL
	elif (instructionName == "div"):
		instructionEnum = INST.DIV
	elif (instructionName == "divu"):
		instructionEnum = INST.DIVU
	elif (instructionName == "rem"):
		instructionEnum = INST.REM
	elif (instructionName == "remu"):
		instructionEnum = INST.REMU
	elif (instructionName == "slti"):
		instructionEnum = INST.SLTI
	elif (instructionName == "sltiu"):
		instructionEnum = INST.SLTIU
	elif (instructionName == "slt"):
		instructionEnum = INST.SLT
	elif (instructionName == "sltu"):
		instructionEnum = INST.SLTU
	elif (instructionName == "jal"):
		instructionEnum = INST.JAL
	elif (instructionName == "j"):
		instructionEnum = INST.J

	if (instructionEnum == -1):
		raise Exception("Unsupported instruction \"{}\"".format(instructionName))

	instruction = []
	instruction.append(instructionEnum)

	#Parse instruction args
	instructionArgs = [i.strip() for i in asmLine.replace(instructionName, "").split(",")]

	totalArgs = len(instructionArgs)
	if ((instructionEnum == INST.ADDI) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"addi\"")
	elif ((instructionEnum == INST.ADD) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"add\"")
	elif ((instructionEnum == INST.MOVE) and (totalArgs < 2)):
		raise Exception("Incorrect number of arguments for \"move\"")
	elif ((instructionEnum == INST.SUB) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"sub\"")
	elif ((instructionEnum == INST.MUL) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"mul\"")
	elif ((instructionEnum == INST.DIV) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"div\"")
	elif ((instructionEnum == INST.DIVU) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"divu\"")
	elif ((instructionEnum == INST.REM) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"rem\"")
	elif ((instructionEnum == INST.REMU) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"remu\"")
	elif ((instructionEnum == INST.SLTI) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"slti\"")
	elif ((instructionEnum == INST.SLTIU) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"sltiu\"")
	elif ((instructionEnum == INST.SLT) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"slt\"")
	elif ((instructionEnum == INST.SLTU) and (totalArgs < 3)):
		raise Exception("Incorrect number of arguments for \"sltu\"")
	elif ((instructionEnum == INST.JAL) and (totalArgs < 1)):
		raise Exception("Incorrect number of arguments for \"jal\"")
	elif ((instructionEnum == INST.J) and (totalArgs < 1)):
		raise Exception("Incorrect number of arguments for \"j\"")

	for arg in instructionArgs:
		try:
			#Check for explicit value
			argValue = int(arg)
			instruction.append(argValue)
		except Exception as e:
			try:
				#Check for register name
				instruction.append(registerNameMaping[arg])
			except Exception as e:
				#Presume arg is a label
				instruction.append(arg)

	return instruction

def parseAssemblyFile(filepath):
	'''
	Parses assembly file and outputs in-order list of instructions lists
		instruction tuple = [<lineNumber>, [<instruction_enum>,<arg1>,<arg2>,...]]
	'''
	labels = {}
	linedInstructions = []

	assemblyFile = open(filepath, "r")

	asmLine = " "
	lineNumber = 0
	while (asmLine):
		#Filter comments
		commentIndex = asmLine.find("#")
		if (commentIndex != -1):
			asmLine = asmLine[:commentIndex]

		#Trim whitespace
		asmLine = asmLine.strip().rstrip()
		instStart = -1
		for index in range(0,len(asmLine)):
			character = asmLine[index]
			if ((character != " ") and (character != "\t")):
				instStart = index
				asmLine = asmLine[index:]
				break
		if (instStart == -1):
			#no instruction on this line. Move on to next
			asmLine = assemblyFile.readline()
			lineNumber += 1
			continue

		#Identify line
		try:
			if (":" in asmLine):
				#line is a label. Add location index to labels dict
				labelName = asmLine.split(":")[0]
				labels[labelName] = len(linedInstructions)*4
			else:
				#line is an instruction
				instruction = parseInstruction(asmLine)
				linedInstructions.append([lineNumber, instruction])
		except Exception as e:
			raise Exception("ERROR: {} , line #{} | {}".format(filepath, lineNumber, e))

		asmLine = assemblyFile.readline()
		lineNumber += 1

	assemblyFile.close()

	#Link labels in linedInstructions
	finalInstructions = []
	for instructionElement in linedInstructions:
		lineNumber, instruction = instructionElement
		for index in range(1, len(instruction)):
			arg = instruction[index]
			if (isinstance(arg, str)):
				try:
					instruction[index] = labels[arg]
				except Exception as e:
					raise Exception("ERROR: {} , line #{} | Unkown label \"{}\"".format(filepath, lineNumber, arg))

		finalInstructions.append(instruction)

	return finalInstructions


def instructionsToInts(instructionList):
	'''
	Converts a list of instruction objects into a list of integers representing final machine code
	Refer to page 146 of risv-spec.pdf for instruction type specifications
	'''
	instructionValues = []

	for programCounter in range(0,len(instructionList)):
		instruction = instructionList[programCounter]
		instructionEnum = instruction[0]
		args = instruction[1:]

		#Determine instruction type and fields
		instructionFields = {}
		if (instructionEnum == INST.ADDI):
			instructionFields["type"] = "I"
			instructionFields["imm"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 0
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 19
		elif (instructionEnum == INST.ADD):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 0
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 0
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.MOVE):
			#pseudoinstruction | move rd,rs = add rd,zero,rs
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 0
			instructionFields["rs2"] = 0
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 0
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.SUB):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 32
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 0
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.MUL):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 1
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 0
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.DIV):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 1
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 4
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.DIVU):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 1
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 5
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.REM):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 1
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 6
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.REMU):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 1
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 7
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.SLTI):
			instructionFields["type"] = "I"
			instructionFields["imm"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 2
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 19
		elif (instructionEnum == INST.SLTIU):
			instructionFields["type"] = "I"
			instructionFields["imm"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 3
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 19
		elif (instructionEnum == INST.SLT):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 0
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 2
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.SLTU):
			instructionFields["type"] = "R"
			instructionFields["funct7"] = 0
			instructionFields["rs2"] = args[2]
			instructionFields["rs1"] = args[1]
			instructionFields["funct3"] = 3
			instructionFields["rd"] = args[0]
			instructionFields["opcode"] = 51
		elif (instructionEnum == INST.JAL):
			instructionFields["type"] = "J"
			instructionFields["imm"] = args[0] - programCounter
			instructionFields["rd"] = 1
			instructionFields["opcode"] = 111
		elif (instructionEnum == INST.J):
			instructionFields["type"] = "J"
			instructionFields["imm"] = args[0] - programCounter
			instructionFields["rd"] = 0
			instructionFields["opcode"] = 111

		#Concatenate instruction fields into binary string
		binaryString = ""
		if (instructionFields["type"] == "R"):
			funct7_string = format(instructionFields["funct7"], "07b")  #7bit value
			rs2_string = format(instructionFields["rs2"], "05b")  #5bit value
			rs1_string = format(instructionFields["rs1"], "05b")  #5bit value
			funct3_string = format(instructionFields["funct3"], "03b")  #3bit value
			rd_string = format(instructionFields["rd"], "05b")  #5bit value
			opcode_string = format(instructionFields["opcode"], "07b")  #7bit value

			binaryString = "{}{}{}{}{}{}".format(funct7_string, rs2_string, rs1_string, funct3_string, rd_string, opcode_string)

		elif (instructionFields["type"] == "I"):
			imm_string = ""
			if (instructionFields["imm"] < 0):
				#handle negative immediate arguments
				absVal = instructionFields["imm"] * -1
				absBinString = format(absVal, "012b")  #get binary string of abs value 

				#Convert to 2s compliment negative number
				flippedBitsString = absBinString.replace("0","z").replace("1","0").replace("z","1")  #Flip all bits
				unsignedVal = int(flippedBitsString, 2)
				twoCompInt = unsignedVal + 1

				imm_string = format(twoCompInt, "012b")
			else:
				imm_string = format(instructionFields["imm"], "012b")  #12bit value

			rs1_string = format(instructionFields["rs1"], "05b")  #5bit value
			funct3_string = format(instructionFields["funct3"], "03b")  #3bit value
			rd_string = format(instructionFields["rd"], "05b")  #5bit value
			opcode_string = format(instructionFields["opcode"], "07b")  #7bit value

			binaryString = "{}{}{}{}{}".format(imm_string, rs1_string, funct3_string, rd_string, opcode_string)

		elif (instructionFields["type"] == "J"):
			imm_string = ""
			if (instructionFields["imm"] < 0):
				#handle negative immediate arguments
				absVal = instructionFields["imm"] * -1
				absBinString = format(absVal, "021b")  #get binary string of abs value 

				#Convert to 2s compliment negative number
				flippedBitsString = absBinString.replace("0","z").replace("1","0").replace("z","1")  #Flip all bits
				unsignedVal = int(flippedBitsString, 2)
				twoCompInt = unsignedVal + 1

				imm_string = format(twoCompInt, "021b")
			else:
				imm_string = format(instructionFields["imm"], "021b")  #12bit value

			
			imm_stringReordered = "{}{}{}{}".format(imm_string[-21], imm_string[-11:-1], imm_string[-12], imm_string[-20:-12])  #Rearrange imm_stringOrdered to fit J-type bit index format [20|10:1|11|19:12]
			rd_string = format(instructionFields["rd"], "05b")  #5bit value
			opcode_string = format(instructionFields["opcode"], "07b")  #7bit value

			binaryString = "{}{}{}".format(imm_stringReordered, rd_string, opcode_string)

		else:
			raise Exception("Unsupported instruction type {}".format(instruction))

		#Convert binary instruction string to int and store in list
		instructionValues.append(int(binaryString, 2))

	return instructionValues


def writeLogisimHexFile(integerList, filepath):
	'''
	Write a list of integers into a Logisim hex file
	'''
	outputFile = open(filepath, "w")

	outputFile.write("v2.0 raw\n")
	# for val in integerList:
	# 	outputFile.write(hex(val)[2:])
	# 	outputFile.write(" ")
	# outputFile.write("\n")
	for val in integerList:
		outputFile.write(hex(val)[2:])
		outputFile.write("\n")

	outputFile.close()


def writeHexFile(integerList, filepath):
	'''
	Write a list of integers into a hex file
	'''
	outputFile = open(filepath, "w")

	for val in integerList:
		hexVal = hex(val)[2:].zfill(8)
		outputFile.write(hexVal)
		outputFile.write("\n")

	outputFile.close()


def generateCsvIndex(instructions, instructionIntValues, filepath):
	'''
	Will generate a csv index for each instruction
	'''
	indexDict = {
		"Address": [],
		"instruction": [],
		"DEC": [],
		"HEX": [],
		"BIN": []
	}

	for address in range(0, len(instructions)):
		intructionStr = str(instructions[address])
		intValue = instructionIntValues[address]
		hexValue = hex(intValue)
		binValue = format(intValue, "032b")
		
		indexDict["Address"].append(address)
		indexDict["instruction"].append(intructionStr)
		indexDict["DEC"].append(intValue)
		indexDict["HEX"].append(hexValue)
		indexDict["BIN"].append(binValue)

	df = pd.DataFrame(indexDict)
	df.to_csv(filepath, index=False)

	return df


if __name__ == '__main__':

	#Read command line arguments
	helpdesc = '''
SC Assembler v1.0 | Converts RISC-V assembly files into machine code.
Currently outputs only Logisim hex files.
'''

	parser = argparse.ArgumentParser(description = helpdesc)

	parser.add_argument("-asm", action="store", dest="asmPath", help="Filepath to input assembly file")
	parser.add_argument("-ohex", action="store", dest="hexPath", help="Specify path for output hex file. Defaults to same path as input asm")
	parser.add_argument("-oindex", action="store", dest="indexPath", help="If specified, assembler will output a csv index for each instruction")
	parser.add_argument("-logisim", action="store_true", help="If specified, assembler will add the Logisim-required header to the hex file. Note: This will break verilog simulations.")

	arguments = parser.parse_args()

	asmPath = arguments.asmPath
	hexPathArg = arguments.hexPath
	indexPath = arguments.indexPath
	logisim = arguments.logisim

	#Generate machine code
	print(" ")
	if (asmPath):
		instructions = parseAssemblyFile(asmPath)
		instructionIntValues = instructionsToInts(instructions)

		outputPath = asmPath.replace(".asm", "") + ".hex"
		if (hexPathArg):
			outputPath = hexPathArg

		if (logisim):
			outputPath = outputPath.replace(".hex", "_logisim.hex")
			writeLogisimHexFile(instructionIntValues, outputPath)
		else:
			writeHexFile(instructionIntValues, outputPath)

		if (indexPath):
			generateCsvIndex(instructions, instructionIntValues, indexPath)

		print("Done!")
		print ("{} total instructions".format(len(instructionIntValues)))
		addressBits = math.log(len(instructionIntValues),2)
		if (logisim and (addressBits > 24)):
			print ("WARNING: Program too large to run in Logisim")
	else:
		print("ERROR: Missing required argument \"-asm\"")
		sys.exit()
