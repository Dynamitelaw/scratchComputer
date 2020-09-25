import json


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