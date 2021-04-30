# Plant Automated Watering System (PAWS)

## Team Members
Bryan Cisneros and Mike Fruge

## Languages and Environments
This project is written in Python and runs in several different environments,
as detailed below

## Overview
The following sections describe the various components of our system

### Soil Moisture sensor
Measures the amount of moisture present in the soil.

### XBee
MicroPython running on a Digi XBee3 interfaces with the soil moisture sensor and
sends the measurements to the gateway.

### Gateway
The gateway, Raspberry Pi 4, receives the incoming measurements from sensors and
interfaces with AWS to store the measurements in the cloud

### AWS
The measurents and configurations of the sensors are stored in the AWS cloud.
An IoT Thing is used to collect data from the gateway, and an API Gateway
provides an interface for the UI to access the sensor data. A Lambda function
bridges the gap between each of these elements to pass data around as needed.

### Qt UI
The Qt UI application code runs on a Windows machine and allows the user to
create new sensors and monitor and update existing sensors.

  This file has dependencies that can be installed using `python -m pip install <package>`
  
  The list of packages is as follows:
  - requests
  - PyQt5

## Execution instructions
1. The AWS code can be run as is, assuming you have proper permissions set up.
2. There are two processes to run the gateway code. You can run them with
`python3 receive.py` and `python3 gateway.py`
3. The XBee code runs on a Digi XBee3 module. Instructions on how to run code
can be found in Digi's
[MicroPython Programming Guide](https://www.digi.com/resources/documentation/digidocs/PDFs/90002219.pdf)
4. The Qt UI runs on a Windows machine with `python PAWS_InterfaceRoutine.py`
