import copy 

from pycparser import c_parser, c_ast, parse_file, c_generator
import compGlobals as globals
from compScopeController import *
from compClasses import *


def getArrayElementPointer(arrayRef, scope, indentLevel=0):
	'''
	Get a pointer to an array element into a register

	Returns:
		<tuple> ( <instructionList> instructions , <str> pointerRegister , <int> size, <str> pointerVariableName)
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Get name of array root
	arrayRootName = arrayRef.name
	while (not isinstance(arrayRootName, str)):
		arrayRootName = arrayRootName.name

	subscript = arrayRef.subscript

	#Get pointer to start of array
	pointerVariableName  = None
	rootVariable = scope.getVariable(arrayRootName)
	if (isinstance(rootVariable.type, c_ast.PtrDecl)):
		instructions += scope.loadStack(arrayRootName, indentLevel=indentLevel)
		currentPointerRegister = scope.getRegisterLocation(arrayRootName)  #we don't want to modify this, so we will copy to another register
		instructionsTemp, arrayPointerReg = scope.getFreeRegister(preferTemp=True, tag="arrayPointerReg", indentLevel=indentLevel)
		instructions += instructionsTemp
		instructions.append("{}mv {}, {}".format(indentString, arrayPointerReg, currentPointerRegister))
	else:
		instructionsTemp, arrayPointerReg, pointerVariableName = scope.getPointer(arrayRootName, indentLevel=indentLevel)
		instructions += instructionsTemp

	#Determine element length and starting offset from pointer
	subElementSize = None
	elementLength = None  #Size of root element in array

	if isinstance(rootVariable.type, c_ast.ArrayDecl):
		subElementSize = rootVariable.subElementSize
		elementLength = rootVariable.subElementSize[-1]
	elif isinstance(rootVariable.type, c_ast.PtrDecl):
		elementLength = globals.typeSizeDictionary[" ".join(rootVariable.type.type.type.names)]
		subElementSize = [elementLength]
	elif isinstance(rootVariable.type.type, c_ast.Struct):
		structDefObject = globals.structDictionary[rootVariable.type.type.name]
		#Get member name
		tempRef = copy.deepcopy(arrayRef)
		while isinstance(tempRef, c_ast.ArrayRef):
			tempRef = tempRef.name

		memberName = tempRef.field.name
		while (not isinstance(tempRef.name, c_ast.ID)):
			tempRef = tempRef.name
			memberName = tempRef.field.name + "." + memberName

		#Get element length
		subElementSize = structDefObject.members[memberName].subDimensions
		elementLength = structDefObject.members[memberName].subDimensions[-1]

		#Increase pointer reg by member offset
		memberOffset = structDefObject.members[memberName].offset
		instructions.append("{}addi {}, {}, {}".format(indentString, arrayPointerReg, arrayPointerReg, memberOffset))  #<TODO> handle offsets too large for immediate
	else:
		raise Exception("UNSUPPORTED ARRAY ROOT TYPE | {}\n{}".format(globals.cFileCoord, rootVariable))


	#Determine subscript depth (>1 for multi-dimensional arrays)
	subscriptDepth = 1
	tempArrayRef = copy.deepcopy(arrayRef)
	while isinstance(tempArrayRef.name, c_ast.ArrayRef):
		subscriptDepth += 1
		tempArrayRef = tempArrayRef.name

	#Increase root pointer by offset
	for i in range(subscriptDepth, 0, -1):
		#Get size of iTh dimenstion
		subSize = subElementSize[-1*i]

		#Get correct subscript item
		tempArrayRef = copy.deepcopy(arrayRef)
		for j in range(0, i-1, 1):
			tempArrayRef = tempArrayRef.name

		subscript = tempArrayRef.subscript

		#Get pointer offset from subscript into register
		instructionsTemp, offsetIndex = operandToRegister(subscript, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		instructionsTemp, elementLengthReg = scope.getFreeRegister(preferTemp=True, tag="elementLength_dim{}".format(subscriptDepth-i), indentLevel=indentLevel)
		instructions += instructionsTemp
		instructions.append("{}addi {}, zero, {}".format(indentString, elementLengthReg, subSize))  #<TODO> handle element lengths too long for immediate
		offsetReg = elementLengthReg
		instructions.append("{}mul {}, {}, {}".format(indentString, offsetReg, offsetIndex, elementLengthReg))

		#Combine offset and array pointer
		elementPointerReg = arrayPointerReg
		instructions.append("{}add {}, {}, {}".format(indentString, elementPointerReg, arrayPointerReg, offsetReg))

		#Release offset register
		instructions += scope.releaseRegister(offsetReg, indentLevel=indentLevel)

	return instructions, elementPointerReg, elementLength, pointerVariableName


def getStructMemberPointer(structRef, scope, indentLevel=0):
	'''
	Get a pointer to a struct member into a register

	Returns:
		<tuple> ( <instructionList> instructions , <str> pointerRegister , <int> size, <str> pointerVariableName)
	'''
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])

	#Get name of root struct
	structName = structRef.name
	while (not isinstance(structName, str)):
		structName = structName.name

	#Get pointer to start of struct
	pointerVariableName = None
	structVariable = scope.getVariable(structName)
	if (isinstance(structVariable.type, c_ast.PtrDecl)):
		structVariable = structVariable.type
		instructions += scope.loadStack(structName, indentLevel=indentLevel)
		currentPointerRegister = scope.getRegisterLocation(structName)  #we don't want to modify this, so we will copy to another register
		instructionsTemp, structPointerReg = scope.getFreeRegister(preferTemp=True, tag="structMemberPointerReg", indentLevel=indentLevel)
		instructions += instructionsTemp
		instructions.append("{}mv {}, {}".format(indentString, structPointerReg, currentPointerRegister))
	else:
		instructionsTemp, structPointerReg, pointerVariableName = scope.getPointer(structName, indentLevel=indentLevel)
		instructions += instructionsTemp

	#Get member name
	tempRef = copy.deepcopy(structRef)
	memberName = tempRef.field.name
	while (not isinstance(tempRef.name, c_ast.ID)):
		tempRef = tempRef.name
		memberName = tempRef.field.name + "." + memberName

	#Get offset of member
	structDefObject = globals.structDictionary[structVariable.type.type.name]
	offset = structDefObject.members[memberName].offset

	#Combine offset and struct pointer
	memberPointerReg = structPointerReg
	if (offset > 0):
		instructions.append("{}addi {}, {}, {}".format(indentString, memberPointerReg, structPointerReg, offset))  #<TODO> handle offsets too large for immediate

	#Get member size
	size = structDefObject.members[memberName].size

	return instructions, memberPointerReg, size, pointerVariableName


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
	globals.cFileCoord = operandItem.coord


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
			if (targetReg):
				operandReg = targetReg
				instructions.append("{}mv {}, zero".format(indentString, operandReg))
			else:
				operandReg = "zero"
		elif (value < 2048) and (value >= -2048):
			#Value is small enough for addi
			if (targetReg):
				instructionsTemp, operandReg = scope.getFreeRegister(regOverride=targetReg, tag="CONSTANT", indentLevel=indentLevel)
				instructions += instructionsTemp
			else:
				instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, tag="CONSTANT", indentLevel=indentLevel)
				instructions += instructionsTemp
			instructions.append("{}addi {}, zero, {}".format(indentString, operandReg, value))
		else:
			#Too large for immediate. Build using LUI+ADDI
			#<TODO> handle non-ints
			upperValue = None
			lowerValue = None
			if (value > 0):
				upperValue = int(value/4096)
				lowerValue = value%4096
			else:
				negativePortion = -1*(2**32)
				positivePortion = value - negativePortion
				lowerValue = positivePortion%4096
				upperValue = int(positivePortion/4096) + 2**20
			#Load into register
			instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, tag="CONSTANT", indentLevel=indentLevel, regOverride=targetReg)
			instructions += instructionsTemp
			if (int(lowerValue/2048) == 1):
				# Sad :(  <TODO> don't do this awefulness when we have better instruction support
				#Get lower val into register
				instructions.append("{}lui {}, 1  #Loading val {}".format(indentString, operandReg, value))
				instructions.append("{}addi {}, {}, {}".format(indentString, operandReg, operandReg, lowerValue))
				if (upperValue > 0):
					#Get upper val into temp register
					instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, tag="largeValTemp", indentLevel=indentLevel)
					instructions += instructionsTemp
					instructions.append("{}lui {}, {}".format(indentString, tempRegister, upperValue))
					#Combine them
					instructions.append("{}add {}, {}, {}".format(indentString, operandReg, operandReg, tempRegister))

					instructions += scope.releaseRegister(tempRegister, indentLevel=indentLevel)
			else:
				instructions.append("{}lui {}, {} #Loading val {}".format(indentString, operandReg, upperValue, value))
				instructions.append("{}addi {}, {}, {}".format(indentString, operandReg, operandReg, lowerValue))

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
			instructionsTemp, operandReg = scope.getFreeRegister(regOverride=targetReg, tag="funcResult", indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}mv {}, a0".format(indentString, operandReg))
	elif isinstance(operandItem, c_ast.ArrayRef):
		#Get pointer to array element
		instructionsTemp, pointerRegister, elementSize, pointerVariableName = getArrayElementPointer(operandItem, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		#Load element into operandReg
		instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, tag="arrayElement", regOverride=targetReg, indentLevel=indentLevel)
		instructions += instructionsTemp

		if (elementSize == 4):
			instructions.append("{}lw {}, 0({})".format(indentString, operandReg, pointerRegister)) #<TODO> handle unsigned values
		elif (elementSize == 2):
			instructions.append("{}lh {}, 0({})".format(indentString, operandReg, pointerRegister))
		elif (elementSize == 1):
			instructions.append("{}lb {}, 0({})".format(indentString, operandReg, pointerRegister))
		#Release pointer register
		instructions += scope.releaseRegister(pointerRegister, indentLevel=indentLevel)
	elif isinstance(operandItem, c_ast.StructRef):
		#Get pointer to struct member
		instructionsTemp, pointerRegister, memberSize, pointerVariableName = getStructMemberPointer(operandItem, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Load member into operandReg
		instructionsTemp, operandReg = scope.getFreeRegister(preferTemp=True, tag="structMember", regOverride=targetReg, indentLevel=indentLevel)
		instructions += instructionsTemp

		if (memberSize == 4):
			instructions.append("{}lw {}, 0({})".format(indentString, operandReg, pointerRegister)) #<TODO> handle unsigned values
		elif (memberSize == 2):
			instructions.append("{}lh {}, 0({})".format(indentString, operandReg, pointerRegister))
		elif (memberSize == 1):
			instructions.append("{}lb {}, 0({})".format(indentString, operandReg, pointerRegister))
		#Release pointer register
		instructions += scope.releaseRegister(pointerRegister, indentLevel=indentLevel)
	else:
		errorStr = "UNSUPPORTED OPERAND | {}\n{}".format(globals.cFileCoord, operandItem)
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
	globals.cFileCoord = item.coord

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
			instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, tag="negation", indentLevel=indentLevel)
			instructions += instructionsTemp

		#Get or create variable name for result of negation
		if (targetVariableName):
			instructions += scope.addVariable(targetVariableName, size=resultSize, register=regDest, varType=resultType, indentLevel=indentLevel)

			resultVariableName = targetVariableName
		else:
			instructionsTemp, resultVariableName = scope.createExpressionResult(register=regDest, indentLevel=indentLevel)
			instructions += instructionsTemp

		#Negate operand
		instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, tag="temp", indentLevel=indentLevel)
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
				instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, tag="logicalInvert", indentLevel=indentLevel)
				instructions += instructionsTemp

			#Logically invert operand
			instructions.append("{}sltu {}, {}, zero".format(indentString, regDest, operandReg))

	elif (operator == "&"):
		#Get memory location of variable
		if isinstance(item.expr, c_ast.StructRef):
			instructionsTemp, regDest, size, resultVariableName= getStructMemberPointer(item.expr, scope, indentLevel=indentLevel)
			instructions += instructionsTemp
		elif isinstance(item.expr, c_ast.ArrayRef):
			instructionsTemp, regDest, size, resultVariableName = getArrayElementPointer(item.expr, scope, indentLevel=indentLevel)
			instructions += instructionsTemp
		else:
			instructionsTemp, regDest, resultVariableName = scope.getPointer(item.expr.name, regDestOverride=targetReg, indentLevel=indentLevel)
			instructions += instructionsTemp
	elif (operator == "*"):
		if isinstance(item.expr, c_ast.ID):
			#Get memory location of variable
			instructions += scope.loadStack(item.expr.name, indentLevel=indentLevel)
			regPointer = scope.getRegisterLocation(item.expr.name)

			#Load value from memory
			#<TODO> handle values smaller than 4 bytes
			instructionsTemp, regDest = scope.getFreeRegister(regOverride=targetReg, tag="dereference", preferTemp=True, indentLevel=indentLevel)
			instructions += instructionsTemp

			varSize = scope.variableDict[item.expr.name].size
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
	globals.cFileCoord = item.coord

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
			instructionsTemp, regDest = scope.getFreeRegister(preferTemp=True, tag="binaryOp", indentLevel=indentLevel)
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
			instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, tag="temp", indentLevel=indentLevel)
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
			instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, tag="temp", indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions.append("{}slt {}, {}, {}".format(indentString, regDest, leftOperandReg, rightOperandReg))
			instructions.append("{}slt {}, {}, {}".format(indentString, tempRegister, rightOperandReg, leftOperandReg))
			instructions.append("{}add {}, {}, {}".format(indentString, regDest, regDest, tempRegister))
			instructions += scope.releaseRegister(tempRegister)
	elif (operator == "&&"):
		if (branch):
			instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, tag="temp", indentLevel=indentLevel)
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

	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	globals.cFileCoord = item.coord

	#Handle condition branching
	onTrueLabel = "true_{}".format(globals.ifCounter)
	onFalseLabel = "false_{}".format(globals.ifCounter)
	ifExitLabel = "ifElseExit_{}".format(globals.ifCounter)
	globals.ifCounter += 1

	conditionItem = item.cond
	if isinstance(conditionItem, c_ast.BinaryOp):
		instructionsTemp, conditionVariableName = convertBinaryOpItem(conditionItem, scope, branch=onTrueLabel, indentLevel=indentLevel)
		instructions += instructionsTemp
	elif isinstance(conditionItem, c_ast.UnaryOp):
		instructionsTemp, conditionVariableName = convertUnaryOpItem(conditionItem, scope, branch=onTrueLabel, indentLevel=indentLevel)
		instructions += instructionsTemp
	elif isinstance(conditionItem, c_ast.ArrayRef):
		instructionsTemp, conditionValReg = operandToRegister(conditionItem, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		instructions.append("{}bne {}, zero, {}".format(indentString, conditionValReg, onTrueLabel))
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
	globals.cFileCoord = item.coord

	functionName = item.name.name

	#Check for inline assembly
	if (functionName == "asm") or ((functionName == "_asm_")):
		inlineAssembly = item.args.exprs[0].value
		inlineAssembly = inlineAssembly.replace("\"","")
		instructions.append("{}{}".format(indentString, inlineAssembly))

		return instructions

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
					instructionsTemp, tempSaveReg = scope.getFreeRegister(tempsAllowed=False, tag="argumentSave", indentLevel=indentLevel)
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
		elif isinstance(argument, c_ast.ArrayRef):
			#Function argument is a contant
			instructionsTemp, operandReg = operandToRegister(argument, scope, targetReg=argumentRegister, indentLevel=indentLevel)
			instructions += instructionsTemp
		elif isinstance(argument, c_ast.StructRef):
			#Function argument is a contant
			instructionsTemp, operandReg = operandToRegister(argument, scope, targetReg=argumentRegister, indentLevel=indentLevel)
			instructions += instructionsTemp

		else:
			raise Exception("UNSUPPORTED ITEM | convertFuncCallItem\n{}".format(item))

		argIndex += 1

	#Save return address to stack
	instructions += scope.saveReturnAddress(indentLevel=indentLevel)

	#Save temps
	instructions += scope.saveTemps(indentLevel=indentLevel)

	#Align stack
	instructions += scope.alignStack(indentLevel=indentLevel)

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
	globals.cFileCoord = item.coord

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
			leftSize = 4;

			#Get pointer into register
			if isinstance(leftOperand.expr, c_ast.ID):
				#Pointer is a variable
				instructions += scope.loadStack(leftOperand.expr.name, indentLevel=indentLevel)
				pointerRegister = scope.getRegisterLocation(leftOperand.expr.name)
			elif isinstance(leftOperand.expr, c_ast.Constant):
				#Pointer is a constant
				instructionsTemp, pointerRegister = scope.getFreeRegister(preferTemp=True, tag="pointer", indentLevel=indentLevel)
				instructions += instructionsTemp

				pointerValue = int(leftOperand.expr.value)
				if (pointerValue < 2048):
					#Pointer small enough for immediate
					instructions.append("{}addi {}, zero, {}".format(indentString, pointerRegister, pointerValue))
				else:
					#Pointer value too large. Add to data segment
					dataType = "pointer"
					dataLabelName = "data_{}_{}".format(dataType, pointerValue)
					globals.dataSegment[dataLabelName] = dataElement(dataLabelName, value=pointerValue, size=4)
					instructions.append("{}lw {}, {}".format(indentString, pointerRegister, dataLabelName))
			else:
				raise Exception("UNSUPPORTED DEREFERENCE TYPE | {}".format(globals.cFileCoord))

	#Handle array element references
	isArrayReference = False

	if isinstance(leftOperand, c_ast.ArrayRef):
		isArrayReference = True

		#Get pointer to array element
		instructionsTemp, pointerRegister, leftSize, pointerVariableName = getArrayElementPointer(leftOperand, scope, indentLevel=indentLevel)
		instructions += instructionsTemp
		#Load element into leftValReg
		instructionsTemp, leftValReg = scope.getFreeRegister(preferTemp=True, tag="assignLeft", indentLevel=indentLevel)
		instructions += instructionsTemp

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

		#Get pointer to struct member
		instructionsTemp, pointerRegister, leftSize, pointerVariableName = getStructMemberPointer(leftOperand, scope, indentLevel=indentLevel)
		instructions += instructionsTemp

		#Load member into leftValReg
		instructionsTemp, leftValReg = scope.getFreeRegister(preferTemp=True, tag="assignLeft", indentLevel=indentLevel)
		instructions += instructionsTemp

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
		else:
			raise Exception("leftSize is not defined | convertAssignmentItem")
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
	globals.cFileCoord = item.coord

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
			#Too large for immediate. Build using LUI+ADDI
			#<TODO> handle non-ints
			upperValue = None
			lowerValue = None
			if (value > 0):
				upperValue = int(value/4096)
				lowerValue = value%4096
			else:
				negativePortion = -1*(2**32)
				positivePortion = value - negativePortion
				lowerValue = positivePortion%4096
				upperValue = int(positivePortion/4096) + 2**20

			#Load into register
			if (int(lowerValue/2048) == 1):
				# Sad :(
				#Get lower val into register
				instructions.append("{}lui a0, 1 #Loading val {}".format(indentString, value))
				instructions.append("{}addi a0, a0, {}".format(indentString, lowerValue))
				if (upperValue > 0):
					#Get upper val into temp register a2
					instructions.append("{}lui a2, {}".format(indentString, upperValue))
					#Combine them
					instructions.append("{}add a0, a0, a2".format(indentString))
			else:
				instructions.append("{}lui a0, {} #Loading val {}".format(indentString, upperValue, value))
				instructions.append("{}addi a0, a0, {}".format(indentString, lowerValue))

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
	globals.cFileCoord = item.coord

	variableName = item.name

	if (item.init):
		#Declared with initial value
		if isinstance(item.init, c_ast.Constant):
			#Initialized variable to a constant value
			instructionsTemp, destinationRegister = scope.getFreeRegister(tag="declare", indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions += scope.addVariable(variableName, register=destinationRegister, varType=item.type, signed=True, indentLevel=indentLevel)


			value = int(item.init.value) #<TODO> Handle floats and doubles
			if (value < 2048) and (value >= -2048):
				#Value is small enough for addi
				instructions.append("{}addi {}, zero, {}".format(indentString, destinationRegister, value))
			else:
				#Too large for immediate. Build using LUI+ADDI
				#<TODO> handle non-ints
				upperValue = None
				lowerValue = None
				if (value > 0):
					upperValue = int(value/4096)
					lowerValue = value%4096
				else:
					negativePortion = -1*(2**32)
					positivePortion = value - negativePortion
					lowerValue = positivePortion%4096
					upperValue = int(positivePortion/4096) + 2**20
				
				#Load into register
				if (int(lowerValue/2048) == 1):
					# Sad :(  <TODO> don't do this awefulness when we have better instruction support
					#Get lower val into register
					instructions.append("{}lui {}, 1  #Loading val {}".format(indentString, destinationRegister, value))
					instructions.append("{}addi {}, {}, {}".format(indentString, destinationRegister, destinationRegister, lowerValue))
					if (upperValue > 0):
						#Get upper val into temp register
						instructionsTemp, tempRegister = scope.getFreeRegister(preferTemp=True, tag="largeValTemp", indentLevel=indentLevel)
						instructions += instructionsTemp
						instructions.append("{}lui {}, {}".format(indentString, tempRegister, upperValue))
						#Combine them
						instructions.append("{}add {}, {}, {}".format(indentString, destinationRegister, destinationRegister, tempRegister))

						instructions += scope.releaseRegister(tempRegister, indentLevel=indentLevel)
				else:
					instructions.append("{}lui {}, {} #Loading val {}".format(indentString, destinationRegister, upperValue, value))
					instructions.append("{}addi {}, {}, {}".format(indentString, destinationRegister, destinationRegister, lowerValue))

		elif isinstance(item.init, c_ast.ID):
			#Initialized variable is set to another variable
			#<TODO>
			raise Exception("TODO, add support for variable inits\n{}".format(item))

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
				instructionsTemp, pointerReg, pointerVariableName = scope.getPointer(variableName, indentLevel=indentLevel)
				instructions += instructionsTemp

				for arrayIndex in range(0, len(item.init.exprs)):
					expression = item.init.exprs[arrayIndex]
					if isinstance(expression, c_ast.Constant):
						#Get constant into a register
						instructionsTemp, tempReg = scope.getFreeRegister(preferTemp=True, tag="temp", indentLevel=indentLevel)
						instructions += instructionsTemp

						instructionsTemp, valueReg = operandToRegister(expression, scope, targetReg=tempReg, indentLevel=indentLevel)
						instructions += instructionsTemp

						#Determine pointer offset
						elementSize = globals.typeSizeDictionary[expression.type]
						pointerOffset = elementSize * arrayIndex

						#Store value onto stack
						if (elementSize == 4):
							instructions.append("{}sw {}, {}({})".format(indentString, valueReg, pointerOffset, pointerReg))
						elif (elementSize == 2):
							instructions.append("{}sh {}, {}({})".format(indentString, valueReg, pointerOffset, pointerReg))
						elif (elementSize == 1):
							instructions.append("{}sb {}, {}({})".format(indentString, valueReg, pointerOffset, pointerReg))
						else:
							raise Exception("UNSUPPORTED ARRAY ELEMENT SIZE | {}".format(globals.cFileCoord))

						#Release temp registers
						instructions += scope.releaseRegister(tempReg)
						instructions += scope.releaseRegister(valueReg)
					else:
						raise Exception("UNSUPPORTED INITIAL VALUE FOR ARRAY | {}".format(globals.cFileCoord))

				instructions += scope.releaseRegister(pointerReg)
			else:
				raise Exception("Cannot initialize non-array to a list of values | {}".format(globals.cFileCoord))

		elif isinstance(item.init, c_ast.ArrayRef):
			#Get destination register
			instructionsTemp, destinationRegister = scope.getFreeRegister(tag="declare", indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions += scope.addVariable(variableName, register=destinationRegister, varType=item.type, signed=True, indentLevel=indentLevel)

			#Get pointer to array element
			instructionsTemp, pointerRegister, size, pointerVariableName = getArrayElementPointer(item.init, scope, indentLevel=indentLevel)
			instructions += instructionsTemp

			#Load element into destination register
			if (size == 4):
				instructions.append("{}lw {}, 0({})".format(indentString, destinationRegister, pointerRegister)) #<TODO> handle unsigned values
			elif (size == 2):
				instructions.append("{}lh {}, 0({})".format(indentString, destinationRegister, pointerRegister))
			elif (size == 1):
				instructions.append("{}lb {}, 0({})".format(indentString, destinationRegister, pointerRegister))

		elif isinstance(item.init, c_ast.StructRef):
			#Get destination register
			instructionsTemp, destinationRegister = scope.getFreeRegister(tag="declare", indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions += scope.addVariable(variableName, register=destinationRegister, varType=item.type, signed=True, indentLevel=indentLevel)

			#Get pointer to struct element
			instructionsTemp, pointerRegister, size, pointerVariableName = getStructMemberPointer(item.init, scope, indentLevel=indentLevel)
			instructions += instructionsTemp

			#Load element into destination register
			if (size == 4):
				instructions.append("{}lw {}, 0({})".format(indentString, destinationRegister, pointerRegister)) #<TODO> handle unsigned values
			elif (size == 2):
				instructions.append("{}lh {}, 0({})".format(indentString, destinationRegister, pointerRegister))
			elif (size == 1):
				instructions.append("{}lb {}, 0({})".format(indentString, destinationRegister, pointerRegister))

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
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	globals.cFileCoord = item.coord

	#Initialize for loop counting variable
	if isinstance(item.init, c_ast.DeclList):
		for declareItem in item.init.decls:
			instructionsTemp, variableName = convertDeclItem(declareItem, scope, indentLevel=indentLevel)
			instructions += instructionsTemp
			instructions += scope.storeStack(variableName, indentLevel=indentLevel)
	else:
		raise Exception("UNSUPPORTED ITEM | convertForItem\n{}".format(item.init))

	#For loop start/end labels
	startLabel = "forLoopStart_{}".format(globals.forCounter)
	endLabel = "forLoopEnd_{}".format(globals.forCounter)
	bodyLabel = "forLoopBody_{}".format(globals.forCounter)
	globals.forCounter += 1

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
	instructions = instructionList(scope)
	indentString = "".join(["\t" for i in range(indentLevel)])
	globals.cFileCoord = item.coord

	#While loop start/end labels
	startLabel = "whileLoopStart_{}".format(globals.whileCounter)
	endLabel = "whileLoopEnd_{}".format(globals.whileCounter)
	bodyLabel = "whileLoopBody_{}".format(globals.whileCounter)
	globals.whileCounter += 1

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


def convertAstItem(item, scope, indentLevel=0, freeTempRegisters=False):
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
			instructions += convertAstItem(subItem, scope, indentLevel=indentLevel, freeTempRegisters=freeTempRegisters)
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
	elif isinstance(item, c_ast.FuncCall):
		instructions += convertFuncCallItem(item, scope, indentLevel=indentLevel)
	else:
		raise Exception("UNSUPPORTED ITEM | convertAstItem\n{}".format(item))
		
	if (freeTempRegisters):
		scope.regexReleaseVariable("<TAG_", indentLevel=indentLevel)

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
	instructions += convertAstItem(funcDef.body, scope, indentLevel=1, freeTempRegisters=True)

	#Restore save variables
	instructions += scope.restoreSaves(indentLevel=1)

	#Deallocate local stack
	instructions += scope.deallocateScope(indentLevel=1)

	#Return to caller
	instructions.append("\tjr ra")

	funcDef.coord = instructions  #Borrow coord variable, since it seems to be unused by pycparser