import os
import sys
import traceback
import json

#import Verilog_VCD as vcd 
import vcdReader as vcd 
import utils

filepath = "/home/jose/Documents/gitRepos/scratchComputer/verilog/simulation/coreTestbench/coreTestbench_dump.vcd"
data = vcd.parse_vcd(filepath)

#jsonString = utils.dictToJson(data)
#print(jsonString) 

configPath = "/home/jose/Documents/gitRepos/scratchComputer/pythonScripts/vcdDebugger/debuggerConfig.json"
debugConfig = utils.jsonToDict(configPath)

captureList = debugConfig["captureList"]
filteredData = {}

for firstLevelKey in data:
	changeData = data[firstLevelKey]
	netList = changeData["nets"]
	
	for net in netList:
		storeKey = "{}.{}".format(net["hier"], net["name"])

		if (storeKey in captureList):
			filteredData[storeKey] = changeData["tv"]


print(utils.dictToJson(filteredData))