import xbee
from machine import I2C
from moisture_sensor import Seesaw
import time
import json

i2c_bus = I2C(1, freq=400000)
 
ss = Seesaw(i2c_bus, addr=0x36)
 

while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()
 
    # read temperature from the temperature sensor
    #temp = ss.get_temp()
    data = {
        'SensorID': 1,
        'Humidity': touch
    }
    output = json.dumps(data) + '\n'
    print(output)
    xbee.transmit(xbee.ADDR_BROADCAST, output)
     
    time.sleep(10)
