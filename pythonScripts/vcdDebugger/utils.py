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
	value = None

	if (len(binaryString) == 32):
		#Handle 2s compliment
		positivePortion = int(binaryString[1:], 2)
		negativePortion = int(binaryString[0], 2)*2**31

		value = positivePortion - negativePortion
	else:
		value = int(binaryString, 2)

	return value