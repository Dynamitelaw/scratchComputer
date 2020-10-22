import argparse
import os
import sys
import time
import traceback
import multiprocessing
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation


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


def displayFrameBuffer(displayWidth, displayHeight, frameBufferPath, workDir):
	fig = plt.figure()

	flatPixelArray = None
	flatByteArray = np.fromfile(frameBufferPath, dtype='>B')
	flatPixelArray = np.reshape(flatByteArray, (-1, 4))

	pixelArray = np.zeros([displayHeight, displayWidth, 3], dtype=np.uint8)
	imagePath = os.path.join(workDir, "createdImage.png")

	def animate(i):
		#Update pixel array with values
		flatByteArray = np.fromfile(frameBufferPath, dtype='B')
		flatPixelArray = np.reshape(flatByteArray, (-1, 4))

		for row in range(0, displayHeight):
			for column in range(0, displayWidth):
				pixelIndex = row*displayWidth + column
				if (len(flatPixelArray) > 0):
					try:
						pixelArray[row, column] = np.flip(flatPixelArray[pixelIndex][0:-1])
					except Exception as e:
						pass
				else:
					break

		#Display updated pixel array
		img = Image.fromarray(pixelArray)
		img.save(imagePath)

		img = mpimg.imread(imagePath)
		plt.clf()
		plt.axis('off')
		imgplot = plt.imshow(img)
		
		time.sleep(0.05)

	ani = animation.FuncAnimation(fig, animate, interval=50)
	plt.show()

if __name__ == '__main__':
	displayThread = None

	try:
		#Read command line arguments
		helpdesc = '''
help yourself
'''

		parser = argparse.ArgumentParser(description = helpdesc)

		parser.add_argument("-bench", action="store", dest="testbenchPath", help="Filepath to verilog testbench")
		parser.add_argument("-prog", action="store", dest="programPath", help="Path to hex program to run, if supported by the testbench")
		parser.add_argument("-mem", action="store", dest="memorySize", default="4096", help="Size of main memory to allocate in bytes")
		parser.add_argument("-cycles", action="store", dest="maxSimCycles", help="If specified, simulation will end if total cycles exceed this limit")
		parser.add_argument("-display", action="store", dest="screenSize", help="If specified, simulation will define and display a frame buffer. Argument format: \"<WIDTH_PIXELS>,<HEIGHT_PIXELS>\"")
		parser.add_argument("-dump", action="store_true", dest="dumpValues", help="If specified, will create an vcd dump file from simulation. Required to view waveforms in Gtkwave")

		args = parser.parse_args()

		testbenchPath = args.testbenchPath
		programPath = args.programPath
		
		memorySizeString = args.memorySize
		memorySize = None
		if ("K" in memorySizeString):
			memorySizeString = memorySizeString.replace("K", "")
			memorySize = int(memorySizeString) * 2**10
		elif ("M" in memorySizeString):
			memorySizeString = memorySizeString.replace("M", "")
			memorySize = int(memorySizeString) * 2**20
		elif ("G" in memorySizeString):
			memorySizeString = memorySizeString.replace("G", "")
			memorySize = int(memorySizeString) * 2**30
		else:
			memorySize = int(4 * int(int(memorySizeString) / 4))

		maxSimCycles = args.maxSimCycles
		dumpValues = args.dumpValues
		screenSizeString = args.screenSize

		if (not testbenchPath):
			raise Exception("ERROR: -testbenchPath arg required")

		#Create output folders if they do not exist yet
		testbenchName = testbenchPath.split(".")[0].split("/")[-1]
		if (not os.path.exists("simulation")):
			os.mkdir("simulation")
		if (not os.path.exists("simulation/{}".format(testbenchName))):
			os.mkdir("simulation/{}".format(testbenchName))

		if (programPath):
			#Program specified. Determine length of program
			programFile = open(programPath, "r")

			line = " "
			lineCount = 0

			while(line):
				line = programFile.readline()
				if (len(line) > 0):
					if ("00000000" in line):
						break
					lineCount += 1

			programFile.close()

			#Update testbench program inputs
			programInputsFile = open("{}_programInputs.v".format(testbenchPath.split(".")[0]), "w")

			programInputsFile.write("`define programLength {}\n".format(lineCount))
			programInputsFile.write("`define programFilename \"{}\"\n".format(programPath))
			programInputsFile.write("`define memorySize {}\n".format(memorySize))
			if (maxSimCycles):
				programInputsFile.write("`define MAX_CYLCLES {}\n".format(int(maxSimCycles)))

			if (screenSizeString):
				#Determine frame buffer file path
				frameBufferPath = "simulation/{}/frameBuffer.b".format(testbenchName)

				#Determine size of frame buffer and frameBufferStart
				frameBufferStart, displayWidth, displayHeight = [int(i) for i in screenSizeString.replace(" ","").strip().rstrip().split(",")]
				frameBufferSize = displayHeight * displayWidth *4

				if (frameBufferStart < 0):
					raise Exception("Allocated memory of {} bytes cannot fit frame buffer of size {}".format(memorySize, frameBufferSize))
				
				programInputsFile.write("`define FRAME_BUFFER_ENABLE\n")
				programInputsFile.write("`define frameBufferPath \"{}\"\n".format(frameBufferPath))
				programInputsFile.write("`define frameBufferSize {}\n".format(frameBufferSize))
				programInputsFile.write("`define frameBufferStart {}\n".format(frameBufferStart))
				
				#Initialize frame buffer file
				emptyByteArray = bytearray(frameBufferSize)
				bufferFile = open(frameBufferPath, "wb")
				bufferFile.write(emptyByteArray)
				bufferFile.close()

				#Initialize display viewer
				displayThread = multiprocessing.Process(target=displayFrameBuffer, args=(displayWidth, displayHeight, frameBufferPath, "simulation/{}".format(testbenchName)))
				displayThread.start()

			programInputsFile.close()


		#Compile into vvp with icarus verilog
		print("Compiling verilog")
		command = "iverilog {} -I rtl -I testbenches -g2005-sv -o simulation/{}/{}.vvp | grep error".format(testbenchPath, testbenchName, testbenchName)
		print("+ {}{}".format(command, COLORS.ERROR))
		os.system(command)
		print(COLORS.DEFAULT)

		#Run vvp
		dumpFlag = ""
		if (dumpValues):
			dumpFlag = "-vcd"

		print("Running simulation")
		startTime = time.time()
		command = "vvp simulation/{}/{}.vvp {}".format(testbenchName, testbenchName, dumpFlag)
		print("+ {}".format(command))
		os.system(command)
		endTime = time.time()

		print("runtime = {} seconds".format(endTime-startTime))

		#Move dump file
		command = "mv dump.vcd simulation/{}/{}_dump.vcd".format(testbenchName, testbenchName)
		print("+ {}".format(command))
		os.system(command)

		#Kill display thread
		if (displayThread):
			pass
			#displayThread.terminate()
	except Exception as e:
		printColor(traceback.format_exc(), color=COLORS.ERROR)
		if (displayThread):
			displayThread.terminate()