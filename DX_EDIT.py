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

# NodeSerial will open 6 serial ports for you
S = NodeSerial.NodeSerial()

# the first byte in command structure
# signifies that next 3 bytes are a message
COMMAND_BYTE = b'\xff'

# Raspberry Pi type
# my_type = 'master' for master Raspberry Pi (external networked machines
#                                             can send OSC messages to IP address
#                                             of master Pi)
# my_type = 'slave' for slave Raspberry Pi (master sends OSC commands to slaves)
my_type = 'master'

# counter used for counting messages later on
class GlobalVariable():
    def __init__(self):
        self.count = 0


# OSC addresses for each LED with pin numbers
# led_pin_dict[addr] = Teensy pin number for LED specified by that address
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

# OSC addresses for each moth with pin numbers
# moth_pin_dict[addr] = Teensy pin number for moth specified by that address
moth_pin_dict = { '/sphereUnit1/speaker/0':9, '/sphereUnit1/speaker/1':10, '/sphereUnit1/speaker/2': 22,
                  '/sphereUnit1/speaker/3': 23, '/sphereUnit1/speaker/4':29, '/sphereUnit1/speaker/5':30,
                  '/sphereUnit2/speaker/0':9, '/sphereUnit2/speaker/1':10, '/sphereUnit2/speaker/2': 22,
                  '/sphereUnit2/speaker/3': 23, '/sphereUnit2/speaker/4':29, '/sphereUnit2/speaker/5':30,
                  '/sphereUnit3/speaker/0':9, '/sphereUnit3/speaker/1':10, '/sphereUnit3/speaker/2': 22,
                  '/sphereUnit3/speaker/3': 23, '/sphereUnit3/speaker/4':29, '/sphereUnit3/speaker/5':30,
                  '/sphereUnit4/speaker/0':9, '/sphereUnit4/speaker/1':10, '/sphereUnit4/speaker/2': 22,
                  '/sphereUnit4/speaker/3': 23, '/sphereUnit4/speaker/4':29, '/sphereUnit4/speaker/5':30,
                   '/sphereUnit5/speaker/0':9, '/sphereUnit5/speaker/1':10, '/sphereUnit5/speaker/2': 22,
                  '/sphereUnit5/speaker/3': 23, '/sphereUnit5/speaker/4':29, '/sphereUnit5/speaker/5':30,
                   '/sphereUnit6/speaker/0':9, '/sphereUnit6/speaker/1':10, '/sphereUnit6/speaker/2': 22,
                  '/sphereUnit6/speaker/3': 23, '/sphereUnit6/speaker/4':29, '/sphereUnit6/speaker/5':30,
                   '/sphereUnit7/speaker/0':9, '/sphereUnit7/speaker/1':10, '/sphereUnit7/speaker/2': 22,
                  '/sphereUnit7/speaker/3': 23, '/sphereUnit7/speaker/4':29, '/sphereUnit7/speaker/5':30,
                   '/sphereUnit8/speaker/0':9, '/sphereUnit8/speaker/1':10, '/sphereUnit8/speaker/2': 22,
                  '/sphereUnit8/speaker/3': 23, '/sphereUnit8/speaker/4':29, '/sphereUnit8/speaker/5':30,
                   '/sphereUnit9/speaker/0':9, '/sphereUnit9/speaker/1':10, '/sphereUnit9/speaker/2': 22,
                  '/sphereUnit9/speaker/3': 23, '/sphereUnit9/speaker/4':29, '/sphereUnit9/speaker/5':30,
                   '/sphereUnit10/speaker/0':9, '/sphereUnit10/speaker/1':10, '/sphereUnit10/speaker/2': 22,
                  '/sphereUnit10/speaker/3': 23, '/sphereUnit10/speaker/4':29, '/sphereUnit10/speaker/5':30,
                   '/sphereUnit11/speaker/0':9, '/sphereUnit11/speaker/1':10, '/sphereUnit11/speaker/2': 22,
                  '/sphereUnit11/speaker/3': 23, '/sphereUnit11/speaker/4':29, '/sphereUnit11/speaker/5':30,
                  '/sphereUnit12/speaker/0':9, '/sphereUnit12/speaker/1':10, '/sphereUnit12/speaker/2': 22,
                  '/sphereUnit12/speaker/3': 23, '/sphereUnit12/speaker/4':29, '/sphereUnit12/speaker/5':30,
                '/sphereUnit1/A/7':22, '/sphereUnit1/B/10':6, '/sphereUnit1/C/7':20, '/sphereUnit1/C/8':16,
                '/sphereUnit2/A/7':22, '/sphereUnit2/B/10':6, '/sphereUnit2/C/7':20, '/sphereUnit2/C/8':20,
                '/sphereUnit3/A/7':22, '/sphereUnit3/B/10':6, '/sphereUnit3/C/7':20, '/sphereUnit3/C/8':16,
                '/sphereUnit4/A/7':22, '/sphereUnit4/B/10':6, '/sphereUnit4/C/7':20, '/sphereUnit4/C/8':16,
                '/sphereUnit5/A/7':22, '/sphereUnit5/B/10':6, '/sphereUnit5/C/7':20, '/sphereUnit5/C/8':20,
                '/sphereUnit6/A/7':22, '/sphereUnit6/B/10':6, '/sphereUnit6/C/7':20, '/sphereUnit6/C/8':16,
                '/sphereUnit7/A/7':22, '/sphereUnit7/B/10':6, '/sphereUnit7/C/7':20, '/sphereUnit7/C/8':16,
                '/sphereUnit8/A/7':22, '/sphereUnit8/B/10':6, '/sphereUnit8/C/7':20, '/sphereUnit8/C/8':20,
                '/sphereUnit9/A/7':22, '/sphereUnit9/B/10':6, '/sphereUnit9/C/7':20, '/sphereUnit9/C/8':16,
                '/sphereUnit10/A/7':22, '/sphereUnit10/B/10':6, '/sphereUnit10/C/7':20, '/sphereUnit10/C/8':16,
                '/sphereUnit11/A/7':22, '/sphereUnit11/B/10':6, '/sphereUnit11/C/7':20, '/sphereUnit11/C/8':20,
                '/sphereUnit12/A/7':22, '/sphereUnit12/B/10':6, '/sphereUnit12/C/7':20, '/sphereUnit12/C/8':16,
                }


# Sphere chunks
# RPi_s# = list of sphere units attached to RPi on sphere unit #
RPi_s2 = [1,2,3] #master
RPi_s5 = [4,5,6] #slave
RPi_s8 = [7,8,9] #slave
RPi_s11 = [10,11,12] #slave

# IP addresses corresponding to each Raspberry Pi
s5_ip = '10.1.19.12'
s8_ip = '10.1.19.16'
s11_ip = '10.1.19.17'

# 4D laptop IP address
# not used
laptop_4d_ip = '1.2.3.4'

if __name__ == '__main__':

    global_variable = GlobalVariable()

    ###
    ### OSC handlers ###
    ###

    # Checks to see if the incoming OSC address is meant for the master
    # if so, sends a sequence of bytes to each node to actuate the LED or moth

    # COMMAND STRUCTURE
    # <COMMAND_BYTE><teensy number><pin><value>
    # effect: sets the pin on teensy_number to value

    # NODE ENUMERATION (teensy_number)
    # Each node is assigned a unique number from 0-23
    # With 0-11 denoting central nodes in order of their sphere units
    # and 12-23 denoting peripheral nodes in order of their sphere units
    

    # if message is for slave,
    # forward the OSC message to the appropriate Raspberry Pi
    def led_handler_master(addr, value):

        print("addr: " + addr)
        #global_variable.count += 1
        #print("count: " + str(global_variable.count))

        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])
        
        pin = led_pin_dict[addr]

        if my_type == 'master':
            if unit in RPi_s2:
                teensy_number = unit - 1 + 12
                for ser in S.serial_list:
                    print('sending: ' + str(teensy_number) + ', ' + str(pin) + ', ' + str(value))
                    ser.write(COMMAND_BYTE)
                    ser.write(bytes([teensy_number]))
                    ser.write(bytes([pin]))
                    ser.write(bytes([value]))
                print('serial message sent')
            elif unit in RPi_s5:
                slave_s5.send_message(addr, value)
                print('OSC message sent')
            elif unit in RPi_s8:
                slave_s8.send_message(addr, value)
                print('OSC message sent')
            elif unit in RPi_s11:
                slave_s11.send_message(addr, value)
                print('OSC message sent')
        else:
            teensy_number = unit - 1 + 12
            for ser in S.serial_list:
                print('sending: ' + str(teensy_number) + ', ' + str(pin) + ', ' + str(value))
                ser.write(COMMAND_BYTE)
                ser.write(bytes([teensy_number]))
                ser.write(bytes([pin]))
                ser.write(bytes([value]))
            print('serial message sent')
            
            


    def moth_handler_master(addr, value):
        print("addr: " + addr)            

        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])
        
        pin = moth_pin_dict[addr]

        if my_type == 'master':
            if unit in RPi_s2:
                teensy_number = unit - 1
                for ser in S.serial_list:
                    print('sending: ' + str(teensy_number) + ', ' + str(pin) + ', ' + str(value))
                    ser.write(COMMAND_BYTE)
                    ser.write(bytes([teensy_number]))
                    ser.write(bytes([pin]))
                    ser.write(bytes([value]))
                print('serial message sent')
            elif unit in RPi_s5:
                slave_s5.send_message(addr, value)
                print('OSC message sent')
            elif unit in RPi_s8:
                slave_s8.send_message(addr, value)
                print('OSC message sent')
            elif unit in RPi_s11:
                slave_s11.send_message(addr, value)
                print('OSC message sent')

        else:
            teensy_number = unit - 1
            for ser in S.serial_list:
                print('sending: ' + str(teensy_number) + ', ' + str(pin) + ', ' + str(value))
                ser.write(COMMAND_BYTE)
                ser.write(bytes([teensy_number]))
                ser.write(bytes([pin]))
                ser.write(bytes([value]))
            print('serial message sent')
            
            
        
    # OSC message dispatcher
    # maps functions to OSC addresses
    dispatcher = dispatcher.Dispatcher()

    # add all addresses to dispatcher with respective function
    # note for future: just make a handler with the '?' OSC identifier
    # to catch all addresses in one dispatcher function
    for key in led_pin_dict.keys():       
        dispatcher.map(key, led_handler_master)

    for key in moth_pin_dict.keys():          
        dispatcher.map(key, moth_handler_master)
        

    # Initialize blocking OSC server
    # will process OSC messages sequentially
    # For laptop control: port 3005
    # For 4D Engine control: port 3001
    OSC_listener = osc_server.BlockingOSCUDPServer(('0.0.0.0', 3005), dispatcher)#3001), dispatcher)

    # start server on its own thread
    OSC_listener_thread = threading.Thread(target=OSC_listener.serve_forever)
    OSC_listener_thread.start()

    # OSC outputs
    slave_s5 = udp_client.SimpleUDPClient(s5_ip, 3005)#3001)
    slave_s8 = udp_client.SimpleUDPClient(s8_ip, 3005)#3001)
    slave_s11 = udp_client.SimpleUDPClient(s11_ip, 3005)#3001)
    laptop_4d = udp_client.SimpleUDPClient(laptop_4d_ip, 3000)
    

    print("Starting Main Program")

    ## Interrupts OSC control, don't use
##    while True:
##        pass
##        for ser in S.serial_list:
##            if ser.inWaiting() > 0:
##                ser.read()
##                laptop_4d.send_message('/bang', 0)
##                print('IR bang sent')
