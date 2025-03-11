import serial.tools.list_ports
import time
from PyQt5.QtWidgets import QMessageBox


class SerialCtrl():
    def __init__(self):
        '''
        Initializing the main varialbles for the serial data
        '''
        self.com_list = []
        self.getCOMList()
        self.cur_port = "-"
        self.logs=[]
    
    def getCOMList(self):
        '''
        Method that get the lost of available coms in the system
        '''
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]
        self.com_list.insert(0,"-")

    def SerialOpen(self, port, baud):
        '''
        Method to setup the serial connection and make sure to go for the next only 
        if the connection is done properly
        '''
        try:
            self.ser.is_open
            if self.ser.is_open == True:
                print("connection already made")

        except:
            PORT = port
            BAUD = baud
            self.ser = serial.Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
            self.ser.timeout = 0.1
            
        
        try:
            if self.ser.is_open:
                self.ser.status = True
                print("connection already made")

            else:
                PORT = port
                BAUD = baud
                self.ser = serial.Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.timeout = 0.1
                self.ser.open()
                self.ser.status = True
                print("connection made")
                self.cur_port = PORT
        except:
            self.ser.status= False  
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText("Please select a COM port")
            # Show the error box
            error_box.exec_()


    def SerialClose(self):
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
            print("connection closed")
        except:
            self.ser.status= False    
        print("Connection is closed") 

    def send_letter_over_serial(self, letter):
        try:
           
            # Check if the serial connection is open
            self.ser.is_open
            # Send the letter over the serial port
            self.ser.write(letter.encode())  # 'A' is encoded to bytes and sent
            # time.sleep(0.2)

        except serial.SerialException as e:
            print(f"Error: {e}")

    def receive_over_serial(self):
        try:
           
            # Check if the serial connection is open
            self.ser.is_open
            # Read a line from the serial port
            time.sleep(0.1)
            received_data = self.ser.readline()
            received_data = str(received_data,'UTF-8')
            # Check if data is received
            if received_data:
                return received_data


        except serial.SerialException as e:
            print(f"Error: {e}")  

# def run_motor(self,serial:SerialCtrl,period,steps,motor,mot_speed):
#     if steps >0:
#         dir=1
#     else:
#         dir=0    

#     done_mes = serial.receive_over_serial()

#     while(done_mes!=None):
#         serial.logs.append(done_mes)
#         time.sleep(0.2)
#         done_mes=serial.receive_over_serial()

#     # Set Motor
#     input_string = "p"+str(period)+"\r\n"
#     for char in input_string:
#         serial.send_letter_over_serial(char)
    
#     # time.sleep(0.5)
#     input_string = "s"+str(abs(steps))+"\r\n"
#     for char in input_string:
#         serial.send_letter_over_serial(char)
#     # time.sleep(0.5)
#     input_string = "d"+str(dir)+"\r\n"
#     for char in input_string:
#         serial.send_letter_over_serial(char)
#     # time.sleep(0.5)
#     input_string = "m"+str(motor)+"\r\n"
#     for char in input_string:
#         serial.send_letter_over_serial(char)
#     # time.sleep(0.5)
#     input_string = "r"
#     for char in input_string:
#         serial.send_letter_over_serial(char)

#     # example interrupt
#     # time.sleep(5)
#     # serial.send_letter_over_serial('i')
#     # while(done_mes==None):
#     #     time.sleep(0.2)
#     #     done_mes=serial.receive_over_serial()
#     #Wait for message 'done'
#     # done_mes=serial.receive_over_serial()
#     # done_mes=serial.receive_over_serial()
#     # time.sleep(abs(steps/mot_speed)+5)
#     # Initialize a counter to track the number of receive calls
#     receive_count = 0
#    # Wait for message 'done'
#     while done_mes != "done\n":
#         # time.sleep(0.2)
#         done_mes = serial.receive_over_serial()
#         serial.logs.append(done_mes)

#         if motor == self.settings["motor_configuration"]["Angular_mot"]:
#             self.last_value_encoder_angular = int(done_mes)
#         elif motor == self.settings["motor_configuraton"]["Radial_mot"]:
#             self.last_value_encoder_radial = int(done_mes)
        
#         # Increment the counter
#         receive_count += 1

#         # If we've called receive 20 times without "done", send reset command
#         if receive_count >= 20:
#             input_string = "r"
#             for char in input_string:
#                 serial.send_letter_over_serial(char)
#             # Reset the counter and continue checking for "done"
#             receive_count = 0

    
#     #receive feedback from µC
#     done_mes=serial.receive_over_serial()
#     serial.logs.append(done_mes)
#     print(done_mes)

#     done_mes2 =serial.receive_over_serial()
#     serial.logs.append(done_mes2)
 
#     return steps, {"radial_mot": int(done_mes2), "angular_mot": int(done_mes)}



def homing(serial:SerialCtrl,period,steps,dir,motor):
    pass

def step_translator(serial:SerialCtrl,period,steps,dir,motor,x_coor,y_coor):
    pass

# if __name__ == "__main__":
#     myserial=SerialCtrl()
#     myserial.getCOMList() 
#     print(myserial.com_list)   
#     myserial.SerialOpen(port=myserial.com_list[3],baud=115200)
#     run_motor(myserial,-20000,100,0)
#     myserial.SerialClose()