import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
import sys
import os
import numpy as np
from PIL import Image

'''
rootPath = "/home/jose/Downloads/testImages"
bmpFiles = os.listdir(rootPath)
bmpFiles.sort()

bmpPaths = []
for fileName in bmpFiles:
	bmpPaths.append(os.path.join(rootPath, fileName))

fig = plt.figure()

def animate(i):
	imageIndex = i%len(bmpPaths)
	#print(imageIndex)
	img = mpimg.imread(bmpPaths[imageIndex])
	plt.clf()
	plt.axis('off')
	imgplot = plt.imshow(img)


	#plt.show()
'''
'''
fig = plt.figure()
pixelArray = np.zeros([100, 200, 3], dtype=np.uint8)
imagePath = "createdImage.png"

def animate(i):
	#Update pixel array with values
	if (i%2 == 0):
		pixelArray[:,:100] = [255, 128, 0] #Orange left side
		pixelArray[:,100:] = [0, 0, 255]   #Blue right side
	else:
		pixelArray[:,:100] = [0, 0, 255]  #Blue left side
		pixelArray[:,100:] = [255, 128, 0]  #Orange right side

	img = Image.fromarray(pixelArray)
	img.save(imagePath)

	#Display updated array
	img = mpimg.imread(imagePath)
	plt.clf()
	plt.axis('off')
	imgplot = plt.imshow(img)
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