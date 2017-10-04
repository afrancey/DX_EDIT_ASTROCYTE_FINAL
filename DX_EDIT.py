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

S = NodeSerial.NodeSerial()

#Instruction Message Codes
INSTRUCT_CODE_GET_TEENSY_ID = b'\x00'
INSTRUCT_CODE_ACTIVATE_LED = b'\xAA'
##INSTRUCT_CODE_PLAY_SD_WAV = b'\x0F'

COMMAND_BYTE = b'\xff'



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

slave_moth_pin_dict = { '/slave/sphereUnit1/speaker/0':9, '/slave/sphereUnit1/speaker/1':10, '/slave/sphereUnit1/speaker/2': 22,
                  '/slave/sphereUnit1/speaker/3': 23, '/slave/sphereUnit1/speaker/4':29, '/slave/sphereUnit1/speaker/5':30,
                  '/slave/sphereUnit2/speaker/0':9, '/slave/sphereUnit2/speaker/1':10, '/slave/sphereUnit2/speaker/2': 22,
                  '/slave/sphereUnit2/speaker/3': 23, '/slave/sphereUnit2/speaker/4':29, '/slave/sphereUnit2/speaker/5':30,
                  '/slave/sphereUnit3/speaker/0':9, '/slave/sphereUnit3/speaker/1':10, '/slave/sphereUnit3/speaker/2': 22,
                  '/slave/sphereUnit3/speaker/3': 23, '/slave/sphereUnit3/speaker/4':29, '/slave/sphereUnit3/speaker/5':30,
                  '/slave/sphereUnit4/speaker/0':9, '/slave/sphereUnit4/speaker/1':10, '/slave/sphereUnit4/speaker/2': 22,
                  '/slave/sphereUnit4/speaker/3': 23, '/slave/sphereUnit4/speaker/4':29, '/slave/sphereUnit4/speaker/5':30,
                   '/slave/sphereUnit5/speaker/0':9, '/slave/sphereUnit5/speaker/1':10, '/slave/sphereUnit5/speaker/2': 22,
                  '/slave/sphereUnit5/speaker/3': 23, '/slave/sphereUnit5/speaker/4':29, '/slave/sphereUnit5/speaker/5':30,
                   '/slave/sphereUnit6/speaker/0':9, '/slave/sphereUnit6/speaker/1':10, '/slave/sphereUnit6/speaker/2': 22,
                  '/slave/sphereUnit6/speaker/3': 23, '/slave/sphereUnit6/speaker/4':29, '/slave/sphereUnit6/speaker/5':30,
                   '/slave/sphereUnit7/speaker/0':9, '/slave/sphereUnit7/speaker/1':10, '/slave/sphereUnit7/speaker/2': 22,
                  '/slave/sphereUnit7/speaker/3': 23, '/slave/sphereUnit7/speaker/4':29, '/slave/sphereUnit7/speaker/5':30,
                   '/slave/sphereUnit8/speaker/0':9, '/slave/sphereUnit8/speaker/1':10, '/slave/sphereUnit8/speaker/2': 22,
                  '/slave/sphereUnit8/speaker/3': 23, '/slave/sphereUnit8/speaker/4':29, '/slave/sphereUnit8/speaker/5':30,
                   '/slave/sphereUnit9/speaker/0':9, '/slave/sphereUnit9/speaker/1':10, '/slave/sphereUnit9/speaker/2': 22,
                  '/slave/sphereUnit9/speaker/3': 23, '/slave/sphereUnit9/speaker/4':29, '/slave/sphereUnit9/speaker/5':30,
                   '/slave/sphereUnit10/speaker/0':9, '/slave/sphereUnit10/speaker/1':10, '/slave/sphereUnit10/speaker/2': 22,
                  '/slave/sphereUnit10/speaker/3': 23, '/slave/sphereUnit10/speaker/4':29, '/slave/sphereUnit10/speaker/5':30,
                   '/slave/sphereUnit11/speaker/0':9, '/slave/sphereUnit11/speaker/1':10, '/slave/sphereUnit11/speaker/2': 22,
                  '/slave/sphereUnit11/speaker/3': 23, '/slave/sphereUnit11/speaker/4':29, '/slave/sphereUnit11/speaker/5':30,
                  '/slave/sphereUnit12/speaker/0':9, '/slave/sphereUnit12/speaker/1':10, '/slave/sphereUnit12/speaker/2': 22,
                  '/slave/sphereUnit12/speaker/3': 23, '/slave/sphereUnit12/speaker/4':29, '/slave/sphereUnit12/speaker/5':30,
                        
                  '/slave/sphereUnit1/A/7':22, '/slave/sphereUnit1/B/10':6, '/slave/sphereUnit1/C/7':20, '/slave/sphereUnit1/C/8':16,
                '/slave/sphereUnit2/A/7':22, '/slave/sphereUnit2/B/10':6, '/slave/sphereUnit2/C/7':20, '/slave/sphereUnit2/C/8':20,
                '/slave/sphereUnit3/A/7':22, '/slave/sphereUnit3/B/10':6, '/slave/sphereUnit3/C/7':20, '/slave/sphereUnit3/C/8':16,
                '/slave/sphereUnit4/A/7':22, '/slave/sphereUnit4/B/10':6, '/slave/sphereUnit4/C/7':20, '/slave/sphereUnit4/C/8':16,
                '/slave/sphereUnit5/A/7':22, '/slave/sphereUnit5/B/10':6, '/slave/sphereUnit5/C/7':20, '/slave/sphereUnit5/C/8':20,
                '/slave/sphereUnit6/A/7':22, '/slave/sphereUnit6/B/10':6, '/slave/sphereUnit6/C/7':20, '/slave/sphereUnit6/C/8':16,
                '/slave/sphereUnit7/A/7':22, '/slave/sphereUnit7/B/10':6, '/slave/sphereUnit7/C/7':20, '/slave/sphereUnit7/C/8':16,
                '/slave/sphereUnit8/A/7':22, '/slave/sphereUnit8/B/10':6, '/slave/sphereUnit8/C/7':20, '/slave/sphereUnit8/C/8':20,
                '/slave/sphereUnit9/A/7':22, '/slave/sphereUnit9/B/10':6, '/slave/sphereUnit9/C/7':20, '/slave/sphereUnit9/C/8':16,
                '/slave/sphereUnit10/A/7':22, '/slave/sphereUnit10/B/10':6, '/slave/sphereUnit10/C/7':20, '/slave/sphereUnit10/C/8':16,
                '/slave/sphereUnit11/A/7':22, '/slave/sphereUnit11/B/10':6, '/slave/sphereUnit11/C/7':20, '/slave/sphereUnit11/C/8':20,
                '/slave/sphereUnit12/A/7':22, '/slave/sphereUnit12/B/10':6, '/slave/sphereUnit12/C/7':20, '/slave/sphereUnit12/C/8':16,
                        
                }


RPi_s2 = [1,2,3] #master
RPi_s5 = [4,5,6] #slave
RPi_s8 = [7,8,9] #slave
RPi_s11 = [10,11,12] #slave

s5_ip = '10.1.19.12'
s8_ip = '10.1.19.16'
s11_ip = '10.1.19.17'


laptop_4d_ip = '1.2.3.4'

if __name__ == '__main__':

    # OSC handlers
    def led_handler_master(addr, value):
        print("addr: " + addr)

        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])
        
        pin = led_pin_dict[addr]

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
            slave_s5.send_message('/slave' + addr, value)
            print('OSC message sent')
        elif unit in RPi_s8:
            slave_s8.send_message('/slave' + addr, value)
            print('OSC message sent')
        elif unit in RPi_s11:
            slave_s11.send_message('/slave' + addr, value)
            print('OSC message sent')
            
            

    def led_handler_slave(addr, value):
        print("addr: " + addr)
        
        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])

        pin = slave_led_pin_dict[addr]
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
            slave_s5.send_message('/slave' + addr, value)
            print('OSC message sent')
        elif unit in RPi_s8:
            slave_s8.send_message('/slave' + addr, value)
            print('OSC message sent')
        elif unit in RPi_s11:
            slave_s11.send_message('/slave' + addr, value)
            print('OSC message sent')
            
            

    def moth_handler_slave(addr, value):
        print("addr: " + addr)
        
        # parse unit number from address
        s = addr[addr.index('Unit') + 4:]
        unit = int(s[:s.index('/')])

        # parse led number
        pin = slave_moth_pin_dict[addr]
        teensy_number = unit - 1
        for ser in S.serial_list:
            print('sending: ' + str(teensy_number) + ', ' + str(pin) + ', ' + str(value))
            ser.write(COMMAND_BYTE)
            ser.write(bytes([teensy_number]))
            ser.write(bytes([pin]))
            ser.write(bytes([value]))
        print('serial message sent')
        
                
    dispatcher = dispatcher.Dispatcher()

    for key in led_pin_dict.keys():       
        dispatcher.map(key, led_handler_master)
        
    for key in slave_led_pin_dict.keys():         
        dispatcher.map(key, led_handler_slave)

    for key in moth_pin_dict.keys():          
        dispatcher.map(key, moth_handler_master)
        
    for key in slave_moth_pin_dict.keys():     
        dispatcher.map(key, moth_handler_slave)

    OSC_listener = osc_server.BlockingOSCUDPServer(('0.0.0.0', 3001), dispatcher)
    OSC_listener_thread = threading.Thread(target=OSC_listener.serve_forever)
    OSC_listener_thread.start()

    # OSC outputs
    slave_s5 = udp_client.SimpleUDPClient(s5_ip, 3001)
    slave_s8 = udp_client.SimpleUDPClient(s8_ip, 3001)
    slave_s11 = udp_client.SimpleUDPClient(s11_ip, 3001)
    laptop_4d = udp_client.SimpleUDPClient(laptop_4d_ip, 3000)
    

    print("Starting Main Program")

    count = 0

    while True:
        for ser in S.serial_list:
            if ser.inWaiting() > 0:
                ser.read()
                laptop_4d.send_message('/bang', 0)
                print('IR bang sent')
