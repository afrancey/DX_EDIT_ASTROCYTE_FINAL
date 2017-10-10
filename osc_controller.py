import argparse
import random
import time
import math

from pythonosc import osc_message_builder
from pythonosc import udp_client


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="10.1.19.19",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=3005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  def turn_on_test(sphere_unit, val):
    for led in range(1,4):
        client.send_message("/test_1", val)
        client.send_message("/test_1", val)

  def turn_on_sphere_unit(sphere_unit, val):
    for led in range(1,4):
        client.send_message("/sphereUnit" + str(sphere_unit) + "/led" + str(led) + "/in", val)
        client.send_message("/sphereUnit" + str(sphere_unit) + "/led" + str(led) + "/out", val)

    for moth in [1,3]:
        client.send_message("/sphereUnit" + str(sphere_unit) + "/speaker/" + str(moth), val)
      
    


##  start = time.time()
##  for i in range(50):
##    turn_on_test(1,i)
##    turn_on_test(1,i)
##    turn_on_test(1,i)
##    turn_on_test(1,i)
##    #time.sleep(0.01)
##
##  end = time.time()
##
##  print('time: ' + str(end - start))
  
  #time.sleep(1)

  order1 = (1,2,11,3,10,4,9,5,8,6,7)
  order2 = (8,10,11,12,1,2,3,9,5,6,7,8,4)

  orders = [order1, order2]

  while True:

    random_event = random.randint(0, 100) < 20
    max_brightness = 30
    framerate = 0.08

    #random_event = True

    if random_event:

      print('starting global event')

      unit_list = [1,2,3,4,5,6,7,8,9,10,11,12]
      random.shuffle(unit_list)

      for b in range(max_brightness):
        for u in unit_list[0:3]:
          turn_on_sphere_unit(u,b)
          time.sleep(framerate)

      for b in range(max_brightness):
        for u1,u2 in zip(unit_list[0:3], unit_list[3:6]):
          turn_on_sphere_unit(u1,(max_brightness - 1) - b)
          turn_on_sphere_unit(u2, b)
          time.sleep(framerate)

      for b in range(max_brightness):
        for u1,u2 in zip(unit_list[3:6], unit_list[6:9]):
          turn_on_sphere_unit(u1,(max_brightness - 1) - b)
          turn_on_sphere_unit(u2, b)
          time.sleep(framerate)
          
      for b in range(max_brightness):
        for u1,u2 in zip(unit_list[6:9], unit_list[9:12]):
          turn_on_sphere_unit(u1,(max_brightness - 1) - b)
          turn_on_sphere_unit(u2, b)
          time.sleep(framerate)

      for b in range(max_brightness):
        for u in unit_list[9:12]:
          turn_on_sphere_unit(u,(max_brightness - 1) - b)
          time.sleep(framerate)


      print('global event complete')

    else:

      print('cycle starting')
      order = orders[random.randint(0, len(orders)-1)]

      #u = random.randint(1,11)
      #for u in range(1,12,2):
      #for u in range(1,2):
      for u in order:
        for i in range(max_brightness):
          turn_on_sphere_unit(u, i)
          time.sleep(framerate)

        for i in range(max_brightness):
          turn_on_sphere_unit(u, (max_brightness - 1) - i)
          turn_on_sphere_unit(u+1, i)
          time.sleep(framerate)

        for i in range(max_brightness):
          turn_on_sphere_unit(u+1, (max_brightness - 1) - i)
          time.sleep(framerate)

      print("cycle complete")

    time.sleep(60)



          
