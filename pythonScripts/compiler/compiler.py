from __future__ import print_function
import sys
import re
import json
from pycparser import c_parser, c_ast, parse_file, c_generator


#Global vars
g_whileCounter = 0
g_forCounter = 0
g_ifCounter = 0
g_variableNameCoutners = {}


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


def convertBodyItem(item, registerMapping, indentLevel=0):
	global g_ifCounter

	assemblyString = ""
	indentString = "".join(["\t" for i in range(indentLevel)])

	if isinstance(item, c_ast.If):
		#Translate if else block
		leftOperand = item.cond.left
		rightOperand = item.cond.right

		#Get left operand ready
		leftOperandReg = ""
		if isinstance(leftOperand, c_ast.ID):
			#Left operand is variable
			leftOperandReg = registerMapping[leftOperand.name]["register"]
		elif isinstance(leftOperand, c_ast.Constant):
			#Left operand is contant
			value = None
			if (leftOperand.type == "int"):
				value = int(leftOperand.value)
			elif (leftOperand.type == "double"):
				value = float(leftOperand.value)
			elif (leftOperand.type == "float"):
				value = float(leftOperand.value)

			#Get operand into temp register
			if (value < 2048) and (value >= -2048):
				#Value is small enough for addi
				assemblyString += "{}addi t0, zero, {}\n".format(indentString, value)
				leftOperandReg = "t0"
			else:
				#Must load value from memory
				#<TODO>
				leftOperandReg = "t0"

		#Get right operand ready
		rightOperandReg = ""
		if isinstance(rightOperand, c_ast.ID):
			#Left operand is variable
			rightOperandReg = registerMapping[rightOperand.name]["register"]
		elif isinstance(rightOperand, c_ast.Constant):
			#Left operand is contant
			value = None
			if (rightOperand.type == "int"):
				value = int(rightOperand.value)
			elif (rightOperand.type == "double"):
				value = float(rightOperand.value)
			elif (rightOperand.type == "float"):
				value = float(rightOperand.value)

			#Get operand into temp register
			if (value == 0):
				rightOperandReg = "zero"
			elif ((value < 2048) and (value >= -2048)):
				#Value is small enough for addi
				assemblyString += "{}addi t0, zero, {}\n".format(indentString, value)
				rightOperandReg = "t1"
			else:
				#Must load value from memory
				#<TODO>
				rightOperandReg = "t1"

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

		#Contruct true/false code blocks
		assemblyString += "{}{}:\n".format(indentString, onTrueLabel)
		assemblyString += "{}\t#Do true stuff here\n".format(indentString)
		assemblyString += "{}j {}\n".format(indentString, ifExitLabel)

		assemblyString += "{}{}:\n".format(indentString, onFalseLabel)
		assemblyString += "{}\t#Do false stuff here\n".format(indentString)
		assemblyString += "{}j {}\n".format(indentString, ifExitLabel)

		assemblyString += "{}{}:\n".format(indentString, ifExitLabel)
		

	return assemblyString

def covertFuncToAssembly(funcDef):
	'''
	Converts the funcDef node into an assembly snippet. Adds asm string as object variable funcDef.coord
	'''
	assemblyString = ""

	#Function label
	assemblyString += "{}:\n".format(funcDef.decl.name)

	if (funcDef.decl.type.args):
		assemblyString += "\t#Input arg handling\n"
		#Save current value of s0 and s1 onto stack
		assemblyString += "\taddi sp, sp, -8\n"
		assemblyString += "\tsw s0, -4(sp)\n"
		assemblyString += "\tsw s1, 0(sp)\n"

		#Save function args a0 and a1 into s0, and s1
		assemblyString += "\tmv s0, a0\n"
		assemblyString += "\tmv s1, a1\n"

	#Map input argument to their registers
	registerMapping = {}
	if (funcDef.decl.type.args):
		inputParameters = funcDef.decl.type.args.params

		index = 0
		for arg in inputParameters:
			registerName = ""
			if (index < 2):
				registerName = "s{}".format(index)
			else:
				registerName = "a{}".format(index)

			registerMapping[arg.name] = {}
			registerMapping[arg.name]["register"] = registerName
			registerMapping[arg.name]["type"] = arg.type.type.names
			index += 1

	#print(registerMapping)

	#Do some function shit
	assemblyString += "\n\t#Function body\n"
	functionBody = funcDef.body.block_items

	for item in functionBody:
		assemblyString += convertBodyItem(item, registerMapping, indentLevel=1)

	#print(functionBody)
	

	if (funcDef.decl.type.args):
		#Restore s0/s1 from stack
		assemblyString += "\n\t#Restore save registers from stack\n"
		assemblyString += "\tlw s0, -4(sp)\n"
		assemblyString += "\tlw s1, 0(sp)\n"

	#Return to caller
	assemblyString += "\n\tj ra\n"

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