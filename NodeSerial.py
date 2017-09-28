#Serial Communication to Node Libraryr
#Handles messages being sent between Raspberry Pi and Node
import serial
from serial import SerialException
import time

class NodeSerial():

    def __init__(self):

        #Initialized Serial Comm Locations, To Be Rearranged Later
        self.node_addresses = ['/dev/ttyACM5', '/dev/ttyACM0', '/dev/ttyACM2','/dev/ttyACM4', '/dev/ttyACM3', '/dev/ttyACM1']

        #Teensy ID's in Physical Locations
        self.teensy_ids = [2595140, 2585940, 2586000]

        ################################################################
        #CHANGE THIS DEPENDING ON HOW MANY NODES ARE CURRENTLY CONNECTED
        ##############################################################
        self.serial_list = [None, None, None, None, None, None]

        self.SOM_list = [b'\xff',b'\xee',b'\xdd']
        self.EOM_list = [b'\xaa',b'\xbb',b'\xcc']
        self.baud_rate = 57600

        self.waitUntilSerialPortsOpen()

    def waitUntilSerialPortsOpen(self):
        # only continue once we are able to open all serial ports
        print("Attempting to open serial ports...")
        while True:
            try:
                for i in range(len(self.serial_list)):
                    self.serial_list[i] = serial.Serial(self.node_addresses[i],self.baud_rate)
                    self.serial_list[i].flush()
                    self.serial_list[i].flushInput()
                break # if we are able to open all, break out of loop

            # catch the exception, wait one second before trying again
            except SerialException:
                time.sleep(1)
        print("Serial Ports Opened Sucessfully")

    def rearrangeSerialPorts(self):

        for i in range(len(self.serial_list)):
            sendMessage(INSTRUCT_CODE_GET_TEENSY_ID)
            code, tid = checkIncomingMessageFromNode(i)

    def checkIncomingMessageFromNode(self, node_number):

        #Check if port has minimum message length in buffer
        if self.serial_list[node_number].inWaiting() >= 11:

            #Serial port for Target Node
            ser = self.serial_list[node_number]

            #Check for Start of Message
            for i in range(len(self.SOM_list)):
                current_SOM = ser.read()
                if current_SOM != self.SOM_list[i]:
                    print("SOM Not Found, Flushing Input")
                    print(current_SOM)
                    return "error", "none"

            #Teensy IDs, TODO: Use these for validation
            t1 = ser.read()
            t2 = ser.read()
            t3 = ser.read()

            # received_tid = ((t1 << 16) | (t2 << 8)) | t3
            #Read in Length and Code
            message_length = ser.read()
            message_code = ser.read()

            #Find amount of bytes to read and store into data list
            num_bytes_to_receive = int.from_bytes(message_length, byteorder='big') - 8 - len(self.EOM_list);
            incoming_data = []

            if num_bytes_to_receive == 0:
                for i in range(len(self.EOM_list)):
                    current_EOM = ser.read()
                    if current_EOM != self.EOM_list[i]:
                        print("EOM Not Found")
                        ser.flushInput()
                        return "error", "none"

                return message_code, []

            else:

                if ser.inWaiting() >= num_bytes_to_receive:
                    for i in range(num_bytes_to_receive):
                        incoming_data.append(ser.read())

            #Check for End of Message
                for i in range(len(self.EOM_list)):
                    current_EOM = ser.read()
                    if current_EOM != self.EOM_list[i]:
                        print("EOM Not Found")
                        ser.flushInput()
                        return "error", "none"

            #Returns identifier byte for message code and relevant data list
                return message_code, incoming_data


        else:

            return "none", "none"

    def sendMessage(self, outgoing_message_code, outgoing_data, node_number):
            # input:
            # outgoing_message_code: bytes object of length 1
            # outgoing_data: list of ints (can be empty), ASSUMES EACH ITEM CAN BE TRANSFORMED INTO ONE SINGLE BYTE EACH
            # node_number: int

            # first determine number of bytes to send
        messageLength = (len(self.SOM_list) # SOM
                      + 3 # teensy id
                      + 1 # length byte
                      + len(outgoing_message_code) # code
                      + len(outgoing_data) # outgoing data bytes
                      + len(self.EOM_list)) # EOM

            # select serial port
        ser = self.serial_list[node_number]

        # send SOM (3 bytes)
        for SOM in self.SOM_list:
            ser.write(SOM)

        # send teensy id (3 bytes)
        TID_list = list(self.teensy_ids[node_number].to_bytes(3, byteorder='big'))
        for TID in TID_list:
            ser.write(bytes([TID]))

        # send length (1 byte)
        ser.write(bytes([messageLength]))

        # send code (1 bytes)
        ser.write(outgoing_message_code)

        # send data
        for OUT in outgoing_data:
            ser.write(bytes([OUT]))

        # send EOM (3 bytes)
        for EOM in self.EOM_list:
            ser.write(EOM)

        #Print All Bytes

        # print(self.SOM_list, end=" [")
        # for tid in TID_list:
        #     print(bytes([tid]), end=", ")
        # print("] [", end="")
        # print(bytes([messageLength]), end="")
        # print("] [", end="")
        # print(outgoing_message_code, end="")
        # print("] [", end="")
        # for out in outgoing_data:
        #     print(bytes([out]), end=", ")
        # print("]", end="")
        # print(self.EOM_list)
        # print(int.from_bytes(TID_list, byteorder='big'))
        # print("\n")

        print("Sending to " + str(self.node_addresses[node_number]) + " " + str(outgoing_message_code) + " " + str(outgoing_data))

if __name__ == '__main__':

    S = NodeSerial()
    for node_number in range(len(S.serial_list)):
        S.sendMessage(b'\x01', [123], node_number)

    while True:
        try:
            for node_number in range(len(S.serial_list)):
                # if S.serial_list[node_number].inWaiting():
                #     print(S.serial_list[node_number].read())
                incoming_message_code, incoming_data = S.checkIncomingMessageFromNode(node_number)

                if incoming_message_code != "none":
                    print("Received from " + str(S.node_addresses[node_number]) + " " + str(incoming_message_code) + " " + str(incoming_data))
        except KeyboardInterrupt:
            print("Closing Main Program and Serial Ports")

            for i in range(len(S.serial_list)):
                print ("Stopping" + str(S.node_addresses[i]))
                S.serial_list[i].close()

            print("Completed")
            break
