# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scDebugger.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

import argparse
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest

import vcdReader as vcd
import utils


#Global vars
global g_cycleMap
global g_maxCycles

global g_cFileMap
global g_asmFileMap
global g_htmlDict
global g_registerStateMap
global g_stackStateMap
g_htmlDict = {}


htmlText = r'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#ffffff;">Hello world</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline; color:#ffffff;">I'm bold/underlined</span></p></body>
</html>
'''

def highlightLine(htmlList, lineNumber):
	tempList = htmlList.copy()

	lineToHighlight = tempList[lineNumber]
	lineToHighlight = lineToHighlight.replace('style="', 'style=" font-weight:900;').replace('</p>', '<span style=" font-size:18pt;font-weight:1000;color:#ffdd00;">  &#8592;</span></p>')
	tempList[lineNumber] = lineToHighlight

	return "\n".join(tempList)


def fileToHtmlList(filepath, fileType=None):
	file = open(filepath, "r")

	htmlHeader = r'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;">
'''
	htmlList = [htmlHeader]
	line = file.readline()
	inLongComment = False

	while(line):
		########
		# Syntax highlighting
		########
		lineList = line.rstrip().replace("(", " ( ").replace(")", " ) ").replace(";", " ; ").replace(",", " , ").replace("\t", "").split(" ")
		lineList =  list(filter(lambda i: i != "", lineList))

		#Color defs
		white = "ffffff"
		blue = "67d8ef"
		red = "f92472"
		green = "a6e22b"
		purple = "ac80ff"
		grey = "848066"
		orange = "fd9622"

		#C keywords
		c_blueKeywords = ["int", "float", "char", "double", "long", "unisgned", "byte", "bool"]
		c_redKeywords = ["return", "if", "else", "&&", "||", "!"]
		c_constantKeywords = ["true", "false"]

		#assembly keywords
		asm_blueKeywords = [
			"addi", "add", "mv", "move", "sub", "mul", "div", "divu", "rem", "remu", "slti", "sltiu", "slt", "sltu",
			"jal", "j", "jr", "jalr", "bne", "bltu", "blt", "bge", "bgeu", "beq",
			"lh", "lhu", "lb", "lbu", "lw", "sw", "sh", "sb"
			]
		asm_orangeKeywords = [
			"s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
			"a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
			"t0", "t1", "t2", "t3", "t4", "t5", "t6",
			"sp", "gp", "fp", "ra",
			"zero", "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20", "x22", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30", "x31"
			]

		formattedLineList = []
		inComment = False

		for index in range(0, len(lineList)):
			lineElement = lineList[index]
			#Syntax highlighting
			color = white
			if (fileType):
				#C file syntax highlighting
				if (fileType == "C"):
					#Typedefs = blue
					if (lineElement in c_blueKeywords):
						color = blue
					#Function calls = blue
					if (index < len(lineList)-1):
						nextElement = lineList[index+1]
						if (nextElement == "("):
							if ((lineElement != "(") and (lineElement != "&&") and (lineElement != "||") and (lineElement != "!")):
								color = blue
					#Control keywords = red
					if (lineElement in c_redKeywords):
						color = red
					#Function defs = green
					if ((index < len(lineList)-1) and (index != 0)):
						previousElement = lineList[index-1]
						nextElement = lineList[index+1]

						if ((previousElement in c_blueKeywords) and (nextElement == "(")):
							color = green
					#Constants = purple
					if (lineElement in c_constantKeywords):
						color = purple
					try:
						k = int(lineElement)
						color = purple
					except Exception as e:
						pass
					try:
						k = float(lineElement)
						color = purple
					except Exception as e:
						pass		
					#Comments = grey
					if (inComment):
						color = grey
					elif (("*/" in lineElement) and (inLongComment)):
						inLongComment = False
						inComment = False
						color = grey
					elif (inLongComment):
						inComment = True
						color = grey
					elif ("//" in lineElement):
						inComment = True
						color = grey
					elif ("/*" in lineElement):
						inLongComment = True
						inComment = True
						color = grey

				#assembly file syntax highlighting
				if (fileType == "asm"):
					#Instructions = blue
					if (lineElement in asm_blueKeywords):
						color = blue
					#Registers = orange
					if (lineElement in asm_orangeKeywords):
						color = orange
					#Labels = red
					if (lineElement[-1] == ":"):
						color = red
					#Constants = purple
					if (lineElement in c_constantKeywords):
						color = purple
					try:
						k = int(lineElement)
						color = purple
					except Exception as e:
						pass
					try:
						k = float(lineElement)
						color = purple
					except Exception as e:
						pass		
					#Comments = grey
					if (inComment):
						color = grey
					elif ("#" in lineElement):
						inComment = True
						color = grey	

			#Construction html line element
			prespace = " "
			if (lineElement == "("):
				prespace = ""
				if (index != 0):
					previousElement = lineList[index-1]
					if (previousElement in c_redKeywords):
						prespace = " "
			elif (lineElement == ")"):
				prespace = ""
			elif (lineElement == ","):
				prespace = ""
			elif (lineElement == ";"):
				prespace = ""
			elif (index != 0):
				if (lineList[index-1] == "("):
					prespace = ""
			elif (index == 0):
				prespace = ""

			htmlElement = '<span style=" color:#{};">{}{}</span>'.format(color, prespace, lineElement)
			formattedLineList.append(htmlElement)

		#Contruct fintal htmlline
		tabSearchEnd = line.find(';')
		htmlLineStart = '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:{}; text-indent:0px;">'.format(line.count("\t", 0, tabSearchEnd))
		htmlLine = '{}{}</p>'.format(htmlLineStart, "".join(formattedLineList))
		htmlList.append(htmlLine)

		line = file.readline()

	htmlList.append("</html>")
	return htmlList

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
		previousCycle = 0
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
					cycleMap[cycle][displayKey] = str(utils.binStringToInt(previousBinaryString))

				cycleMap[currentCycle][displayKey] = str(utils.binStringToInt(binaryString))

				previousTimeStep = timeStep
				previousCycle = timeCycleMap[previousTimeStep]
				previousBinaryString = binaryString

		for cycle in range(previousCycle, len(cycleMap), 1):
			cycleMap[cycle][displayKey] = str(utils.binStringToInt(previousBinaryString))

	return cycleMap


class registerDisplay:
	def __init__(self, label, value, variable):
		self.label = label
		self.value = value
		self.variable = variable

	def setValueText(self, text):
		self.value.setText(QtCore.QCoreApplication.translate("MainWindow", text))

	def setVariableText(self, text):
		self.variable.setText(QtCore.QCoreApplication.translate("MainWindow", text))

	def setStyleDefault(self):
		oldStyleList = self.label.styleSheet().split(";")
		newStyleList = []

		for styleLine in oldStyleList:
			if (("color:" in styleLine) and (styleLine.find("color:") == 0)):
				newline = "color: rgb(255, 255, 255)"
				newStyleList.append(newline)
			elif ("border" in styleLine):
				pass
			else:
				newStyleList.append(styleLine)

		newStyleSheet = ";".join(newStyleList)
		oldStyleSheet = ";".join(oldStyleList)

		self.label.setStyleSheet(newStyleSheet)
		self.value.setStyleSheet(newStyleSheet)
		if (self.variable):
			self.variable.setStyleSheet(newStyleSheet)

	def setStyleHighlight(self):
		oldStyleList = self.label.styleSheet().split(";")
		newStyleList = []

		for styleLine in oldStyleList:
			if (("color:" in styleLine) and (styleLine.find("color:") == 0)):
				newline = "color: rgb(50, 255, 50)"
				newStyleList.append(newline)
			else:
				newStyleList.append(styleLine)

		newStyleList.append("border: 3px solid white")

		newStyleSheet = ";".join(newStyleList)
		oldStyleSheet = ";".join(oldStyleList)

		self.label.setStyleSheet(newStyleSheet)
		self.value.setStyleSheet(newStyleSheet)
		if (self.variable):
			self.variable.setStyleSheet(newStyleSheet)


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(1189, 1071)
		MainWindow.setStyleSheet("background-color: rgb(40, 41, 35);")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
		self.verticalLayout_2.setObjectName("verticalLayout_2")
		spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_2.addItem(spacerItem)
		self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_3.setObjectName("horizontalLayout_3")
		self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_4.setObjectName("horizontalLayout_4")
		self.verticalLayout_3 = QtWidgets.QVBoxLayout()
		self.verticalLayout_3.setObjectName("verticalLayout_3")
		self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_7.setObjectName("horizontalLayout_7")
		self.programCounter_display = QtWidgets.QLCDNumber(self.centralwidget)
		self.programCounter_display.setMinimumSize(QtCore.QSize(0, 30))
		self.programCounter_display.setMaximumSize(QtCore.QSize(16777215, 30))
		self.programCounter_display.setObjectName("programCounter_display")
		self.horizontalLayout_7.addWidget(self.programCounter_display)
		self.programCounterLabel = QtWidgets.QLabel(self.centralwidget)
		self.programCounterLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.programCounterLabel.setStyleSheet("color: rgb(255, 255, 255);")
		self.programCounterLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
		self.programCounterLabel.setObjectName("programCounterLabel")
		self.horizontalLayout_7.addWidget(self.programCounterLabel)
		self.verticalLayout_3.addLayout(self.horizontalLayout_7)
		self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_9.setObjectName("horizontalLayout_9")
		self.cycle_display = QtWidgets.QLCDNumber(self.centralwidget)
		self.cycle_display.setMinimumSize(QtCore.QSize(0, 30))
		self.cycle_display.setMaximumSize(QtCore.QSize(16777215, 30))
		self.cycle_display.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.cycle_display.setObjectName("cycle_display")
		self.horizontalLayout_9.addWidget(self.cycle_display)
		self.cycleLabel = QtWidgets.QLabel(self.centralwidget)
		self.cycleLabel.setStyleSheet("color: rgb(255, 255, 255);")
		self.cycleLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
		self.cycleLabel.setObjectName("cycleLabel")
		self.horizontalLayout_9.addWidget(self.cycleLabel)
		self.verticalLayout_3.addLayout(self.horizontalLayout_9)
		self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_5.setObjectName("horizontalLayout_5")
		self.gotoCycle_textBox = QtWidgets.QLineEdit(self.centralwidget)
		self.gotoCycle_textBox.setStyleSheet("background-color: rgb(255, 255, 255);")
		self.gotoCycle_textBox.setObjectName("gotoCycle_textBox")
		self.horizontalLayout_5.addWidget(self.gotoCycle_textBox)
		self.gotoCycle_button = QtWidgets.QPushButton(self.centralwidget)
		self.gotoCycle_button.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(160, 160, 160);")
		self.gotoCycle_button.setObjectName("gotoCycle_button")
		self.horizontalLayout_5.addWidget(self.gotoCycle_button)
		spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.horizontalLayout_5.addItem(spacerItem1)
		self.verticalLayout_3.addLayout(self.horizontalLayout_5)
		self.horizontalLayout_4.addLayout(self.verticalLayout_3)
		self.verticalLayout_7 = QtWidgets.QVBoxLayout()
		self.verticalLayout_7.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
		self.verticalLayout_7.setContentsMargins(5, 0, 0, 0)
		self.verticalLayout_7.setSpacing(0)
		self.verticalLayout_7.setObjectName("verticalLayout_7")
		spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_7.addItem(spacerItem2)
		self.playbackSpeed_label = QtWidgets.QLabel(self.centralwidget)
		self.playbackSpeed_label.setStyleSheet("color: rgb(255, 255, 255);")
		self.playbackSpeed_label.setObjectName("playbackSpeed_label")
		self.verticalLayout_7.addWidget(self.playbackSpeed_label)
		self.playbackSpeed_select = QtWidgets.QComboBox(self.centralwidget)
		self.playbackSpeed_select.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
		self.playbackSpeed_select.setObjectName("playbackSpeed_select")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.playbackSpeed_select.addItem("")
		self.verticalLayout_7.addWidget(self.playbackSpeed_select)
		spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_7.addItem(spacerItem3)
		self.horizontalLayout_4.addLayout(self.verticalLayout_7)
		self.backButton = QtWidgets.QPushButton(self.centralwidget)
		self.backButton.setStyleSheet("color: rgb(0, 0, 0);\n"
"background-color: rgb(0, 160, 61);")
		self.backButton.setObjectName("backButton")
		self.horizontalLayout_4.addWidget(self.backButton)
		self.pauseButton = QtWidgets.QPushButton(self.centralwidget)
		self.pauseButton.setStyleSheet("background-color: rgb(0, 160, 61);\n"
"color: rgb(0,0, 0);")
		self.pauseButton.setObjectName("pauseButton")
		self.horizontalLayout_4.addWidget(self.pauseButton)
		self.playButton = QtWidgets.QPushButton(self.centralwidget)
		self.playButton.setStyleSheet("background-color: rgb(0, 160, 61);\n"
"color: rgb(0,0, 0);")
		self.playButton.setObjectName("playButton")
		self.horizontalLayout_4.addWidget(self.playButton)
		self.fowardButton = QtWidgets.QPushButton(self.centralwidget)
		self.fowardButton.setStyleSheet("background-color: rgb(0, 160, 61);\n"
"color: rgb(0,0, 0);")
		self.fowardButton.setObjectName("fowardButton")
		self.horizontalLayout_4.addWidget(self.fowardButton)
		spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.horizontalLayout_4.addItem(spacerItem4)
		self.horizontalLayout_3.addLayout(self.horizontalLayout_4)
		self.verticalLayout_2.addLayout(self.horizontalLayout_3)
		spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_2.addItem(spacerItem5)
		self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_2.setObjectName("horizontalLayout_2")
		self.cCode_text = QtWidgets.QTextBrowser(self.centralwidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.cCode_text.sizePolicy().hasHeightForWidth())
		self.cCode_text.setSizePolicy(sizePolicy)
		self.cCode_text.setMinimumSize(QtCore.QSize(0, 875))
		self.cCode_text.setStyleSheet("background-color: rgb(50, 51, 45);\ncolor: rbg(255,255,255);")
		self.cCode_text.setObjectName("cCode_text")
		self.horizontalLayout_2.addWidget(self.cCode_text)
		self.assembly_text = QtWidgets.QTextBrowser(self.centralwidget)
		self.assembly_text.setMinimumSize(QtCore.QSize(0, 875))
		self.assembly_text.setStyleSheet("background-color: rgb(50, 51, 45);\ncolor: rbg(255,255,255);")
		self.assembly_text.setObjectName("assembly_text")
		self.horizontalLayout_2.addWidget(self.assembly_text)
		self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_8.setObjectName("horizontalLayout_8")
		self.verticalLayout_10 = QtWidgets.QVBoxLayout()
		self.verticalLayout_10.setObjectName("verticalLayout_10")
		self.horizontalLayout_35 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_35.setObjectName("horizontalLayout_35")
		self.t0reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t0reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t0reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t0reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t0reg_label.setObjectName("t0reg_label")
		self.horizontalLayout_35.addWidget(self.t0reg_label)
		self.t0Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t0Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t0Reg_value.setObjectName("t0Reg_value")
		self.horizontalLayout_35.addWidget(self.t0Reg_value)
		self.t0_varName = QtWidgets.QLabel(self.centralwidget)
		self.t0_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t0_varName.setObjectName("t0_varName")
		self.horizontalLayout_35.addWidget(self.t0_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_35)
		self.horizontalLayout_34 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_34.setObjectName("horizontalLayout_34")
		self.t1reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t1reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t1reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t1reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t1reg_label.setObjectName("t1reg_label")
		self.horizontalLayout_34.addWidget(self.t1reg_label)
		self.t1Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t1Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t1Reg_value.setObjectName("t1Reg_value")
		self.horizontalLayout_34.addWidget(self.t1Reg_value)
		self.t1_varName = QtWidgets.QLabel(self.centralwidget)
		self.t1_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t1_varName.setObjectName("t1_varName")
		self.horizontalLayout_34.addWidget(self.t1_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_34)
		self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_33.setObjectName("horizontalLayout_33")
		self.t2reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t2reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t2reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t2reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t2reg_label.setObjectName("t2reg_label")
		self.horizontalLayout_33.addWidget(self.t2reg_label)
		self.t2Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t2Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t2Reg_value.setObjectName("t2Reg_value")
		self.horizontalLayout_33.addWidget(self.t2Reg_value)
		self.t2_varName = QtWidgets.QLabel(self.centralwidget)
		self.t2_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t2_varName.setObjectName("t2_varName")
		self.horizontalLayout_33.addWidget(self.t2_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_33)
		self.horizontalLayout_32 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_32.setObjectName("horizontalLayout_32")
		self.t3reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t3reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t3reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t3reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);\n"
"")
		self.t3reg_label.setObjectName("t3reg_label")
		self.horizontalLayout_32.addWidget(self.t3reg_label)
		self.t3Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t3Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t3Reg_value.setObjectName("t3Reg_value")
		self.horizontalLayout_32.addWidget(self.t3Reg_value)
		self.t3_varName = QtWidgets.QLabel(self.centralwidget)
		self.t3_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t3_varName.setObjectName("t3_varName")
		self.horizontalLayout_32.addWidget(self.t3_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_32)
		self.horizontalLayout_36 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_36.setObjectName("horizontalLayout_36")
		self.t4reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t4reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t4reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t4reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t4reg_label.setObjectName("t4reg_label")
		self.horizontalLayout_36.addWidget(self.t4reg_label)
		self.t4Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t4Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t4Reg_value.setObjectName("t4Reg_value")
		self.horizontalLayout_36.addWidget(self.t4Reg_value)
		self.t4_varName = QtWidgets.QLabel(self.centralwidget)
		self.t4_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t4_varName.setObjectName("t4_varName")
		self.horizontalLayout_36.addWidget(self.t4_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_36)
		self.horizontalLayout_38 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_38.setObjectName("horizontalLayout_38")
		self.t5reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t5reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t5reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t5reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t5reg_label.setObjectName("t5reg_label")
		self.horizontalLayout_38.addWidget(self.t5reg_label)
		self.t5Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t5Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t5Reg_value.setObjectName("t5Reg_value")
		self.horizontalLayout_38.addWidget(self.t5Reg_value)
		self.t5_varName = QtWidgets.QLabel(self.centralwidget)
		self.t5_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t5_varName.setObjectName("t5_varName")
		self.horizontalLayout_38.addWidget(self.t5_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_38)
		self.horizontalLayout_41 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_41.setObjectName("horizontalLayout_41")
		self.t6reg_label = QtWidgets.QLabel(self.centralwidget)
		self.t6reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.t6reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.t6reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t6reg_label.setObjectName("t6reg_label")
		self.horizontalLayout_41.addWidget(self.t6reg_label)
		self.t6Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.t6Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t6Reg_value.setObjectName("t6Reg_value")
		self.horizontalLayout_41.addWidget(self.t6Reg_value)
		self.t6_varName = QtWidgets.QLabel(self.centralwidget)
		self.t6_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(160, 0, 170, 170);")
		self.t6_varName.setObjectName("t6_varName")
		self.horizontalLayout_41.addWidget(self.t6_varName)
		self.verticalLayout_10.addLayout(self.horizontalLayout_41)
		spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_10.addItem(spacerItem6)
		self.horizontalLayout_8.addLayout(self.verticalLayout_10)
		self.verticalLayout_9 = QtWidgets.QVBoxLayout()
		self.verticalLayout_9.setObjectName("verticalLayout_9")
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.s0reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s0reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s0reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(208, 248, 221))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(81, 121, 94))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(108, 161, 125))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(208, 248, 221))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(208, 248, 221))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(81, 121, 94))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(108, 161, 125))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(208, 248, 221))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(208, 248, 221))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(81, 121, 94))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(108, 161, 125))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(162, 242, 188))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
		self.s0reg_label.setPalette(palette)
		self.s0reg_label.setAutoFillBackground(False)
		self.s0reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s0reg_label.setFrameShape(QtWidgets.QFrame.NoFrame)
		self.s0reg_label.setFrameShadow(QtWidgets.QFrame.Plain)
		self.s0reg_label.setObjectName("s0reg_label")
		self.horizontalLayout.addWidget(self.s0reg_label)
		self.s0Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s0Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s0Reg_value.setObjectName("s0Reg_value")
		self.horizontalLayout.addWidget(self.s0Reg_value)
		self.s0_varName = QtWidgets.QLabel(self.centralwidget)
		self.s0_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s0_varName.setObjectName("s0_varName")
		self.horizontalLayout.addWidget(self.s0_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout)
		self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_15.setObjectName("horizontalLayout_15")
		self.s1reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s1reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s1reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(108, 255, 145))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(54, 248, 102))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 121, 30))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 161, 40))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(127, 248, 157))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(108, 255, 145))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(54, 248, 102))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 121, 30))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 161, 40))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(127, 248, 157))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(108, 255, 145))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(54, 248, 102))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 121, 30))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 161, 40))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 242, 60))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
		self.s1reg_label.setPalette(palette)
		self.s1reg_label.setAutoFillBackground(False)
		self.s1reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s1reg_label.setFrameShape(QtWidgets.QFrame.NoFrame)
		self.s1reg_label.setObjectName("s1reg_label")
		self.horizontalLayout_15.addWidget(self.s1reg_label)
		self.s1Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s1Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s1Reg_value.setObjectName("s1Reg_value")
		self.horizontalLayout_15.addWidget(self.s1Reg_value)
		self.s1_varName = QtWidgets.QLabel(self.centralwidget)
		self.s1_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s1_varName.setObjectName("s1_varName")
		self.horizontalLayout_15.addWidget(self.s1_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_15)
		self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_14.setObjectName("horizontalLayout_14")
		self.s2reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s2reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s2reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 214, 214))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(248, 157, 157))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(121, 50, 50))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(161, 66, 66))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(248, 177, 177))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 214, 214))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(248, 157, 157))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(121, 50, 50))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(161, 66, 66))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(248, 177, 177))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 214, 214))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
		brush = QtGui.QBrush(QtGui.QColor(248, 157, 157))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
		brush = QtGui.QBrush(QtGui.QColor(121, 50, 50))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
		brush = QtGui.QBrush(QtGui.QColor(161, 66, 66))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 131, 171, 170))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
		brush = QtGui.QBrush(QtGui.QColor(242, 100, 100))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
		self.s2reg_label.setPalette(palette)
		self.s2reg_label.setAutoFillBackground(False)
		self.s2reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s2reg_label.setObjectName("s2reg_label")
		self.horizontalLayout_14.addWidget(self.s2reg_label)
		self.s2Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s2Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s2Reg_value.setObjectName("s2Reg_value")
		self.horizontalLayout_14.addWidget(self.s2Reg_value)
		self.s2_varName = QtWidgets.QLabel(self.centralwidget)
		self.s2_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s2_varName.setObjectName("s2_varName")
		self.horizontalLayout_14.addWidget(self.s2_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_14)
		self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_13.setObjectName("horizontalLayout_13")
		self.s3reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s3reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s3reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s3reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s3reg_label.setObjectName("s3reg_label")
		self.horizontalLayout_13.addWidget(self.s3reg_label)
		self.s3Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s3Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s3Reg_value.setObjectName("s3Reg_value")
		self.horizontalLayout_13.addWidget(self.s3Reg_value)
		self.s3_varName = QtWidgets.QLabel(self.centralwidget)
		self.s3_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s3_varName.setObjectName("s3_varName")
		self.horizontalLayout_13.addWidget(self.s3_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_13)
		self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_12.setObjectName("horizontalLayout_12")
		self.s4reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s4reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s4reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s4reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s4reg_label.setObjectName("s4reg_label")
		self.horizontalLayout_12.addWidget(self.s4reg_label)
		self.s4Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s4Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s4Reg_value.setObjectName("s4Reg_value")
		self.horizontalLayout_12.addWidget(self.s4Reg_value)
		self.s4_varName = QtWidgets.QLabel(self.centralwidget)
		self.s4_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s4_varName.setObjectName("s4_varName")
		self.horizontalLayout_12.addWidget(self.s4_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_12)
		self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_11.setObjectName("horizontalLayout_11")
		self.s5reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s5reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s5reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s5reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s5reg_label.setObjectName("s5reg_label")
		self.horizontalLayout_11.addWidget(self.s5reg_label)
		self.s5Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s5Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s5Reg_value.setObjectName("s5Reg_value")
		self.horizontalLayout_11.addWidget(self.s5Reg_value)
		self.s5_varName = QtWidgets.QLabel(self.centralwidget)
		self.s5_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s5_varName.setObjectName("s5_varName")
		self.horizontalLayout_11.addWidget(self.s5_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_11)
		self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_10.setObjectName("horizontalLayout_10")
		self.s6reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s6reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s6reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s6reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s6reg_label.setObjectName("s6reg_label")
		self.horizontalLayout_10.addWidget(self.s6reg_label)
		self.s6Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s6Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s6Reg_value.setObjectName("s6Reg_value")
		self.horizontalLayout_10.addWidget(self.s6Reg_value)
		self.s6_varName = QtWidgets.QLabel(self.centralwidget)
		self.s6_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s6_varName.setObjectName("s6_varName")
		self.horizontalLayout_10.addWidget(self.s6_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_10)
		self.horizontalLayout_21 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_21.setObjectName("horizontalLayout_21")
		self.s7reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s7reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s7reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s7reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s7reg_label.setObjectName("s7reg_label")
		self.horizontalLayout_21.addWidget(self.s7reg_label)
		self.s7Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s7Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s7Reg_value.setObjectName("s7Reg_value")
		self.horizontalLayout_21.addWidget(self.s7Reg_value)
		self.s7_varName = QtWidgets.QLabel(self.centralwidget)
		self.s7_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s7_varName.setObjectName("s7_varName")
		self.horizontalLayout_21.addWidget(self.s7_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_21)
		self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_20.setObjectName("horizontalLayout_20")
		self.s8reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s8reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s8reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s8reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s8reg_label.setObjectName("s8reg_label")
		self.horizontalLayout_20.addWidget(self.s8reg_label)
		self.s8Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s8Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s8Reg_value.setObjectName("s8Reg_value")
		self.horizontalLayout_20.addWidget(self.s8Reg_value)
		self.s8_varName = QtWidgets.QLabel(self.centralwidget)
		self.s8_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s8_varName.setObjectName("s8_varName")
		self.horizontalLayout_20.addWidget(self.s8_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_20)
		self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_19.setObjectName("horizontalLayout_19")
		self.s9reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s9reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s9reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s9reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s9reg_label.setObjectName("s9reg_label")
		self.horizontalLayout_19.addWidget(self.s9reg_label)
		self.s9Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s9Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s9Reg_value.setObjectName("s9Reg_value")
		self.horizontalLayout_19.addWidget(self.s9Reg_value)
		self.s9_varName = QtWidgets.QLabel(self.centralwidget)
		self.s9_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s9_varName.setObjectName("s9_varName")
		self.horizontalLayout_19.addWidget(self.s9_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_19)
		self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_18.setObjectName("horizontalLayout_18")
		self.s10reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s10reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s10reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s10reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s10reg_label.setObjectName("s10reg_label")
		self.horizontalLayout_18.addWidget(self.s10reg_label)
		self.s10Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s10Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s10Reg_value.setObjectName("s10Reg_value")
		self.horizontalLayout_18.addWidget(self.s10Reg_value)
		self.s10_varName = QtWidgets.QLabel(self.centralwidget)
		self.s10_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s10_varName.setObjectName("s10_varName")
		self.horizontalLayout_18.addWidget(self.s10_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_18)
		self.horizontalLayout_42 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_42.setObjectName("horizontalLayout_42")
		self.s11reg_label = QtWidgets.QLabel(self.centralwidget)
		self.s11reg_label.setMinimumSize(QtCore.QSize(30, 50))
		self.s11reg_label.setMaximumSize(QtCore.QSize(30, 16777215))
		self.s11reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s11reg_label.setObjectName("s11reg_label")
		self.horizontalLayout_42.addWidget(self.s11reg_label)
		self.s11Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.s11Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s11Reg_value.setObjectName("s11Reg_value")
		self.horizontalLayout_42.addWidget(self.s11Reg_value)
		self.s11_varName = QtWidgets.QLabel(self.centralwidget)
		self.s11_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(0, 131, 171, 170);")
		self.s11_varName.setObjectName("s11_varName")
		self.horizontalLayout_42.addWidget(self.s11_varName)
		self.verticalLayout_9.addLayout(self.horizontalLayout_42)
		spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_9.addItem(spacerItem7)
		self.horizontalLayout_8.addLayout(self.verticalLayout_9)
		self.verticalLayout_13 = QtWidgets.QVBoxLayout()
		self.verticalLayout_13.setObjectName("verticalLayout_13")
		self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_16.setObjectName("horizontalLayout_16")
		self.a0reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a0reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a0reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a0reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a0reg_label.setObjectName("a0reg_label")
		self.horizontalLayout_16.addWidget(self.a0reg_label)
		self.a0Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a0Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a0Reg_value.setObjectName("a0Reg_value")
		self.horizontalLayout_16.addWidget(self.a0Reg_value)
		self.a0_varName = QtWidgets.QLabel(self.centralwidget)
		self.a0_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a0_varName.setObjectName("a0_varName")
		self.horizontalLayout_16.addWidget(self.a0_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_16)
		self.horizontalLayout_27 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_27.setObjectName("horizontalLayout_27")
		self.a1reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a1reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a1reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a1reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a1reg_label.setObjectName("a1reg_label")
		self.horizontalLayout_27.addWidget(self.a1reg_label)
		self.a1Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a1Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a1Reg_value.setObjectName("a1Reg_value")
		self.horizontalLayout_27.addWidget(self.a1Reg_value)
		self.a1_varName = QtWidgets.QLabel(self.centralwidget)
		self.a1_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a1_varName.setObjectName("a1_varName")
		self.horizontalLayout_27.addWidget(self.a1_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_27)
		self.horizontalLayout_26 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_26.setObjectName("horizontalLayout_26")
		self.a2reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a2reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a2reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a2reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a2reg_label.setObjectName("a2reg_label")
		self.horizontalLayout_26.addWidget(self.a2reg_label)
		self.a2Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a2Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a2Reg_value.setObjectName("a2Reg_value")
		self.horizontalLayout_26.addWidget(self.a2Reg_value)
		self.a2_varName = QtWidgets.QLabel(self.centralwidget)
		self.a2_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a2_varName.setObjectName("a2_varName")
		self.horizontalLayout_26.addWidget(self.a2_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_26)
		self.horizontalLayout_25 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_25.setObjectName("horizontalLayout_25")
		self.a3reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a3reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a3reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a3reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a3reg_label.setObjectName("a3reg_label")
		self.horizontalLayout_25.addWidget(self.a3reg_label)
		self.a3Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a3Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a3Reg_value.setObjectName("a3Reg_value")
		self.horizontalLayout_25.addWidget(self.a3Reg_value)
		self.a3_varName = QtWidgets.QLabel(self.centralwidget)
		self.a3_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a3_varName.setObjectName("a3_varName")
		self.horizontalLayout_25.addWidget(self.a3_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_25)
		self.horizontalLayout_24 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_24.setObjectName("horizontalLayout_24")
		self.a4reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a4reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a4reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a4reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a4reg_label.setObjectName("a4reg_label")
		self.horizontalLayout_24.addWidget(self.a4reg_label)
		self.a4Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a4Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a4Reg_value.setObjectName("a4Reg_value")
		self.horizontalLayout_24.addWidget(self.a4Reg_value)
		self.a4_varName = QtWidgets.QLabel(self.centralwidget)
		self.a4_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a4_varName.setObjectName("a4_varName")
		self.horizontalLayout_24.addWidget(self.a4_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_24)
		self.horizontalLayout_23 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_23.setObjectName("horizontalLayout_23")
		self.a5reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a5reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a5reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a5reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a5reg_label.setObjectName("a5reg_label")
		self.horizontalLayout_23.addWidget(self.a5reg_label)
		self.a5Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a5Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a5Reg_value.setObjectName("a5Reg_value")
		self.horizontalLayout_23.addWidget(self.a5Reg_value)
		self.a5_varName = QtWidgets.QLabel(self.centralwidget)
		self.a5_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a5_varName.setObjectName("a5_varName")
		self.horizontalLayout_23.addWidget(self.a5_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_23)
		self.horizontalLayout_22 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_22.setObjectName("horizontalLayout_22")
		self.a6reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a6reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a6reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a6reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a6reg_label.setObjectName("a6reg_label")
		self.horizontalLayout_22.addWidget(self.a6reg_label)
		self.a6Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a6Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a6Reg_value.setObjectName("a6Reg_value")
		self.horizontalLayout_22.addWidget(self.a6Reg_value)
		self.a6_varName = QtWidgets.QLabel(self.centralwidget)
		self.a6_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a6_varName.setObjectName("a6_varName")
		self.horizontalLayout_22.addWidget(self.a6_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_22)
		self.horizontalLayout_43 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_43.setObjectName("horizontalLayout_43")
		self.a7reg_label = QtWidgets.QLabel(self.centralwidget)
		self.a7reg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.a7reg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.a7reg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a7reg_label.setObjectName("a7reg_label")
		self.horizontalLayout_43.addWidget(self.a7reg_label)
		self.a7Reg_value = QtWidgets.QLabel(self.centralwidget)
		self.a7Reg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a7Reg_value.setObjectName("a7Reg_value")
		self.horizontalLayout_43.addWidget(self.a7Reg_value)
		self.a7_varName = QtWidgets.QLabel(self.centralwidget)
		self.a7_varName.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 180, 0, 170);")
		self.a7_varName.setObjectName("a7_varName")
		self.horizontalLayout_43.addWidget(self.a7_varName)
		self.verticalLayout_13.addLayout(self.horizontalLayout_43)
		spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_13.addItem(spacerItem8)
		self.horizontalLayout_8.addLayout(self.verticalLayout_13)
		self.verticalLayout_11 = QtWidgets.QVBoxLayout()
		self.verticalLayout_11.setObjectName("verticalLayout_11")
		self.horizontalLayout_28 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_28.setObjectName("horizontalLayout_28")
		self.rareg_label = QtWidgets.QLabel(self.centralwidget)
		self.rareg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.rareg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.rareg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.rareg_label.setObjectName("rareg_label")
		self.horizontalLayout_28.addWidget(self.rareg_label)
		self.raReg_value = QtWidgets.QLabel(self.centralwidget)
		self.raReg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.raReg_value.setObjectName("raReg_value")
		self.horizontalLayout_28.addWidget(self.raReg_value)
		self.verticalLayout_11.addLayout(self.horizontalLayout_28)
		self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_31.setObjectName("horizontalLayout_31")
		self.spreg_label = QtWidgets.QLabel(self.centralwidget)
		self.spreg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.spreg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.spreg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.spreg_label.setObjectName("spreg_label")
		self.horizontalLayout_31.addWidget(self.spreg_label)
		self.spReg_value = QtWidgets.QLabel(self.centralwidget)
		self.spReg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.spReg_value.setObjectName("spReg_value")
		self.horizontalLayout_31.addWidget(self.spReg_value)
		self.verticalLayout_11.addLayout(self.horizontalLayout_31)
		self.horizontalLayout_30 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_30.setObjectName("horizontalLayout_30")
		self.gpreg_label = QtWidgets.QLabel(self.centralwidget)
		self.gpreg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.gpreg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.gpreg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.gpreg_label.setObjectName("gpreg_label")
		self.horizontalLayout_30.addWidget(self.gpreg_label)
		self.gpReg_value = QtWidgets.QLabel(self.centralwidget)
		self.gpReg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.gpReg_value.setObjectName("gpReg_value")
		self.horizontalLayout_30.addWidget(self.gpReg_value)
		self.verticalLayout_11.addLayout(self.horizontalLayout_30)
		self.horizontalLayout_44 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_44.setObjectName("horizontalLayout_44")
		self.fpreg_label = QtWidgets.QLabel(self.centralwidget)
		self.fpreg_label.setMinimumSize(QtCore.QSize(25, 50))
		self.fpreg_label.setMaximumSize(QtCore.QSize(25, 16777215))
		self.fpreg_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.fpreg_label.setObjectName("fpreg_label")
		self.horizontalLayout_44.addWidget(self.fpreg_label)
		self.fpReg_value = QtWidgets.QLabel(self.centralwidget)
		self.fpReg_value.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(210, 210, 189, 190);")
		self.fpReg_value.setObjectName("fpReg_value")
		self.horizontalLayout_44.addWidget(self.fpReg_value)
		self.verticalLayout_11.addLayout(self.horizontalLayout_44)
		spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout_11.addItem(spacerItem9)
		self.horizontalLayout_8.addLayout(self.verticalLayout_11)
		self.horizontalLayout_2.addLayout(self.horizontalLayout_8)
		#self.stackView = QtWidgets.QListView(self.centralwidget)
		self.stackView = QtWidgets.QListWidget(self.centralwidget)
		self.stackView.setMinimumSize(QtCore.QSize(150, 875))
		self.stackView.setMaximumSize(QtCore.QSize(150, 16777215))
		self.stackView.setStyleSheet("background-color: rgb(50, 51, 45);\ncolor: rgb(255, 255, 255);")
		self.stackView.setObjectName("stackView")
		self.horizontalLayout_2.addWidget(self.stackView)
		self.verticalLayout_14 = QtWidgets.QVBoxLayout()
		self.verticalLayout_14.setObjectName("verticalLayout_14")
		self.horizontalLayout_2.addLayout(self.verticalLayout_14)
		self.verticalLayout_2.addLayout(self.horizontalLayout_2)
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 1189, 25))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

		####################
		# Custom setup below this separator
		####################

		self.cycle = 0
		self.pauseNotPushed = False

		#Connect buttons to function methods
		self.backButton.clicked.connect(self.backButton_pushed)
		self.pauseButton.clicked.connect(self.pauseButton_pushed)
		self.playButton.clicked.connect(self.playButton_pushed)
		self.fowardButton.clicked.connect(self.fowardButton_pushed)
		self.gotoCycle_button.clicked.connect(self.gotoCycle_button_pushed)

		#Combine register displays into dictionary of display objects
		self.registerDisplays = {}

		self.registerDisplays["t0"] = registerDisplay(self.t0reg_label, self.t0Reg_value, self.t0_varName)
		self.registerDisplays["t1"] = registerDisplay(self.t1reg_label, self.t1Reg_value, self.t1_varName)
		self.registerDisplays["t2"] = registerDisplay(self.t2reg_label, self.t2Reg_value, self.t2_varName)
		self.registerDisplays["t3"] = registerDisplay(self.t3reg_label, self.t3Reg_value, self.t3_varName)
		self.registerDisplays["t4"] = registerDisplay(self.t4reg_label, self.t4Reg_value, self.t4_varName)
		self.registerDisplays["t5"] = registerDisplay(self.t5reg_label, self.t5Reg_value, self.t5_varName)
		self.registerDisplays["t6"] = registerDisplay(self.t6reg_label, self.t6Reg_value, self.t6_varName)
		self.registerDisplays["s0"] = registerDisplay(self.s0reg_label, self.s0Reg_value, self.s0_varName)
		self.registerDisplays["s1"] = registerDisplay(self.s1reg_label, self.s1Reg_value, self.s1_varName)
		self.registerDisplays["s2"] = registerDisplay(self.s2reg_label, self.s2Reg_value, self.s2_varName)
		self.registerDisplays["s3"] = registerDisplay(self.s3reg_label, self.s3Reg_value, self.s3_varName)
		self.registerDisplays["s4"] = registerDisplay(self.s4reg_label, self.s4Reg_value, self.s4_varName)
		self.registerDisplays["s5"] = registerDisplay(self.s5reg_label, self.s5Reg_value, self.s5_varName)
		self.registerDisplays["s6"] = registerDisplay(self.s6reg_label, self.s6Reg_value, self.s6_varName)
		self.registerDisplays["s7"] = registerDisplay(self.s7reg_label, self.s7Reg_value, self.s7_varName)
		self.registerDisplays["s8"] = registerDisplay(self.s8reg_label, self.s8Reg_value, self.s8_varName)
		self.registerDisplays["s9"] = registerDisplay(self.s9reg_label, self.s9Reg_value, self.s9_varName)
		self.registerDisplays["s10"] = registerDisplay(self.s10reg_label, self.s10Reg_value, self.s10_varName)
		self.registerDisplays["s11"] = registerDisplay(self.s11reg_label, self.s11Reg_value, self.s11_varName)
		self.registerDisplays["a0"] = registerDisplay(self.a0reg_label, self.a0Reg_value, self.a0_varName)
		self.registerDisplays["a1"] = registerDisplay(self.a1reg_label, self.a1Reg_value, self.a1_varName)
		self.registerDisplays["a2"] = registerDisplay(self.a2reg_label, self.a2Reg_value, self.a2_varName)
		self.registerDisplays["a3"] = registerDisplay(self.a3reg_label, self.a3Reg_value, self.a3_varName)
		self.registerDisplays["a4"] = registerDisplay(self.a4reg_label, self.a4Reg_value, self.a4_varName)
		self.registerDisplays["a5"] = registerDisplay(self.a5reg_label, self.a5Reg_value, self.a5_varName)
		self.registerDisplays["a6"] = registerDisplay(self.a6reg_label, self.a6Reg_value, self.a6_varName)
		self.registerDisplays["a7"] = registerDisplay(self.a7reg_label, self.a7Reg_value, self.a7_varName)
		self.registerDisplays["ra"] = registerDisplay(self.rareg_label, self.raReg_value, None)
		self.registerDisplays["sp"] = registerDisplay(self.spreg_label, self.spReg_value, None)
		self.registerDisplays["gp"] = registerDisplay(self.gpreg_label, self.gpReg_value, None)
		self.registerDisplays["fp"] = registerDisplay(self.fpreg_label, self.fpReg_value, None)


		#Initialize scope name for stack state
		self.currentScopeName = None
		self.currentStackList = None

		#Add some test elements to the stackView
		'''
		for i in range(7):
			# listElement = QtWidgets.QListWidgetItem(str(i), parent=self.stackView)
			self.stackView.addItem(str(i))

		self.stackView.addItems([str(i) for i in range(9)])
		'''

		#Add some test cCode to text browser



	def backButton_pushed(self):
		if (self.cycle > 0):
			self.cycle += -1

		self.updateGui()

	def pauseButton_pushed(self):
		self.pauseNotPushed = False

	def playButton_pushed(self):
		#Determine cycle step delay
		selectedFrequency = self.playbackSpeed_select.currentText()

		selectedDelay = 10  #in ms
		if (selectedFrequency == "0.5 Hz"):
			selectedDelay = 2000
		elif (selectedFrequency == "1 Hz"):
			selectedDelay = 1000
		elif (selectedFrequency == "2 Hz"):
			selectedDelay = 500
		elif (selectedFrequency == "4 Hz"):
			selectedDelay = 250
		elif (selectedFrequency == "8 Hz"):
			selectedDelay = 125
		elif (selectedFrequency == "16 Hz"):
			selectedDelay = 62.5
		elif (selectedFrequency == "32 Hz"):
			selectedDelay = 31.25
		elif (selectedFrequency == "64 Hz"):
			selectedDelay = 15.625
		elif (selectedFrequency == "128 Hz"):
			selectedDelay = 7.8125

		self.pauseNotPushed = True

		#Increment cycle until paused or max cycles is reached
		while(self.pauseNotPushed):
			self.updateGui()

			QtTest.QTest.qWait(selectedDelay)

			if (self.cycle < g_maxCycles):
				self.cycle += 1
			else:
				self.pauseNotPushed = False


	def fowardButton_pushed(self):
		if (self.cycle < g_maxCycles):
			self.cycle += 1

		self.updateGui()

	def gotoCycle_button_pushed(self):
		self.cycle = int(self.gotoCycle_textBox.text())
		self.updateGui()

	def updateGui(self):
		_translate = QtCore.QCoreApplication.translate

		#Update displayed values
		currentValues = g_cycleMap[self.cycle]

		self.cycle_display.display(self.cycle)
		self.programCounter_display.display(currentValues["programCounter"])

		for regName in self.registerDisplays:
			regDisplay = self.registerDisplays[regName]
			regDisplay.setValueText(currentValues["{}_value".format(regName)])

		#Update register variables
		try:
			usedRegisters = g_registerStateMap[str(currentValues["programCounter"])]
			for regName in self.registerDisplays:
				regDisplay = self.registerDisplays[regName]
				if (regName in usedRegisters):
					regDisplay.setVariableText(usedRegisters[regName])
				else:
					regDisplay.setVariableText("<None>")
		except Exception as e:
			pass

		#Highlight changed values
		if (self.cycle > 0):
			previousValues = g_cycleMap[self.cycle-1]
			for regName in self.registerDisplays:
				valueKey = "{}_value".format(regName)
				regDisplay = self.registerDisplays[regName]

				if (currentValues[valueKey] != previousValues[valueKey]):
					regDisplay.setStyleHighlight()
				else:
					regDisplay.setStyleDefault()

		#Update C code display
		try:
			coord = g_cFileMap[str(currentValues["programCounter"])]
			filepath = coord["file"]
			lineNumber = coord["lineNum"]

			self.cCode_text.setHtml(highlightLine(g_htmlDict[filepath]["htmlList"], lineNumber))

			scrollBar = self.cCode_text.verticalScrollBar()
			scrollLocation = int(scrollBar.maximum() * (float(lineNumber) /float(g_htmlDict[filepath]["fileLength"])))
			scrollBar.setValue(scrollLocation)
		except Exception as e:
			pass

		#Update assembly code display
		try:
			coord = g_asmFileMap[str(currentValues["programCounter"])]
			filepath = coord["file"]
			lineNumber = coord["lineNum"]

			self.assembly_text.setHtml(highlightLine(g_htmlDict[filepath]["htmlList"], lineNumber))

			scrollBar = self.assembly_text.verticalScrollBar()
			scrollLocation = int(scrollBar.maximum() * (float(lineNumber) /float(g_htmlDict[filepath]["fileLength"])))
			scrollBar.setValue(scrollLocation)
		except Exception as e:
			pass

		#Update stack display
		try:
			newScopeName = next(iter(g_stackStateMap[str(currentValues["programCounter"])]))
			stackItems = [str(i) for i in g_stackStateMap[str(currentValues["programCounter"])][newScopeName]]
			self.stackItems = [newScopeName] + stackItems

			for i in range(self.stackView.count()):
				self.stackView.takeItem(0)	
			self.stackView.addItems(self.stackItems)
			self.stackView.scrollToBottom()
		except Exception as e:
			pass



	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "SC Debugger"))
		self.programCounterLabel.setText(_translate("MainWindow", "Program Counter"))
		self.cycleLabel.setText(_translate("MainWindow", "Cycle"))
		self.gotoCycle_button.setText(_translate("MainWindow", "Go To Cycle"))
		self.playbackSpeed_label.setText(_translate("MainWindow", "Playback Speed"))
		self.playbackSpeed_select.setItemText(0, _translate("MainWindow", "0.5 Hz"))
		self.playbackSpeed_select.setItemText(1, _translate("MainWindow", "1 Hz"))
		self.playbackSpeed_select.setItemText(2, _translate("MainWindow", "2 Hz"))
		self.playbackSpeed_select.setItemText(3, _translate("MainWindow", "4 Hz"))
		self.playbackSpeed_select.setItemText(4, _translate("MainWindow", "8 Hz"))
		self.playbackSpeed_select.setItemText(5, _translate("MainWindow", "16 Hz"))
		self.playbackSpeed_select.setItemText(6, _translate("MainWindow", "32 Hz"))
		self.playbackSpeed_select.setItemText(7, _translate("MainWindow", "64 Hz"))
		self.playbackSpeed_select.setItemText(8, _translate("MainWindow", "128 Hz"))
		self.backButton.setToolTip(_translate("MainWindow", "Rewind a single cycle"))
		self.backButton.setText(_translate("MainWindow", "Back"))
		self.pauseButton.setToolTip(_translate("MainWindow", "Pause cycle incrementing"))
		self.pauseButton.setText(_translate("MainWindow", "Pause"))
		self.playButton.setToolTip(_translate("MainWindow", "Increment displayed cylce at the speficied playback frequency"))
		self.playButton.setText(_translate("MainWindow", "Play"))
		self.fowardButton.setToolTip(_translate("MainWindow", "Increment a single cycle"))
		self.fowardButton.setText(_translate("MainWindow", "Foward"))
		self.t0reg_label.setText(_translate("MainWindow", "t0"))
		self.t0Reg_value.setText(_translate("MainWindow", "t0_value"))
		self.t0_varName.setText(_translate("MainWindow", "t0_var"))
		self.t1reg_label.setText(_translate("MainWindow", "t1"))
		self.t1Reg_value.setText(_translate("MainWindow", "t1_value"))
		self.t1_varName.setText(_translate("MainWindow", "t1_var"))
		self.t2reg_label.setText(_translate("MainWindow", "t2"))
		self.t2Reg_value.setText(_translate("MainWindow", "t2_value"))
		self.t2_varName.setText(_translate("MainWindow", "t2_var"))
		self.t3reg_label.setText(_translate("MainWindow", "t3"))
		self.t3Reg_value.setText(_translate("MainWindow", "t3_value"))
		self.t3_varName.setText(_translate("MainWindow", "t3_var"))
		self.t4reg_label.setText(_translate("MainWindow", "t4"))
		self.t4Reg_value.setText(_translate("MainWindow", "t4_value"))
		self.t4_varName.setText(_translate("MainWindow", "t4_var"))
		self.t5reg_label.setText(_translate("MainWindow", "t5"))
		self.t5Reg_value.setText(_translate("MainWindow", "t5_value"))
		self.t5_varName.setText(_translate("MainWindow", "t5_var"))
		self.t6reg_label.setText(_translate("MainWindow", "t6"))
		self.t6Reg_value.setText(_translate("MainWindow", "t6_value"))
		self.t6_varName.setText(_translate("MainWindow", "t6_var"))
		self.s0reg_label.setText(_translate("MainWindow", "s0"))
		self.s0Reg_value.setText(_translate("MainWindow", "s0_value"))
		self.s0_varName.setText(_translate("MainWindow", "s0_var"))
		self.s1reg_label.setText(_translate("MainWindow", "s1"))
		self.s1Reg_value.setText(_translate("MainWindow", "s1_value"))
		self.s1_varName.setText(_translate("MainWindow", "s1_var"))
		self.s2reg_label.setText(_translate("MainWindow", "s2"))
		self.s2Reg_value.setText(_translate("MainWindow", "s2_value"))
		self.s2_varName.setText(_translate("MainWindow", "s2_var"))
		self.s3reg_label.setText(_translate("MainWindow", "s3"))
		self.s3Reg_value.setText(_translate("MainWindow", "s3_value"))
		self.s3_varName.setText(_translate("MainWindow", "s3_var"))
		self.s4reg_label.setText(_translate("MainWindow", "s4"))
		self.s4Reg_value.setText(_translate("MainWindow", "s4_value"))
		self.s4_varName.setText(_translate("MainWindow", "s4_var"))
		self.s5reg_label.setText(_translate("MainWindow", "s5"))
		self.s5Reg_value.setText(_translate("MainWindow", "s5_value"))
		self.s5_varName.setText(_translate("MainWindow", "s5_var"))
		self.s6reg_label.setText(_translate("MainWindow", "s6"))
		self.s6Reg_value.setText(_translate("MainWindow", "s6_value"))
		self.s6_varName.setText(_translate("MainWindow", "s6_var"))
		self.s7reg_label.setText(_translate("MainWindow", "s7"))
		self.s7Reg_value.setText(_translate("MainWindow", "s7_value"))
		self.s7_varName.setText(_translate("MainWindow", "s7_var"))
		self.s8reg_label.setText(_translate("MainWindow", "s8"))
		self.s8Reg_value.setText(_translate("MainWindow", "s8_value"))
		self.s8_varName.setText(_translate("MainWindow", "s8_var"))
		self.s9reg_label.setText(_translate("MainWindow", "s9"))
		self.s9Reg_value.setText(_translate("MainWindow", "s9_value"))
		self.s9_varName.setText(_translate("MainWindow", "s9_var"))
		self.s10reg_label.setText(_translate("MainWindow", "s10"))
		self.s10Reg_value.setText(_translate("MainWindow", "s10_value"))
		self.s10_varName.setText(_translate("MainWindow", "s10_var"))
		self.s11reg_label.setText(_translate("MainWindow", "s11"))
		self.s11Reg_value.setText(_translate("MainWindow", "s11_value"))
		self.s11_varName.setText(_translate("MainWindow", "s11_var"))
		self.a0reg_label.setText(_translate("MainWindow", "a0"))
		self.a0Reg_value.setText(_translate("MainWindow", "a0_value"))
		self.a0_varName.setText(_translate("MainWindow", "a0_var"))
		self.a1reg_label.setText(_translate("MainWindow", "a1"))
		self.a1Reg_value.setText(_translate("MainWindow", "a1_value"))
		self.a1_varName.setText(_translate("MainWindow", "a1_var"))
		self.a2reg_label.setText(_translate("MainWindow", "a2"))
		self.a2Reg_value.setText(_translate("MainWindow", "a2_value"))
		self.a2_varName.setText(_translate("MainWindow", "a2_var"))
		self.a3reg_label.setText(_translate("MainWindow", "a3"))
		self.a3Reg_value.setText(_translate("MainWindow", "a3_value"))
		self.a3_varName.setText(_translate("MainWindow", "a3_var"))
		self.a4reg_label.setText(_translate("MainWindow", "a4"))
		self.a4Reg_value.setText(_translate("MainWindow", "a4_value"))
		self.a4_varName.setText(_translate("MainWindow", "a4_var"))
		self.a5reg_label.setText(_translate("MainWindow", "a5"))
		self.a5Reg_value.setText(_translate("MainWindow", "a5_value"))
		self.a5_varName.setText(_translate("MainWindow", "a5_var"))
		self.a6reg_label.setText(_translate("MainWindow", "a6"))
		self.a6Reg_value.setText(_translate("MainWindow", "a6_value"))
		self.a6_varName.setText(_translate("MainWindow", "a6_var"))
		self.a7reg_label.setText(_translate("MainWindow", "a7"))
		self.a7Reg_value.setText(_translate("MainWindow", "a7_value"))
		self.a7_varName.setText(_translate("MainWindow", "a7_var"))
		self.rareg_label.setText(_translate("MainWindow", "ra"))
		self.raReg_value.setText(_translate("MainWindow", "ra_value"))
		self.spreg_label.setText(_translate("MainWindow", "sp"))
		self.spReg_value.setText(_translate("MainWindow", "sp_value"))
		self.gpreg_label.setText(_translate("MainWindow", "gp"))
		self.gpReg_value.setText(_translate("MainWindow", "gp_value"))
		self.fpreg_label.setText(_translate("MainWindow", "fp"))
		self.fpReg_value.setText(_translate("MainWindow", "fp_value"))


if __name__ == "__main__":
	#########
	# Read command line arguments
	#########
	helpdesc = '''
Help yourself
'''

	parser = argparse.ArgumentParser(description = helpdesc)

	parser.add_argument("vcd", action="store", help="Filepath to vcd dump file")
	parser.add_argument("-a", action="store", dest="annotationPath", help="Path to debugger annotation file produced by compiler or assembler. Used to view step-by-step C Code and assembly in debugger gui")
	parser.add_argument("-cfg", action="store", dest="configPath", default="/home/jose/Documents/gitRepos/scratchComputer/pythonScripts/vcdDebugger/debuggerConfig.json", help="Path to debugger config file")
	
	arguments = parser.parse_args()

	vcdFilePath = arguments.vcd
	annotationPath = arguments.annotationPath
	configPath = arguments.configPath
	
	#########
	# Parse VCD dump file
	#########
	global g_cycleMap
	g_cycleMap = getCycleMap(vcdFilePath, configPath)
	global g_maxCycles
	g_maxCycles = len(g_cycleMap)-1

	#print(utils.dictToJson(g_cycleMap))
	#sys.exit()


	#########
	# Parse annotation file
	#########
	if (annotationPath):
		annotationDict = utils.jsonToDict(annotationPath)

		global g_cFileMap
		if ("cFileMap" in annotationDict):
			g_cFileMap = annotationDict["cFileMap"]

			for pcKey in g_cFileMap:
				coord = g_cFileMap[pcKey]
				filepath = coord["file"]

				if (filepath in g_htmlDict):
					pass
				else:
					g_htmlDict[filepath] = {}
					g_htmlDict[filepath]["htmlList"] = fileToHtmlList(filepath, fileType="C")
					g_htmlDict[filepath]["fileLength"] = len(g_htmlDict[filepath]["htmlList"])-2
		else:
			g_cFileMap = None

		global g_asmFileMap
		if ("asmFileMap" in annotationDict):
			g_asmFileMap = annotationDict["asmFileMap"]

			for pcKey in g_asmFileMap:
				coord = g_asmFileMap[pcKey]
				filepath = coord["file"]

				if (filepath in g_htmlDict):
					pass
				else:
					g_htmlDict[filepath] = {}
					g_htmlDict[filepath]["htmlList"] = fileToHtmlList(filepath, fileType="asm")
					g_htmlDict[filepath]["fileLength"] = len(g_htmlDict[filepath]["htmlList"])-2
					#print(utils.dictToJson(g_htmlDict[filepath]))
		else:
			g_asmFileMap = None

		global g_registerStateMap
		if ("scopeStateMap" in annotationDict):
			g_registerStateMap = {}
			for programCounterStr in annotationDict["scopeStateMap"]:
				scopeState = annotationDict["scopeStateMap"][programCounterStr]

				usedRegisters = {}
				if isinstance(scopeState, int):
					referenceIndex = int(programCounterStr)+(scopeState*4)
					usedRegisters = annotationDict["scopeStateMap"][str(referenceIndex)]["usedRegisters"]
				else:
					usedRegisters = scopeState["usedRegisters"]

				g_registerStateMap[programCounterStr] = usedRegisters
		else:
			g_registerStateMap = None

		global g_stackStateMap
		if ("scopeStateMap" in annotationDict):
			g_stackStateMap = {}
			for programCounterStr in annotationDict["scopeStateMap"]:
				scopeState = annotationDict["scopeStateMap"][programCounterStr]

				stackState = {}
				if isinstance(scopeState, int):
					referenceIndex = int(programCounterStr)+(scopeState*4)
					stackState = {annotationDict["scopeStateMap"][str(referenceIndex)]["scope"]["name"]: annotationDict["scopeStateMap"][str(referenceIndex)]["localStack"]}
				else:
					stackState = {scopeState["scope"]["name"]: scopeState["localStack"]}

				g_stackStateMap[programCounterStr] = stackState
		else:
			g_stackStateMap = None



		#print(utils.dictToJson(g_stackStateMap))
		#sys.exit()

	

	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())

