import json


#Colored printed for errors
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


def jsonToDict(filepath):
	'''
	Reads json file, and returns as dictionary
	'''

	jsonFile = open(filepath, "r")
	dictionary = json.load(jsonFile)
	jsonFile.close()

	return dictionary


def dictToJson(dictionary):
	'''
	Converts dictionary to json string
	'''

	jsonString = json.dumps(dictionary, sort_keys=True, indent=2, separators=(',', ': '))
	return jsonString


def binStringToInt(binaryString, signed=False):
	return int(binaryString, 2)