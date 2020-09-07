import argparse
import os
import sys


if __name__ == '__main__':

	#Read command line arguments
	helpdesc = '''
help yourself
'''

	parser = argparse.ArgumentParser(description = helpdesc)

	parser.add_argument("-bench", action="store", dest="testbenchPath", help="Filepath to verilog testbench")
	parser.add_argument("-prog", action="store", dest="programPath", help="Path to hex program to run, if supported by the testbench")
	parser.add_argument("-dump", action="store_true", dest="dumpValues", help="If specified, will create an lxt2 dump file from simulation. Required to view waveforms in Gtkwave")

	results = parser.parse_args()

	testbenchPath = results.testbenchPath
	programPath = results.programPath
	dumpValues = results.dumpValues

	if (not testbenchPath):
		print("ERROR: -testbenchPath arg required")
		sys.exit()

	if (programPath):
		#Program specified. Determine length of program
		programFile = open(programPath, "r")

		line = " "
		lineCount = 0

		while(line):
			line = programFile.readline()
			lineCount += 1

		programFile.close()

		#Update testbench program inputs
		programInputsFile = open("{}_programInputs.v".format(testbenchPath.split(".")[0]), "w")

		programInputsFile.write("`define programLength {}\n".format(lineCount))
		programInputsFile.write("`define programFilename \"{}\"\n".format(programPath))

		programInputsFile.close()

	#Create output folders if they do not exist yet
	testbenchName = testbenchPath.split(".")[0].split("/")[-1]
	if (not os.path.exists("simulation")):
		os.mkdir("simulation")
	if (not os.path.exists("simulation/{}".format(testbenchName))):
		os.mkdir("simulation/{}".format(testbenchName))

	#Compile into vvp with icarus verilog
	command = "iverilog {} -I rtl -I testbenches -g2005-sv -o simulation/{}/{}.vvp".format(testbenchPath, testbenchName, testbenchName)
	print("+ {}".format(command))
	os.system(command)

	#Run vvp
	dumpFlag = ""
	if (dumpValues):
		dumpFlag = "-lxt2"

	command = "vvp simulation/{}/{}.vvp {}".format(testbenchName, testbenchName, dumpFlag)
	print("+ {}".format(command))
	os.system(command)

	#Move dump file
	command = "mv dump.lx2 simulation/{}/{}_dump.lx2".format(testbenchName, testbenchName)
	print("+ {}".format(command))
	os.system(command)