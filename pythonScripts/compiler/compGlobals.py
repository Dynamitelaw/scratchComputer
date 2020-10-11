#Global vars
global cFileCoord
cFileCoord = None

global whileCounter
whileCounter = 0

global forCounter
forCounter = 0

global ifCounter
ifCounter = 0

global dataSegment
dataSegment = {}

global typeSizeDictionary
typeSizeDictionary = {
	"int": 4,
	"unsigned int": 4,
	"short": 2,
	"unsigned short": 2,
	"long": 8,
	"unsigned long": 8,
	"char": 1,
	"unsigned char": 1,
	"float": 4,
	"double": 8,
	"long double": 10
}

global structDictionary
structDictionary = {}