import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
import sys
import os
import numpy as np
from PIL import Image
from pynput.keyboard import Listener, Key, KeyCode
import time
from collections import OrderedDict
from keyboardArray import *

'''
fig = plt.figure()
displayHeight = 2
displayWidth = 4

binaryPath = "testBinary2.b"
flatPixelArray = None

flatByteArray = np.fromfile(binaryPath, dtype='>B')
flatPixelArray = np.reshape(flatByteArray, (-1, 4))

print(flatPixelArray)
#sys.exit()

pixelArray = np.zeros([displayHeight, displayWidth, 3], dtype=np.uint8)
imagePath = "createdImage.png"

def animate(i):
	#Update pixel array with values
	binaryPath = "testBinary2.b"
	flatByteArray = np.fromfile(binaryPath, dtype='>B')
	flatPixelArray = np.reshape(flatByteArray, (-1, 4))

	for row in range(0, displayHeight):
		for column in range(0, displayWidth):
			pixelIndex = row*displayWidth + column
			pixelArray[row, column] = flatPixelArray[pixelIndex][1:]

	#Display updated pixel array
	img = Image.fromarray(pixelArray)
	img.save(imagePath)

	img = mpimg.imread(imagePath)
	plt.clf()
	plt.axis('off')
	imgplot = plt.imshow(img)

ani = animation.FuncAnimation(fig, animate, interval=50)
plt.show()
'''


keyIndexes = OrderedDict()

for index in range(0, len(keyArray), 1):
	headLine = "#define {}_OFFSET {}".format(keyArray[index], index)
	print(headLine)
	keyIndexes[keyArray[index]] = index
'''
print(keyIndexes)

stateArrayLength = len(keyIndexes)
if (len(keyIndexes)%4):
	stateArrayLength += 4 - len(keyIndexes)%4
keyboardStateArray = np.zeros(stateArrayLength, dtype=np.uint8)
print(len(keyboardStateArray))

def updateInputBufferFile(filepath, keyboardStateArray):
	hexFile = open(filepath, "w")

	iterator = 0
	for byte in keyboardStateArray:
		if (iterator == 4):
			hexFile.write("\n")
			iterator = 0

		hexFile.write("0{}".format(str(byte)))
		iterator += 1

	hexFile.close()

def on_press(key):
	print(key)
	keyboardStateArray[keyIndexes[key]]= 1
	updateInputBufferFile("temp.hex", keyboardStateArray)

def on_release(key):
	keyboardStateArray[keyIndexes[key]] = 0
	updateInputBufferFile("temp.hex", keyboardStateArray)

#print(Key.A)

listener = Listener(on_press=on_press, on_release=on_release)
listener.start()  # Join the listener thread to the main thread to keep waiting for keys

time.sleep(10)
'''

'''
xLocations = [4,8,12,16,20,24,28,32,36,40,44,48,52,56,60]
yLocations = [4,8,12,16,20,24,28,32,36,40,44]

xPos = 8
yPos = 4


def getNextPos(xPos, yPos, iterator):
	xIndex = (xPos*3 + yPos*7 + iterator*5)%65
	yIndex = (yPos*2 + xPos*11 + iterator*3)%49

	return xIndex, yIndex


seed = 1
for i in range(20):
	print(xPos, yPos)
	xPos, yPos = getNextPos(xPos, yPos, i)
'''