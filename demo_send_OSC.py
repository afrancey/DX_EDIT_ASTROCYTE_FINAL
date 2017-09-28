"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="10.1.19.19",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=3001,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  #for x in range(10):
  #client.send_message("/sphereUnit5/led2/out", 100)
  #time.sleep(1)

  while True:

      for b in range(50):
          for led in range(1,4):
              client.send_message("/sphereUnit2/led" + str(led) + "/in", b)
              time.sleep(0.05)
              
      for b in range(50):
          for led in range(1,4):
              client.send_message("/sphereUnit2/led" + str(led) + "/in", 50-b)
              time.sleep(0.05)


      for unit in range(1,6):
          for moth in range(0,6):
              client.send_message("/sphereUnit" + str(unit) + "/speaker/" + str(moth), 100)
              time.sleep(0.5)
              client.send_message("/sphereUnit" + str(unit) + "/speaker/" + str(moth), 0)
              time.sleep(0.1)

          for led in range(1,4):
              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/in", 100)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/in", 0)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/out", 100)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/out", 0)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit*2) + "/led" + str(led) + "/in", 100)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit*2) + "/led" + str(led) + "/in", 0)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit*2) + "/led" + str(led) + "/out", 100)
              time.sleep(0.1)
              client.send_message("/sphereUnit" + str(unit*2) + "/led" + str(led) + "/out", 0)
              time.sleep(0.1)

##      for unit in range(1,6):
##          for moth in range(0,6):
##              client.send_message("/sphereUnit" + str(unit) + "/speaker/" + str(moth), 100)
##              time.sleep(0.5)
##              client.send_message("/sphereUnit" + str(unit) + "/speaker/" + str(moth), 0)
##              time.sleep(0.1)

              
     ############################################ 
##      for unit in range(1,13):
##
##          for led in range(1,4):
##              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/in", 100)
##              time.sleep(0.1)
##              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/in", 0)
##              time.sleep(0.1)
##              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/out", 100)
##              time.sleep(0.1)
##              client.send_message("/sphereUnit" + str(unit) + "/led" + str(led) + "/out", 0)
##              time.sleep(0.1)
##          
