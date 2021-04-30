import sys

import requests

from PyQt5.QtWidgets import QMainWindow, QApplication , QDialog, QRadioButton, QCheckBox, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from PAWS_MainInterface import Ui_MainWindow
import CreateSensorWindow
import EditSensorWindow


import json


groupsEnabled = 0
# Create a class for application error emitting



def scaleValuesUp(value):
	value = int(value)
	return 200 + (value * 8)


def scaleValuesDown(value):
	value = int(value)
	return int((value -200)/8)

class customError(QObject):

	nameError = pyqtSignal()
	idError	  = pyqtSignal()
	valError  = pyqtSignal()
	editError = pyqtSignal()
	selectionError = pyqtSignal()


class AppWindow(QMainWindow): 
	def __init__(self):
		super().__init__() 
		self.ui=  Ui_MainWindow()
		self.ui.setupUi(self)
		self.initApp()
		self.show()


	def initApp(self):

		self.sensorList = []
		self.selectedSensor = None
		self.errorEvt = customError()
		self.errorEvt.nameError.connect(self.nameErrorHandler)
		self.errorEvt.editError.connect(self.editErrorHandler)
		self.errorEvt.idError.connect(self.idErrorHandler)
		self.errorEvt.selectionError.connect(self.selectionErrorHandler)
		# self.errorEvt.valError.connect(self.valErrorHandler)
		self.initSubwindows()
		self.initSensorList()




		# Register all the event callback functions
		self.ui.addSensor_PB.clicked.connect(self.subWindowOpened)
		self.ui.editSensor_PB.clicked.connect(self.subWindowOpened)
		self.ui.control_WaterOn.clicked.connect(self.waterOnPressed)
		self.ui.control_WaterOff.clicked.connect(self.waterOffPressed)
		self.ui.control_Reset.clicked.connect(self.resetSensorPressed)


		self.updateTimer = QTimer()

		self.updateTimer.timeout.connect(self.dataGetReq)
		self.updateTimer.start(10000)


		self.initOutputs()



	def initSubwindows(self):

		self.createSensorWindow = QDialog()
		self.createSensorWindow_ui = CreateSensorWindow.Ui_Dialog()
		self.createSensorWindow_ui.setupUi(self.createSensorWindow)


		self.editSensorWindow = QDialog()
		self.editSensorWindow_ui = EditSensorWindow.Ui_Dialog()
		self.editSensorWindow_ui.setupUi(self.editSensorWindow)


		self.subwindows = [self.createSensorWindow, self.editSensorWindow]

		self.windowInputFields = {

					"createSensor" : [self.createSensorWindow_ui.newSensorName, 
										self.createSensorWindow_ui.targetHumiditySpinBox, 
										self.createSensorWindow_ui.newSensorID],


					"editSensor"   : [self.editSensorWindow_ui.editSensorName, 
									self.editSensorWindow_ui.editTargetHumiditySpinBox]


		}

		self.windowButtons = [self.ui.addSensor_PB, self.ui.editSensor_PB]


		self.createSensorWindow_ui.createSensorSave.clicked.connect(self.subWindowSaved)
		self.createSensorWindow_ui.createSensorCancel.clicked.connect(self.subWindowClosed)

		self.editSensorWindow_ui.editSensorSave.clicked.connect(self.subWindowSaved)
		self.editSensorWindow_ui.editSensorCancel.clicked.connect(self.subWindowClosed)


	def nameErrorHandler(self):

		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Information)
		msgBox.setText("Please Enter a Unique Sensor Name")
		msgBox.setWindowTitle("Name Error")
		msgBox.setStandardButtons(QMessageBox.Ok)

		returnValue = msgBox.exec()


	def editErrorHandler(self):

		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Information)
		msgBox.setText("There are no sensors to edit")
		msgBox.setWindowTitle("No Sensor Selected Error")
		msgBox.setStandardButtons(QMessageBox.Ok)

		returnValue = msgBox.exec()
		self.subWindowClosed()


	def idErrorHandler(self):

		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Information)
		msgBox.setText("Invalid Sensor ID. Please check the device for the Unique ID")
		msgBox.setWindowTitle("Sensor ID Error")
		msgBox.setStandardButtons(QMessageBox.Ok)

		returnValue = msgBox.exec()


	def selectionErrorHandler(self):

		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Information)
		msgBox.setText("Please Select A Sensor")
		msgBox.setWindowTitle("No Sensor Selected Error")
		msgBox.setStandardButtons(QMessageBox.Ok)

		returnValue = msgBox.exec()



	def initSensorList(self):



		resp = requests.get("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/targets")

		response = resp.json()

		for entry in response['Items']:

			newSensor = {
			"SensorName" : None,
			"SensorID"	: None,
			"Target": None,
			"buttonObject": None
			}

			for item in entry.items():
				key = None
				value = None
				s = (item)

				for thing in s:

					if(type(thing) is str):
						key = thing
					else:
						for x, y in thing.items():
							value = y

				newSensor[key] = value
				
				# Create the button object to display
			radioButton = QRadioButton("sensorRB_" + newSensor['SensorID'])
			radioButton.setText(newSensor['SensorName'])
			self.ui.sensorSelectionLayout.addWidget(radioButton)

			# Connect the button to sensor button handler
			radioButton.clicked.connect(self.sensorSelectChanged)

			newSensor['buttonObject'] = radioButton

			self.sensorList.append(newSensor)



	def newSensorSaved(self):

		newSensor = {
				"SensorName" : None,
				"SensorID"	: None,
				"Target": None,
				"buttonObject": None
		}

		# Grab all the input data from the window
		

		for field in self.windowInputFields["createSensor"]:

			index = self.windowInputFields["createSensor"].index(field)

			if(index == 0):
				newSensor['SensorName'] = field.text()

			elif(index == 1):
				newSensor["Target"] = field.value()

			elif(index == 2):
				newSensor["SensorID"] = field.text()



		# Should ensure that sensor name and ID are unique, and allow application to continue or not
		for sensor in self.sensorList:

			(existingName, existingID) = (sensor["SensorName"], sensor["SensorID"])

			if(newSensor['SensorName'] == existingName):

				print("Error: Sensor Name is not unique. Please try a different name")
				self.errorEvt.nameError.emit()
				return

			if(newSensor['SensorID'] == existingID):

				print("Error: Sensor ID is not unique")
				self.errorEvt.idError.emit()




		# Create the button object to display
		radioButton = QRadioButton("sensorRB_" + newSensor['SensorID'])
		radioButton.setText(newSensor['SensorName'])
		self.ui.sensorSelectionLayout.addWidget(radioButton)

		# Connect the button to sensor button handler
		radioButton.clicked.connect(self.sensorSelectChanged)

		newSensor['buttonObject'] = radioButton


		newSensorPostData = {}

		for key, value in newSensor.items():

			if key != "buttonObject":
				if key != "SensorID":
					newSensorPostData[key] = value
					if key == "Target":
						newSensorPostData[key] = scaleValuesUp(value)

		resp = requests.post("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/" + newSensor['SensorID'], json = newSensorPostData)

				# Add the sensor to the local list
		self.sensorList.append(newSensor)


		self.subWindowClosed()



	def initOutputs(self):

		self.displays = {

					'currentHum': self.ui.output_CurrentHumidity,
					'Target'	: self.ui.output_TargetHumidity
		}


		for display in self.displays.values():
			display.setText("No Data to Show")




	def sensorSelectChanged(self):

		clicked_btn = self.sender()

		for sensor in self.sensorList:

			if(clicked_btn == sensor["buttonObject"]):
				print("Sensor Selected")
				self.selectedSensor = sensor


	def sensorEditsSaved(self):

		for field in self.windowInputFields["editSensor"]:

			index = self.windowInputFields["editSensor"].index(field)


			if(index == 0):
				self.selectedSensor['SensorName'] = field.text()

			elif(index == 1):
				self.selectedSensor["Target"] = field.value()

			elif(index == 2):
				# self.selectedSensor["SensorID"] = field.text()
				break


		sensorPutData = {}

		for key, value in self.selectedSensor.items():

			if key != 'buttonObject':
				if key != 'SensorID': 
					sensorPutData[key] = value
					if key == "Target":
						sensorPutData[key] = scaleValuesUp(value)
					

		resp = requests.put("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/" + self.selectedSensor['SensorID'], json = sensorPutData)


		self.selectedSensor['buttonObject'].setText(self.selectedSensor['SensorName'])
		

		self.subWindowClosed()


	def subWindowOpened(self):


		self.hide()

		windowIdx = self.windowButtons.index(self.sender())

		self.window = self.subwindows[windowIdx]

		self.window.show()

		self.subWindowInit()

		


	def subWindowInit(self):

		# if(self.window == self.createSensorWindow):

			# for field in self.windowInputFields["createSensor"]:

			# 	index = self.windowInputFields["createSensor"].index(field)

			# 	if(index == 0):
					

			# 	elif(index == 1):
					

			# 	elif(index == 2):
					
		if(self.window == self.editSensorWindow):

			if(self.selectedSensor != None):

				for field in self.windowInputFields["editSensor"]:

					index = self.windowInputFields["editSensor"].index(field)

					if(index == 0):

						field.setText(str(self.selectedSensor["SensorName"]))

					if(index == 1):

						field.setValue(int(self.selectedSensor["Target"]))

					if(index == 2):
						# Top level define to control groups
						if(groupsEnabled):
							break

			else:
				self.errorEvt.editError.emit()




	def dataGetReq(self):

		if(self.selectedSensor):

			print("Getting data")
			resp = requests.get("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/" + self.selectedSensor['SensorID'])

			response = resp.json()

			maxMeasID = 0
			maxMeasIdx = 0

			print(response)

			for entry in response['Items']:

				if(entry['SensorID']['N'] == self.selectedSensor['SensorID']):

					print(maxMeasID)
					print(maxMeasIdx)

					print(entry)
					if(int(entry['MeasurementID']['N']) > maxMeasID):

						maxMeasID = int(entry['MeasurementID']['N'])

						maxMeasIdx = response['Items'].index(entry)


			data = response['Items'][maxMeasIdx]


			self.displays['currentHum'].setText(str(scaleValuesDown(data['Humidity']['N'])))

			try:
				self.displays['Target'].setText(str(scaleValuesDown(data['Target']['S'])))

			except:
				self.displays['Target'].setText(str(scaleValuesDown(data['Target']['N'])))




	def waterOnPressed(self):

		try:
			print("Pressed")
			resp = requests.post("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/" + self.selectedSensor['SensorID'] + "/water/on")

			print(resp)
		except:
			self.errorEvt.selectionError.emit()

	def waterOffPressed(self):

		try:
			print("Off Pressed")

			resp = requests.post("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/" + self.selectedSensor['SensorID'] + "/water/off")

			print(resp)

		except:
			self.errorEvt.selectionError.emit()

	def resetSensorPressed(self):

		try:
			print("Sensor Reset")

			resp = requests.post("https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/" + self.selectedSensor['SensorID'] + "/reset")

			print(resp)

		except:
			self.errorEvt.selectionError.emit()


	def subWindowSaved(self):

		if(self.sender() == self.createSensorWindow_ui.createSensorSave):
			self.newSensorSaved()

		elif(self.sender() == self.editSensorWindow_ui.editSensorSave):
			self.sensorEditsSaved()


		else:
			print("Unhandled Button Press")




	def subWindowClosed(self):

		self.window.hide()

		self.show()


	def subWindowRestore(self):
		self.window.show()







app = QApplication(sys.argv)
w = AppWindow()
w.show() 
sys.exit(app.exec_())