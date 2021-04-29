import requests

targets = {}

def init_targets():
    url = 'https://hb4bbdba0i.execute-api.us-east-2.amazonaws.com/alpha/sensors/targets'
    resp = requests.get(url)
    for sensor in resp.json()['Items']:
        targets[sensor['SensorID']['N']] = sensor['Target']['N']
