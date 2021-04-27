# This file was based on the following two sources:
# https://stackoverflow.com/a/66214236
# https://www.rabbitmq.com/tutorials/tutorial-one-python.html

import serial
import time
import json
import pika

MeasurementID = 0

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='PAWS_DataQ')

serialPort = serial.Serial(
    port="/dev/ttyUSB0", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART
while 1:
    # Wait until there is data waiting in the serial buffer
    if serialPort.in_waiting > 0:

        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()

        # Print the contents of the serial data
        try:
            print(serialString.decode("Ascii"))
            MeasurementID += 1
            data = {
                'SensorID': 1,
                'MeasurementID': MeasurementID,
                'Humidity': int(serialString.strip()),
                'Target': 400
            }
            channel.basic_publish(exchange='', routing_key='PAWS_DataQ', body=json.dumps(data))
            print(f'  [x] sent {data}')
        except:
            pass
