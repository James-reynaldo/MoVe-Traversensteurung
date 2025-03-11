from Manual_Overwrite import Ui_ManualOverwrite
from PyQt5.QtWidgets import QWidget

class Manual_Ovewrite_Window(QWidget, Ui_ManualOverwrite):
    def __init__(self, toplevel_manual_overwrite):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start_manual_overwrite)
        self.toplevel_manual_overwrite = toplevel_manual_overwrite
        self.spinBox.setRange(-1000,1000)
        self.spinBox_2.setRange(-1000,1000)
        self.spinBox_3.setRange(-1000,1000)
        self.spinBox_4.setRange(-1000,1000)

    def start_manual_overwrite(self):
        self.stepsstepper1 = self.spinBox.value()
        self.stepsstepper2 = self.spinBox_2.value()
        self.stepsstepper3 = self.spinBox_3.value()
        self.stepsstepper4 = self.spinBox_4.value()
        stepper_dict = {
        self.label.text(): self.stepsstepper1,
        self.label_2.text(): self.stepsstepper2,
        self.label_3.text(): self.stepsstepper3,
        self.label_4.text(): self.stepsstepper4
    }
        self.toplevel_manual_overwrite(stepper_dict)
        self.close()
    
