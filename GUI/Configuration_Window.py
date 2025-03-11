from Configuration import Ui_Configuration
from PyQt5.QtWidgets import QDialog

class Configuration_Window(QDialog, Ui_Configuration):
    def __init__(self):
        super().__init__()
        self.setupUi(self)