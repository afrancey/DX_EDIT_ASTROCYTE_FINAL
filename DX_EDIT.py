import serial
from serial import SerialException
import random
import NodeSerial
#import CommunicationManager
from collections import deque

import socket
import threading
import time
from pythonosc import osc_message_builder
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server


class Messages():
    def __init__(self):
        self.led_serial_message = [0,0,0] # [id, pin, value]
        self.led_OSC_message = [0,0,0] # [slave pi, address, value]


S = NodeSerial.NodeSerial()

#Instruction Message Codes
INSTRUCT_CODE_GET_TEENSY_ID = b'\x00'
INSTRUCT_CODE_ACTIVATE_LED = b'\xAA'
##INSTRUCT_CODE_PLAY_SD_WAV = b'\x0F'



#######################################################################################
#Main Function Globals
#######################################################################################


led_pin_dict = {'/sphereUnit1/led1/in':3, '/sphereUnit1/led1/out':4,
            '/sphereUnit1/led2/in':25, '/sphereUnit1/led2/out':32,
            '/sphereUnit1/led3/in':9, '/sphereUnit1/led3/out':10,
            '/sphereUnit2/led1/in':3, '/sphereUnit2/led1/out':4,
            '/sphereUnit2/led2/in':25, '/sphereUnit2/led2/out':32,
            '/sphereUnit2/led3/in':9, '/sphereUnit2/led3/out':10,
            '/sphereUnit3/led1/in':3, '/sphereUnit3/led1/out':4,
            '/sphereUnit3/led2/in':25, '/sphereUnit3/led2/out':32,
            '/sphereUnit3/led3/in':9, '/sphereUnit3/led3/out':10,
            '/sphereUnit4/led1/in':3, '/sphereUnit4/led1/out':4,
            '/sphereUnit4/led2/in':25, '/sphereUnit4/led2/out':32,
            '/sphereUnit4/led3/in':9, '/sphereUnit4/led3/out':10,
            '/sphereUnit5/led1/in':3, '/sphereUnit5/led1/out':4,
            '/sphereUnit5/led2/in':25, '/sphereUnit5/led2/out':32,
            '/sphereUnit5/led3/in':9, '/sphereUnit5/led3/out':10,
            '/sphereUnit6/led1/in':3, '/sphereUnit6/led1/out':4,
            '/sphereUnit6/led2/in':25, '/sphereUnit6/led2/out':32,
            '/sphereUnit6/led3/in':9, '/sphereUnit6/led3/out':10,
            '/sphereUnit7/led1/in':3, '/sphereUnit7/led1/out':4,
            '/sphereUnit7/led2/in':25, '/sphereUnit7/led2/out':32,
            '/sphereUnit7/led3/in':9, '/sphereUnit7/led3/out':10,
            '/sphereUnit8/led1/in':3, '/sphereUnit8/led1/out':4,
            '/sphereUnit8/led2/in':25, '/sphereUnit8/led2/out':32,
            '/sphereUnit8/led3/in':9, '/sphereUnit8/led3/out':10,
            '/sphereUnit9/led1/in':3, '/sphereUnit9/led1/out':4,
            '/sphereUnit9/led2/in':25, '/sphereUnit9/led2/out':32,
            '/sphereUnit9/led3/in':9, '/sphereUnit9/led3/out':10,
            '/sphereUnit10/led1/in':3, '/sphereUnit10/led1/out':4,
            '/sphereUnit10/led2/in':25, '/sphereUnit10/led2/out':32,
            '/sphereUnit10/led3/in':9, '/sphereUnit10/led3/out':10,
            '/sphereUnit11/led1/in':3, '/sphereUnit11/led1/out':4,
            '/sphereUnit11/led2/in':25, '/sphereUnit11/led2/out':32,
            '/sphereUnit11/led3/in':9, '/sphereUnit11/led3/out':10,
            '/sphereUnit12/led1/in':3, '/sphereUnit12/led1/out':4,
            '/sphereUnit12/led2/in':25, '/sphereUnit12/led2/out':32,
            '/sphereUnit12/led3/in':9, '/sphereUnit12/led3/out':10,}

slave_led_pin_dict = {'/slave/sphereUnit1/led1/in':3, '/slave/sphereUnit1/led1/out':4,
            '/slave/sphereUnit1/led2/in':25, '/slave/sphereUnit1/led2/out':32,
            '/slave/sphereUnit1/led3/in':9, '/slave/sphereUnit1/led3/out':10,
            '/slave/sphereUnit2/led1/in':3, '/slave/sphereUnit2/led1/out':4,
            '/slave/sphereUnit2/led2/in':25, '/slave/sphereUnit2/led2/out':32,
            '/slave/sphereUnit2/led3/in':9, '/slave/sphereUnit2/led3/out':10,
            '/slave/sphereUnit3/led1/in':3, '/slave/sphereUnit3/led1/out':4,
            '/slave/sphereUnit3/led2/in':25, '/slave/sphereUnit3/led2/out':32,
            '/slave/sphereUnit3/led3/in':9, '/slave/sphereUnit3/led3/out':10,
            '/slave/sphereUnit4/led1/in':3, '/slave/sphereUnit4/led1/out':4,
            '/slave/sphereUnit4/led2/in':25, '/slave/sphereUnit4/led2/out':32,
            '/slave/sphereUnit4/led3/in':9, '/slave/sphereUnit4/led3/out':10,
            '/slave/sphereUnit5/led1/in':3, '/slave/sphereUnit5/led1/out':4,
            '/slave/sphereUnit5/led2/in':25, '/slave/sphereUnit5/led2/out':32,
            '/slave/sphereUnit5/led3/in':9, '/slave/sphereUnit5/led3/out':10,
            '/slave/sphereUnit6/led1/in':3, '/slave/sphereUnit6/led1/out':4,
            '/slave/sphereUnit6/led2/in':25, '/slave/sphereUnit6/led2/out':32,
            '/slave/sphereUnit6/led3/in':9, '/slave/sphereUnit6/led3/out':10,
            '/slave/sphereUnit7/led1/in':3, '/slave/sphereUnit7/led1/out':4,
            '/slave/sphereUnit7/led2/in':25, '/slave/sphereUnit7/led2/out':32,
            '/slave/sphereUnit7/led3/in':9, '/slave/sphereUnit7/led3/out':10,
            '/slave/sphereUnit8/led1/in':3, '/slave/sphereUnit8/led1/out':4,
            '/slave/sphereUnit8/led2/in':25, '/slave/sphereUnit8/led2/out':32,
            '/slave/sphereUnit8/led3/in':9, '/slave/sphereUnit8/led3/out':10,
            '/slave/sphereUnit9/led1/in':3, '/slave/sphereUnit9/led1/out':4,
            '/slave/sphereUnit9/led2/in':25, '/slave/sphereUnit9/led2/out':32,
            '/slave/sphereUnit9/led3/in':9, '/slave/sphereUnit9/led3/out':10,
            '/slave/sphereUnit10/led1/in':3, '/slave/sphereUnit10/led1/out':4,
            '/slave/sphereUnit10/led2/in':25, '/slave/sphereUnit10/led2/out':32,
            '/slave/sphereUnit10/led3/in':9, '/slave/sphereUnit10/led3/out':10,
            '/slave/sphereUnit11/led1/in':3, '/slave/sphereUnit11/led1/out':4,
            '/slave/sphereUnit11/led2/in':25, '/slave/sphereUnit11/led2/out':32,
            '/slave/sphereUnit11/led3/in':9, '/slave/sphereUnit11/led3/out':10,
            '/slave/sphereUnit12/led1/in':3, '/slave/sphereUnit12/led1/out':4,
            '/slave/sphereUnit12/led2/in':25, '/slave/sphereUnit12/led2/out':32,
            '/slave/sphereUnit12/led3/in':9, '/slave/sphereUnit12/led3/out':10,}


RPi_s2 = [1,2,3] #master
RPi_s5 = [4,5,6] #slave
RPi_s8 = [7,8,9] #slave
RPi_s11 = [10,11,12] #slave

s5_ip = '10.1.19.12'
s8_ip = '10.1.19.16'
s11_ip = '10.1.19.17'


if __name__ == '__main__':

    # Object to hold messages, avoids getting blocked by OSC handlers
    messages = Messages()

    # OSC handlers
    def led_handler_master(addr, value):
        print("addr: " + addr)

        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])

        # parse led number
        led = int(addr[addr.index('led') + 3])
        
        pin = led_pin_dict[addr]

        if unit in RPi_s2:
            messages.led_serial_message = [unit - 1 + 12, pin, value]
        elif unit in RPi_s5:
            messages.led_OSC_message = ['s5', '/slave' + addr, value]
        elif unit in RPi_s8:
            messages.led_OSC_message = ['s8', '/slave' + addr, value]
        elif unit in RPi_s11:
            messages.led_OSC_message = ['s11', '/slave' + addr, value]
            
            

    def led_handler_slave(addr, value):
        print("addr: " + addr)
        
        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])

        # parse led number
        led = int(addr[addr.index('led') + 3])
        pin = slave_led_pin_dict[addr]
        messages.led_serial_message = [unit - 1 + 12, pin, value]
        
                
    dispatcher = dispatcher.Dispatcher()

    for key in led_pin_dict.keys():
                
        dispatcher.map(key, led_handler_master)
        
    for key in slave_led_pin_dict.keys():
                
        dispatcher.map(key, led_handler_slave)

    OSC_listener = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 3001), dispatcher)
    OSC_listener_thread = threading.Thread(target=OSC_listener.serve_forever)
    OSC_listener_thread.start()

    # OSC outputs
    slave_s5 = udp_client.SimpleUDPClient(s5_ip, 3001)
    slave_s8 = udp_client.SimpleUDPClient(s8_ip, 3001)
    slave_s11 = udp_client.SimpleUDPClient(s11_ip, 3001)

    print("Starting Main Program")

    while True:
        if messages.led_serial_message != [0,0,0]:
            for ser in S.serial_list:
                print('sending: ' + str(messages.led_serial_message[0]) + ', ' + str(messages.led_serial_message[1]) + ', ' + str(messages.led_serial_message[2]))
                ser.write(b'\xff')
                ser.write(bytes([messages.led_serial_message[0]]))
                ser.write(bytes([messages.led_serial_message[1]]))
                ser.write(bytes([messages.led_serial_message[2]]))
            messages.led_serial_message = [0,0,0]
            print('serial message sent')

        if messages.led_OSC_message != [0,0,0]:
            if messages.led_OSC_message[0] == 's5':
                slave_s5.send_message(messages.led_OSC_message[1], messages.led_OSC_message[2])
            if messages.led_OSC_message[0] == 's8':
                slave_s8.send_message(messages.led_OSC_message[1], messages.led_OSC_message[2])
            if messages.led_OSC_message[0] == 's11':
                slave_s11.send_message(messages.led_OSC_message[1], messages.led_OSC_message[2])

            messages.led_OSC_message = [0,0,0]
            print('OSC message sent')
            
            

    
    

    #main()
