import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,'
        },
    }


def publish_mqtt(topic, data):
    client = boto3.client('iot-data', region_name='us-east-2')
    response = client.publish(
            topic=topic,
            qos=1,
            payload=data
        )
    print(response)

def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    print("Begin Event")
    
    print(event)


    print("Begin Context")
    
    print(context)
    
    
    operation = event['httpMethod']
    
    sensorId = None
    if(event['pathParameters']):
        sensorId = int(event['pathParameters']['id'])
    
    
    if operation == 'GET':
        payload = { 'TableName': 'PAWS_SensorData' }
        
        if 'targets' in event['path']:
            payload = { 'TableName': 'PAWS_SensorConfigurations' }
        
        print("Begin Payload")
        print(payload)
        all_sensor_data = dynamo.scan(**payload)
        print(all_sensor_data)
        return respond(None, all_sensor_data)
    elif operation == 'PUT':
        if sensorId:
            body = json.loads(event['body'])
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('PAWS_SensorConfigurations')
            response = table.update_item(
                Key = {'SensorID': sensorId},
                UpdateExpression="set SensorName=:n, Target=:t",
                ExpressionAttributeValues={
                    ':n': body['SensorName'],
                    ':t': body['Target'],
                },
                ReturnValues="UPDATED_NEW"
            )
            print(response)
            publish_mqtt('PAWS/SensorTargets', json.dumps({'SensorID': sensorId, 'Target': body['Target']}))
            return respond(None)
        else:
            return respond(ValueError('Please provide sensor id'))
    elif operation == 'POST':
        if sensorId:
            if 'water/on' in event['path']:
                publish_mqtt('PAWS/SensorActions', json.dumps({'SensorID': sensorId, 'Action': 'on'}))
            elif 'water/off' in event['path']:
                publish_mqtt('PAWS/SensorActions', json.dumps({'SensorID': sensorId, 'Action': 'off'}))
                pass
            elif 'reset' in event['path']:
                publish_mqtt('PAWS/SensorActions', json.dumps({'SensorID': sensorId, 'Action': 'reset'}))
                pass
            else:
                body = json.loads(event['body'])
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table('PAWS_SensorConfigurations')
                response = table.put_item(
                   Item={
                        'SensorID': sensorId,
                        'SensorName': body['SensorName'],
                        'Target': body['Target']
                    }
                )
                publish_mqtt('PAWS/SensorTargets', json.dumps({'SensorID': sensorId, 'Target': body['Target']}))
            return respond(None)
        else:
            return respond(ValueError('Please provide sensor id'))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
