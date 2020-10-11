import os
import sys
import traceback
import argparse
import copy
from collections import OrderedDict

from pycparser import c_parser, c_ast, parse_file, c_generator
import assembler
import utils


#Global vars
g_cFileCoord = None
g_whileCounter = 0
g_forCounter = 0
g_ifCounter = 0
g_variableNameCoutners = {}

g_dataSegment = {}
g_typeSizeDictionary = {
	"int": 4,
	"unsigned int": 4,
	"short": 2,
	"unsigned short": 2,
	"long": 8,
	"unsigned long": 8,
	"char": 1,
	"unsigned char": 1,
	"float": 4,
	"double": 8,
	"long double": 10
}
g_structDictionary = {}


#Colored printed for errors
class COLORS:
	DEFAULT = '\033[0m'
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	ERROR = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


def printColor(text, color=COLORS.DEFAULT, resetColor=True):
	'''
	Prints colored text to the terminal
	'''
	if (resetColor):
		formattedText = "{}{}{}".format(color, text, COLORS.DEFAULT)
		print(formattedText)
	else:
		formattedText = "{}{}".format(color, text)
		print(formattedText)


class dataElement:
	def __init__(self, label, value=None, dataType=None, size=4, signed=True):
		self.label = label
		self.value = value
		self.dataType = dataType
		self.size = size
		self.signed = signed


def getArraySize(arrayDecl):
		'''
		Returns the size of an array in bytes.
		'''
		arrayLength = int(arrayDecl.dim.value)
		arrayType = arrayDecl.type

		if isinstance(arrayType, c_ast.TypeDecl):
			elementType = "".join(arrayType.type.names)
			elementSize = g_typeSizeDictionary[elementType]

			returnVar = [arrayLength * elementSize, [elementSize]]
			return returnVar
		elif isinstance(arrayType, c_ast.ArrayDecl):
			subArraySize, subElementSize = getArraySize(arrayType)
			returnVar = [arrayLength * subArraySize, [subArraySize]+subElementSize]
			return returnVar
		else:
			raise Exception("Input declaration must be a c_ast.ArrayDecl object")


class struct:
	'''
	This class is used to represent all defined structures
	This acts as a place to store:
		struct name
		struct size
		member items
		member offsets
	'''
	class structMember:
		def __init__(self, name, size, memberType=None, reference=None, offset=None):
			self.name = name
			self.size = size
			self.type = memberType
			self.reference = reference
			self.offset = offset

		def __str__(self):
			tempDict = {}
			tempDict["name"] = self.name
			tempDict["type"] = self.type
			tempDict["size"] = self.size
			tempDict["offset"] = self.offset
			tempDict["reference"] = self.reference

			return str(tempDict)
		def __repr__(self):
			tempDict = {}
			tempDict["name"] = self.name
			tempDict["type"] = self.type
			tempDict["size"] = self.size
			tempDict["offset"] = self.offset
			tempDict["reference"] = self.reference

			return str(tempDict)

	def __init__(self, structItem):
		global g_cFileCoord
		g_cFileCoord = structItem.coord

		self.name = structItem.name
		self.members = {}

		membersTemp = []  #[(size, name), ...]

		for declItem in structItem.decls:
			if isinstance(declItem.type, c_ast.ArrayDecl):
				name = declItem.name
				size = getArraySize(declItem.type)[0]
				membersTemp.append((size, name))

				self.members[name] = self.structMember(name, size)
			elif isinstance(declItem.type.type, c_ast.IdentifierType):
				name = declItem.name
				varType = " ".join(declItem.type.type.names)
				size = g_typeSizeDictionary[varType]
				membersTemp.append((size, name))

				self.members[name] = self.structMember(name, size)
			elif isinstance(declItem.type.type, c_ast.Struct):
				name = declItem.name
				structType = declItem.type.type.name
				size = g_typeSizeDictionary[structType]
				membersTemp.append((size, name))

				self.members[name] = self.structMember(name, size)
			else:
				raise Exception("Unsupported decl in structure | {}\n{}".format(g_cFileCoord, declItem))

		#Determine struct size and member offsets
		membersTemp.sort(reverse=True)
		self.size = 0

		for element in membersTemp:
			size, name = element

			#Add buffer space between items if we need to
			bufferSize = 0
			if (size >= 4):
				if (self.size%4 != 0):
					#Current structure not word aligned. Need to add buffer space
					bufferSize = 4 - (self.size%4)
			elif (size >= 2):
				if (self.size%2 != 0):
					#Current structure not half aligned. Need to add buffer space
					bufferSize = 2 - (self.size%2)
			self.size += bufferSize

			#Set offset for struct member
			self.members[name].offset = self.size

			#Increment struct size
			self.size += size

		#Add buffer space to end of struct if we need to
		bufferSize = 0
		if (self.size%4 != 0):
			#Current structure not word aligned. Need to add buffer space
			bufferSize = 4 - (self.size%4)
		self.size += bufferSize


	def __str__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["size"] = self.size
		tempDict["members"] = self.members

		return str(tempDict)
	def __repr__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["size"] = self.size
		tempDict["members"] = self.members

		return str(tempDict)


class variable:
	'''
	This class is used to represent all explicit and implicit variables in a given scope.
	This acts as a place to store:
		variable name
		current register location
		variable type
		variable size (in bytes)
	'''
	def __init__(self, name, register=None, varType=None, size=None, subElementSize=None, signed=True, volatileRegister=False):
		self.name = name
		self.register = register
		self.type = varType
		self.size = size
		self.subElementSize = subElementSize
		self.signed = signed
		self.volatileRegister = volatileRegister

	def __str__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["register"] = self.register
		tempDict["type"] = self.type
		tempDict["size"] = self.size
		tempDict["signed"] = self.signed
		tempDict["volatileRegister"] = self.volatileRegister

		return str(tempDict)
	def __repr__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["register"] = self.register
		tempDict["type"] = "\"{}\"".format(self.type).replace("\n","").replace(" ", "")
		tempDict["size"] = self.size
		tempDict["signed"] = self.signed
		tempDict["volatileRegister"] = self.volatileRegister

		return str(tempDict)


class instructionList:
	'''
	This class is used to store all assembly instructions for a given scope.
	This acts as a place to store:
		list of instruction strings
		scope states over time
		C filename and line numbers over time
	'''
	def __init__(self, scope):
		self.instructions = []
		self.scopeStates = []
		self.coords = []
		self.scope = scope

	def __str__(self):
		return str(self.instructions)


	def __repr__(self):
		return str(self.instructions)


	def append(self, instructionString):
		'''
		Add an instruction string to this instructionList
		'''
		self.instructions.append(copy.deepcopy(instructionString))
		self.scopeStates.append(copy.deepcopy(self.scope.getState()))
		if (g_cFileCoord):
			self.coords.append({"file": os.path.abspath(g_cFileCoord.file.replace(".temp","")), "lineNum": g_cFileCoord.line})
		else:
			self.coords.append({"file": None, "lineNum": None})

	def __add__(self, otherList):
		returnList = instructionList(self.scope)
		returnList.instructions = copy.deepcopy(self.instructions) + copy.deepcopy(otherList.instructions)
		returnList.scopeStates = copy.deepcopy(self.scopeStates) + otherList.scopeStates
		returnList.coords = copy.deepcopy(self.coords) + copy.deepcopy(otherList.coords)

		return returnList

	def length(self):
		return len(self.instructions)

	def updateScopeState(self):
		if (len(self.scopeStates) > 0):
			self.scopeStates[-1] = self.scope.getState()


	def compressScopeStates(self):
		'''
		Compress scopeStates list to decrease annotation size. 
		If a scope state has not changed from a previous value, it is replaced with the index of the most recent state change
		'''
		compressedStateList = []

		previousState = self.scopeStates[0]
		previousStateIndex = 0
		compressedStateList.append(previousState)

		for index in range(1, len(self.scopeStates)):
			currentState = self.scopeStates[index]

			#Determine if we should update scope state
			scopeDifferent = False
			if (":" in self.instructions[index-1]):
				scopeDifferent = True

			if isinstance(currentState, dict):
				for majorKey in currentState:
					currentMinorKeys = None
					if isinstance(currentState[majorKey], dict):
						currentMinorKeys = currentState[majorKey].keys()
					elif isinstance(currentState[majorKey], list):
						currentMinorKeys = [i for i in range(0,len(currentState[majorKey]))]

					prevMinorKeys = None
					if isinstance(currentState[majorKey], dict):
						prevMinorKeys = previousState[majorKey].keys()
					elif isinstance(currentState[majorKey], list):
						prevMinorKeys = [i for i in range(0,len(previousState[majorKey]))]


					if (len(prevMinorKeys) != len(currentMinorKeys)):
						scopeDifferent = True
						break

					if isinstance(currentState[majorKey], dict):
						for minorKey in currentState[majorKey]:
							if (minorKey in previousState[majorKey]):
								currentVal = currentState[majorKey][minorKey]
								previousVal = previousState[majorKey][minorKey]

								if (previousVal != currentVal):
									scopeDifferent = True
									break
							else:
								scopeDifferent = True
								break

					if (scopeDifferent):
						break

			if (scopeDifferent):
				compressedStateList.append(currentState)
				previousState = currentState
				previousStateIndex = index
			else:
				compressedStateList.append(previousStateIndex - len(compressedStateList))


		self.scopeStates = compressedStateList


class scopeController:
	'''
	This class manages and controls the local scope of any given function.
	The scopeController is responsible for 
		storing and managing variables within the scope
		managing register usage
		managing local stack
		maintaining variable coherency
	'''
	def __init__(self, name):
		self.name = name
		self.variableDict = {}
		self.localStack = OrderedDict()
		self.usedRegisters = OrderedDict()
		self.availableRegisters = [
			"s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
			"a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
			"t0", "t1", "t2", "t3", "t4", "t5", "t6"
			]
		self.loadHistory = []
		self.virginSaveRegisters = ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"]
		self.expressionCounter = 0
		self.stackBufferCounter = 0

	def __str__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["variableDict"] = self.variableDict
		tempDict["localStack"] = self.localStack
		tempDict["usedRegisters"] = self.usedRegisters
		tempDict["availableRegisters"] = self.availableRegisters
		tempDict["virginSaveRegisters"] = self.virginSaveRegisters

		return str(tempDict)
	def __repr__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["variableDict"] = self.variableDict
		tempDict["localStack"] = self.localStack
		tempDict["usedRegisters"] = self.usedRegisters
		tempDict["availableRegisters"] = self.availableRegisters
		tempDict["virginSaveRegisters"] = self.virginSaveRegisters

		return str(tempDict)


	def mergeScopeBranch(self, scopeBranch, indentLevel=0):
		'''
		Will undro any differences between this scope and the current branch scope.
		All variable locations and the state of the stack will be reverted from the branched state to this scope.
		
		Returns an instructionList item.
		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		branchVariableDict = scopeBranch.variableDict
		branchLocalStack = scopeBranch.localStack
		branchUsedRegisters = scopeBranch.usedRegisters
		branchAvailableRegisters = scopeBranch.availableRegisters

		#Undo any scope diffs for branched variables
		for variableName in self.variableDict:
			if (variableName in branchVariableDict):
				branchVariableObj = branchVariableDict[variableName]
				variableObj = self.variableDict[variableName]

				if (variableObj.register != branchVariableObj.register):
					if (variableObj.register):
						#Variable should be in a different register
						instructions += scopeBranch.moveVariable(variableName, variableObj.register, indentLevel=indentLevel)
					else:
						#Variable should be on stack
						instructions += scopeBranch.storeStack(variableName, freeRegister=True, indentLevel=indentLevel)

		#Reset stack to parent state
		if (len(self.localStack) != len(branchLocalStack)):
			#branch added things to the stack. Check if any are register saves
			for variableName in branchLocalStack:
				if not (variableName in self.localStack):
					if ("<SAVE>" in variableName):
						#Restore save variable
						instructions += scopeBranch.moveVariable(variableName, variableName.replace("<SAVE>_", ""), indentLevel=indentLevel)
			
			#Deallocate branch stack
			deallocateLength = 0
			branchStackList = list(branchLocalStack.items())
			for index in range(len(self.localStack), len(branchLocalStack)):
				deallocateLength += branchStackList[index][1]
				
			instructions.append("{}addi sp, sp, {}".format(indentString, deallocateLength))


		return instructions
	

	def createExpressionResult(self, register=None,varType=None, size=4, signed=True, indentLevel=0):
		'''
		Will create an variable to represent the implicit variable of an expression result.
		Returns the variable name to caller

		returnType:
			<str> variableName
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableName = "<EXPR_RESULT>_{}".format(self.expressionCounter)
		self.expressionCounter += 1
		instructions += self.addVariable(variableName, register=register, varType=varType, size=size, signed=signed, indentLevel=indentLevel)

		return instructions, variableName


	def addVariable(self, variableName, register=None, varType=None, size=None, signed=None, volatileRegister=False, indentLevel=0):
		'''
		Declare a new variable in this scope.
		If register keyword is included, the variable will be initialized the the value currently stored in specified register. 
		Specified register will be removed from available registers.
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		#Get size of variable
		varSize = None
		subElementSize = None
		if (size):
			varSize = size
		elif (varType):
			if isinstance(varType, c_ast.TypeDecl):
				if isinstance(varType.type, c_ast.IdentifierType):
					names = "".join(varType.type.names)
					varSize = g_typeSizeDictionary[names]
				elif isinstance(varType.type, c_ast.Struct):
					name = varType.type.name
					varSize = g_typeSizeDictionary[name]
				else:
					raise Exception("Unsupported TypeDecl | {}\n{}".format(g_cFileCoord, varType))
			elif isinstance(varType, c_ast.ArrayDecl):
				varSize, subElementSize = getArraySize(varType)
		else:
			varSize = 4

		#Get if variable is signed
		varSigned = None
		if (signed):
			varSigned = signed
		elif (varType):
			if isinstance(varType.type, c_ast.IdentifierType):
				names = varType.type.names
				if ("unsigned" in names):
					varSigned = False
				else:
					varSigned = True
			else:
				varSigned = None
		else:
			varSigned = True

		#Set register location
		if (register):
			if (variableName in self.variableDict):
				instructions += self.moveVariable(variableName, register, indentLevel=indentLevel)
			else:
				#Current register location specified
				if (register in self.usedRegisters):
					print(self.usedRegisters.items())
					raise Exception("Register \"{}\" already in use by variable \"{}\"".format(register, self.usedRegisters[register]))

				self.usedRegisters[register] = variableName

				if (register in self.availableRegisters):
					self.availableRegisters.remove(register)

				self.variableDict[variableName] = variable(variableName, register=register, varType=varType, size=varSize, subElementSize=subElementSize, signed=varSigned, volatileRegister=volatileRegister)
		else:
			if (variableName in self.variableDict):
				pass
			else:
				#No register location specified. Leave blank
				self.variableDict[variableName] = variable(variableName, register=None, varType=varType, size=varSize, subElementSize=subElementSize, signed=varSigned, volatileRegister=volatileRegister)

		return instructions


	def removeVariable(self, variableName):
		'''
		Remove an existing variable from this scope.
		'''
		if (variableName):
			try:
				variableObj = self.variableDict[variableName]
				if (variableObj.register):
					del self.usedRegisters[variableObj.register]
					self.availableRegisters.append(variableObj.register)
					self.availableRegisters.sort()
				del self.variableDict[variableName]
			except Exception as e:
				raise Exception("ERROR: Could not remove variable \"{}\"{}".format(variableName, e))


	def storeStack(self, variableName, freeRegister=False, indentLevel=0):
		'''
		Store the specified variable onto the stack.
		If freeRegister is True, will also deallocate current register.

		Returns a list of instruction strings.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope".format(variableName))


		if (not variableObj.volatileRegister):
			#Check if variable already on stack
			if (variableName in self.localStack):
				#Get location of variable relative to current stack pointer  #<TODO> handle storing values on non-word aligned locations
				varLocation = 0
				currentLocation = 0
				for var in self.localStack:
					currentLocation += self.localStack[var]
					if (var == variableName):
						varLocation = currentLocation
				currentStackSize = currentLocation

				stackOffset = currentStackSize - varLocation

				#Update value of variable in stack
				if (variableObj.register):
					if (variableObj.size == 1):
						instructions.append("{}sb {}, {}(sp)".format(indentString, variableObj.register, stackOffset))
					elif (variableObj.size == 2):
						instructions.append("{}sh {}, {}(sp)".format(indentString, variableObj.register, stackOffset))
					elif (variableObj.size == 4):
						instructions.append("{}sw {}, {}(sp)".format(indentString, variableObj.register, stackOffset))

			else:
				#Get current size of stack
				currentStackSize = 0
				for var in self.localStack:
					currentStackSize += self.localStack[var]

				#Add buffer space if needed
				#<TODO> reassign buffer space to store sub-word variables when possible
				bufferSize = 0
				if (variableObj.size >= 4):
					if (currentStackSize%4 != 0):
						#SP is not word aligned. Need to add buffer space to stack
						bufferName = "<BUFFER>_{}".format(self.stackBufferCounter)
						self.stackBufferCounter += 1
						bufferSize = 4 - (currentStackSize%4)
						self.localStack[bufferName] = bufferSize
				elif (variableObj.size >= 2):
					if (currentStackSize%2 != 0):
						#SP is not half aligned. Need to add buffer space to stack
						bufferName = "<BUFFER>_{}".format(self.stackBufferCounter)
						self.stackBufferCounter += 1
						bufferSize = 2 - (currentStackSize%2)
						self.localStack[bufferName] = bufferSize

				#Allocate space on stack and store current value of regSource
				self.localStack[variableName] = variableObj.size	

				instructions.append("{}addi sp, sp, -{}".format(indentString, variableObj.size+bufferSize))
				if (variableObj.register):
					if (variableObj.size == 1):
						instructions.append("{}sb {}, 0(sp)".format(indentString, variableObj.register))
					elif (variableObj.size == 2):
						instructions.append("{}sh {}, 0(sp)".format(indentString, variableObj.register))
					elif (variableObj.size == 4):
						instructions.append("{}sw {}, 0(sp)".format(indentString, variableObj.register))


		if (freeRegister):
			del self.usedRegisters[variableObj.register]
			self.availableRegisters.append(variableObj.register)
			variableObj.register = None

		if (variableObj.volatileRegister):
			self.removeVariable(variableName)

		return instructions


	def getVariable(self, variableName):
		return self.variableDict[variableName]


	def getPointer(self, variableName, regDestOverride=None, indentLevel=0):
		'''
		Get the memory location of specified variable on the stack.
		Will allocate stack space to variable if not already allocated.
		Returns an instructionList object, and the register name the pointer was written to.

		returnType:
			<tuple> ( <instructionList> instructions , <str> destinationRegister , <str> pointerVariableName)
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		#Get variable object
		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope | {}".format(variableName, g_cFileCoord))

		if not (variableName in self.localStack):
			#Allocate space on stack for variable
			instructions += self.storeStack(variableName, indentLevel=indentLevel)

		#Get location of variable relative to current stack pointer
		varLocation = 0
		currentLocation = 0
		for var in self.localStack:
			currentLocation += self.localStack[var]
			if (var == variableName):
				varLocation = currentLocation
		currentStackSize = currentLocation

		stackOffset = currentStackSize - varLocation

		#Write address of variable to register
		regDest = None
		pointerName = "<PTR>_&{}".format(variableName)
		if (pointerName in self.variableDict):
			regDest = self.variableDict[pointerName].register
		
		if (not regDest):
			instructionsTemp, regDest = self.getFreeRegister(preferTemp=True, regOverride=regDestOverride, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions +=  self.addVariable(pointerName, register=regDest, volatileRegister=True, indentLevel=indentLevel)


		instructions.append("{}addi {}, sp, {}".format(indentString, regDest, stackOffset))  #<TODO> handle if offset is too big for immediate


		return instructions, regDest, pointerName


	def loadStack(self, variableName, regDestOverride=None, indentLevel=0):
		'''
		Load the specified variable from the stack into a register.
		Returns a list of instruction strings.

		params:
			regDestOverride - if defined, the variable will be loaded into the specified register. Else, it can be loaded into any regsiter. 
		
		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		#Get variable object
		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope".format(variableName))

		#Check if variable already in register
		if (self.getRegisterLocation(variableName)):
			if (regDestOverride):
				instructions += self.moveVariable(variableName, regDestOverride)
			return instructions

		#Get free register to store
		instructionsTemp, regDest = self.getFreeRegister(indentLevel=indentLevel, regOverride=regDestOverride)
		instructions += instructionsTemp

		if (variableName in self.variableDict):
			if (variableName in self.localStack):
				#Get location of variable relative to current stack pointer
				varLocation = 0
				currentLocation = 0
				for var in self.localStack:
					currentLocation += self.localStack[var]
					if (var == variableName):
						varLocation = currentLocation
				currentStackSize = currentLocation

				stackOffset = currentStackSize - varLocation

				#Load variable from stack 
				if (variableObj.size == 1):
					if (variableObj.signed):
						instructions.append("{}lb {}, {}(sp)".format(indentString, regDest, stackOffset))
					else:
						instructions.append("{}lbu {}, {}(sp)".format(indentString, regDest, stackOffset))
				elif (variableObj.size == 2):
					if (variableObj.signed):
						instructions.append("{}lh {}, {}(sp)".format(indentString, regDest, stackOffset))
					else:
						instructions.append("{}lhu {}, {}(sp)".format(indentString, regDest, stackOffset))
				elif (variableObj.size == 4):
					instructions.append("{}lw {}, {}(sp)".format(indentString, regDest, stackOffset))

				
			#Assign regDest to variable object
			variableObj.register = regDest
			self.usedRegisters[regDest] = variableName
			self.loadHistory.append(variableName)


			return instructions
		
		else:
			raise Exception("ERROR: variable \"{}\" not currently defined in variableDict".format(variableName))


	def getRegisterLocation(self, variableName):
		'''
		Returns None if variable is not currently in a register

		returnType:
			<str> registerName
		'''
		if (variableName in self.variableDict):
			return self.variableDict[variableName].register
		else:
			raise Exception("ERROR: variable \"{}\" not currently defined in variableDict".format(variableName))


	def getVariableName(self, registerName):
		'''
		Returns None if a variable is not currently in the specified register

		returnType:
			<str> variableName
		'''
		if (registerName in self.usedRegisters):
			return self.usedRegisters[registerName]
		else:
			return None


	def getFreeRegister(self, preferTemp=False, tempsAllowed=True, forceFree=True, regOverride=None, indentLevel=0):
		'''
		Returns the name of an available register to the caller.
		params:
			preferTemp - if True, will prioritize returning a temporary register. Else, will priotize returning save register
			tempsAllowed - if False, will only return save registers
			forceFree - if True, will deallocate a register if no free registers exist. if False, will return None
			regOverride - if specified, function will allocate the specified register

		returnType:
			( <instructionList> instructions, <str> registerName )
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		self.availableRegisters.sort()

		registerName = None

		if (regOverride):
			registerName = regOverride
			instructions += self.releaseRegister(registerName, indentLevel=indentLevel)
			self.availableRegisters.remove(registerName)

			return instructions, registerName

		if (preferTemp):
			#Check for free temp register
			t_Registers = [i for i in self.availableRegisters if "t" in i]
			if (len(t_Registers) > 0):
				registerName = t_Registers[0]
				self.availableRegisters.remove(registerName)

				return instructions, registerName

			#Check for free argument register
			a_Registers = [i for i in self.availableRegisters if "a" in i]
			if (len(a_Registers) > 0):
				registerName = a_Registers[0]
				self.availableRegisters.remove(registerName)

				return instructions, registerName

			#Check for free save register
			s_Registers = [i for i in self.availableRegisters if "s" in i]
			if (len(s_Registers) > 0):
				registerName = s_Registers[0]
				self.availableRegisters.remove(registerName)
				#don't return yet. must check if it is virgin save reg
		else:
			#Check for free save register
			s_Registers = [i for i in self.availableRegisters if "s" in i]
			if (len(s_Registers) > 0):
				registerName = s_Registers[0]
				self.availableRegisters.remove(registerName)
			
			if (not registerName and tempsAllowed):
				#Check for free temp register
				t_Registers = [i for i in self.availableRegisters if "t" in i]
				if (len(t_Registers) > 0):
					registerName = t_Registers[0]
					self.availableRegisters.remove(registerName)

					return instructions, registerName

				#Check for free argument register
				a_Registers = [i for i in self.availableRegisters if "a" in i]
				if (len(a_Registers) > 0):
					registerName = a_Registers[0]
					self.availableRegisters.remove(registerName)

					return instructions, registerName


		if (registerName in self.virginSaveRegisters):
			#Returning a save register that doesn't belong to us yet. Save onto stack
			variableName = "<SAVE>_{}".format(registerName)
			instructions += self.addVariable(variableName, register=registerName, indentLevel=indentLevel)
			instructions += self.storeStack(variableName, freeRegister=True, indentLevel=indentLevel)
			self.virginSaveRegisters.remove(registerName)


		if ((not registerName) and (forceFree)):
			#No free register. Eject a variable to get a free one
			registerName, ejectVariableName = list(self.usedRegisters.items())[0]
			instructions += self.storeStack(ejectVariableName, freeRegister=True, indentLevel=indentLevel)


		return instructions, registerName


	def releaseRegister(self, registerName, indentLevel=0):
		'''
		Deallocates the specified register. If in use, variable will be stored on the stack.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)

		if (registerName in self.virginSaveRegisters):
			#Requesting a save register that doesn't belong to us yet. Save onto stack
			variableName = "<SAVE>_{}".format(registerName)
			instructions += self.addVariable(variableName, register=registerName, indentLevel=indentLevel)
			instructions += self.storeStack(variableName, indentLevel=indentLevel)
			self.virginSaveRegisters.remove(registerName)

		if (registerName in self.availableRegisters):
			pass
		elif (registerName in self.usedRegisters):
			#Register in use. Eject current variable
			ejectVariableName = self.usedRegisters[registerName]
			instructions += self.storeStack(ejectVariableName, freeRegister=True, indentLevel=indentLevel)

			self.availableRegisters.sort()
		elif (registerName != "zero"):
			self.availableRegisters.append(registerName)
			self.availableRegisters.sort()

		return instructions


	def moveVariable(self, variableName, regDest, indentLevel=0):
		'''
		Moves the specified variable into the specified destination register.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope".format(variableName))

		#Move variable into new register
		oldRegister = variableObj.register
		if (regDest != oldRegister):
			instructions += self.releaseRegister(regDest, indentLevel=indentLevel)
			if (oldRegister):
				#Variable currently in register
				instructions.append("{}mv {}, {}".format(indentString, regDest, oldRegister))
				variableObj.register = regDest
				self.usedRegisters[regDest] = variableName
				del self.usedRegisters[oldRegister]
				self.availableRegisters.remove(regDest)
				self.availableRegisters.append(oldRegister)
				self.availableRegisters.sort()
			else:
				#Variable not in register. Check the stack
				if (variableName in self.localStack):
					instructions += self.loadStack(variableName, regDestOverride=regDest, indentLevel=indentLevel)
				else:
					#Variable is not on stack nor in register. Instantiate into regDest
					variableObj.register = regDest
					self.usedRegisters[regDest] = variableName
					self.availableRegisters.remove(regDest)


		return instructions


	def saveTemps(self, indentLevel=0):
		'''
		Saves the state of all temporary registers currently in use.
		Will prioritize saving data into save registers, then the stack.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		for registerName in list(self.usedRegisters.keys()):
			variableName = self.usedRegisters[registerName]

			if (("a" in registerName) or ("t" in registerName)):
				#Temp register. Must save somewhere

				#Try to find a free save register
				instructionsTemp, freeReg = self.getFreeRegister(tempsAllowed=False, forceFree=False, indentLevel=indentLevel)
				instructions += instructionsTemp
				if (freeReg):
					#Save register available
					instructions += self.moveVariable(variableName, freeReg, indentLevel=indentLevel)
				else:
					#No free register. Save to stack
					instructions += self.storeStack(variableName, freeRegister=True, indentLevel=indentLevel)


		return instructions


	def saveReturnAddress(self, indentLevel=0):
		'''
		Saves the current value of the ra register onto the stack

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableName = "<SAVE>_ra"
		if not (variableName in self.variableDict):
			instructions += self.addVariable(variableName, register="ra", indentLevel=indentLevel)
			instructions += self.storeStack(variableName, indentLevel=indentLevel)


		return instructions


	def restoreSaves(self, indentLevel=0):
		'''
		Restores the value of all save registers touched within this scope.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		for variableName in self.variableDict:
			if ("<SAVE>" in variableName):
				regDest = variableName.replace("<SAVE>_", "")
				instructions += self.moveVariable(variableName, regDest, indentLevel=indentLevel)


		return instructions


	def deallocateScope(self, indentLevel=0):
		'''
		Deallocates the current stack. All variables stored on the stack will be lost.
		This instance of scopeController cannot be used after this method is called.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		deallocateLength = 0
		stackList = list(self.localStack.items())
		for index in range(0, len(stackList)):
			deallocateLength += stackList[index][1]
			
		if (deallocateLength > 0):
			instructions.append("{}addi sp, sp, {}".format(indentString, deallocateLength))

		self.localStack = OrderedDict()


		return instructions

	def getState(self):
		stateDict = {}
		stateDict["scope"] = {"name": self.name}
		stateDict["usedRegisters"] = self.usedRegisters
		stateDict["localStack"] = [{v: self.localStack[v]} for v in self.localStack]

		return stateDict


def getArrayElementPointer(arrayName, subscript, scope, indentLevel=0):
	'''
	Get a pointer to an array element into a register

	Returns:
		<tuple> ( <instructionList> instructions , <str> pointerRegister )
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord

	elementPointerReg = None

	#Get pointer to start of array
	instructionsTemp, arrayPointerReg, pointerVariableName = scope.getPointer(arrayName, indentLevel=indentLevel)
	instructions += instructionsTemp

	#Get pointer offset from subscript into register
	arrayVariable = scope.getVariable(arrayName)
	elementLength = arrayVariable.subElementSize[0]

	instructionsTemp, offsetIndex = operandToRegister(subscript, scope, indentLevel=indentLevel)
	instructions += instructionsTemp
	instructionsTemp, elementLengthReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
	instructions += instructionsTemp
	instructions.append("{}addi {}, zero, {}".format(indentString, elementLengthReg, elementLength))  #<TODO> handle element lengths too long for immediate
	offsetReg = elementLengthReg
	instructions.append("{}mul {}, {}, {}".format(indentString, offsetReg, offsetIndex, elementLengthReg))

	#Combine offset and array pointer
	elementPointerReg = arrayPointerReg
	instructions.append("{}add {}, {}, {}".format(indentString, elementPointerReg, arrayPointerReg, offsetReg))

	instructions += scope.releaseRegister(offsetReg, indentLevel=indentLevel)


	return instructions, elementPointerReg


def getStructMemberPointer(structName, memberName, scope, indentLevel=0):
	'''
	Get a pointer to a struct member into a register

	Returns:
		<tuple> ( <instructionList> instructions , <str> pointerRegister , <struct> structDef)
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord

	memberPointerReg = None

	#Get pointer to start of struct
	instructionsTemp, structPointerReg, pointerVariableName = scope.getPointer(structName, indentLevel=indentLevel)
	instructions += instructionsTemp

	#Get offset of member
	structVariable = scope.getVariable(structName)
	structDefObject = g_structDictionary[structVariable.type.type.name]
	offset = structDefObject.members[memberName].offset

	#Combine offset and struct pointer
	memberPointerReg = structPointerReg
	if (offset > 0):
		instructions.append("{}addi {}, {}, {}".format(indentString, memberPointerReg, structPointerReg, offset))  #<TODO> handle offsets too large for immediate

	return instructions, memberPointerReg, structDefObject


def operandToRegister(operandItem, scope, targetReg=None, indentLevel=0):
	'''
	Moved the operandItem into an register.
	
	params:
		targetReg - if degined, operand will be stored in specified register 
	returnType:
		( <instructionList> instructions, <str> registerName )
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = operandItem.coord


	operandReg = ""
	if isinstance(operandItem, c_ast.ID):
		#operand is variable
		if (targetReg):
			operandReg = targetReg
			instructions += scope.moveVariable(operandItem.name, operandReg)
		else:
			operandReg = scope.getRegisterLocation(operandItem.name)
			if (operandReg == None):
				instructions += scope.loadStack(operandItem.name, indentLevel=indentLevel)
				operandReg = scope.getRegisterLocation(operandItem.name)
	elif isinstance(operandItem, c_ast.Constant):
		# operand is contant
		value = None
		if (operandItem.type == "int"):
			value = int(operandItem.value)
		elif (operandItem.type == "double"):
			value = float(operandItem.value)
		elif (operandItem.type == "float"):
			value = float(operandItem.value)

		#Get operand into temp register
		if (value == 0):
			operandReg = "zero"
		elif (value < 2048) and (value >= -2048):
			#Value is small enough for addi
			if (targetReg):
				instructionsTemp, operandReg = scope.getFreeRegister(regOverride=targetReg)
				instructions += instructionsTemp
			else:
				instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
				instructions += instructionsTemp
			instructions.append("{}addi {}, zero, {}".format(indentString, operandReg, value))
		else:
			#Too large for immediate. Must load value from memory.
			#Add value to data segment
			dataType = "int"
			dataLabelName = "data_{}_{}".format(dataType, value)
			g_dataSegment[dataLabelName] = dataElement(dataLabelName, value=value, size=4)
			#Load into register
			instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel, regOverride=targetReg)
			instructions += instructionsTemp
			instructions.append("{}lw {}, {}".format(indentString, operandReg, dataLabelName))

	elif isinstance(operandItem, c_ast.BinaryOp):
		#Operand is binary op
		instructionsTemp, resultVariableName = convertBinaryOpItem(operandItem, scope, targetReg=targetReg, indentLevel=indentLevel)
		instructions += instructionsTemp
		operandReg = scope.getRegisterLocation(resultVariableName)
	elif isinstance(operandItem, c_ast.UnaryOp):
		#Operand is unary op
		instructionsTemp, resultVariableName = convertUnaryOpItem(operandItem, scope, targetReg=targetReg, indentLevel=indentLevel)
		instructions += instructionsTemp
		operandReg = scope.getRegisterLocation(resultVariableName)
	elif isinstance(operandItem, c_ast.FuncCall):
		#Operand is function result
		instructions += convertFuncCallItem(operandItem, scope, indentLevel=indentLevel)
		operandReg = "a0"
		if (targetReg):
			instructionsTemp, operandReg = scope.getFreeRegister(regOverride=targetReg, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}mv {}, a0".format(indentString, operandReg))
	elif isinstance(operandItem, c_ast.ArrayRef):
		arrayName = operandItem.name.name
		subscript = operandItem.subscript
		#Get pointer to array element
		instructionsTemp, pointerRegister = getArrayElementPointer(arrayName, subscript, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		#Load element into operandReg
		instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
		instructions += instructionsTemp

		elementSize = scope.variableDict[arrayName].subElementSize[-1]
		if (elementSize == 4):
			instructions.append("{}lw {}, 0({})".format(indentString, operandReg, pointerRegister)) #<TODO> handle unsigned values
		elif (elementSize == 2):
			instructions.append("{}lh {}, 0({})".format(indentString, operandReg, pointerRegister))
		elif (elementSize == 1):
			instructions.append("{}lb {}, 0({})".format(indentString, operandReg, pointerRegister))
		#Release pointer register
		instructions += scope.releaseRegister(pointerRegister, indentLevel=indentLevel)
	elif isinstance(operandItem, c_ast.StructRef):
		structName = operandItem.name.name
		memberName = operandItem.field.name
		#Get pointer to struct member
		instructionsTemp, pointerRegister, structDef = getStructMemberPointer(structName, memberName, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Load member into operandReg
		instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
		instructions += instructionsTemp

		memberSize = structDef.members[memberName].size
		if (memberSize == 4):
			instructions.append("{}lw {}, 0({})".format(indentString, operandReg, pointerRegister)) #<TODO> handle unsigned values
		elif (memberSize == 2):
			instructions.append("{}lh {}, 0({})".format(indentString, operandReg, pointerRegister))
		elif (memberSize == 1):
			instructions.append("{}lb {}, 0({})".format(indentString, operandReg, pointerRegister))
		#Release pointer register
		instructions += scope.releaseRegister(pointerRegister, indentLevel=indentLevel)
	else:
		errorStr = "UNSUPPORTED OPERAND | {}\n{}".format(g_cFileCoord, operandItem)
		raise Exception(errorStr)


	return instructions, operandReg


def convertUnaryOpItem(item, scope, branch=None, targetVariableName=None, targetReg=None, resultSize=4, resultType=None, indentLevel=0):
	'''
	Converts a c_ast.UnaryOp object into an assembly snippet.
	Returns an instructionList item, as well as the variable name of the operation result

	params:
		branch - if defined and unary op is logical, will branch to specified label if result=True
		targetVariableName - if defined, result will be stored in specified variable
		targetReg - if degined, result will be stored in specified register 
	
	returnType:
		( <instructionList> instructions, <str> variableName )
	'''

	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	resultVariableName = None

	#Determine operation to perform
	operator = item.op

	if (operator == "p++"):
		#Get operand into register
		instructionsTemp, operandReg = operandToRegister(item.expr, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Increment  #<TODO> handle pointer incrementation based on size
		instructions.append("{}addi {}, {}, 1".format(indentString, operandReg, operandReg))
		if isinstance(item.expr, c_ast.ID):
			resultVariableName = item.expr.name

	elif (operator == "p--"):
		#Get operand into register
		instructionsTemp, operandReg = operandToRegister(item.expr, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Decrement  #<TODO> handle pointer decrementation based on size
		instructions.append("{}addi {}, {}, -1".format(indentString, operandReg, operandReg))
		if isinstance(item.expr, c_ast.ID):
			resultVariableName = item.expr.name

	elif (operator == "-"):
		#Get operand into register
		instructionsTemp, operandReg = operandToRegister(item.expr, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Get a register to store result
		regDest = ""
		if (targetReg):
			instructions += scope.releaseRegister(targetReg, indentLevel=indentLevel)
			regDest = targetReg
		else:
			instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp

		#Get or create variable name for result of negation
		if (targetVariableName):
			instructions += scope.addVariable(targetVariableName, size=resultSize, register=regDest, varType=resultType, indentLevel=indentLevel)

			resultVariableName = targetVariableName
		else:
			instructionsTemp, resultVariableName = scope.createExpressionResult(register=regDest, indentLevel=indentLevel)
			instructions += instructionsTemp

		#Negate operand
		instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
		instructions += instructionsTemp

		instructions.append("{}addi {}, zero, -1".format(indentString, tempRegister))
		instructions.append("{}mul {}, {}, {}".format(indentString, regDest, operandReg, tempRegister))

		instructions += scope.releaseRegister(tempRegister)

	elif (operator == "!"):
		#Get operand into register
		instructionsTemp, operandReg = operandToRegister(item.expr, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Logical invert
		if (branch):
			instructions.append("{}beq {}, zero, {}".format(indentString, operandReg, branch))
		else:
			#Get or create variable name for result
			if (targetVariableName):
				instructions += scope.addVariable(targetVariableName, size=resultSize, varType=resultType, indentLevel=indentLevel)

				resultVariableName = targetVariableName
			else:
				instructionsTemp, resultVariableName = scope.createExpressionResult(indentLevel=indentLevel)
				instructions += instructionsTemp

			#Get a register to store result
			regDest = ""
			if (targetReg):
				instructions += scope.releaseRegister(targetReg, indentLevel=indentLevel)
				regDest = targetReg
			else:
				instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
				instructions += instructionsTemp

			#Logically invert operand
			instructions.append("{}sltu {}, {}, zero".format(indentString, regDest, operandReg))

	elif (operator == "&"):
		#Get memory location of variable
		instructionsTemp, regDest, resultVariableName = scope.getPointer(item.expr.name, regDestOverride=targetReg, indentLevel=indentLevel)
		instructions += instructionsTemp
	elif (operator == "*"):
		if isinstance(item.expr, c_ast.ID):
			#Get memory location of variable
			instructions += scope.loadStack(item.expr.name, indentLevel=indentLevel)
			regPointer = scope.getRegisterLocation(item.expr.name)

			#Load value from memory
			#<TODO> handle values smaller than 4 bytes
			instructionsTemp, regDest = scope.getFreeRegister(regOverride=targetReg, preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp

			varSize = scope.variableDict[item.expr.name].subElementSize[-1]
			if (varSize == 4):
				instructions.append("{}lw {}, 0({})".format(indentString, regDest, regPointer)) #<TODO> handle unsigned values
			elif (varSize == 2):
				instructions.append("{}lh {}, 0({})".format(indentString, regDest, regPointer))
			elif (varSize == 1):
				instructions.append("{}lb {}, 0({})".format(indentString, regDest, regPointer))

			#Get or create variable name for reference result
			if (targetVariableName):
				instructions += scope.addVariable(targetVariableName, register=regDest, size=resultSize, varType=resultType, indentLevel=indentLevel)

				resultVariableName = targetVariableName
			else:
				instructionsTemp, resultVariableName = scope.createExpressionResult(register=regDest, indentLevel=indentLevel)
				instructions += instructionsTemp
		else:
			raise Exception("ATTEMPT TO DEREFERENCE CONSTANT | convertUnaryOpItem\n{}".format(item.coord))

	else:
		print(item)
		raise Exception("UNSUPPORTED OPERATOR \"{}\"| convertUnaryOpItem".format(operator))


	#Update value in memory if variable and modified
	if isinstance(item.expr, c_ast.ID):
		#Operand is a variable. Did we change it?
		if ((operator == "p++") or (operator == "p--")):
			#Modified variable. Update in memory
			instructions += scope.storeStack(item.expr.name, indentLevel=indentLevel)

	return instructions, resultVariableName


def convertBinaryOpItem(item, scope, branch=None, targetVariableName=None, targetReg=None, resultSize=4, resultType=None, indentLevel=0):
	'''
	Converts a c_ast.BinaryOp object into an assembly snippet.
	Returns an instructionList item, as well as the variable name of the operation result
	
	params:
		branch - if defined and binary op is logical, will branch to specified label if result=True
		targetVariableName - if defined, result will be stored in specified variable
		targetReg - if degined, result will be stored in specified register

	returnType:
		( <instructionList> instructions, <str> variableName )
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	#Get variable and register for result
	resultVariableName = ""
	if (not branch):
		if (targetVariableName):
			instructions += scope.addVariable(targetVariableName, size=resultSize, varType=resultType, indentLevel=indentLevel)

			resultVariableName = targetVariableName
		else:
			instructionsTemp, resultVariableName = scope.createExpressionResult(indentLevel=indentLevel)
			instructions += instructionsTemp

	#Get a register to store result
	regDest = ""
	if (not branch):
		if (targetReg):
			instructions += scope.releaseRegister(targetReg, indentLevel=indentLevel)
			regDest = targetReg
		else:
			instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp

	if (not branch):
		#Instantiate variable into destinamtion register
		instructions += scope.moveVariable(resultVariableName, regDest, indentLevel=indentLevel)

	#Get left operand into register  #<TODO> handle values small enought for immediates
	leftOperand = item.left
	instructionsTemp, leftOperandReg = operandToRegister(leftOperand, scope, indentLevel=indentLevel)
	instructions += instructionsTemp

	#Get right operand into register  #<TODO> handle values small enought for immediates
	rightOperand = item.right
	instructionsTemp, rightOperandReg = operandToRegister(rightOperand, scope, indentLevel=indentLevel)
	instructions += instructionsTemp

	#Handler operators
	#<TODO>, handle unsigned operands
	operator = item.op

	#Numeric results
	if (operator == "*"):
		instructions.append("{}mul {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
	elif (operator == "/"):
		instructions.append("{}div {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
	elif (operator == "%"):
		instructions.append("{}rem {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
	elif (operator == "+"):
		instructions.append("{}add {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
		#<TODO> use addi if one operand is a small constant
	elif (operator == "-"):
		instructions.append("{}sub {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
		#<TODO> use addi if one operand is a small constant
	#Boolean results
	elif (operator == "=="):
		if (branch):
			instructions.append("{}beq {}, {}, {}".format(indentString, leftOperandReg, rightOperandReg, branch))
		else:
			instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
			instructions.append("{}slt {}, {}, {}".format(indentString, tempRegister, rightOperandReg, leftOperandReg))
			instructions.append("{}add {}, {}, {}".format(indentString, regDest, regDest, tempRegister))
			instructions.append("{}slti {}, {}, 1".format(indentString, regDest, regDest))
			instructions += scope.releaseRegister(tempRegister)
	elif (operator == ">="):
		if (branch):
			instructions.append("{}bge {}, {}, {}".format(indentString, leftOperandReg, rightOperandReg, branch))
		else:
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
			instructions.append("{}slti {}, {}, 1".format(indentString, regDest, regDest))
	elif (operator == "<="):
		if (branch):
			#Swap operands to save an instruction
			instructions.append("{}bge {}, {}, {}".format(indentString, rightOperandReg, leftOperandReg, branch))
		else:
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, rightOperandReg, leftOperandReg))
			instructions.append("{}slti {}, {}, 1".format(indentString, regDest, regDest))
	elif (operator == ">"):
		if (branch):
			#Swap operands to save an instruction
			instructions.append("{}blt {}, {}, {}".format(indentString, rightOperandReg, leftOperandReg, branch))
		else:
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, rightOperandReg, leftOperandReg))
	elif (operator == "<"):
		if (branch):
			instructions.append("{}blt {}, {}, {}".format(indentString, leftOperandReg, rightOperandReg, branch))
		else:
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
	elif (operator == "!="):
		if (branch):
			instructions.append("{}bne {}, {}, {}".format(indentString, leftOperandReg, rightOperandReg, branch))
		else:
			instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
			instructions.append("{}slt {}, {}, {}".format(indentString, tempRegister, rightOperandReg, leftOperandReg))
			instructions.append("{}add {}, {}, {}".format(indentString, regDest, regDest, tempRegister))
			instructions += scope.releaseRegister(tempRegister)
	elif (operator == "&&"):
		if (branch):
			instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}mul {}, {}, {}".format(indentString, tempRegister, leftOperandReg, rightOperandReg))
			instructions.append("{}bne {}, zero, {}".format(indentString, tempRegister, branch))
			instructions += scope.releaseRegister(tempRegister)
		else:
			instructions.append("{}mul {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
	else:
		raise Exception("UNSUPPORTED OPERATOR \"{}\"| convertBinaryOpItem".format(operator))


	#Free temp constant registers
	if isinstance(leftOperand, c_ast.Constant):
		instructions += scope.releaseRegister(leftOperandReg, indentLevel=indentLevel)
	if isinstance(rightOperand, c_ast.Constant):
		instructions += scope.releaseRegister(rightOperandReg, indentLevel=indentLevel)


	return instructions, resultVariableName


def convertIfItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.If object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	global g_ifCounter

	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	#Handle condition branching
	onTrueLabel = "true_{}".format(g_ifCounter)
	onFalseLabel = "false_{}".format(g_ifCounter)
	ifExitLabel = "ifElseExit_{}".format(g_ifCounter)
	g_ifCounter += 1

	conditionItem = item.cond
	if isinstance(conditionItem, c_ast.BinaryOp):
		instructionsTemp, conditionVariableName = convertBinaryOpItem(conditionItem, scope, branch=onTrueLabel, indentLevel=indentLevel)
		instructions += instructionsTemp
	elif isinstance(conditionItem, c_ast.UnaryOp):
		instructionsTemp, conditionVariableName = convertUnaryOpItem(conditionItem, scope, branch=onTrueLabel, indentLevel=indentLevel)
		instructions += instructionsTemp
	else:
		raise Exception("UNSUPPORTED CONDITION | convertIfItem\n{}".format(conditionItem))

	instructions.append("{}j {}".format(indentString, onFalseLabel))

	#Contruct true/false code blocks
	instructions.append("{}{}:".format(indentString, onTrueLabel))
	scopeBranch = copy.deepcopy(scope)
	instructions += convertAstItem(item.iftrue, scopeBranch, indentLevel=indentLevel+1)
	instructions += scope.mergeScopeBranch(scopeBranch, indentLevel=indentLevel+1)  #<TODO> Skip this part if the true section ends with a return
	instructions.append("{}j {}".format(indentString, ifExitLabel))

	instructions.append("{}{}:".format(indentString, onFalseLabel))
	if (item.iffalse):
		scopeBranch = copy.deepcopy(scope)
		instructions += convertAstItem(item.iffalse, scopeBranch, indentLevel=indentLevel+1)
		instructions += scope.mergeScopeBranch(scopeBranch, indentLevel=indentLevel+1)  #<TODO> Skip this part if the false section ends with a return
	instructions.append("{}{}:".format(indentString, ifExitLabel))

	return instructions


def convertFuncCallItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.FuncCall object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	functionName = item.name.name

	#Sets up function parameters into argument registers
	argIndex = 0
	for argument in item.args.exprs:
		argumentRegister = "a{}".format(argIndex)

		if isinstance(argument, c_ast.ID):
			#Function argument is variable
			instructions += scope.moveVariable(argument.name, argumentRegister, indentLevel=indentLevel)

		elif isinstance(argument, c_ast.BinaryOp):
			#Function argument is binary op
			instructionsTemp, resultVariableName = convertBinaryOpItem(argument, scope, targetReg=argumentRegister, indentLevel=indentLevel)
			instructions += instructionsTemp
		elif isinstance(argument, c_ast.UnaryOp):
			#Function argument is binary op
			instructionsTemp, resultVariableName = convertUnaryOpItem(argument, scope, targetReg=argumentRegister, indentLevel=indentLevel)
			instructions += instructionsTemp
		elif isinstance(argument, c_ast.Constant):
			#Function argument is a contant
			instructionsTemp, operandReg = operandToRegister(argument, scope, targetReg=argumentRegister, indentLevel=indentLevel)
			instructions += instructionsTemp
		elif isinstance(argument, c_ast.FuncCall):
			#Function argument is another function call
			argumentSaves = {}
			if (argIndex != 0):
				#Save current values of prepared arugements
				for saveIndex in range(0,argIndex):
					instructionsTemp, tempSaveReg = scope.getFreeRegister(tempsAllowed=False, indentLevel=indentLevel)
					instructions += instructionsTemp
					instructions.append("{}mv {}, a{}".format(indentString, tempSaveReg, saveIndex))

					argumentSaves[saveIndex] = tempSaveReg

			instructions += convertFuncCallItem(argument, scope, indentLevel=indentLevel)
			
			if (argIndex != 0):
				#Move return value into required argument register
				instructions.append("{}mv {}, a0".format(indentString, argumentRegister))

				#Restore previous argument values
				for saveIndex in range(0,argIndex):
					tempSaveReg = argumentSaves[saveIndex]
					instructions.append("{}mv a{}, {}".format(indentString, saveIndex, tempSaveReg))
					scope.releaseRegister(tempSaveReg)

		else:
			raise Exception("UNSUPPORTED ITEM | convertFuncCallItem\n{}".format(item))

		argIndex += 1

	#Save return address to stack
	instructions += scope.saveReturnAddress(indentLevel=indentLevel)

	#Save temps
	instructions += scope.saveTemps(indentLevel=indentLevel)

	#Call function
	instructions.append("{}jal {}".format(indentString, functionName))

	return instructions


def convertAssignmentItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.Assignment object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	#Get right value into register  #<TODO> handle values small enought for immediates
	#<TODO> remove uneeded expressionResult variables. Perhaps add volatile arg to createExpressionResult
	rightOperand = item.rvalue
	instructionsTemp, rightValReg = operandToRegister(rightOperand, scope, indentLevel=indentLevel)  
	instructions += instructionsTemp

	#########
	# Get left value into register  #<TODO> handle constant values small enough for immediates
	#########
	leftOperand = item.lvalue
	leftValReg = None
	leftSize = None

	#Handle pointer dereference
	isPointerDereference = False
	pointerRegister = None

	if isinstance(leftOperand, c_ast.UnaryOp):
		if (leftOperand.op == "*"):
			isPointerDereference = True
			#Get pointer into register
			if isinstance(leftOperand.expr, c_ast.ID):
				#Pointer is a variable
				instructions += scope.loadStack(leftOperand.expr.name, indentLevel=indentLevel)
				pointerRegister = scope.getRegisterLocation(leftOperand.expr.name)
			elif isinstance(leftOperand.expr, c_ast.Constant):
				#Pointer is a constant
				instructionsTemp, pointerRegister = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
				instructions += instructionsTemp

				pointerValue = int(leftOperand.expr.value)
				if (pointerValue < 2048):
					#Pointer small enough for immediate
					instructions.append("{}addi {}, zero, {}".format(indentString, pointerRegister, pointerValue))
				else:
					#Pointer value too large. Add to data segment
					dataType = "pointer"
					dataLabelName = "data_{}_{}".format(dataType, pointerValue)
					g_dataSegment[dataLabelName] = dataElement(dataLabelName, value=pointerValue, size=4)
					instructions.append("{}lw {}, {}".format(indentString, pointerRegister, dataLabelName))
			else:
				raise Exception("UNSUPPORTED DEREFERENCE TYPE | {}".format(g_cFileCoord))

	#Handle array element references
	isArrayReference = False
	arrayName = None

	if isinstance(leftOperand, c_ast.ArrayRef):
		isArrayReference = True

		arrayName = leftOperand.name.name
		subscript = leftOperand.subscript
		#Get pointer to array element
		instructionsTemp, pointerRegister = getArrayElementPointer(arrayName, subscript, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		#Load element into leftValReg
		instructionsTemp, leftValReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
		instructions += instructionsTemp

		leftSize = scope.variableDict[arrayName].subElementSize[-1]
		if (leftSize == 4):
			instructions.append("{}lw {}, 0({})".format(indentString, leftValReg, pointerRegister)) #<TODO> handle unsigned values
		elif (leftSize == 2):
			instructions.append("{}lh {}, 0({})".format(indentString, leftValReg, pointerRegister))
		elif (leftSize == 1):
			instructions.append("{}lb {}, 0({})".format(indentString, leftValReg, pointerRegister))

	#Handle struct member references
	isStructReference = False
	if isinstance(leftOperand, c_ast.StructRef):
		isStructReference = True

		structName = leftOperand.name.name
		memberName = leftOperand.field.name
		#Get pointer to struct member
		instructionsTemp, pointerRegister, structDef = getStructMemberPointer(structName, memberName, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Load member into leftValReg
		instructionsTemp, leftValReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
		instructions += instructionsTemp

		leftSize = structDef.members[memberName].size
		if (leftSize == 4):
			instructions.append("{}lw {}, 0({})".format(indentString, leftValReg, pointerRegister)) #<TODO> handle unsigned values
		elif (leftSize == 2):
			instructions.append("{}lh {}, 0({})".format(indentString, leftValReg, pointerRegister))
		elif (leftSize == 1):
			instructions.append("{}lb {}, 0({})".format(indentString, leftValReg, pointerRegister))

	#Get left value into register if not already handled
	if ((not isArrayReference) and (not isStructReference)):
		instructionsTemp, leftValReg = operandToRegister(leftOperand, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

	#########
	# Handler operators
	#########
	#<TODO>, handle unsigned operands
	operator = item.op

	if (operator == "="):
		instructions.append("{}mv {}, {}".format(indentString, leftValReg, rightValReg))
	elif (operator == "+="):
		instructions.append("{}add {}, {}, {}".format(indentString, leftValReg, leftValReg, rightValReg))
	elif (operator == "-="):
		instructions.append("{}sub {}, {}, {}".format(indentString, leftValReg, leftValReg, rightValReg))
	else:
		raise Exception("UNSUPPORTED OPERATOR \"{}\" | convertAssignmentItem".format(operator))

	#Update values in memory
	if (isPointerDereference or isArrayReference or isStructReference):
		#Update memory with value
		if (leftSize == 4):
			instructions.append("{}sw {}, 0({})".format(indentString, leftValReg, pointerRegister))
		elif (leftSize == 2):
			instructions.append("{}sh {}, 0({})".format(indentString, leftValReg, pointerRegister))
		elif (leftSize == 1):
			instructions.append("{}sb {}, 0({})".format(indentString, leftValReg, pointerRegister))
		instructions += scope.releaseRegister(leftValReg, indentLevel=indentLevel)
	elif isinstance(leftOperand, c_ast.ID):
		#Left operand is a variable. Update in memory
		instructions += scope.storeStack(leftOperand.name, indentLevel=indentLevel)

	#Release pointer register
	if (pointerRegister):
		instructions += scope.releaseRegister(pointerRegister, indentLevel=indentLevel)


	return instructions


def convertReturnItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.Return object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	#<TODO> Prevent uneeded saving of variables onto stack when we are returning
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	if isinstance(item.expr, c_ast.ID):
		#Return variable
		variableName = item.expr.name
		currentRegister = scope.getRegisterLocation(variableName)

		if (not currentRegister):
			#variable on stack. Load into a0
			instructions += scope.loadStack(variableName, regDestOverride="a0", indentLevel=indentLevel)
		else:
			#variable in register. Move into a0
			instructions += scope.moveVariable(variableName, "a0", indentLevel=indentLevel)
		
		#Restore save variables, deallocate scope, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateScope(indentLevel=indentLevel)
		instructions.append("{}jr ra".format(indentString))

	elif isinstance(item.expr, c_ast.FuncCall):
		#Call function, then return result
		instructions += convertFuncCallItem(item.expr, scope, indentLevel=indentLevel)

		#Restore save variables, deallocate scope, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateScope(indentLevel=indentLevel)
		instructions.append("{}jr ra".format(indentString))

	elif isinstance(item.expr, c_ast.Constant):
		#Return constant value
		value = int(item.expr.value) #<TODO> Handle floats and doubles
		if (value < 2048) and (value >= -2048):
			#Value is small enough for addi
			scope.removeVariable(scope.getVariableName("a0"))
			instructions.append("{}addi {}, zero, {}".format(indentString, "a0", value))
		else:
			#Must load value from memory
			#Too large for immediate. Must load value from memory.
			#Add value to data segment
			dataType = "int"
			dataLabelName = "data_{}_{}".format(dataType, value)
			g_dataSegment[dataLabelName] = dataElement(dataLabelName, value=value, size=4)
			#Load into register
			instructions.append("{}lw a0, {}".format(indentString, dataLabelName))

		#Restore save variables, deallocate scope, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateScope(indentLevel=indentLevel)
		instructions.append("{}jr ra".format(indentString))

	elif isinstance(item.expr, c_ast.BinaryOp):
		instructionsTemp, resultVariableName = convertBinaryOpItem(item.expr, scope, targetReg="a0", indentLevel=indentLevel)
		instructions += instructionsTemp

		#Restore save variables, deallocate scope, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateScope(indentLevel=1)
		instructions.append("{}jr ra".format(indentString))
	elif isinstance(item.expr, c_ast.UnaryOp):
		instructionsTemp, resultVariableName = convertUnaryOpItem(item.expr, scope, targetReg="a0", indentLevel=indentLevel)
		instructions += instructionsTemp

		#Restore save variables, deallocate scope, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateScope(indentLevel=indentLevel)
		instructions.append("{}jr ra".format(indentString))
	else:
		raise Exception("UNSUPPORTED ITEM | convertReturnItem\n{}".format(item))


	return instructions


def convertDeclItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.Decl(Declaration) object into an assembly snippet.
	Returns an instructionList item, along with the variableName of the declared variable
	
	returnType:
		( <instructionList> instructions, <str> variableName )
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	variableName = item.name

	if (item.init):
		#Declared with initial value
		if isinstance(item.init, c_ast.Constant):
			#Initialized variable to a constant value
			instructionsTemp, destinationRegister = scope.getFreeRegister(indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions += scope.addVariable(variableName, register=destinationRegister, varType=item.type, signed=True, indentLevel=indentLevel)


			value = int(item.init.value) #<TODO> Handle floats and doubles
			if (value < 2048) and (value >= -2048):
				#Value is small enough for addi
				instructions.append("{}addi {}, zero, {}".format(indentString, destinationRegister, value))
			else:
				#Too large for immediate. Must load value from memory.
				#Add value to data segment
				dataType = "int"
				dataLabelName = "data_{}_{}".format(dataType, value)
				g_dataSegment[dataLabelName] = dataElement(dataLabelName, value=value, size=4)
				#Load into register
				instructions.append("{}lw {}, {}".format(indentString, destinationRegister, dataLabelName))

		elif isinstance(item.init, c_ast.BinaryOp):
			#Initialized variable is result of binary expression
			instructionsTemp, resultVariableName = convertBinaryOpItem(item.init, scope, targetVariableName=variableName, indentLevel=indentLevel)
			instructions += instructionsTemp

		elif isinstance(item.init, c_ast.UnaryOp):
			#Initialized variable is result of binary expression
			instructionsTemp, resultVariableName = convertUnaryOpItem(item.init, scope, targetVariableName=variableName, indentLevel=indentLevel)
			instructions += instructionsTemp

		elif isinstance(item.init, c_ast.FuncCall):
			#Initialized variable is result of function call
			instructions += convertFuncCallItem(item.init, scope, indentLevel=indentLevel)
			instructions += scope.addVariable(variableName, register="a0", varType=item.type, indentLevel=indentLevel)
		elif isinstance(item.init, c_ast.InitList):
			if isinstance(item.type, c_ast.ArrayDecl):
				#Add array to scope
				instructions += scope.addVariable(variableName, varType=item.type, signed=True, indentLevel=indentLevel)

				#Get pointer to start of array
				instructionsTemp, pointerReg = scope.getPointer(variableName, indentLevel=indentLevel)
				instructions += instructionsTemp

				for arrayIndex in range(0, len(item.init.exprs)):
					expression = item.init.exprs[arrayIndex]
					if isinstance(expression, c_ast.Constant):
						#Get constant into a register
						instructionsTemp, tempReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
						instructions += instructionsTemp

						instructionsTemp, valueReg = operandToRegister(expression, scope, targetReg=tempReg, indentLevel=indentLevel)
						instructions += instructionsTemp

						#Determine pointer offset
						elementSize = g_typeSizeDictionary[expression.type]
						pointerOffset = elementSize * arrayIndex

						#Store value onto stack
						if (elementSize == 4):
							instructions.append("{}sw {}, {}({})".format(indentString, valueReg, pointerOffset, pointerReg))
						elif (elementSize == 2):
							instructions.append("{}sh {}, {}({})".format(indentString, valueReg, pointerOffset, pointerReg))
						elif (elementSize == 1):
							instructions.append("{}sb {}, {}({})".format(indentString, valueReg, pointerOffset, pointerReg))
						else:
							raise Exception("UNSUPPORTED ARRAY ELEMENT SIZE | {}".format(g_cFileCoord))

						#Release temp registers
						instructions += scope.releaseRegister(tempReg)
						instructions += scope.releaseRegister(valueReg)
					else:
						raise Exception("UNSUPPORTED INITIAL VALUE FOR ARRAY | {}".format(g_cFileCoord))

				instructions += scope.releaseRegister(pointerReg)
			else:
				raise Exception("Cannot initialize non-array to a list of values | {}".format(g_cFileCoord))

		else:
			raise Exception("UNSUPPORTED DECLARATION | convertDeclItem\n{}".format(item))
	else:
		#Declared without initial value
		instructions += scope.addVariable(variableName, varType=item.type, indentLevel=indentLevel)

	#Allocate space on stack for variable
	instructions += scope.storeStack(variableName, indentLevel=indentLevel)

	return instructions, variableName


def convertForItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.For(For Loop) object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	global g_forCounter

	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	#Initialize for loop counting variable
	if isinstance(item.init, c_ast.DeclList):
		for declareItem in item.init.decls:
			instructionsTemp, variableName = convertDeclItem(declareItem, scope, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions += scope.storeStack(variableName, indentLevel=indentLevel)
	else:
		raise Exception("UNSUPPORTED ITEM | convertForItem\n{}".format(item.init))

	#For loop start/end labels
	startLabel = "forLoopStart_{}".format(g_forCounter)
	endLabel = "forLoopEnd_{}".format(g_forCounter)
	bodyLabel = "forLoopBody_{}".format(g_forCounter)
	g_forCounter += 1

	instructions.append("{}{}:".format(indentString, startLabel))

	#For loop condition check
	conditionItem = item.cond
	conditionVariableName = None
	if isinstance(conditionItem, c_ast.BinaryOp):
		instructionsTemp, conditionVariableName = convertBinaryOpItem(conditionItem, scope, branch=bodyLabel, indentLevel=indentLevel+1)
		instructions += instructionsTemp
		instructions.append("{}\tj {}".format(indentString, endLabel))

	else:
		raise Exception("UNSUPPORTED CONDITION | convertForItem\n{}".format(conditionItem))


	#For loop body
	scopeBranch = copy.deepcopy(scope)
	loopBodyItem = item.stmt
	instructions.append("{}\t{}:".format(indentString, bodyLabel))
	instructions += convertAstItem(loopBodyItem, scopeBranch, indentLevel=indentLevel+2)
	instructions += scope.mergeScopeBranch(scopeBranch, indentLevel=indentLevel+1)

	#For loop increment
	nextItem = item.next
	if isinstance(nextItem, c_ast.UnaryOp):
		instructionsTemp, resultVariableName = convertUnaryOpItem(nextItem, scope, indentLevel=indentLevel+1)
		instructions += instructionsTemp
	elif isinstance(nextItem, c_ast.Assignment):
		raise Exception("UNSUPPORTED NEXT ITEM | convertForItem\n{}".format(nextItem))
	else:
		raise Exception("UNSUPPORTED NEXT ITEM | convertForItem".format(nextItem))

	#For loop exit
	instructions.append("{}\tj {}".format(indentString, startLabel))
	instructions.append("{}{}:".format(indentString, endLabel))

	return instructions


def convertWhileItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast.For(For Loop) object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	global g_whileCounter

	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	global g_cFileCoord
	g_cFileCoord = item.coord

	#While loop start/end labels
	startLabel = "whileLoopStart_{}".format(g_whileCounter)
	endLabel = "whileLoopEnd_{}".format(g_whileCounter)
	bodyLabel = "whileLoopBody_{}".format(g_whileCounter)
	g_whileCounter += 1

	instructions.append("{}{}:".format(indentString, startLabel))

	#While loop condition check
	conditionItem = item.cond
	conditionVariableName = None
	if isinstance(conditionItem, c_ast.BinaryOp):
		instructionsTemp, conditionVariableName = convertBinaryOpItem(conditionItem, scope, branch=bodyLabel, indentLevel=indentLevel+1)
		instructions += instructionsTemp
		instructions.append("{}\tj {}".format(indentString, endLabel))

	else:
		raise Exception("UNSUPPORTED CONDITION | convertForItem\n{}".format(conditionItem))


	#While loop body
	scopeBranch = copy.deepcopy(scope)
	loopBodyItem = item.stmt
	instructions.append("{}\t{}:".format(indentString, bodyLabel))
	instructions += convertAstItem(loopBodyItem, scopeBranch, indentLevel=indentLevel+2)
	instructions += scope.mergeScopeBranch(scopeBranch, indentLevel=indentLevel+1)

	#While loop exit
	instructions.append("{}\tj {}".format(indentString, startLabel))
	instructions.append("{}{}:".format(indentString, endLabel))

	return instructions


def convertAstItem(item, scope, indentLevel=0):
	'''
	Converts a c_ast object into an assembly snippet.
	Returns an instructionList item
	
	returnType:
		<instructionList> instructions
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])

	if isinstance(item, c_ast.Compound):
		for subItem in item.block_items:
			instructions += convertAstItem(subItem, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.If):
		instructions += convertIfItem(item, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.Return):
		instructions += convertReturnItem(item, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.For):
		instructions += convertForItem(item, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.Decl):
		instructionsTemp, variableName = convertDeclItem(item, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
	elif isinstance(item, c_ast.Assignment):
		instructions += convertAssignmentItem(item, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.While):
		instructions += convertWhileItem(item, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.UnaryOp):
		instructionsTemp, variableName  = convertUnaryOpItem(item, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
	elif isinstance(item, c_ast.BinaryOp):
		instructionsTemp, variableName  = convertBinaryOpItem(item, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
	else:
		raise Exception("UNSUPPORTED ITEM | convertAstItem\n{}".format(item))
		

	return instructions


def covertFuncToAssembly(funcDef):
	'''
	Converts the c_ast.funcDef object into an assembly snippet.
	Writes list of instructions to object variable funcDef.coord
	'''
	scope = scopeController(funcDef.decl.name)
	instructions = instructionList(scope)
	
	#Function label
	instructions.append("{}:".format(funcDef.decl.name))

	#Add input variables too function scope
	if (funcDef.decl.type.args):
		inputParameters = funcDef.decl.type.args.params

		argIndex = 0
		for arg in inputParameters:
			registerName = "a{}".format(argIndex)
			instructions += scope.addVariable(arg.name, register=registerName, varType=arg.type, signed=True, indentLevel=1)


			argIndex += 1

	#Write function body
	instructions += convertAstItem(funcDef.body, scope, indentLevel=1)

	#Restore save variables
	instructions += scope.restoreSaves(indentLevel=1)

	#Deallocate local stack
	instructions += scope.deallocateScope(indentLevel=1)

	#Return to caller
	instructions.append("\tjr ra")

	funcDef.coord = instructions  #Borrow coord variable, since it seems to be unused by pycparser


def getDefinitions(ast):
	'''
	Returns a dictionary of function definitions in the following format
		{"<functionName>": c_ast.FuncDef, ...}
	Also returns a list of global variable declarations
		[c_ast.Decl, ...]
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

	cOutPath = "{}.temp".format(os.path.split(filepath)[-1])
	cFileOut = open(cOutPath, "w")

	inLine = " "
	while (inLine):
		inLine = cFileIn.readline()
		outline = inLine

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
	memorySize = arguments.memorySize
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

		#Parse struct definitions
		for structDecl in structDeclarations:
			structObj = struct(structDecl.type)
			g_typeSizeDictionary[structObj.name] = structObj.size
			g_structDictionary[structObj.name] = structObj
		
		#Translate functions into assembly snippets
		if ("main" in definedFunctions):
			for functionName in definedFunctions:
				#<TODO> multithread these translations
				funcDef = definedFunctions[functionName]
				covertFuncToAssembly(funcDef)
				#print("\n".join(funcDef.coord))
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
			else:
				g_dataSegment["stackPointerStart"] = dataElement("stackPointerStart", value=stackPointerStart, size=4)
				asmFile.write("lw sp, stackPointerStart\n")
			programCounter += 4

		asmFile.write("addi ra, zero, PROGRAM_END\n")  #initialize return address for main
		programCounter += 4

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

			if not (("#" in inst) or (":" in inst)):
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

				if not (("#" in inst) or (":" in inst)):
					programCounter += 4
			asmFile.write("\n")

		asmFile.write("PROGRAM_END:\nadd zero, zero, zero\n")  #Program end label/nop

		#Write data section
		asmFile.write(".data\n")

		for dataLabel in g_dataSegment:
			dataElement = g_dataSegment[dataLabel]
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

		asmFile.close()


		#Convert assembly file to hex
		assembler.main(assemblyFilePath, hexPath, indexPath, logisim, debuggerAnnotations)

		#Cleanup
		os.remove(cleanFilePath)

	except Exception as e:
		printColor("{}\n{}".format(traceback.format_exc(), g_cFileCoord), color=COLORS.ERROR)
		sys.exit()
