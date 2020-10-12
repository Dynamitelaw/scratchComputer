import copy
import os

from pycparser import c_parser, c_ast, parse_file, c_generator
import compGlobals as globals


class dataElement:
	'''
	Used to represent a data element stored in the .data section of assembly file
	'''
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
			elementSize = globals.typeSizeDictionary[elementType]

			returnVar = [arrayLength * elementSize, [elementSize]]
			return returnVar
		elif isinstance(arrayType, c_ast.ArrayDecl):
			subArraySize, subElementSize = getArraySize(arrayType)
			returnVar = [arrayLength * subArraySize, [subArraySize]+subElementSize]
			return returnVar
		else:
			raise Exception("Input declaration must be a c_ast.ArrayDecl object")


class structDef:
	'''
	This class is used to represent all defined structures
	This acts as a place to store:
		struct name
		struct size
		member items
		member offsets
	'''
	class structMember:
		def __init__(self, name, size, subDimensions=None, memberType=None, structType=None, offset=None):
			self.name = name
			self.size = size
			self.subDimensions = subDimensions
			self.type = memberType
			self.structType = structType  #for use if a member is another structure
			self.offset = offset

		def __str__(self):
			tempDict = {}
			tempDict["name"] = self.name
			tempDict["type"] = self.type
			tempDict["size"] = self.size
			tempDict["subDimensions"] = self.subDimensions
			tempDict["offset"] = self.offset
			tempDict["structType"] = self.structType

			return str(tempDict)
		def __repr__(self):
			tempDict = {}
			tempDict["name"] = self.name
			tempDict["type"] = self.type
			tempDict["size"] = self.size
			tempDict["subDimensions"] = self.subDimensions
			tempDict["offset"] = self.offset
			tempDict["structType"] = self.structType

			return str(tempDict)

	
	def __init__(self, structItem):
		globals.cFileCoord = structItem.coord

		self.name = structItem.name
		self.members = {}

		#Instantiate structMember objects for all members
		membersTemp = []  #[(size, name), ...]

		for declItem in structItem.decls:
			if isinstance(declItem.type, c_ast.ArrayDecl):
				name = declItem.name
				size, subDimensions = getArraySize(declItem.type)
				membersTemp.append((size, name))

				self.members[name] = self.structMember(name, size, subDimensions=subDimensions)
			elif isinstance(declItem.type.type, c_ast.IdentifierType):
				name = declItem.name
				varType = " ".join(declItem.type.type.names)
				size = globals.typeSizeDictionary[varType]
				membersTemp.append((size, name))

				self.members[name] = self.structMember(name, size)
			elif isinstance(declItem.type.type, c_ast.Struct):
				name = declItem.name
				structType = declItem.type.type.name
				size = globals.typeSizeDictionary[structType]
				membersTemp.append((size, name))

				self.members[name] = self.structMember(name, size, structType=structType)
				
				#This is a nested struct. Copy over subMembers from child struct definition
				subMembers = globals.structDictionary[structType].members
				for subName in subMembers:
					memberName = "{}.{}".format(name, subName)
					subSize = globals.structDictionary[structType].members[subName].size
					membersTemp.append((subSize, memberName))

			else:
				raise Exception("Unsupported decl in structure | {}\n{}".format(globals.cFileCoord, declItem))

		#Determine struct size and offsets of primary members
		membersTemp.sort(reverse=True)
		self.size = 0
		nestedReferences = []

		for element in membersTemp:
			size, name = element
			if ("." in name):
				#This is a reference to a nested struct member. Get offset later. Do not include in total size
				nestedReferences.append(name)
			else:
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

		#Determine offsets of nested submembers
		for name in nestedReferences:
			subRootName = name.split(".")[0]
			subMemberName = ".".join(name.split(".")[1:])
			rootOffset = self.members[subRootName].offset
			rootType = self.members[subRootName].structType
			subMemberOffset = globals.structDictionary[rootType].members[subMemberName].offset
			offset = rootOffset + subMemberOffset
			
			self.members[name] = copy.deepcopy(globals.structDictionary[rootType].members[subMemberName])
			self.members[name].offset = offset


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
		if (globals.cFileCoord):
			self.coords.append({"file": os.path.abspath(globals.cFileCoord.file.replace(".temp","")), "lineNum": globals.cFileCoord.line})
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

