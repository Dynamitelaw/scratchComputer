import codeObjects as cobj


def preprocessCFile(filepath):
	'''
	temp
	'''
	codeLines = []

	cFile = open(filepath, "r")

	cLine = " "
	lineNumber = 0
	longComment = False
	while (cLine):
		#Filter long comments 
		longComment_Start = cLine.find("/*")
		if (longComment_Start != -1):
			#Start of a long comment
			longComment = True

		longComment_End = cLine.find("*/")
		if (longComment_End != -1):
			#End of a long comment
			longComment = False
			cLine = cLine[longComment_End+2:]

		if (not longComment):
			#Filter comments
			commentIndex = cLine.find("//")
			if (commentIndex != -1):
				cLine = cLine[:commentIndex]

			#Trim whitespace
			cLine = cLine.strip().rstrip()
			codeStart = -1
			for index in range(0,len(cLine)):
				character = cLine[index]
				if ((character != " ") and (character != "\t")):
					codeStart = index
					cLine = cLine[index:]
					break
			if (codeStart == -1):
				#no code on this line. Move on to next
				cLine = cFile.readline()
				lineNumber += 1
				continue
			else:
				codeLines.append((cLine, lineNumber))
				cLine = cFile.readline()
				lineNumber += 1
		else:
			cLine = cFile.readline()
			lineNumber += 1

	cFile.close()

	return codeLines

def parseCLines(cLines, functionObjects=[]):
	'''
	Parses lines of c code into a program structure
	'''

	for lineTuple in cLines:
		code = lineTuple[0]
		lineNumber = lineTuple[1]

		identifier = code.split(" ")[0]




filePath = "/home/jose/Documents/gitRepos/scratchComputer/testCode/c_Code/main.c"
codeLines = preprocessCFile(filePath)

for line in codeLines:
	print(line)


#https://raw.githubusercontent.com/bisqwit/compiler_series/master/ep1/jit-conj-parser1.png