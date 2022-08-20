import boto3
import json
import logging
from custom_encoder import CustomEncoder


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName ='product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)


getMethod ='GET'
postMethod ='POST'
patchMethod ='PATCH'
deleteMethod = 'DELETE'

healthPath ='/health'
productPath = '/product'
productsPath = '/products'



def lambda_handler(event, contect ):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
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
        response = modifyProduct(requestBody)  
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
            return buildResponse(404, {'Message:' 'ProductID: %s not found' % productId})   
    except:
        logger.exception('Do your custome error handling')

def getProducts():
    try:
        response = table.scan()
        result = response['item']

        while 'LastEvaluatedkey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedkey'])
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

            UpdateExpression='set %s = :value'% updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            returnValues ='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdateAttributes': response
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
            returnValues= 'ALL_OLD'   
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