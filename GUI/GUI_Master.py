import sys


from PyQt5.QtWidgets import (

    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog

)

from PyQt5.uic import loadUi


from py_files.QT_Project import Ui_MainWindow

from Manual_Overwrite_Window import Manual_Ovewrite_Window
from Generate_Gitter_Window import Generate_Gitter_Window
from Configuration_Window import Configuration_Window

import numpy as np
import file_operations
import Grid
import Serial_Com_Dummy
import time
from PyQt5 import QtCore

class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setupUi(self)
        self.current_pos= [100,30]


        self.manual_overwrite_window = None
        self.generate_gitter_window = None
        self.configuration_window = None

        self.grid = Grid.Grid("output.txt")
        self.Serial_Com = Serial_Com_Dummy.SerialCtrl()
        # Widget 2 is matplotlib figure

        self.comboBox.addItems(self.Serial_Com.com_list)

        # Set information on Double Spin Box (Float input gadgets)
        self.settings = file_operations.load_settings()
        self.clear_points()
        self.doubleSpinBox.setRange(self.settings["dimensions"]["min_deflection"], self.settings["dimensions"]["max_deflection"])
        self.doubleSpinBox_2.setRange(self.settings["dimensions"]["inner_radius"], self.settings["dimensions"]["outer_radius"])

        self.widget_2.reload_plot(self.grid, self.settings)
        #self.connectSignalsSlots()

        self.init_value_encoder_radial=None
        self.init_value_encoder_angular = None
        self.last_value_encoder_radial=None
        self.last_value_encoder_angular = None

        self.status = "Disconnected"
        self.textEdit_2.setText(self.status)

    # Based on: https://www.pythonguis.com/tutorials/creating-multiple-windows/ (zuletzt aufgerufen am: 06.04.2024)
    def show_manual_overwrite(self):
        if self.manual_overwrite_window is None:  # open Window if clicked.
            self.manual_overwrite_window = Manual_Ovewrite_Window(self.start_manual_overwrite)
            self.manual_overwrite_window.show()
        else:  # Close Window if clicked again.
            self.manual_overwrite_window = None

    def show_generate_gitter(self):
        if self.generate_gitter_window is None:  # open Window if clicked.
            self.generate_gitter_window = Generate_Gitter_Window()
            self.generate_gitter_window.exec_()
            rad_inc = self.generate_gitter_window.radSteps
            ang_inc = self.generate_gitter_window.angSteps            
            print(rad_inc)
            print(ang_inc)

            dir = 0
            self.clear_points()
            for i in range (int(((self.generate_gitter_window.angEnd-self.generate_gitter_window.angStart)/ self.generate_gitter_window.angSteps))+1):
                if dir == 0:
                    for j in range (int(((self.generate_gitter_window.radEnd-self.generate_gitter_window.radStart)/ self.generate_gitter_window.radSteps))+1):
                        self.plainTextEdit.insertPlainText("%.3f" % (self.generate_gitter_window.angStart + i*ang_inc))
                        self.plainTextEdit.insertPlainText("; ")
                        self.plainTextEdit.insertPlainText("%.3f" % (self.generate_gitter_window.radStart + j*rad_inc))
                        self.plainTextEdit.insertPlainText("\n")
                        dir=1
                else:
                    for j in range (int(((self.generate_gitter_window.radEnd-self.generate_gitter_window.radStart)/ self.generate_gitter_window.radSteps))+1):
                        self.plainTextEdit.insertPlainText("%.3f" % (self.generate_gitter_window.angStart + i*ang_inc))
                        self.plainTextEdit.insertPlainText("; ")
                        self.plainTextEdit.insertPlainText("%.3f" % (self.generate_gitter_window.radEnd - j*rad_inc))
                        self.plainTextEdit.insertPlainText("\n") 
                        dir=0

            self.export_text()
            self.grid = Grid.Grid("output.txt")
            self.widget_2.reload_plot(self.grid, self.settings)


        else:  # Close Window if clicked again.
            self.generate_gitter_window = None
    
    def conf_wind(self):
        if self.configuration_window is None:  # open Window if clicked.
            self.configuration_window = Configuration_Window()
            self.configuration_window.exec_()
            self.grid = Grid.Grid("output.txt")
            self.settings = file_operations.load_settings()
            self.widget_2.reload_plot(self.grid, self.settings)
            self.doubleSpinBox.setRange(self.settings["dimensions"]["min_deflection"], self.settings["dimensions"]["max_deflection"])
            self.doubleSpinBox_2.setRange(self.settings["dimensions"]["inner_radius"], self.settings["dimensions"]["outer_radius"])
            self.clear_points()
        else:  # Close Window if clicked again.
            self.configuration_window = None


            

    def connectSignalsSlots(self):

        self.action_Exit.triggered.connect(self.close)

        self.action_Find_Replace.triggered.connect(self.findAndReplace)

        self.action_About.triggered.connect(self.about)

    def get_avaible_Ports(self):
        port = self.comboBox.currentText() 
        if self.Serial_Com.cur_port != port and self.Serial_Com.cur_port != "-":
            self.Serial_Com.SerialClose()
        self.Serial_Com.SerialOpen(port, self.settings["serial_configuration"]["baud"])  # Replace with value from settings.yaml
        self.textEdit_2.setText(f"Connected")

        self.refresh()

    def clear_points(self):
        self.plainTextEdit.clear()
        self.export_text()
        self.grid = Grid.Grid("output.txt")
        self.widget_2.reload_plot(self.grid, self.settings)


    def export_text(self):
        # Get the content of the QPlainTextEdit
        text_content = self.plainTextEdit.toPlainText()
        text_content = text_content.replace(";","")

        # Define the predefined file path and name
        file_path = "output.txt"  # Change this to your desired file path and name

        try:
            # Write the text content to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            # QMessageBox.information(self, "Success", f"Text exported successfully to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")


    # Based on: https://stackoverflow.com/questions/42046092/how-do-i-create-a-signal-to-open-a-qfiledialog-in-qt-designer (zuletzt abgerufen am 06.04.2024)
    def load_gitter_clicked(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Gitter einladen", "", "All Files (*)", options=options)
        self.plainTextEdit.clear()
        self.grid = Grid.Grid(fileName)
        self.plainTextEdit.insertPlainText(self.grid.__str__())

        # Widget 2 is matplotlib figure
        self.widget_2.reload_plot(self.grid, settings)

    def findAndReplace(self):

        dialog = FindReplaceDialog(self)

        dialog.exec()

    def stop_motor(self):
        if self.status == "Performing":
            self.Serial_Com.send_letter_over_serial(letter="s")
        else:
            self.Error_box("Motor is not running!")

    def load_gitter(self):
        pass

    def perform2(self):
        self.status = "Performming"
        self.textEdit_2.setText(self.status)
        for x_coor, y_coor in self.grid:
            print(x_coor, y_coor)

    def perform(self):
        # try:
        cur_prog = 0
        self.progressBar.setProperty("value", cur_prog)
        self.textEdit_2.setText(f"Moving")


        text_content = self.plainTextEdit.toPlainText()
        # Strip the text to remove leading/trailing whitespace, then split by lines
        lines = text_content.strip().splitlines()

        # Convert each line into a tuple of floatsFcon
        list_of_tuples = [tuple(map(float, line.split(';'))) for line in lines]
        self.textEdit_2.setText("Okay")

        self.poll_enc_status_last()
        
        _translate = QtCore.QCoreApplication.translate
        for i in range(len(list_of_tuples)-1):
            self.label_7.setText(_translate("MainWindow", "x:%02d y:%02d"%(list_of_tuples[i][0],list_of_tuples[i][1])))
            self.label_8.setText(_translate("MainWindow", "x:%02d y:%02d"%(list_of_tuples[i+1][0],list_of_tuples[i+1][1])))
            if list_of_tuples[i][1] != list_of_tuples[i+1][1]:
                # Define parameters for run_motor
                period = (1 / self.settings["movement_configuration"]["Radial_mot_speed"]) * 1000000 #Convert Hz to Period in µs
                steps = self.settings["movement_configuration"]["radial_dir"] * (list_of_tuples[i+1][1] - list_of_tuples[i][1])
                motor = self.settings["motor_configuration"]["Radial_mot"]
                mot_speed = self.settings["movement_configuration"]["Radial_mot_speed"]

                

                expected_encoder_steps = self.last_value_encoder_radial + (steps/self.settings["motor_configuration"]["Steps/rot_Radial"]
                                                                           *self.settings["motor_configuration"]["Encoder_Steps/rot_Radial"])
                

                self.run_process(period=period, steps=steps, motor=motor, 
                                 mot_speed=mot_speed, expected_encoder_steps=expected_encoder_steps)
                
                
                self.textEdit_2.setText(f"Measuring")
                time.sleep(self.settings["movement_configuration"]["Delay_time"])
            if list_of_tuples[i][0] != list_of_tuples[i+1][0]:
                # Define parameters for run_motor
                period = (1 / self.settings["movement_configuration"]["Angular_mot_speed"]) * 1000000 #Convert Hz to Period in µs
                steps = self.settings["movement_configuration"]["phi_dir"] * (list_of_tuples[i+1][0] - list_of_tuples[i][0])
                motor = self.settings["motor_configuration"]["Angular_mot"]
                mot_speed = self.settings["movement_configuration"]["Angular_mot_speed"]

                
                expected_encoder_steps = self.last_value_encoder_angular + (steps/self.settings["motor_configuration"]["Steps/rot_Angular"]
                                                                           *self.settings["motor_configuration"]["Encoder_Steps/rot_Angular"])
                self.textEdit_2.setText(f"Moving")
                self.run_process(period=period, steps=steps, motor=motor, 
                                 mot_speed=mot_speed, expected_encoder_steps=expected_encoder_steps)
                self.textEdit_2.setText(f"Measuring")
                time.sleep(self.settings["movement_configuration"]["Delay_time"])

            
            cur_prog += int((100/(len(list_of_tuples)-1)))
            self.progressBar.setProperty("value", cur_prog)
        self.label_7.setText(_translate("MainWindow", "x:%02d y:%02d"%(list_of_tuples[len(list_of_tuples)-1][0],list_of_tuples[len(list_of_tuples)-1][1])))
        self.label_8.setText(_translate("MainWindow", "x:-- y:--"))
        cur_prog = 100
        self.progressBar.setProperty("value", cur_prog)
    
    def run_process(self,period,steps,motor, mot_speed, expected_encoder_steps):
        retries = 0
        max_retries = 2
        step_num = 0
        if motor == self.settings["motor_configuration"]["Radial_mot"]:
            
            while retries <= max_retries:
                # Run motor and get encoder steps
                print("expected_enc_steps:%d last_val_enc_rad:%d steps_num:%d period:%d steps:%d motor:%d"%(expected_encoder_steps,self.last_value_encoder_radial,step_num,period,steps,motor))
                step_num+=1
                try:
                    self.run_motor(serial=self.Serial_Com, period=period, steps=steps, motor=motor, mot_speed=mot_speed)
                except Exception as e:
                    self.textEdit_2.setText(f"ERROR: Failed to run motor. Details: {str(e)}")
                    print(e)
                    return  # Exit the loop or method if necessary
                # Check if the discrepancy is acceptable
                if abs(expected_encoder_steps - self.last_value_encoder_radial) < 100:
                    break  # Success, exit the retry loop

                # If not successful and retries are remaining
                retries += 1
                if retries > max_retries:
                    self.textEdit_2.setText("ERROR Radial: Maximum retries reached. Expected encoder steps still do not match.")
                    return # Exit the loop or method
                else:
                    discrepancy = expected_encoder_steps - self.last_value_encoder_radial
                    steps = (discrepancy / self.settings["motor_configuration"]["Encoder_Steps/rot_Radial"] * 
                                self.settings["motor_configuration"]["Steps/rot_Radial"])
                

        elif motor == self.settings["motor_configuration"]["Angular_mot"]:
            while retries <= max_retries:
                # Run motor and get encoder steps
                print("expected_enc_steps:%d last_val_enc:%d step_num%d period%d steps%d motor:%d"%(expected_encoder_steps,self.last_value_encoder_angular,step_num,period,steps,motor))
                step_num+=1
                try:
                    self.run_motor(serial=self.Serial_Com, period=period, steps=steps, motor=motor, mot_speed=mot_speed)
                except Exception as e:
                    self.textEdit_2.setText(f"ERROR: Failed to run motor. Details: {str(e)}")
                    print(e)
                    return  # Exit the loop or method
                # Check if the discrepancy is acceptable
                if abs(expected_encoder_steps - self.last_value_encoder_angular) < 100:
                    break  # Success, exit the retry loop

                # If not successful and retries are remaining
                retries += 1
                if retries > max_retries:
                    self.textEdit_2.setText("ERROR Angular: Maximum retries reached. Expected encoder steps still do not match.")
                    return # Exit the loop or method
                else:
                    discrepancy = expected_encoder_steps - self.last_value_encoder_angular
                    steps = (discrepancy / self.settings["motor_configuration"]["Encoder_Steps/rot_Angular"] * 
                    self.settings["motor_configuration"]["Steps/rot_Angular"]) 


    def add_point(self):
        self.plainTextEdit.insertPlainText("%.3f" % self.doubleSpinBox.value())
        self.plainTextEdit.insertPlainText("; ")
        self.plainTextEdit.insertPlainText("%.3f" % self.doubleSpinBox_2.value())
        self.plainTextEdit.insertPlainText("\n")

        self.export_text()
        self.grid = Grid.Grid("output.txt")
        self.widget_2.reload_plot(self.grid, self.settings)

    def start_manual_overwrite(self, steps_dict: dict):
        
        for label_text, steps in steps_dict.items():

            motorname = label_text
            period = (1 / self.settings["movement_configuration"][motorname+"_speed"]) * 1000000 #Convert Hz to Period in µs
            steps = steps
            motor = self.settings["motor_configuration"][motorname]
            mot_speed = self.settings["movement_configuration"][motorname+"_speed"]
            if steps ==0:
                continue
            else:
                if motorname == "Angular_mot":
                    expected_encoder_steps = self.last_value_encoder_angular + (steps/self.settings["motor_configuration"]["Steps/rot_Angular"]
                                                                           *self.settings["motor_configuration"]["Encoder_Steps/rot_Angular"])
                    self.run_process(last_value_encoder= self.last_value_encoder_angular,period=period, 
                                     steps=steps, motor=motor,mot_speed=mot_speed,expected_encoder_steps= expected_encoder_steps)
                elif motorname == "Radial_mot": 
                    expected_encoder_steps = self.last_value_encoder_radial + (steps/self.settings["motor_configuration"]["Steps/rot_Radial"]
                                                                           *self.settings["motor_configuration"]["Encoder_Steps/rot_Radial"])
                    self.run_process(last_value_encoder= self.last_value_encoder_radial,period=period, 
                                     steps=steps, motor=motor,mot_speed=mot_speed,expected_encoder_steps= expected_encoder_steps)

    def run_motor(self,serial:Serial_Com_Dummy.SerialCtrl,period,steps,motor,mot_speed):
        if steps >0:
            dir=1
        else:
            dir=0    
        callback_int = None
        self.refresh()
               

        while(callback_int!=int(steps)):
            
            # Set Motor
            input_string = "p"+str(period)+"\r\n"
            for char in input_string:
                serial.send_letter_over_serial(char)
            self.refresh()
            
            input_string = "s"+str(abs(int(steps)))+"\r\n"
            for char in input_string:
                serial.send_letter_over_serial(char)
            self.refresh()
            
            input_string = "d"+str(dir)+"\r\n"
            for char in input_string:
                serial.send_letter_over_serial(char)
            self.refresh()

            input_string = "m"+str(motor)+"\r\n"
            for char in input_string:
                serial.send_letter_over_serial(char)
            self.refresh()

             #callback
            input_string = "c"+"\r\n"
            for char in input_string:
                serial.send_letter_over_serial(char)
            
            callback = serial.receive_over_serial()
            try:
                callback_int = int(callback)
            except Exception as e:
                print("cannot make callback as integer")


        input_string = "r"
        for char in input_string:
            serial.send_letter_over_serial(char)

        print(steps)

        # example interrupt
        # time.sleep(5)
        # serial.send_letter_over_serial('i')
        # while(done_mes==None):
        #     time.sleep(0.2)
        #     done_mes=serial.receive_over_serial()
        #Wait for message 'done'
        # done_mes=serial.receive_over_serial()
        # done_mes=serial.receive_over_serial()
        # time.sleep(abs(steps/mot_speed)+5)
        # Initialize a counter to track the number of receive calls
        invalid_receive_count = 0
        receive_count = 0
    # Wait for message 'done'
        valid_number_received = False  # Flag to track if a valid number was received initially
        done_mes = serial.receive_over_serial()

        while done_mes != "done\n":
            
            done_mes = serial.receive_over_serial()

            try:
                done_mes = int(done_mes)
                valid_number_received = True
            except:

                if done_mes :  # Check if done_mes is not empty and is a valid number
                    serial.logs.append(done_mes)
                else:
                    # valid_number = None  # Handle invalid case (optional)
                    if receive_count >= 7 or invalid_receive_count>=7: #if in 45 seconds not done, resend command
                        input_string = "m"+str(motor)+"\r\n"
                        for char in input_string:
                            serial.send_letter_over_serial(char)
                        self.refresh()
                        input_string = "r"
                        for char in input_string:
                            serial.send_letter_over_serial(char)
                        self.refresh()

                        # Reset the counter and continue checking for "done"
                        receive_count = 0

                    invalid_receive_count += 1
                    time.sleep(5)
                    continue
                # If a valid number was received in the first receive, break the loop early (this means 'done' feedback message was skipped)
            if valid_number_received:
                break


        
        # 'done' received, now receive encoder value
        if not valid_number_received:
            time.sleep(0.1)
            done_mes = serial.receive_over_serial()
        if(done_mes!= None):
            serial.logs.append(done_mes)
        self.poll_enc_status_last()
        
        
    def refresh(self):
        # Set Motor
        input_string = "\r\n"

        for i in range(1):
            for char in input_string:
                self.Serial_Com.send_letter_over_serial(char)
                self.Serial_Com.receive_over_serial()
            time.sleep(0.01)
                
            



    def poll_enc_status(self):
        # Set Motor
        self.init_value_encoder_angular = None
        self.init_value_encoder_radial = None
        
        while self.init_value_encoder_angular == None or self.init_value_encoder_radial == None or self.init_value_encoder_angular>70000 or self.init_value_encoder_radial<100000:
            try:
                input_string = "e"+"\r\n"
                for char in input_string:
                    self.Serial_Com.send_letter_over_serial(char)
                self.init_value_encoder_angular = int(self.Serial_Com.receive_over_serial())
                self.init_value_encoder_radial = int(self.Serial_Com.receive_over_serial())
            except Exception as e:
                print("Init Encoder value not int()")


    def poll_enc_status_last(self):
        self.last_value_encoder_angular = None
        self.last_value_encoder_radial = None
        
        while self.last_value_encoder_angular == None or self.last_value_encoder_radial == None or self.last_value_encoder_angular>70000 or self.last_value_encoder_radial<100000 :
            try:
                input_string = "e"+"\r\n"
                for char in input_string:
                    self.Serial_Com.send_letter_over_serial(char)
                self.last_value_encoder_angular = int(self.Serial_Com.receive_over_serial())
                self.last_value_encoder_radial = int(self.Serial_Com.receive_over_serial())
            except:
                print("Last Encoder value not int()")
        return
    def home(self):
        
        self.textEdit_2.setText(f"Homing")
        self.poll_enc_status_last()

        # home Radial motor
        period = (1 / self.settings["movement_configuration"]["Radial_mot_speed"]) * 1000000 #Convert Hz to Period in µs
        motor = self.settings["motor_configuration"]["Radial_mot"]
        mot_speed = self.settings["movement_configuration"]["Radial_mot_speed"]

        steps = (self.last_value_encoder_radial - self.init_value_encoder_radial)*(self.settings["motor_configuration"]["Steps/rot_Radial"]
                                                                           /self.settings["motor_configuration"]["Encoder_Steps/rot_Radial"])
        

        self.run_process(period=period,mot_speed=mot_speed,motor=motor,steps=-steps,expected_encoder_steps=self.init_value_encoder_radial)

        # home Angular motor
        period = (1 / self.settings["movement_configuration"]["Angular_mot_speed"]) * 1000000 #Convert Hz to Period in µs
        motor = self.settings["motor_configuration"]["Angular_mot"]
        mot_speed = self.settings["movement_configuration"]["Angular_mot_speed"]
        steps = (self.last_value_encoder_angular - self.init_value_encoder_angular)*(self.settings["motor_configuration"]["Steps/rot_Angular"]
                                                                           /self.settings["motor_configuration"]["Encoder_Steps/rot_Angular"])
        

        self.run_process(period=period,mot_speed=mot_speed,motor=motor,steps=-steps,expected_encoder_steps=self.init_value_encoder_angular)
                         
        



    def about(self):

        QMessageBox.about(

            self,

            "About Sample Editor",

            "<p>A sample text editor app built with:</p>"

            "<p>- PyQt</p>"

            "<p>- Qt Designer</p>"

            "<p>- Python</p>",

        )


class FindReplaceDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        loadUi("ui_files/ManualOverwrite.ui", self)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = Window()

    settings = file_operations.load_settings("settings.yaml")

    win.show()

    sys.exit(app.exec())