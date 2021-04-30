import requests
import json

targets_file = 'targets.json'

def init_targets():
    targets = {}
    url = 'https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/targets'
    resp = requests.get(url)
    for sensor in resp.json()['Items']:
        targets[sensor['SensorID']['N']] = sensor['Target']['N']
    with open(targets_file, 'w+') as f:
        json.dump(targets, f, indent=4)

def get_target(sensorID):
    targets = {}
    with open(targets_file, 'r') as f:
        targets = json.load(f)
    return targets[sensorID]

def set_target(sensorID, target):
    targets = {}
    with open(targets_file, 'r') as f:
        targets = json.load(f)
    with open(targets_file, 'w') as f:
        targets[sensorID] = target
        json.dump(targets, f, indent=4)
