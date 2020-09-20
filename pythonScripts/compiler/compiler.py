import os
import sys
import argparse
import copy
from collections import OrderedDict

from pycparser import c_parser, c_ast, parse_file, c_generator
import assembler



#Global vars
g_whileCounter = 0
g_forCounter = 0
g_ifCounter = 0
g_variableNameCoutners = {}


class variable:
	def __init__(self, name, register=None, varType=None, size=None, signed=True):
		self.name = name
		self.register = register
		self.type = varType
		self.size = size
		self.signed = signed
	def __str__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["register"] = self.register
		tempDict["type"] = self.type
		tempDict["size"] = self.size
		tempDict["signed"] = self.signed

		return str(tempDict)
	def __repr__(self):
		tempDict = {}
		tempDict["name"] = self.name
		tempDict["register"] = self.register
		tempDict["type"] = self.type
		tempDict["size"] = self.size
		tempDict["signed"] = self.signed

		return str(tempDict)


class scopeController:
	def __init__(self, name):
		self.name = name
		self.variableDict = {}
		self.localStack = OrderedDict()
		self.usedRegisters = {}
		self.availableRegisters = [
			"s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
			"a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
			"t0", "t1", "t2", "t3", "t4", "t5", "t6"
			]
		self.loadHistory = []
		self.virginSaveRegisters = ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"]
		self.expressionCounter = 0


	def mergeScopeBranch(self, scopeBranch, indentLevel=0):
		instructions = []
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
						instructions += scopeBranch.storeStack(variableName, indentLevel=indentLevel)

		#Reset stack to parent state
		if (len(self.localStack) != len(branchLocalStack)):
			#branch added things to the stack. Deallocate them
			deallocateLength = 0
			branchStackList = list(branchLocalStack.items())
			for index in range(len(self.localStack), len(branchLocalStack)):
				deallocateLength += branchStackList[index][1]
				
			instructions.append("{}addi sp, sp, {}".format(indentString, deallocateLength))

		return instructions
	

	def createExpressionResult(self, varType=None, size=4, signed=True):
		variableName = "<EXPR_RESULT>_{}".format(self.expressionCounter)
		self.expressionCounter += 1
		self.addVariable(variableName, varType=varType, size=size, signed=signed)

		return variableName


	def addVariable(self, variableName, register=None, varType=None, size=4, signed=True):
		self.variableDict[variableName] = variable(variableName, register=register, varType=varType, size=size, signed=signed)
		if (register):
			self.usedRegisters[register] = variableName
			if (register in self.availableRegisters):
				self.availableRegisters.remove(register)


	def removeVariable(self, variableName):
		try:
			variableObj = self.variableDict[variableName]
			self.usedRegisters.remove(variableObj.register)
			self.availableRegisters.append(variableObj.register)
			self.availableRegisters.sort()
			del variableDict[variableName]
		except Exception as e:
			raise Exception("ERROR: Could not remove variable \"{}\"{}".format(variableName, e))


	def storeStack(self, variableName, indentLevel=0):
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope".format(variableName))

		#Check if variable already on stack
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

			#Update value of variable in stack
			if (variableObj.size == 1):
				instructions.append("{}sb {}, {}(sp)".format(indentString, variableObj.register, stackOffset))
			elif (variableObj.size == 2):
				instructions.append("{}sh {}, {}(sp)".format(indentString, variableObj.register, stackOffset))
			elif (variableObj.size == 4):
				instructions.append("{}sw {}, {}(sp)".format(indentString, variableObj.register, stackOffset))

		else:
			#Allocate space on stack and store current value of regSource
			self.localStack[variableName] = variableObj.size	

			instructions.append("{}addi sp, sp, -{}".format(indentString, variableObj.size))
			instructions.append("{}sw {}, 0(sp)".format(indentString, variableObj.register))


		del self.usedRegisters[variableObj.register]
		self.availableRegisters.append(variableObj.register)
		variableObj.register = None

		return instructions


	def loadStack(self, variableName, regDestOverride=None, indentLevel=0):
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope".format(variableName))

		#Get free register to store
		regDest = None
		if (regDestOverride):
			regDest = regDestOverride
			instructions += self.releaseRegister(regDest)
		elif (len(self.availableRegisters) > 0):
			instructionsTemp, regDest = self.getFreeRegister(indentLevel=indentLevel)
			instructions += instructionsTemp
		else:
			ejectVariableName = self.loadHistory.pop(0)
			self.storeStack(ejectVariableName, indentLevel=indentLevel)
			regDest = self.variableDict[ejectVariableName].register

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
		return self.variableDict[variableName].register


	def getFreeRegister(self, preferTemp=False, tempsAllowed=True, forceFree=True, indentLevel=0):
		#<TODO> implement forceFree
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		registerName = None

		if (preferTemp):
			t_Registers = [i for i in self.availableRegisters if "t" in i]
			if (len(t_Registers) > 0):
				registerName = t_Registers[0]
				self.availableRegisters.remove(registerName)
				return instructions, registerName

			a_Registers = [i for i in self.availableRegisters if "a" in i]
			if (len(a_Registers) > 0):
				registerName = a_Registers[0]
				self.availableRegisters.remove(registerName)
				return instructions, registerName

			s_Registers = [i for i in self.availableRegisters if "s" in i]
			if (len(s_Registers) > 0):
				registerName = s_Registers[0]
				self.availableRegisters.remove(registerName)
				#don't return yet. must check if it is virgin save reg
		else:
			s_Registers = [i for i in self.availableRegisters if "s" in i]
			if (len(s_Registers) > 0):
				registerName = s_Registers[0]
				self.availableRegisters.remove(registerName)
			
			if (not registerName and tempsAllowed):
				t_Registers = [i for i in self.availableRegisters if "t" in i]
				if (len(t_Registers) > 0):
					registerName = t_Registers[0]
					self.availableRegisters.remove(registerName)
					return instructions, registerName

				a_Registers = [i for i in self.availableRegisters if "a" in i]
				if (len(a_Registers) > 0):
					registerName = a_Registers[0]
					self.availableRegisters.remove(registerName)
					return instructions, registerName


		if (registerName in self.virginSaveRegisters):
			#Returning a save register that doesn't belong to us yet. Save onto stack
			variableName = "<SAVE>_{}".format(registerName)
			self.addVariable(variableName, register=registerName)
			instructions += self.storeStack(variableName, indentLevel=indentLevel)
			self.virginSaveRegisters.remove(registerName)

		return instructions, registerName


	def releaseRegister(self, registerName, indentLevel=0):
		instructions = []

		if (registerName in self.virginSaveRegisters):
			#Requesting a save register that doesn't belong to us yet. Save onto stack
			variableName = "<SAVE>_{}".format(registerName)
			self.addVariable(variableName, register=registerName)
			self.storeStack(variableName)
			self.virginSaveRegisters.remove(registerName)

		if (registerName in self.availableRegisters):
			pass
		elif (registerName in self.usedRegisters):
			ejectVariableName = self.usedRegisters[registerName]
			instructions += self.storeStack(ejectVariableName, indentLevel=indentLevel)

			self.availableRegisters.sort()
		elif (registerName != "zero"):
			self.availableRegisters.append(registerName)
			self.availableRegisters.sort()

		return instructions


	def moveVariable(self, variableName, regDest, indentLevel=0):
		instructions = []
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
				instructions.append("{}mv {}, {}".format(indentString, regDest, oldRegister))
				variableObj.register = regDest
				self.usedRegisters[regDest] = variableName
				del self.usedRegisters[oldRegister]
				self.availableRegisters.remove(regDest)
				self.availableRegisters.append(oldRegister)
				self.availableRegisters.sort()
			else:
				if (variableName in self.localStack):
					instructions += self.loadStack(variableName, regDestOverride=regDest, indentLevel=indentLevel)
				else:
					#Variable is not on stack nor in register. Instantiate into regDest
					variableObj.register = regDest
					self.usedRegisters[regDest] = variableName
				self.availableRegisters.remove(regDest)

		return instructions


	def saveTemps(self, indentLevel=0):
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		for registerName in list(self.usedRegisters.keys()):
			variableName = self.usedRegisters[registerName]

			if (("a" in registerName) or ("t" in registerName)):
				#Temp register. Must save somewhere

				#Try to find a free save register
				instructionsTemp, freeReg = self.getFreeRegister(tempsAllowed=False, forceFree=False, indentLevel=indentLevel)
				instructions += instructionsTemp
				if (freeReg):
					instructions += self.moveVariable(variableName, freeReg, indentLevel=indentLevel)
				else:
					instructions += self.storeStack(variableName, indentLevel=indentLevel)

		return instructions


	def saveReturnAddress(self, indentLevel=0):
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableName = "<SAVE>_ra"
		if not (variableName in self.variableDict):
			self.addVariable(variableName, register="ra")
			instructions += self.storeStack(variableName, indentLevel=indentLevel)

		return instructions


	def restoreSaves(self, indentLevel=0):
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		for variableName in self.variableDict:
			if ("<SAVE>" in variableName):
				regDest = variableName.replace("<SAVE>_", "")
				instructions += self.moveVariable(variableName, regDest, indentLevel=indentLevel)

		return instructions


	def deallocateStack(self, indentLevel=0):
		instructions = []
		indentString = "".join(["\t" for i in range(indentLevel)])

		deallocateLength = 0
		stackList = list(self.localStack.items())
		for index in range(0, len(stackList)):
			deallocateLength += stackList[index][1]
			
		if (deallocateLength > 0):
			instructions.append("{}addi sp, sp, {}".format(indentString, deallocateLength))

		self.localStack = OrderedDict()

		return instructions


def getFunctionDefinitions(ast):
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

	for item in childrens:
		if isinstance(item,c_ast.FuncDef):
			functions[item.decl.name] = item
		elif isinstance(item, c_ast.Decl):
			globalVarDelcarations.append(item)

	return functions, globalVarDelcarations


def operandToRegister(operandItem, scope, indentLevel=0):
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	operandReg = ""
	if isinstance(operandItem, c_ast.ID):
		#operand is variable
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
			instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}addi {}, zero, {}".format(indentString, operandReg, value))
		else:
			#Must load value from memory
			#<TODO>
			operandReg = "TOO_LARGE"
	elif isinstance(operandItem, c_ast.BinaryOp):
		#Operand is binary op
		instructionsTemp, resultVariableName = convertBinaryOpItem(operandItem, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		operandReg = scope.getRegisterLocation(resultVariableName)
	elif isinstance(operandItem, c_ast.FuncCall):
		#Operand is function result
		instructions += convertFuncCallItem(operandItem, scope, indentLevel=indentLevel)
		operandReg = "a0"
	else:
		instructions.append("{}#UNSUPPORTED OPERAND".format(indentString))
		instructions.append("{}".format(operandItem))


	return instructions, operandReg


def convertUnaryOpItem(item, scope, branch=None, targetVariableName=None, targetReg=None, resultSize=4, resultType=None, indentLevel=0):
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	instructionsTemp, operandReg = operandToRegister(item.expr, scope, indentLevel=indentLevel)
	instructions += instructionsTemp

	resultVariableName = None
	if isinstance(item.expr, c_ast.ID):
		variableName = item.expr.name

	operator = item.op

	if (operator == "p++"):
		instructions.append("{}addi {}, {}, 1".format(indentString, operandReg, operandReg))
	elif (operator == "p--"):
		instructions.append("{}addi {}, {}, -1".format(indentString, operandReg, operandReg))
	elif (operator == "-"):
		if (targetVariableName):
			scope.addVariable(targetVariableName, size=resultSize, varType=resultType)
			resultVariableName = targetVariableName
		else:
			resultVariableName = scope.createExpressionResult()

		regDest = ""
		if (targetReg):
			instructions += scope.releaseRegister(targetReg, indentLevel=indentLevel)
			regDest = targetReg
		else:
			instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp

		instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
		instructions += instructionsTemp

		instructions.append("{}addi {}, zero, -1".format(indentString, tempRegister))
		instructions.append("{}mul {}, {}, {}".format(indentString, regDest, operandReg, tempRegister))

		instructions += scope.releaseRegister(tempRegister)
	elif (operator == "!"):
		if (branch):
			instructions.append("{}beq {}, zero, {}".format(indentString, operandReg, branch))
		else:
			if (targetVariableName):
				scope.addVariable(targetVariableName, size=resultSize, varType=resultType)
				resultVariableName = targetVariableName
			else:
				resultVariableName = scope.createExpressionResult()

			regDest = ""
			if (targetReg):
				instructions += scope.releaseRegister(targetReg, indentLevel=indentLevel)
				regDest = targetReg
			else:
				instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, indentLevel=indentLevel)
				instructions += instructionsTemp


			instructions.append("{}sltu {}, {}, zero".format(indentString, regDest, operandReg))
	else:
		instructions.append("{}###UNSUPPORTED OPERATOR \"{}\"| convertUnaryOpItem".format(indentString, operator))

	return instructions, resultVariableName


def convertBinaryOpItem(item, scope, branch=None, targetVariableName=None, targetReg=None, resultSize=4, resultType=None, indentLevel=0):
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Get variable and register for result
	resultVariableName = ""
	if (not branch):
		if (targetVariableName):
			scope.addVariable(targetVariableName, size=resultSize, varType=resultType)
			resultVariableName = targetVariableName
		else:
			resultVariableName = scope.createExpressionResult()

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
		instructions += scope.moveVariable(resultVariableName, regDest)

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
			instructions.append("{}beq {}, {}, {}".format(indentString, leftOperandReg, rightOperandReg, branch))
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
		instructions.append("{}###UNSUPPORTED OPERATOR \"{}\"| convertBinaryOpItem".format(indentString, operator))


	#Free temp constant registers
	if isinstance(leftOperand, c_ast.Constant):
		instructions += scope.releaseRegister(leftOperandReg, indentLevel=indentLevel)
	if isinstance(rightOperand, c_ast.Constant):
		instructions += scope.releaseRegister(rightOperandReg, indentLevel=indentLevel)


	return instructions, resultVariableName


def convertIfItem(item, scope, indentLevel=0):
	global g_ifCounter

	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

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
		instructions.append("{}###UNSUPPORTED CONDITION | convertIfItem".format(indentString))
		instructions.append("".format(conditionItem))

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
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	functionName = item.name.name

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
		else:
			instructions.append("{}#UNSUPPORTED ITEM | convertFuncCallItem".format(indentString))
			instructions.append("{}".format(item))

		argIndex += 1

	#Save return address to stack
	instructions += scope.saveReturnAddress(indentLevel=indentLevel)

	#Save temps
	instructions += scope.saveTemps(indentLevel=indentLevel)

	#Call function
	instructions.append("{}j {}".format(indentString, functionName))

	return instructions


def convertAssignmentItem(item, scope, indentLevel=0):
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Get left value into register  #<TODO> handle values small enought for immediates
	leftOperand = item.lvalue
	instructionsTemp, leftValReg = operandToRegister(leftOperand, scope, indentLevel=indentLevel)
	instructions += instructionsTemp

	#Get right value into register  #<TODO> handle values small enought for immediates
	rightOperand = item.rvalue
	instructionsTemp, rightValReg = operandToRegister(rightOperand, scope, indentLevel=indentLevel)
	instructions += instructionsTemp

	#Handler operators
	#<TODO>, handle unsigned operands
	operator = item.op

	if (operator == "="):
		instructions.append("{}mv {}, {}".format(indentString, leftValReg, rightValReg))
	elif (operator == "+="):
		instructions.append("{}add {}, {}, {}".format(indentString, leftValReg, leftValReg, rightValReg))
	elif (operator == "-="):
		instructions.append("{}sub {}, {}, {}".format(indentString, leftValReg, leftValReg, rightValReg))
	else:
		instructions.append("{}###UNSUPPORTED OPERATOR \"{}\" | convertAssignmentItem".format(indentString, operator))

	return instructions


def convertReturnItem(item, scope, indentLevel=0):
	#<TODO> Prevent uneeded saving of variables onto stack when we are returning
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	if isinstance(item.expr, c_ast.ID):
		#Return variable
		variableName = item.expr.name
		currentRegister = scope.getRegisterLocation(variableName)

		if (not currentRegister):
			#variable on stack. Load into a0
			pass
			#instructions += scope.loadStack(variableName, regDestOverride="a0", indentLevel=indentLevel)
		else:
			#variable in register. Move into a0
			instructions += scope.moveVariable(variableName, "a0", indentLevel=indentLevel)
		
		#Restore save variables, deallocate stack, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateStack(indentLevel=indentLevel)
		instructions.append("{}j ra".format(indentString))

	elif isinstance(item.expr, c_ast.FuncCall):
		#Call function, then return result
		instructions += convertFuncCallItem(item.expr, scope, indentLevel=indentLevel)

		#Restore save variables, deallocate stack, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateStack(indentLevel=indentLevel)
		instructions.append("{}j ra".format(indentString))

	elif isinstance(item.expr, c_ast.Constant):
		#Return constant value
		value = int(item.expr.value) #<TODO> Handle floats and doubles
		if (value < 2048) and (value >= -2048):
			#Value is small enough for addi
			instructions.append("{}addi {}, zero, {}".format(indentString, "a0", value))
		else:
			#Must load value from memory
			#<TODO>
			instructions.append("###TOO_LARGE | convertReturnItem")

		#Restore save variables, deallocate stack, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateStack(indentLevel=indentLevel)
		instructions.append("{}j ra".format(indentString))

	elif isinstance(item.expr, c_ast.BinaryOp):
		instructionsTemp, resultVariableName = convertBinaryOpItem(item.expr, scope, targetReg="a0", indentLevel=indentLevel)
		instructions += instructionsTemp

		#Restore save variables then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateStack(indentLevel=1)
		instructions.append("{}j ra".format(indentString))
	elif isinstance(item.expr, c_ast.UnaryOp):
		instructionsTemp, resultVariableName = convertUnaryOpItem(item.expr, scope, targetReg="a0", indentLevel=indentLevel)
		instructions += instructionsTemp

		#Restore save variables, deallocate stack, then return
		instructions += scope.restoreSaves(indentLevel=indentLevel)
		instructions += scope.deallocateStack(indentLevel=indentLevel)
		instructions.append("{}j ra".format(indentString))
	else:
		instructions.append("{}#UNSUPPORTED ITEM | convertReturnItem".format(indentString))
		instructions.append("{}".format(item))


	return instructions


def convertDeclItem(item, scope, indentLevel=0):
	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	variableName = item.name

	if (item.init):
		if isinstance(item.init, c_ast.Constant):
			#Initialized variable to a constant value
			instructionsTemp, destinationRegister = scope.getFreeRegister(indentLevel=indentLevel)
			instructions += instructionsTemp
			scope.addVariable(variableName, register=destinationRegister, varType=item.type.type.names, size=4, signed=True)

			value = int(item.init.value) #<TODO> Handle floats and doubles
			if (value < 2048) and (value >= -2048):
				#Value is small enough for addi
				instructions.append("{}addi {}, zero, {}".format(indentString, destinationRegister, value))
			else:
				#Must load value from memory
				#<TODO>
				instructions.append("###TOO_LARGE | convertDeclItem")

		elif isinstance(item.init, c_ast.BinaryOp):
			#Initialized variable is result of binary expression
			instructionsTemp, resultVariableName = convertBinaryOpItem(item.init, scope, targetVariableName=variableName, indentLevel=indentLevel)
			instructions += instructionsTemp

		elif isinstance(item.init, c_ast.FuncCall):
			#Initialized variable is result of function call
			instructions += convertFuncCallItem(item.init, scope, indentLevel=indentLevel)
			scope.addVariable(variableName, register="a0", varType=item.type.type.names, size=4, signed=True)

		else:
			print("{}###UNSUPPORTED DECLARATION | convertDeclItem".format(indentString))
			print("{}".format(item))
	else:
		#Declared without initial value
		scope.addVariable(variableName, varType=item.type.type.names, size=4, signed=True)


	return instructions, variableName


def convertForItem(item, scope, indentLevel=0):
	global g_forCounter

	instructions = []
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Initialize for loop counting variable
	if isinstance(item.init, c_ast.DeclList):
		for declareItem in item.init.decls:
			instructionsTemp, variableName = convertDeclItem(declareItem, scope, indentLevel=indentLevel)
			instructions += instructionsTemp
	else:
		instructions.append("{}#UNSUPPORTED ITEM | convertForItem".format(indentString))
		instructions.append("{}".format(item.init))

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
		instructions.append("{}\t#UNSUPPORTED CONDITION | convertForItem".format(indentString))
		instructions.append("".format(conditionItem))


	#For loop body
	loopBodyItem = item.stmt
	instructions.append("{}\t{}:".format(indentString, bodyLabel))
	instructions += convertAstItem(loopBodyItem, scope, indentLevel=indentLevel+2)

	#For loop increment
	nextItem = item.next
	if isinstance(nextItem, c_ast.UnaryOp):
		instructionsTemp, resultVariableName = convertUnaryOpItem(nextItem, scope, indentLevel=indentLevel+1)
		instructions += instructionsTemp
	elif isinstance(nextItem, c_ast.Assignment):
		instructions.append("{}###UNSUPPORTED NEXT ITEM | convertForItem".format(indentString))
		instructions.append("".format(nextItem))
	else:
		instructions.append("{}###UNSUPPORTED NEXT ITEM | convertForItem".format(indentString))
		instructions.append("".format(nextItem))

	#For loop exit
	instructions.append("{}\tj {}".format(indentString, startLabel))
	instructions.append("{}{}:".format(indentString, endLabel))

	return instructions


def convertAstItem(item, scope, indentLevel=0):
	instructions = []
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
		instructions += convertAssignmentItem(item, scope, indentLevel)
	else:
		print("{}###UNSUPPORTED ITEM | convertAstItem".format(indentString))
		print("{}".format(item))
		

	return instructions


def covertFuncToAssembly(funcDef):
	'''
	Converts the funcDef node into an assembly snippet. Adds asm string as object variable funcDef.coord
	'''
	instructions = []
	scope = scopeController(funcDef.decl.name)

	#Function label
	instructions.append("{}:".format(funcDef.decl.name))

	#Add input variables too function scope
	if (funcDef.decl.type.args):
		inputParameters = funcDef.decl.type.args.params

		argIndex = 0
		for arg in inputParameters:
			registerName = "a{}".format(argIndex)
			scope.addVariable(arg.name, register=registerName,varType=arg.type.type.names, size=4, signed=True)

			argIndex += 1

	#Write function body
	instructions += convertAstItem(funcDef.body, scope, indentLevel=1)

	#Restore save variables
	instructions += scope.restoreSaves(indentLevel=1)

	#Deallocate local stack
	instructions += scope.deallocateStack(indentLevel=1)

	#Return to caller
	instructions.append("\tj ra")

	funcDef.coord = instructions  #Borrow coord variable, since it seems to be unused by pycparser


def precleanCFile(filepath):
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

	#########
	# Translate C file into assembly file
	#########

	#Parse C file
	cleanFilePath = precleanCFile(cFilePath)
	ast = parse_file(cleanFilePath, use_cpp=True)

	#Translate functions into assembly snippets
	definedFunctions = {}
	globalVarDelcarations = []
	definedFunctions, globalVarDelcarations = getFunctionDefinitions(ast)  #<TODO> handle global variables
	
	if ("main" in definedFunctions):
		for functionName in definedFunctions:
			#<TODO> multithread these translations
			funcDef = definedFunctions[functionName]
			covertFuncToAssembly(funcDef)
			#print("\n".join(funcDef.coord))
	else:
		print("ERROR: main function is not defined")
		sys.exit()
	
	#Create final assembly file
	outputDirectory, hexFilename = os.path.split(hexPath)
	assemblyFilePath = os.path.join(outputDirectory, "{}.asm".format(hexFilename.split(".")[0]))
	
	asmFile = open(assemblyFilePath, "w")
	
	if (memorySize):
		#Initialize sp
		stackPointerStart = int(4 * int(int(memorySize) / 4))
		asmFile.write("addi sp, zero, {}\n".format(int(stackPointerStart)))
	asmFile.write("addi ra, zero, PROGRAM_END\n")  #initialize return address for main

	#Write main first
	instructions = definedFunctions["main"].coord
	asmFile.write("\n".join(instructions))
	asmFile.write("\n")
	del definedFunctions["main"]

	#Write other functions
	for functionName in definedFunctions:
		instructions = definedFunctions[functionName].coord
		asmFile.write("\n".join(instructions))
		asmFile.write("\n")

	asmFile.write("PROGRAM_END:\nadd zero, zero, zero\n")  #Program end label/nop
	asmFile.close()


	#Convert assembly file to hex
	assembler.main(assemblyFilePath, hexPath, indexPath, logisim)

	#Cleanup
	os.remove(cleanFilePath)
