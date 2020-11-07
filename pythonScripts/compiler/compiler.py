import os
import sys
import traceback
import argparse

from pycparser import c_parser, c_ast, parse_file, c_generator
import assembler
import utils
from utils import COLORS, printColor
import compGlobals as globals
from compClasses import dataElement, structDef
from astConversions import covertFuncToAssembly, convertDeclItem


def getDefinitions(ast):
	'''
	Returns:
		-dictionary of function definitions in the following format
			{"<functionName>": c_ast.FuncDef, ...}
		-list of global variable declarations
			[c_ast.Decl, ...]
		-list of struct declarations
			[c_ast.Struct, ...]
	'''
	if ast is None:
		return {}, []

	childrens = [item[1] for item in ast.children()]
	functions = {}
	globalVarDelcarations = []
	structDeclarations = []

	for item in childrens:
		if isinstance(item,c_ast.FuncDef):
			functions[item.decl.name] = item
		elif isinstance(item, c_ast.Decl):
			if isinstance(item.type, c_ast.TypeDecl):
				globalVarDelcarations.append(item)
			elif isinstance(item.type, c_ast.Struct):
				structDeclarations.append(item)
			else:
				raise Exception("Unsupported item declared\n{}".format(item))	
		else:
			raise Exception("Unsupported item declared\n{}".format(item))

	return functions, globalVarDelcarations, structDeclarations


def precleanCFile(filepath):
	'''
	Preprocesses C file into a clean one for parsing.
	Returns filepath of clean C file
	
	returnType:
		<str> filePath
	'''
	cFileIn = open(filepath, "r")
	rootPath = os.path.dirname(os.path.abspath(filepath))

	cOutPath = "{}.temp".format(os.path.split(filepath)[-1])
	cFileOut = open(cOutPath, "w")

	inLine = " "
	while (inLine):
		inLine = cFileIn.readline()
		outline = inLine

		if ("#include" in outline):
			includePath = outline.split(" ")[-1].rstrip().replace("\"", "")
			if (includePath[0] != "/"):
				includePath = "{}".format(os.path.join(rootPath, includePath))
			outline = " ".join([outline.split(" ")[0], "\"{}\"\n".format(includePath)])
		else:
			outline = outline.replace("true", "1")
			outline = outline.replace("false", "0")
			outline = outline.replace("bool ", "unsigned char ")

		cFileOut.write(outline)

	cFileIn.close()
	cFileOut.close()

	return cOutPath


if __name__ == '__main__':
	#########
	# Read command line arguments
	#########
	helpdesc = '''
SC Compiler v0.1 | Converts C code into assembly and machine code.
Currently only supports a subset of the C language
'''

	parser = argparse.ArgumentParser(description = helpdesc)

	parser.add_argument("filepath", action="store", help="Filepath to top-level C code")
	parser.add_argument("-o", action="store", dest="hexPath", help="Specify path for output hex file. Defaults to same path as input file")
	parser.add_argument("-index", action="store", dest="indexPath", help="If specified, assembler will output a csv index for each instruction")
	parser.add_argument("-mem", action="store", dest="memorySize", help="Memory size in bytes. If specified, compiler will initialize stack pointer to specified address, or the closest word-aligned address")
	parser.add_argument("-keepasm", action="store_true", help="If specified, compiler will not delete the intermediate assembly file.")
	parser.add_argument("-logisim", action="store_true", help="If specified, assembler will add the Logisim-required header to the hex file. Note: This will break verilog simulations.")

	arguments = parser.parse_args()

	cFilePath = arguments.filepath
	hexPathArg = arguments.hexPath
	indexPath = arguments.indexPath

	memorySizeString = arguments.memorySize
	memorySize = None
	if (memorySizeString):
		if ("K" in memorySizeString):
			memorySizeString = memorySizeString.replace("K", "")
			memorySize = int(memorySizeString) * 2**10
		elif ("M" in memorySizeString):
			memorySizeString = memorySizeString.replace("M", "")
			memorySize = int(memorySizeString) * 2**20
		elif ("G" in memorySizeString):
			memorySizeString = memorySizeString.replace("G", "")
			memorySize = int(memorySizeString) * 2**30
		else:
			memorySize = int(4 * int(int(memorySizeString) / 4))

	keepasm = arguments.keepasm
	logisim = arguments.logisim

	hexPath = None
	if (not hexPathArg):
		cFilename = os.path.split(cFilePath)[-1].split(".")[0]
		hexPath = cFilename + ".hex"
	else:
		hexPath = hexPathArg

	try:
		#########
		# Translate C file into assembly file
		#########

		#Parse C file
		cleanFilePath = precleanCFile(cFilePath)
		ast = parse_file(cleanFilePath, use_cpp=True)

		#Get function defs, global declarations, and struct defs
		definedFunctions = {}
		globalVarDelcarations = []
		structDeclarations = []
		definedFunctions, globalVarDelcarations, structDeclarations = getDefinitions(ast)  #<TODO> handle global variables

		#Parse global declarations
		#<TODO>
		#print(globalVarDelcarations)

		#Parse struct definitions
		for structDecl in structDeclarations:
			structObj = structDef(structDecl.type)
			globals.typeSizeDictionary[structObj.name] = structObj.size
			globals.structDictionary[structObj.name] = structObj
		
		#Translate functions into assembly snippets
		if ("main" in definedFunctions):
			for functionName in definedFunctions:
				#<TODO> multithread these translations
				funcDef = definedFunctions[functionName]
				covertFuncToAssembly(funcDef)
		else:
			printColor("ERROR: main function is not defined", color=COLORS.ERROR)
			sys.exit()
		

		#Keep track of cLine/programCounter mappings for debugger annotations
		debuggerAnnotations = {}
		debuggerAnnotations["cFileMap"] = {}
		debuggerAnnotations["scopeStateMap"] = {}

		#Create final assembly file
		outputDirectory, hexFilename = os.path.split(hexPath)
		assemblyFilePath = os.path.join(outputDirectory, "{}.asm".format(hexFilename.split(".")[0]))
		
		asmFile = open(assemblyFilePath, "w")
		asmFile.write(".text\n")
		
		programCounter = 0
		if (memorySize):
			#Initialize sp
			stackPointerStart = int(4 * int(int(memorySize) / 4))
			if (stackPointerStart < 2048):
				asmFile.write("addi sp, zero, {}\n".format(int(stackPointerStart)))
				programCounter += 4
			else:
				stackPointerStart_31_12 = int(stackPointerStart/4096)
				stackPointerStart_11 = int((stackPointerStart-(stackPointerStart_31_12*4096))/2048)
				stackPointerStart_11_0 = stackPointerStart%4096

				upperValue = stackPointerStart_31_12 + stackPointerStart_11
				lowerValue = stackPointerStart_11_0

				asmFile.write("lui sp, {} #Loading val {}\n".format(upperValue, stackPointerStart))
				asmFile.write("addi sp, sp, {}\n".format(lowerValue))
				programCounter += 8
				'''
				upperValue = int(stackPointerStart/4096)
				lowerValue = stackPointerStart%4096
				if (int(lowerValue/2048) == 1):
					# Sad :(
					#Get lower val into register
					asmFile.write("lui sp, 1 #Loading val {}\n".format(stackPointerStart))
					asmFile.write("addi sp, sp, {}\n".format(lowerValue))
					if (upperValue > 0):
						#Get upper val into temp register t0
						asmFile.write("lui t0, {}\n".format(upperValue))
						#Combine them
						asmFile.write("add sp, sp, t0\n")

						programCounter += 16
				else:
					asmFile.write("lui sp, {} #Loading val {}\n".format(upperValue, stackPointerStart))
					asmFile.write("addi sp, zero, {}\n".format(lowerValue))
					programCounter += 8
				'''

		asmFile.write("la ra, PROGRAM_END\n")  #initialize return address for main
		programCounter += 8

		asmFile.write("la gp, HEAP_START\n")  #initialize address for global pointer
		programCounter += 8

		#Write main first
		instList = definedFunctions["main"].coord
		instList.compressScopeStates()
		for i in range(0, instList.length()):
			inst = instList.instructions[i]
			coord = instList.coords[i]
			scopeState = instList.scopeStates[i]

			debuggerAnnotations["cFileMap"][programCounter] = coord
			debuggerAnnotations["scopeStateMap"][programCounter] = scopeState

			if not (":" in inst):
				asmFile.write("{}\n".format(inst))
			else:
				asmFile.write("{}\n".format(inst))

			if not (":" in inst):
				programCounter += 4

		asmFile.write("\n")
		del definedFunctions["main"]

		#Write other functions
		for functionName in definedFunctions:
			instList = definedFunctions[functionName].coord
			instList.compressScopeStates()
			for i in range(0, instList.length()):
				inst = instList.instructions[i]
				coord = instList.coords[i]
				scopeState = instList.scopeStates[i]

				debuggerAnnotations["cFileMap"][programCounter] = coord
				debuggerAnnotations["scopeStateMap"][programCounter] = scopeState

				if not (":" in inst):
					asmFile.write("{}\n".format(inst))
				else:
					asmFile.write("{}\n".format(inst))

				if not (":" in inst):
					programCounter += 4
			asmFile.write("\n")

		asmFile.write("PROGRAM_END:\nadd zero, zero, zero\n")  #Program end label/nop

		#Write data section
		asmFile.write(".data\n")

		for dataLabel in globals.dataSegment:
			dataElement = globals.dataSegment[dataLabel]
			value = dataElement.value
			size = dataElement.size

			valueStr = "?"
			if (value):
				valueStr = str(value)

			typeStr = ""
			if (size == 1):
				typeStr = ".byte"
			elif (size == 2):
				typeStr = ".half"
			elif (size == 4):
				typeStr = ".word"
			elif (size == 8):
				typeStr = ".double"

			dataDef = "{}: {} {}\n".format(dataLabel, typeStr, valueStr)
			asmFile.write(dataDef)

		asmFile.write("HEAP_START: .word 0\n")  #Heap start

		asmFile.close()


		#Convert assembly file to hex
		assembler.main(assemblyFilePath, hexPath, indexPath, logisim, debuggerAnnotations)

		#Cleanup
		os.remove(cleanFilePath)

	except Exception as e:
		printColor("{}\n{}".format(traceback.format_exc(), globals.cFileCoord), color=COLORS.ERROR)
		sys.exit()
