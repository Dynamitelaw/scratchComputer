from collections import OrderedDict
import copy

from pycparser import c_parser, c_ast, parse_file, c_generator
import compGlobals as globals
from compClasses import instructionList


def getArraySize(arrayDecl):
		'''
		Returns the size of an array in bytes.
		'''
		arrayLength = int(arrayDecl.dim.value)
		arrayType = arrayDecl.type

		if isinstance(arrayType, c_ast.TypeDecl):
			elementType = "".join(arrayType.type.names)
			elementSize = globals.typeSizeDictionary[elementType]

			returnVar = [arrayLength * elementSize, [elementSize]]
			return returnVar
		elif isinstance(arrayType, c_ast.ArrayDecl):
			subArraySize, subElementSize = getArraySize(arrayType)
			returnVar = [arrayLength * subArraySize, [subArraySize]+subElementSize]
			return returnVar
		else:
			raise Exception("Input declaration must be a c_ast.ArrayDecl object")


class scopeController:
	'''
	This class manages and controls the local scope of any given function.
	The scopeController is responsible for 
		storing and managing variables within the scope
		managing register usage
		managing local stack
		maintaining variable coherency
	'''
	class variable:
		'''
		This subclass is used to represent all explicit and implicit variables in a given scope.
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
			tempDict["subElementSize"] = self.subElementSize
			tempDict["signed"] = self.signed
			tempDict["volatileRegister"] = self.volatileRegister

			return str(tempDict)
		def __repr__(self):
			tempDict = {}
			tempDict["name"] = self.name
			tempDict["register"] = self.register
			tempDict["type"] = "\"{}\"".format(self.type).replace("\n","").replace(" ", "")
			tempDict["size"] = self.size
			tempDict["subElementSize"] = self.subElementSize
			tempDict["signed"] = self.signed
			tempDict["volatileRegister"] = self.volatileRegister

			return str(tempDict)


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
		self.pointerCounter = 0
		self.tagCounter = 0

	
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
		Will undo any differences between this scope and the current branch scope.
		All variable locations and the state of the stack will be reverted from the branched state to this scope.
		
		Returns an instructionList item.
		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		branchVariableDict = scopeBranch.variableDict
		branchLocalStack = copy.deepcopy(scopeBranch.localStack)
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
			branchStackList = list(scopeBranch.localStack.items())
			for index in range(len(self.localStack), len(scopeBranch.localStack)):
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

		Returns:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		#Get size of variable
		varSize = None
		subElementSize = [4]
		if (size):
			varSize = size
		elif (varType):
			if isinstance(varType, c_ast.TypeDecl):
				if isinstance(varType.type, c_ast.IdentifierType):
					names = " ".join(varType.type.names)
					varSize = globals.typeSizeDictionary[names]
				elif isinstance(varType.type, c_ast.Struct):
					name = varType.type.name
					varSize = globals.typeSizeDictionary[name]
				else:
					raise Exception("Unsupported TypeDecl | {}\n{}".format(globals.cFileCoord, varType))
			elif isinstance(varType, c_ast.ArrayDecl):
				varSize, subElementSize = getArraySize(varType)
			else:
				#Other type. Set to default 4
				varSize = 4
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
					if not ("<TAG_" in self.usedRegisters[register]):
						print(self.usedRegisters.items())
						raise Exception("Register \"{}\" already in use by variable \"{}\"".format(register, self.usedRegisters[register]))

				self.usedRegisters[register] = variableName

				if (register in self.availableRegisters):
					self.availableRegisters.remove(register)

				self.variableDict[variableName] = self.variable(variableName, register=register, varType=varType, size=varSize, subElementSize=subElementSize, signed=varSigned, volatileRegister=volatileRegister)
		else:
			if (variableName in self.variableDict):
				pass
			else:
				#No register location specified. Leave blank
				self.variableDict[variableName] = self.variable(variableName, register=None, varType=varType, size=varSize, subElementSize=subElementSize, signed=varSigned, volatileRegister=volatileRegister)

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
			raise Exception("ERROR: variable \"{}\" not declared in scope | {}".format(variableName, globals.cFileCoord))

		if not (variableName in self.localStack):
			#Allocate space on stack for variable
			instructions += self.storeStack(variableName, indentLevel=indentLevel)


		#Create pointer variable and get free register
		regDest = None
		pointerName = "<PTR_{}>_&{}".format(self.pointerCounter, variableName)
		self.pointerCounter += 1
		if (pointerName in self.variableDict):
			regDest = self.variableDict[pointerName].register
		
		if (not regDest):
			instructionsTemp, regDest = self.getFreeRegister(preferTemp=True, regOverride=regDestOverride, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions +=  self.addVariable(pointerName, register=regDest, volatileRegister=True, indentLevel=indentLevel)

		#Get location of variable relative to current stack pointer
		varLocation = 0
		currentLocation = 0
		for var in self.localStack:
			currentLocation += self.localStack[var]
			if (var == variableName):
				varLocation = currentLocation
		currentStackSize = currentLocation

		stackOffset = currentStackSize - varLocation


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


	def getFreeRegister(self, preferTemp=False, tempsAllowed=True, forceFree=True, regOverride=None, tag="None", indentLevel=0):
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

		#Make sure return address register and global pointer did not end up on available reg list
		if ("ra" in self.availableRegisters):
			self.availableRegisters.remove("ra")
		if ("gp" in self.availableRegisters):
			self.availableRegisters.remove("gp")
		self.availableRegisters.sort()

		registerName = None

		if (regOverride):
			registerName = regOverride
			instructions += self.releaseRegister(registerName, indentLevel=indentLevel)
			self.availableRegisters.remove(registerName)

			#Tag released register
			tagName = "<TAG_{}>_{}".format(self.tagCounter, tag)
			self.tagCounter += 1
			instructions += self.addVariable(tagName, register=registerName, volatileRegister=True,indentLevel=indentLevel)
			self.usedRegisters[registerName] = tagName

			return instructions, registerName

		if (preferTemp):
			#Check for free temp register
			t_Registers = [i for i in self.availableRegisters if "t" in i]
			if (len(t_Registers) > 0):
				registerName = t_Registers[0]
				self.availableRegisters.remove(registerName)

				#Tag released register
				tagName = "<TAG_{}>_{}".format(self.tagCounter, tag)
				self.tagCounter += 1
				instructions += self.addVariable(tagName, register=registerName, volatileRegister=True,indentLevel=indentLevel)
				self.usedRegisters[registerName] = tagName

				return instructions, registerName

			#Check for free argument register
			a_Registers = [i for i in self.availableRegisters if "a" in i]
			if (len(a_Registers) > 0):
				registerName = a_Registers[0]
				self.availableRegisters.remove(registerName)

				#Tag released register
				tagName = "<TAG_{}>_{}".format(self.tagCounter, tag)
				self.tagCounter += 1
				instructions += self.addVariable(tagName, register=registerName, volatileRegister=True,indentLevel=indentLevel)
				self.usedRegisters[registerName] = tagName

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

					#Tag released register
					tagName = "<TAG_{}>_{}".format(self.tagCounter, tag)
					self.tagCounter += 1
					instructions += self.addVariable(tagName, register=registerName, volatileRegister=True,indentLevel=indentLevel)
					self.usedRegisters[registerName] = tagName

					return instructions, registerName

				#Check for free argument register
				a_Registers = [i for i in self.availableRegisters if "a" in i]
				if (len(a_Registers) > 0):
					registerName = a_Registers[0]
					self.availableRegisters.remove(registerName)

					#Tag released register
					tagName = "<TAG_{}>_{}".format(self.tagCounter, tag)
					self.tagCounter += 1
					instructions += self.addVariable(tagName, register=registerName, volatileRegister=True,indentLevel=indentLevel)
					self.usedRegisters[registerName] = tagName

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

		#Tag released register
		if (registerName):
			tagName = "<TAG_{}>_{}".format(self.tagCounter, tag)
			self.tagCounter += 1
			instructions += self.addVariable(tagName, register=registerName, volatileRegister=True,indentLevel=indentLevel)
			self.usedRegisters[registerName] = tagName

		return instructions, registerName


	def regexReleaseVariable(self, variableRegex, indentLevel=0):
		'''
		Deallocates a batch of registers, whose allocated variables contain variableRegex.

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)

		for registerName in copy.deepcopy(self.usedRegisters):
			if (registerName in self.usedRegisters):
				variableName = self.usedRegisters[registerName]
				if (variableRegex in variableName):  #<TODO> implement actual regex matching
					instructions += self.releaseRegister(registerName, indentLevel=indentLevel)

		return instructions


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

	
	def alignStack(self, indentLevel=0):
		'''
		If current stack is not word aligned, will add buffer space to stack

		returnType:
			<instructionList> instructions
		'''
		instructions = instructionList(self)
		indentString = "".join(["\t" for i in range(indentLevel)])

		#Get current size of stack
		currentStackSize = 0
		for var in self.localStack:
			currentStackSize += self.localStack[var]

		#Add buffer space if needed
		if (currentStackSize%4 != 0):
			#SP is not word aligned. Need to add buffer space to stack
			bufferName = "<BUFFER>_{}".format(self.stackBufferCounter)
			self.stackBufferCounter += 1
			bufferSize = 4 - (currentStackSize%4)
			self.localStack[bufferName] = bufferSize

			instructions.append("{}addi sp, sp, -{}".format(indentString, bufferSize))

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

		for variableName in copy.deepcopy(self.variableDict):
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
		stateDict["availableRegisters"] = self.availableRegisters
		stateDict["localStack"] = [{v: self.localStack[v]} for v in self.localStack]

		return stateDict

