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
	keyIndexes[keyArray[index]] = index

print(keyIndexes)

stateArrayLength = len(keyIndexes)
if (len(keyIndexes)%4):
	stateArrayLength += 4 - len(keyIndexes)%4
keyboardStateArray = np.zeros(stateArrayLength, dtype=np.uint8)
print(len(keyboardStateArray))

def on_press(key):  # The function that's called when a key is pressed
    print("Key pressed: {0}".format(key))
    keyboardStateArray[keyIndexes[key]]= 1
    print(keyboardStateArray)
    #print(keyIndexes[key])
    #print(key)
    #print(type(KeyCode.from_char("a")))

def on_release(key):  # The function that's called when a key is released
    print("Key released: {0}".format(key))
    keyboardStateArray[keyIndexes[key]] = 0
    print(keyboardStateArray)

#print(Key.A)

with Listener(on_press=on_press, on_release=on_release) as listener:  # Create an instance of Listener
    listener.join()  # Join the listener thread to the main thread to keep waiting for keys