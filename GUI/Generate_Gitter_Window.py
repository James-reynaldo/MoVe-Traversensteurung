from UI_Generate_Gitter import Ui_GenerateGitter
from PyQt5.QtWidgets import QDialog

class Generate_Gitter_Window(QDialog, Ui_GenerateGitter):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.radStart = 0
        self.radEnd = 0
        self.radSteps = 0
        self.angStart = 0
        self.angEnd = 0
        self.angSteps = 0
    def getValues(self):
        self.radStart = self.spinBox.value()
        self.radEnd = self.spinBox2.value()
        self.radSteps = self.spinBox3.value()
        self.angStart = self.spinBox4.value()
        self.angEnd = self.spinBox5.value()
        self.angSteps = self.spinBox6.value()
        self.close()
