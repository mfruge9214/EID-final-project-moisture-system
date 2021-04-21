import xbee
from machine import I2C
from moisture_sensor import Seesaw
import time

i2c_bus = I2C(1, freq=400000)
 
ss = Seesaw(i2c_bus, addr=0x36)
 

while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()
 
    # read temperature from the temperature sensor
    #temp = ss.get_temp()
    output = str(touch) + '\n'
    print(touch)
    xbee.transmit(xbee.ADDR_BROADCAST, output)
     
    #print("temp: " + str(temp) + "  moisture: " + str(touch))
    time.sleep(1)