import json
import boto3


# this function based on https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
def put_measurement(SensorID, MeasurementID, Humidity, Target, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('PAWS_SensorData')
    response = table.put_item(
       Item={
            'SensorID': SensorID,
            'MeasurementID': MeasurementID,
            'Humidity': Humidity,
            'Target': Target,
        }
    )
    return response

def lambda_handler(event, context):
    print(f'Received event: {event}')
    
    ret = put_measurement(event['SensorID'], event['MeasurementID'], event['Humidity'], event['Target'])
    
    return {
        'statusCode': ret['ResponseMetadata']['HTTPStatusCode']
    }