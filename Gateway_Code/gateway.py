# this file was based on a combination of the following two sources:
# https://www.rabbitmq.com/tutorials/tutorial-one-python.html
# https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/basicPubSub/basicPubSub.py

import pika, sys, os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import targets

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    data = json.loads(message.payload)
    targets.targets[data['SensorID']] = data['Target']

AllowedActions = ['both', 'publish', 'subscribe']

host = 'a1uvasdn6ihfum-ats.iot.us-east-2.amazonaws.com'
rootCAPath = '../../root-CA.crt'
certificatePath = '../../rpi4.cert.pem'
privateKeyPath = '../../rpi4.private.key'
port = 8883
clientId = 'basicPubSub'
dataTopic = 'PAWS/SensorData'
targetTopic = 'PAWS/SensorTargets'


myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(targetTopic, 1, customCallback)
time.sleep(2)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='PAWS_DataQ', durable=False)

def rabbitmq_callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    myAWSIoTMQTTClient.publish(dataTopic, body.decode("utf-8"), 1)
    print('Published topic %s: %s\n' % (dataTopic, body))

channel.basic_consume(queue='PAWS_DataQ', on_message_callback=rabbitmq_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
