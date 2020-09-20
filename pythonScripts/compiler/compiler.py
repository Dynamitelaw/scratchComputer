from __future__ import print_function
import sys
import re
import json
from collections import OrderedDict
from pycparser import c_parser, c_ast, parse_file, c_generator
import copy


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
			"a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
			"t0", "t1", "t2", "t3", "t4", "t5", "t6"
			]
		self.loadHistory = []
		self.expressionCounter = 0


	def mergeScopeBranch(self, scopeBranch, indentLevel=0):
		assemblyString = ""
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
						assemblyString += scopeBranch.moveVariable(variableName, variableObj.register, indentLevel=indentLevel)
					else:
						#Variable should be on stack
						assemblyString += scopeBranch.storeStack(variableName, indentLevel=indentLevel)

		#Reset stack to parent state
		if (len(self.localStack) != len(branchLocalStack)):
			#branch added things to the stack. Deallocate them
			deallocateLength = 0
			branchStackList = list(branchLocalStack.items())
			for index in range(len(self.localStack), len(branchLocalStack)):
				deallocateLength += branchStackList[index][1]
				
			assemblyString += "{}addi sp, sp, {}\n".format(indentString, deallocateLength)

		return assemblyString
	

	def createExpressionResult(self, varType=None, size=None, signed=True):
		variableName = "<EXPR_RESULT>_{}".format(self.expressionCounter)
		self.expressionCounter += 1
		self.addVariable(variableName, varType=varType, size=size, signed=signed)

		return variableName


	def addVariable(self, variableName, register=None, varType=None, size=None, signed=True):
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
			raise Exception("ERROR: Could not remove variable \"{}\"\n{}".format(variableName, e))


	def storeStack(self, variableName, indentLevel=0):
		assemblyString = ""
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
			for var in localStack:
				currentLocation += self.localStack[var]
				if (var == variableName):
					varLocation = currentLocation
			currentStackSize = currentLocation

			stackOffset = currentStackSize - varLocation

			#Update value of variable in stack
			if (variableObj.size == 1):
				assemblyString += "{}sb {}, {}(sp)\n".format(indentString, regSource, stackOffset)
			elif (variableObj.size == 2):
				assemblyString += "{}sh {}, {}(sp)\n".format(indentString, regSource, stackOffset)
			elif (variableObj.size == 4):
				assemblyString += "{}sw {}, {}(sp)\n".format(indentString, regSource, stackOffset)

		else:
			#Allocate space on stack and store current value of regSource
			self.localStack[variableName] = variableObj.size	

			assemblyString += "{}addi sp, sp, -{}\n".format(indentString, variableObj.size)
			assemblyString += "{}sw {}, 0(sp)\n".format(indentString, variableObj.register)


		del self.usedRegisters[variableObj.register]
		self.availableRegisters.append(variableObj.register)
		variableObj.register = None

		return assemblyString


	def loadStack(self, variableName, regDestOverride=None, indentLevel=0):
		assemblyString = ""
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
			assemblyString += self.releaseRegister(regDest)
		elif (len(self.availableRegisters) > 0):
			regDest = self.availableRegisters.pop(-1)
		else:
			ejectVariableName = self.loadHistory.pop(0)
			self.storeStack(ejectVariableName, indentLevel=indentLevel)
			regDest = self.variableDict[ejectVariableName].register

		if ((variableName in self.localStack) and (variableName in self.variableDict)):
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
					assemblyString += "{}lb {}, {}(sp)\n".format(indentString, regDest, stackOffset)
				else:
					assemblyString += "{}lbu {}, {}(sp)\n".format(indentString, regDest, stackOffset)
			elif (variableObj.size == 2):
				if (variableObj.signed):
					assemblyString += "{}lh {}, {}(sp)\n".format(indentString, regDest, stackOffset)
				else:
					assemblyString += "{}lhu {}, {}(sp)\n".format(indentString, regDest, stackOffset)
			elif (variableObj.size == 4):
				assemblyString += "{}lw {}, {}(sp)\n".format(indentString, regDest, stackOffset)
				
			variableObj.register = regDest
			self.usedRegisters[regDest] = variableName
			self.loadHistory.append(variableName)

			return assemblyString
		
		else:
			if (self.variableName in self.localStack):
				raise Exception("ERROR: variable \"{}\" not currently defined in variableDict".format(variableName))
			else:
				raise Exception("ERROR: variable \"{}\" not currently in localStack {}".format(variableName, self.localStack))


	def getRegisterLocation(self, variableName):
		return self.variableDict[variableName].register


	def getFreeRegister(self):
		if (len(self.availableRegisters) > 0):
			return self.availableRegisters.pop[-1]
		else:
			return None
			#<TODO>, add automatic register freeing


	def releaseRegister(self, registerName, indentLevel=0):
		assemblyString = ""

		if (registerName in self.availableRegisters):
			pass
		elif (registerName in self.usedRegisters):
			ejectVariableName = self.usedRegisters[registerName]
			assemblyString += self.storeStack(ejectVariableName, indentLevel=indentLevel)

			self.availableRegisters.sort()
		elif (registerName != "zero"):
			self.availableRegisters.append(registerName)
			self.availableRegisters.sort()

		return assemblyString


	def moveVariable(self, variableName, regDest, indentLevel=0):
		assemblyString = ""
		indentString = "".join(["\t" for i in range(indentLevel)])

		variableObj = None
		if (variableName in self.variableDict):
			variableObj = self.variableDict[variableName]
		else:
			raise Exception("ERROR: variable \"{}\" not declared in scope".format(variableName))

		#Move variable into new register
		oldRegister = variableObj.register
		if (regDest != oldRegister):
			assemblyString += self.releaseRegister(regDest, indentLevel=indentLevel)
			if (oldRegister):
				assemblyString += "{}mv {}, {}\n".format(indentString, regDest, oldRegister)
				variableObj.register = regDest
				self.usedRegisters[regDest] = variableName
				del self.usedRegisters[oldRegister]
				self.availableRegisters.remove(regDest)
				self.availableRegisters.append(oldRegister)
				self.availableRegisters.sort()
			else:
				assemblyString += self.loadStack(variableName, regDestOverride=regDest, indentLevel=indentLevel)
				self.availableRegisters.remove(regDest)
		else:
			assemblyString += "###DAFUQ?!\n"

		return assemblyString








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
	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	operandReg = ""
	if isinstance(operandItem, c_ast.ID):
		#operand is variable
		operandReg = scope.getRegisterLocation(operandItem.name)
		if (operandReg == None):
			assemblyString += scope.loadStack(operandItem.name, indentLevel=indentLevel)
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
			operandReg = scope.getFreeRegister()
			assemblyString += "{}addi {}, zero, {}\n".format(indentString, operandReg, value)	
		else:
			#Must load value from memory
			#<TODO>
			operandReg = "TOO_LARGE"
	else:
		assemblyString += "{}#UNSUPPORTED OPERAND\n".format(indentString)


	return assemblyString, operandReg


def convertIfItem(item, scope, indentLevel=0):
	global g_ifCounter

	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Get left operand into register
	leftOperand = item.cond.left
	assemblyTemp, leftOperandReg = operandToRegister(leftOperand, scope, indentLevel=indentLevel)
	assemblyString += assemblyTemp

	#Get right operand into register
	rightOperand = item.cond.right
	assemblyTemp, rightOperandReg = operandToRegister(rightOperand, scope, indentLevel=indentLevel)
	assemblyString += assemblyTemp

	#Handle operator branching
	operator = item.cond.op
	onTrueLabel = "true_{}".format(g_ifCounter)
	onFalseLabel = "false_{}".format(g_ifCounter)
	ifExitLabel = "ifElseExit_{}".format(g_ifCounter)
	g_ifCounter += 1

	#<TODO>, handle unsigned operands
	if (operator == "=="):
		assemblyString += "{}beq {}, {}, {}\n".format(indentString, leftOperandReg, rightOperandReg, onTrueLabel)
	elif (operator == ">="):
		assemblyString += "{}bge {}, {}, {}\n".format(indentString, leftOperandReg, rightOperandReg, onTrueLabel)
	elif (operator == "<="):
		#Swap operands to save an instruction
		assemblyString += "{}bge {}, {}, {}\n".format(indentString, rightOperandReg, leftOperandReg, onTrueLabel)
	elif (operator == ">"):
		#Swap operands to save an instruction
		assemblyString += "{}blt {}, {}, {}\n".format(indentString, rightOperandReg, leftOperandReg, onTrueLabel)
	elif (operator == "<"):
		assemblyString += "{}blt {}, {}, {}\n".format(indentString, leftOperandReg, rightOperandReg, onTrueLabel)

	assemblyString += "{}j {}\n".format(indentString, onFalseLabel)

	#Free temp constant registers
	if isinstance(leftOperand, c_ast.Constant):
		assemblyString += scope.releaseRegister(leftOperandReg, indentLevel=indentLevel)
	if isinstance(rightOperand, c_ast.Constant):
		assemblyString += scope.releaseRegister(rightOperandReg, indentLevel=indentLevel)

	#Contruct true/false code blocks
	scopeBranch = copy.deepcopy(scope)
	assemblyString += "{}{}:\n".format(indentString, onTrueLabel)
	assemblyString += convertAstItem(item.iftrue, scopeBranch, indentLevel=indentLevel+1)
	assemblyString += scope.mergeScopeBranch(scopeBranch, indentLevel=indentLevel+1)  #<TODO> Skip this part if the true section ends with a return
	assemblyString += "{}j {}\n".format(indentString, ifExitLabel)

	scopeBranch = copy.deepcopy(scope)
	assemblyString += "{}{}:\n".format(indentString, onFalseLabel)
	assemblyString += convertAstItem(item.iffalse, scopeBranch, indentLevel=indentLevel+1)
	assemblyString += scope.mergeScopeBranch(scopeBranch, indentLevel=indentLevel+1)  #<TODO> Skip this part if the false section ends with a return
	assemblyString += "{}{}:\n".format(indentString, ifExitLabel)

	return assemblyString


def convertBinaryOpItem(item, scope, targetReg=None, indentLevel=0):
	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Get variable and register for result
	resultVariableName = scope.createExpressionResult()

	regDest = ""
	if (targetReg):
		assemblyString += scope.releaseRegister(targetReg, indentLevel=indentLevel)
		regDest = targetReg
	else:
		regDest = scope.getFreeRegister()

	#Get left operand into register
	leftOperand = item.left
	assemblyTemp, leftOperandReg = operandToRegister(leftOperand, scope, indentLevel=indentLevel)
	assemblyString += assemblyTemp

	#Get right operand into register
	rightOperand = item.right
	assemblyTemp, rightOperandReg = operandToRegister(rightOperand, scope, indentLevel=indentLevel)
	assemblyString += assemblyTemp

	#Handler operators
	#<TODO>, handle unsigned operands
	operator = item.op

	if (operator == "*"):
		assemblyString += "{}mul {}, {}, {}\n".format(indentString, regDest, leftOperandReg, rightOperandReg)
	elif (operator == "/"):
		assemblyString += "{}div {}, {}, {}\n".format(indentString, regDest, leftOperandReg, rightOperandReg)
	elif (operator == "%"):
		assemblyString += "{}rem {}, {}, {}\n".format(indentString, regDest, leftOperandReg, rightOperandReg)
	elif (operator == "+"):
		assemblyString += "{}add {}, {}, {}\n".format(indentString, regDest, leftOperandReg, rightOperandReg)
		#<TODO> use addi if one operand is a small constant
	elif (operator == "-"):
		assemblyString += "{}sub {}, {}, {}\n".format(indentString, regDest, leftOperandReg, rightOperandReg)
		#<TODO> use addi if one operand is a small constant

	#Free temp constant registers
	if isinstance(leftOperand, c_ast.Constant):
		assemblyString += scope.releaseRegister(leftOperandReg, indentLevel=indentLevel)
	if isinstance(rightOperand, c_ast.Constant):
		assemblyString += scope.releaseRegister(rightOperandReg, indentLevel=indentLevel)


	return assemblyString, resultVariableName


def convertFuncCallItem(item, scope, indentLevel=0):
	print(item)
	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	functionName = item.name.name

	argIndex = 0
	for argument in item.args.exprs:
		argumentRegister = "a{}".format(argIndex)

		if isinstance(argument, c_ast.ID):
			#Function argument is variable
			assemblyString += scope.moveVariable(argument.name, argumentRegister, indentLevel=indentLevel)
		elif isinstance(argument, c_ast.BinaryOp):
			#Function argument is binary op
			assemblyTemp, resultVariableName = convertBinaryOpItem(argument, scope, targetReg=argumentRegister, indentLevel=indentLevel)
			assemblyString += assemblyTemp
			pass
		else:
			assemblyString += "{}#UNSUPPORTED ITEM\n".format(indentString)

		argIndex += 1

	#Save return address to stack
	raVarName = "<SAVE>_ra"
	scope.addVariable(raVarName, register="ra", size=4, signed=True)
	assemblyString += scope.storeStack(raVarName, indentLevel=indentLevel)

	#Call function
	assemblyString += "{}j {}\n".format(indentString, functionName)

	#Restore ra
	assemblyString += scope.loadStack(raVarName, regDestOverride="ra", indentLevel=indentLevel)

	return assemblyString


def convertReturnItem(item, scope, indentLevel=0):
	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	if isinstance(item.expr, c_ast.ID):
		#Return variable
		variableName = item.expr.name
		currentRegister = scope.getRegisterLocation(variableName)

		if (not currentRegister):
			#variable on stack. Load into a0
			pass
			#assemblyString += scope.loadStack(variableName, regDestOverride="a0", indentLevel=indentLevel)
		else:
			#variable in register. Move into a0
			assemblyString += scope.moveVariable(variableName, "a0", indentLevel=indentLevel)

		assemblyString += "{}j ra\n".format(indentString)

	elif isinstance(item.expr, c_ast.FuncCall):
		#Call function, then return result
		assemblyString += convertFuncCallItem(item.expr, scope, indentLevel=indentLevel)
		assemblyString += "{}j ra\n".format(indentString)

	else:
		assemblyString += "{}#UNSUPPORTED ITEM\n".format(indentString)


	return assemblyString



def convertAstItem(item, scope, indentLevel=0):
	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	if isinstance(item, c_ast.Compound):
		for subItem in item.block_items:
			assemblyString += convertAstItem(subItem, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.If):
		assemblyString += convertIfItem(item, scope, indentLevel=indentLevel)
	elif isinstance(item, c_ast.Return):
		assemblyString += convertReturnItem(item, scope, indentLevel=indentLevel)
	else:
		assemblyString += "{}#UNSUPPORTED ITEM\n".format(indentString)
		

	return assemblyString

def covertFuncToAssembly(funcDef):
	'''
	Converts the funcDef node into an assembly snippet. Adds asm string as object variable funcDef.coord
	'''
	assemblyString = ""
	scope = scopeController(funcDef.decl.name)

	#Function label
	assemblyString += "{}:\n".format(funcDef.decl.name)

	#Add input variables too function scope
	if (funcDef.decl.type.args):
		inputParameters = funcDef.decl.type.args.params

		argIndex = 0
		for arg in inputParameters:
			registerName = "a{}".format(argIndex)
			scope.addVariable(arg.name, register=registerName,varType=arg.type.type.names, size=4, signed=True)

			argIndex += 1

	#Write function body
	assemblyString += convertAstItem(funcDef.body, scope, indentLevel=1)

	#Return to caller
	assemblyString += "\tj ra\n"

	funcDef.coord = assemblyString  #Borrow coord variable, since it seems to be unused by pycparser


if __name__ == '__main__':
	filename = "/home/jose/Documents/gitRepos/scratchComputer/testCode/c_Code/main.c"
	ast = parse_file(filename, use_cpp=True)
	definedFunctions = {}
	globalVarDelcarations = []
	definedFunctions, globalVarDelcarations = getFunctionDefinitions(ast)
	
	for functionName in definedFunctions:
		funcDef = definedFunctions[functionName]
		#print(functionName)
		#print(funcDef)
		covertFuncToAssembly(funcDef)
		print(funcDef.coord)
		#break

	sys.exit()




	defList = []
	the_dict = {}
	invoke_dict = {}
	
	extract_funcDef(ast,defList)
	# print(len(defList))
	show_deflist(defList)
	nameList = [item.decl.name for item in defList]
	for name in nameList:
		show_func_defs(ast,name,the_dict,invoke_dict)
	# parser(filename)

	print('====Ref_dict====')
	for k,v in the_dict.items():
		print('{}:{}'.format(k,v))

	print('====Invoke_dict====')
	for k,v in invoke_dict.items():
		print('{}:{}'.format(k,v))