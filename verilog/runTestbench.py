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
from collections import OrderedDict
from pynput.keyboard import Listener, Key, KeyCode


#Globals
global g_keyboardStateArray
g_keyboardStateArray = None
global g_keyIndexes
g_keyIndexes = None
global g_inputBufferPath
g_inputBufferPath = None

g_keyArray = [
#lower case letters
	KeyCode.from_char("a"),	KeyCode.from_char("b"),	KeyCode.from_char("c"),	KeyCode.from_char("d"),	KeyCode.from_char("e"),	KeyCode.from_char("f"),
	KeyCode.from_char("g"),	KeyCode.from_char("h"),	KeyCode.from_char("i"),	KeyCode.from_char("j"),	KeyCode.from_char("k"),	KeyCode.from_char("l"),
	KeyCode.from_char("m"),	KeyCode.from_char("n"),	KeyCode.from_char("o"),	KeyCode.from_char("p"),	KeyCode.from_char("q"),	KeyCode.from_char("r"),
	KeyCode.from_char("s"),	KeyCode.from_char("t"),	KeyCode.from_char("u"),	KeyCode.from_char("v"),	KeyCode.from_char("w"),	KeyCode.from_char("x"),
	KeyCode.from_char("y"),	KeyCode.from_char("z"),
#uppder case letters
	KeyCode.from_char("A"),	KeyCode.from_char("B"),	KeyCode.from_char("C"),	KeyCode.from_char("D"),	KeyCode.from_char("E"),	KeyCode.from_char("F"),
	KeyCode.from_char("G"),	KeyCode.from_char("H"),	KeyCode.from_char("I"),	KeyCode.from_char("J"),	KeyCode.from_char("K"),	KeyCode.from_char("L"),
	KeyCode.from_char("M"),	KeyCode.from_char("N"),	KeyCode.from_char("O"),	KeyCode.from_char("P"),	KeyCode.from_char("Q"),	KeyCode.from_char("R"),
	KeyCode.from_char("S"),	KeyCode.from_char("T"),	KeyCode.from_char("U"),	KeyCode.from_char("V"),	KeyCode.from_char("W"),	KeyCode.from_char("X"),
	KeyCode.from_char("Y"),	KeyCode.from_char("Z"),
#numbers
	KeyCode.from_char("0"),	KeyCode.from_char("1"),	KeyCode.from_char("2"),	KeyCode.from_char("3"),	KeyCode.from_char("4"),	KeyCode.from_char("5"),
	KeyCode.from_char("6"),	KeyCode.from_char("7"),	KeyCode.from_char("8"),	KeyCode.from_char("9"),
#symbols
	KeyCode.from_char("!"),	KeyCode.from_char("@"),	KeyCode.from_char("#"),	KeyCode.from_char("$"),	KeyCode.from_char("%"),	KeyCode.from_char("^"),
	KeyCode.from_char("&"),	KeyCode.from_char("*"),	KeyCode.from_char("("),	KeyCode.from_char(")"),	KeyCode.from_char("-"),	KeyCode.from_char("_"),
	KeyCode.from_char("+"),	KeyCode.from_char("="),	KeyCode.from_char("{"),	KeyCode.from_char("["),	KeyCode.from_char("}"),	KeyCode.from_char("]"),
	KeyCode.from_char("|"),	KeyCode.from_char("\\"),KeyCode.from_char(";"),	KeyCode.from_char(":"),	KeyCode.from_char("'"),	KeyCode.from_char("\""),
	KeyCode.from_char(","),	KeyCode.from_char("<"),	KeyCode.from_char("."),	KeyCode.from_char(">"),	KeyCode.from_char("/"),	KeyCode.from_char("?"),
	KeyCode.from_char("`"),	KeyCode.from_char("~"),
#function keys
	Key.f1,	Key.f2,	Key.f3,	Key.f4,	Key.f5,	Key.f6,
	Key.f7,	Key.f8,	Key.f9,	Key.f10, Key.f11, Key.f12,
#Arrow keys
	Key.up,	Key.down, Key.left, Key.right,
#Modifier keys
	Key.ctrl, Key.ctrl_r, Key.cmd, Key.cmd_r, Key.alt,
	Key.alt_r, Key.num_lock, Key.caps_lock, Key.shift,
	Key.shift_r,
#Macro keys
	Key.enter, Key.backspace, Key.delete, Key.home, Key.end,
	Key.insert, Key.page_up, Key.page_down, Key.esc
]


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
		
		#time.sleep(0.05)

	ani = animation.FuncAnimation(fig, animate, interval=20)
	plt.show()


def updateInputBufferFile(filepath, keyboardStateArray):
	hexFile = open(filepath, "r+")

	iterator = 0

	for byteIndex in range(0, len(g_keyboardStateArray)):
		byte = g_keyboardStateArray[byteIndex]
		# if (iterator == 4):
		# 	hexFile.write("\n")
		# 	iterator = 0

		hexFile.seek(byteIndex*2+1+(byteIndex/4), 0)
		hexFile.write("{}".format(str(byte)))
		iterator += 1

	hexFile.close()

def initializeInputBufferFile(filepath, keyboardStateArray):
	hexFile = open(filepath, "w")

	iterator = 0

	for byteIndex in range(0, len(g_keyboardStateArray)):
		byte = g_keyboardStateArray[byteIndex]
		if (iterator == 4):
			hexFile.write("\n")
			iterator = 0

		hexFile.write("0{}".format(str(byte)))
		iterator += 1

	hexFile.close()


def onKeyPress(key):
	g_keyboardStateArray[g_keyIndexes[key]]= 1
	updateInputBufferFile(g_inputBufferPath, g_keyboardStateArray)


def onKeyRelease(key):
	g_keyboardStateArray[g_keyIndexes[key]] = 0
	updateInputBufferFile(g_inputBufferPath, g_keyboardStateArray)


if __name__ == '__main__':
	displayThread = None
	listenerThread = None

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
		parser.add_argument("-display", action="store", dest="screenSize", help="If specified, simulation will define and display a frame buffer. Argument format: \"<BUFFER_ADDRESS>,<WIDTH_PIXELS>,<HEIGHT_PIXELS>\"")
		parser.add_argument("-input", action="store", dest="inputBufferSize", help="If specified, simulation will define and update a keyboard input buffer. Argument format: \"<BUFFER_ADDRESS>,<BUFFER_SIZE>\"")
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
		inputBufferSizeString = args.inputBufferSize

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

				if (frameBufferSize > memorySize-frameBufferStart):
					raise Exception("Allocated memory of {} bytes cannot fit frame buffer of size {}, location {}".format(memorySize, frameBufferSize, frameBufferStart))
				
				#Add defines to program inputs
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

			if (inputBufferSizeString):
				#Determine input buffer file path
				inputBufferPath = "simulation/{}/inputBuffer.hex".format(testbenchName)
				g_inputBufferPath = inputBufferPath

				#Determine size of input buffer and inputBufferStart
				inputBufferStart, inputBufferSize = [int(i) for i in inputBufferSizeString.replace(" ","").strip().rstrip().split(",")]

				if (inputBufferSize > memorySize-inputBufferStart):
					raise Exception("Allocated memory of {} bytes cannot fit frame buffer of size {}, location {}".format(memorySize, inputBufferSize, inputBufferStart))

				#Add defines to program inputs
				programInputsFile.write("`define INPUT_BUFFER_ENABLE\n")
				programInputsFile.write("`define inputBufferPath \"{}\"\n".format(inputBufferPath))
				programInputsFile.write("`define inputBufferSize {}\n".format(inputBufferSize))
				programInputsFile.write("`define inputBufferStart {}\n".format(inputBufferStart))

				#Initialize input buffer file
				g_keyIndexes = OrderedDict()

				for index in range(0, len(g_keyArray), 1):
					g_keyIndexes[g_keyArray[index]] = index

				stateArrayLength = len(g_keyIndexes)
				if (len(g_keyIndexes)%4):
					stateArrayLength += 4 - len(g_keyIndexes)%4
				
				g_keyboardStateArray = np.zeros(stateArrayLength, dtype=np.uint8)
				initializeInputBufferFile(inputBufferPath, g_keyboardStateArray)

				# g_keyboardStateArray[0] = 1
				# g_keyboardStateArray[1] = 1
				# g_keyboardStateArray[2] = 1
				# g_keyboardStateArray[3] = 1
				# g_keyboardStateArray[4] = 1
				# g_keyboardStateArray[5] = 1

				# g_keyboardStateArray[30] = 1
				# g_keyboardStateArray[31] = 1
				# g_keyboardStateArray[32] = 1
				# g_keyboardStateArray[33] = 1
				# g_keyboardStateArray[34] = 1
				# g_keyboardStateArray[35] = 1
				# updateInputBufferFile(inputBufferPath, g_keyboardStateArray)
				#sys.exit()

				#Initialize keyboard listener
				listenerThread = Listener(on_press=onKeyPress, on_release=onKeyRelease)
				listenerThread.start()

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
		if (dumpValues):
			command = "mv dump.vcd simulation/{}/{}_dump.vcd".format(testbenchName, testbenchName)
			print("+ {}".format(command))
			os.system(command)

		#Kill display thread
		if (displayThread):
			time.sleep(2)
			displayThread.terminate()

		#Kill keyboard listener thread
		#Not needed?
		# if (listenerThread):
		# 	listenerThread.close()

	except Exception as e:
		printColor(traceback.format_exc(), color=COLORS.ERROR)
		if (displayThread):
			displayThread.terminate()