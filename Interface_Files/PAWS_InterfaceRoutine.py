import sys


from PyQt5.QtWidgets import QMainWindow, QApplication , QDialog, QRadioButton, QCheckBox, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from PAWS_MainInterface import Ui_MainWindow
import CreateSensorWindow
import EditSensorWindow



groupsEnabled = 0
# Create a class for application error emitting

class customError(QObject):

	nameError = pyqtSignal()
	idError	  = pyqtSignal()
	valError  = pyqtSignal()
	editError = pyqtSignal()


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
		# self.errorEvt.valError.connect(self.valErrorHandler)
		self.initSubwindows()




		# Register all the event callback functions
		self.ui.addSensor_PB.clicked.connect(self.subWindowOpened)
		self.ui.editSensor_PB.clicked.connect(self.subWindowOpened)

		# self.subwindows = {

		# 	1: self.createSensorWindow,
		# 	2: self.editSensorWindow
		# } 



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
									self.editSensorWindow_ui.editTargetHumiditySpinBox, 
									self.editSensorWindow_ui.assignGroupDropdown]


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


	def newSensorSaved(self):

		newSensor = {
				"sensorName" : None,
				"sensorID"	: None,
				"targetHumidity": None,
				"buttonObject": None
		}

		# Grab all the input data from the window
		

		for field in self.windowInputFields["createSensor"]:

			index = self.windowInputFields["createSensor"].index(field)

			if(index == 0):
				newSensor['sensorName'] = field.text()

			elif(index == 1):
				newSensor["targetHumidity"] = field.value()

			elif(index == 2):
				newSensor["sensorID"] = field.text()



		# Should ensure that sensor name and ID are unique, and allow application to continue or not
		for sensor in self.sensorList:

			(existingName, existingID) = (sensor["sensorName"], sensor["sensorID"])

			if(newSensor['sensorName'] == existingName):

				print("Error: Sensor Name is not unique. Please try a different name")
				self.errorEvt.nameError.emit()
				return

			if(newSensor['sensorID'] == existingID):

				print("Error: Sensor ID is not unique")
				self.errorEvt.idError.emit()




		# Create the button object to display
		radioButton = QRadioButton("sensorRB_" + newSensor['sensorID'])
		radioButton.setText(newSensor['sensorName'])
		self.ui.sensorSelectionLayout.addWidget(radioButton)

		# Connect the button to sensor button handler
		radioButton.clicked.connect(self.sensorSelectChanged)

		newSensor['buttonObject'] = radioButton

		# Add the sensor to the local list
		self.sensorList.append(newSensor)


		self.subWindowClosed()



	def sensorSelectChanged(self):

		clicked_btn = self.sender()

		for sensor in self.sensorList:

			if(clicked_btn == sensor["buttonObject"]):

				self.selectedSensor = sensor


	def sensorEditsSaved(self):

		for field in self.windowInputFields["editSensor"]:

			index = self.windowInputFields["editSensor"].index(field)


			if(index == 0):
				self.selectedSensor['sensorName'] = field.text()

			elif(index == 1):
				self.selectedSensor["targetHumidity"] = field.value()

			elif(index == 2):
				# self.selectedSensor["sensorID"] = field.text()
				break

		self.selectedSensor['buttonObject'].setText(self.selectedSensor['sensorName'])

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

						field.setText(self.selectedSensor["sensorName"])

					if(index == 1):

						field.setValue(self.selectedSensor["targetHumidity"])

					if(index == 2):
						# Top level define to control groups
						if(groupsEnabled):
							break

			else:
				self.errorEvt.editError.emit()





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