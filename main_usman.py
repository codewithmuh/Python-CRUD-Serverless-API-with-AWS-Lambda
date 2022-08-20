import boto3
import json
import logging
from custom_encoder import CustomEncoder
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName ='YOUR TABLE NAME'
#dynamodb = boto3.resource('dynamodb')

table_url = f"https://dynamodb.us-east-2.amazonaws.com/{dynamodbTableName}"
dynamodb = boto3.resource(
            'dynamodb', aws_access_key_id='YOUR_ACCESS_KEY_ID',
            aws_secret_access_key='YOUR_ACCESS_KEY_ID',
            region_name="us-west-2", endpoint_url=table_url)

table = dynamodb.Table(dynamodbTableName)

getMethod ='GET'
postMethod ='POST'
patchMethod ='PATCH'
deleteMethod = 'DELETE'
healthPath ='/health'
productPath = '/product'
productsPath = '/products'


def lambda_handler(event, context):
    logger.info(event)
    #return buildResponse(200, event)
    httpMethod = event['httpMethod']
    path = event.get('queryStringParameters', {}).get('action')
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['productId'])
    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()
    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))
    elif httpMethod == patchMethod and path == productPath:
        requestBody =json.loads(event['body'])
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])  
    elif httpMethod == deleteMethod and path == productPath:
        requestBody =json.loads(event['body'])
        response = deleteProduct(requestBody['productId'])  
    else:
        response = buildResponse(404, 'Not Found')        

    return response

def getProduct(productId):
    try:
        response = table.get_item(
            key={
                'productId': productId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'ProductId: %s not found' % productId})   
    except:
        logger.exception('Do your custome error handling')

def getProducts():
    try:
        response = table.scan()
        result = response['item']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Item'])

        body = {

            'products': result
        }    
        return buildResponse(200, body)
    except:
        logger.exception('Do your custome error handling')

def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody  
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custome error handling')

def modifyProduct(productId, updateKey, updateValue):
    try:
        response = table.update_item(
            key={
                'productId': productId
            },
            UpdateExpression='set %s = :value' % updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues ='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttrebutes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custome error handling')
            
def deleteProduct(productId):
    try:
        response = table.delete_item(
            key={
                'productId': productId
            },
            ReturnValues= 'ALL_OLD'   
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custome error handling')
            

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls= CustomEncoder)
    return response    