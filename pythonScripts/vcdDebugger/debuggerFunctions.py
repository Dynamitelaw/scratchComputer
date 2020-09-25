import os
import sys
import traceback
import json

import vcdReader as vcd 
import utils


def getCycleMap(vcdFilePath, configPath):
	#Parse vcd file
	data = vcd.parse_vcd(vcdFilePath)
	 
	#Filter vcd data
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


	#Construct cycle value map for filtered data
	cycleCountLabel = "coreTestbench.cycleCount[31:0]"
	cycleMap = {}
	timeCycleMap = {}

	for cycleCountElement in filteredData[cycleCountLabel]:
		timeStep, cycleCount_bin = cycleCountElement
		cycle = utils.binStringToInt(cycleCount_bin)

		cycleMap[cycle] = {}
		cycleMap[cycle]["timeStep"] = timeStep

		timeCycleMap[timeStep] = cycle

	del filteredData[cycleCountLabel]

	valueMapping = debugConfig["valueMapping"]


	for displayKey in valueMapping:
		dataKey = valueMapping[displayKey]
		
		previousTimeStep = 0
		previousBinaryString = ""
		for valueChange in filteredData[dataKey]:
			timeStep, binaryString = valueChange

			if (timeStep == 0):
				previousTimeStep = timeStep
				previousBinaryString = binaryString
			else:
				previousCycle = timeCycleMap[previousTimeStep]
				currentCycle = timeCycleMap[timeStep]

				for cycle in range(previousCycle, currentCycle, 1):
					cycleMap[cycle][displayKey] = utils.binStringToInt(previousBinaryString)

				cycleMap[currentCycle][displayKey] = utils.binStringToInt(binaryString)

				previousTimeStep = timeStep
				previousBinaryString = binaryString

	return cycleMap