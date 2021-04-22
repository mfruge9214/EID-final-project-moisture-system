import sys


from PyQt5.QtWidgets import QMainWindow, QApplication , QDialog
from PAWS_MainInterface import Ui_MainWindow
import CreateSensorWindow
import EditSensorWindow



class AppWindow(QMainWindow): 
	def __init__(self):
		super().__init__() 
		self.ui=  Ui_MainWindow()
		self.ui.setupUi(self)
		self.initApp()
		self.show()


	def initApp(self):

		# Setup UI for new sensor button press
		self.createSensorWindow = QDialog()
		self.createSensorWindow_ui = CreateSensorWindow.Ui_Dialog()
		self.createSensorWindow_ui.setupUi(self.createSensorWindow)

		#Setup UI for edit sensor button press

		self.editSensorWindow = QDialog()
		self.editSensorWindow_ui = EditSensorWindow.Ui_Dialog()
		self.editSensorWindow_ui.setupUi(self.editSensorWindow)


		# Register all the event callback functions
		self.ui.addSensor_PB.clicked.connect(self.showCreateSensorWindow)
		self.ui.editSensor_PB.clicked.connect(self.showEditSensorWindow)


	def showCreateSensorWindow(self):
		self.createSensorWindow.show()


	def showEditSensorWindow(self):
		self.editSensorWindow.show()
	

app = QApplication(sys.argv)
w = AppWindow()
w.show() 
sys.exit(app.exec_())