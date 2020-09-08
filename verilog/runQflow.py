import os
import sys
import argparse
import shutil


#Globals
g_includedFiles = []

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


def createMonolithicVerilog(outputFile, inputFile, sourceDirectory):
	'''
	Recursive function that generates a linked monolithic verilog file
	'''
	inline = " "

	while(inline):
		inline = inputFile.readline()
		if ("`include" in inline):
			newInputFilename = inline.replace("`include","").strip().rstrip().split("//")[0].replace("\"","")
			newInputFilepath = os.path.join(sourceDirectory, newInputFilename)

			#Insert file contents if not already included
			if not (newInputFilepath in g_includedFiles):
				g_includedFiles.append(newInputFilepath)
				newInputFile = open(newInputFilepath, "r")
				createMonolithicVerilog(outputFile, newInputFile, sourceDirectory)
				newInputFile.close()
		else:
			outputFile.write(inline)

	outputFile.write("\n")

	return


if __name__ == '__main__':
	#Read command line arguments
	helpdesc = '''
help yourself
'''

	parser = argparse.ArgumentParser(description = helpdesc)

	parser.add_argument("-rtl", action="store", dest="verilogPath", help="Filepath to top-level verilog")

	parser.add_argument("-synthesize", action="store_true", dest="synthesize", help="Include to run qflow synthesis")
	parser.add_argument("-sta", action="store_true", dest="sta", help="Include to run qflow static timing analysis")

	args = parser.parse_args()

	verilogPath = args.verilogPath
	synthesizeFlag = args.synthesize
	staFlag = args.sta
	
	if (not verilogPath):
		printColor("ERROR: -rtl <verilog_path> arg required", color=COLORS.ERROR)
		sys.exit()

	#Create output directory and/or remove old sythensis
	printColor("Generating qflow directories\n", color=COLORS.UNDERLINE)

	sourceDirectory, fileName = os.path.split(verilogPath)
	moduleName = fileName.split(".")[0].strip()
	if (not os.path.exists("qflowSynthesis")):
		os.mkdir("qflowSynthesis")

	if (not os.path.exists("qflowSynthesis/{}".format(moduleName))):
		os.mkdir("qflowSynthesis/{}".format(moduleName))
		#Create subdirectories
		os.mkdir("qflowSynthesis/{}/source".format(moduleName))
		os.mkdir("qflowSynthesis/{}/synthesis".format(moduleName))
		os.mkdir("qflowSynthesis/{}/layout".format(moduleName))
	else:
		shutil.rmtree("qflowSynthesis/{}".format(moduleName))
		os.mkdir("qflowSynthesis/{}".format(moduleName))
		#Create subdirectories
		os.mkdir("qflowSynthesis/{}/source".format(moduleName))
		os.mkdir("qflowSynthesis/{}/synthesis".format(moduleName))
		os.mkdir("qflowSynthesis/{}/layout".format(moduleName))

	#Create linked monolithic verilog file for sythesis
	printColor("Generating monolithic verilog\n", color=COLORS.UNDERLINE)

	g_includedFiles.append(verilogPath)

	monolithicFilepath = os.path.join("qflowSynthesis", moduleName, "source",fileName)
	monolithicFilename = fileName
	outputFile = open(monolithicFilepath, "w")
	inputFile = open(verilogPath, "r")

	createMonolithicVerilog(outputFile, inputFile, sourceDirectory)

	outputFile.close()
	inputFile.close()

	#Run qflow steps if specified | http://opencircuitdesign.com/qflow/
	os.chdir(os.path.join("qflowSynthesis", moduleName))
	if(synthesizeFlag):
		printColor("Running qflow synthesis", color=COLORS.UNDERLINE)

		command = "qflow synthesize {} > {}_synth.log".format(moduleName, moduleName)
		print("  + {}".format(command))
		os.system(command)

		#Output errors to terminal
		command = "cat synth.log | grep ERROR".format(moduleName)
		printColor("\r", color=COLORS.ERROR, resetColor=False)
		os.system(command)
		printColor("", color=COLORS.DEFAULT)

	if(staFlag):
		printColor("Running qflow static timing analysis", color=COLORS.UNDERLINE)

		command = "qflow sta {} > {}_sta.log".format(moduleName, moduleName)
		print("  + {}".format(command))
		os.system(command)

		#Output errors to terminal
		command = "cat {}_sta.log | grep error".format(moduleName)
		printColor("", color=COLORS.ERROR, resetColor=False)
		os.system(command)
		printColor("", color=COLORS.DEFAULT)