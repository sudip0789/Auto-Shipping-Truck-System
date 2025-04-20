"""
AWS Utilities for interacting with AWS services like DynamoDB and S3
"""
import boto3
from flask import current_app
import logging
import os

# Global AWS clients
dynamodb = None
s3 = None

def init_aws_services(app):
    """
    Initialize AWS services for the application
    
    Args:
        app: Flask application instance
    """
    global dynamodb, s3

    # Allow explicit local override for development
    use_local = os.getenv('USE_LOCAL_DYNAMODB', 'false').lower() == 'true' or app.config.get('USE_LOCAL_DYNAMODB', False)
    aws_region = app.config.get('AWS_REGION', 'us-east-2')
    aws_access_key = app.config.get('AWS_ACCESS_KEY')
    aws_secret_key = app.config.get('AWS_SECRET_KEY')
    
    # Log configuration details (but mask sensitive parts)
    app.logger.info(f"Initializing AWS services in region: {aws_region}")
    app.logger.info(f"AWS credentials provided: {bool(aws_access_key and aws_secret_key)}")
    app.logger.info(f"Using local endpoints: {use_local}")

    try:
        if use_local:
            app.logger.warning("Using local DynamoDB endpoint (http://localhost:8000)")
            session = boto3.Session(region_name=aws_region)
            dynamodb = session.resource('dynamodb', endpoint_url='http://localhost:8000')
            s3 = session.resource('s3', endpoint_url='http://localhost:4566')  # LocalStack or similar
        else:
            # Use provided credentials if available
            if aws_access_key and aws_secret_key:
                app.logger.info("Using provided AWS credentials")
                session = boto3.Session(
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
            else:
                # Use default AWS credential chain (env vars, ~/.aws/credentials, etc.)
                app.logger.info("Using AWS credential chain from environment or profile")
                session = boto3.Session(region_name=aws_region)
                
            dynamodb = session.resource('dynamodb')
            s3 = session.resource('s3')

        # Test the connection by listing tables
        existing_tables = list(dynamodb.tables.all())
        table_names = [table.name for table in existing_tables]
        app.logger.info(f"AWS services initialized successfully. Found tables: {table_names}")
        
    except Exception as e:
        app.logger.error(f"Failed to initialize AWS services: {str(e)}")
        app.logger.error("Application will continue but AWS features may not work properly")
        # Still create the resources so that app doesn't crash, but operations will fail

    # Check if DynamoDB tables exist, create them if they don't
    ensure_tables_exist(app)

    # Check if S3 bucket exists, create it if it doesn't
    ensure_bucket_exists(app)

def ensure_tables_exist(app):
    """
    Ensure that all required DynamoDB tables exist
    
    Args:
        app: Flask application instance
    """
    tables_to_create = {
        app.config.get('DYNAMODB_USERS_TABLE'): {
            'KeySchema': [{'AttributeName': 'username', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'username', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        app.config.get('DYNAMODB_TRUCKS_TABLE'): {
            'KeySchema': [{'AttributeName': 'truck_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'truck_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        app.config.get('DYNAMODB_ALERTS_TABLE'): {
            'KeySchema': [{'AttributeName': 'alert_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'alert_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        app.config.get('DYNAMODB_ROUTES_TABLE'): {
            'KeySchema': [{'AttributeName': 'route_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'route_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
    }
    
    existing_tables = [table.name for table in dynamodb.tables.all()]
    
    for table_name, table_params in tables_to_create.items():
        if table_name not in existing_tables:
            try:
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=table_params['KeySchema'],
                    AttributeDefinitions=table_params['AttributeDefinitions'],
                    ProvisionedThroughput=table_params['ProvisionedThroughput']
                )
                app.logger.info(f"Created DynamoDB table: {table_name}")
                # Wait for table to be created
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            except Exception as e:
                app.logger.error(f"Error creating DynamoDB table {table_name}: {str(e)}")
        else:
            app.logger.info(f"DynamoDB table already exists: {table_name}")

def ensure_bucket_exists(app):
    """
    Ensure that the S3 bucket exists
    
    Args:
        app: Flask application instance
    """
    bucket_name = app.config.get('S3_BUCKET_NAME')
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        app.logger.info(f"S3 bucket already exists: {bucket_name}")
    except Exception:
        try:
            # Bucket doesn't exist, create it
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': app.config.get('AWS_REGION')}
                if app.config.get('AWS_REGION') != 'us-east-2' else {}
            )
            app.logger.info(f"Created S3 bucket: {bucket_name}")
        except Exception as e:
            app.logger.error(f"Error creating S3 bucket {bucket_name}: {str(e)}")

# DynamoDB Operation Helpers
def dynamodb_get_item(table_name, key):
    """Get an item from DynamoDB table"""
    table = dynamodb.Table(table_name)
    response = table.get_item(Key=key)
    return response.get('Item')

def dynamodb_put_item(table_name, item):
    """Add an item to DynamoDB table"""
    if not table_name:
        logging.warning(f"dynamodb_put_item called with empty table_name! Item: {item}")
        return {'error': 'Empty table name provided'}
    if not item:
        logging.warning(f"dynamodb_put_item called with empty item! Table: {table_name}")
        return {'error': 'Empty item provided'}
    
    try:
        logging.info(f"[DEBUG] Attempting to put item in table '{table_name}'. Key: {item.get('truck_id', 'unknown')}")
        logging.debug(f"Full item details: {item}")
        
        # Check if dynamodb is initialized
        if dynamodb is None:
            logging.error("DynamoDB client is not initialized")
            return {'error': 'DynamoDB client is not initialized'}
            
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item)
        
        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if status_code == 200:
            logging.info(f"[SUCCESS] Item successfully added to table '{table_name}'. Status: {status_code}")
            return {'success': True, 'message': f'Item added to {table_name}'}
        else:
            logging.warning(f"[WARNING] Unexpected status code: {status_code}")
            return {'success': False, 'status_code': status_code}
            
    except Exception as e:
        error_message = str(e)
        logging.error(f"[ERROR] Error putting item in table '{table_name}'. Exception: {error_message}")
        return {'error': error_message}

def dynamodb_update_item(table_name, key, update_expression, expression_values):
    """Update an item in DynamoDB table"""
    if not table_name or not key:
        logging.warning(f"dynamodb_update_item called with missing parameters. Table: {table_name}, Key: {key}")
        return {'error': 'Missing table name or key'}
    
    try:
        logging.info(f"[DEBUG] Attempting to update item in table '{table_name}'. Key: {key}")
        
        # Check if dynamodb is initialized
        if dynamodb is None:
            logging.error("DynamoDB client is not initialized")
            return {'error': 'DynamoDB client is not initialized'}
            
        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        
        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if status_code == 200:
            logging.info(f"[SUCCESS] Item successfully updated in table '{table_name}'. Status: {status_code}")
            return {'success': True, 'attributes': response.get('Attributes', {}), 'message': f'Item updated in {table_name}'}
        else:
            logging.warning(f"[WARNING] Unexpected status code: {status_code}")
            return {'success': False, 'status_code': status_code}
            
    except Exception as e:
        error_message = str(e)
        logging.error(f"[ERROR] Error updating item in table '{table_name}'. Key: {key}. Exception: {error_message}")
        return {'error': error_message}

def dynamodb_delete_item(table_name, key):
    """Delete an item from DynamoDB table"""
    if not table_name or not key:
        logging.warning(f"dynamodb_delete_item called with missing parameters. Table: {table_name}, Key: {key}")
        return {'error': 'Missing table name or key'}
    
    try:
        logging.info(f"[DEBUG] Attempting to delete item from table '{table_name}'. Key: {key}")
        
        # Check if dynamodb is initialized
        if dynamodb is None:
            logging.error("DynamoDB client is not initialized")
            return {'error': 'DynamoDB client is not initialized'}
            
        table = dynamodb.Table(table_name)
        response = table.delete_item(Key=key)
        
        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if status_code == 200:
            logging.info(f"[SUCCESS] Item successfully deleted from table '{table_name}'. Status: {status_code}")
            return {'success': True, 'message': f'Item deleted from {table_name}'}
        else:
            logging.warning(f"[WARNING] Unexpected status code: {status_code}")
            return {'success': False, 'status_code': status_code}
            
    except Exception as e:
        error_message = str(e)
        logging.error(f"[ERROR] Error deleting item from table '{table_name}'. Key: {key}. Exception: {error_message}")
        return {'error': error_message}

def dynamodb_scan(table_name, filter_expression=None, expression_values=None):
    """Scan items from DynamoDB table"""
    table = dynamodb.Table(table_name)
    params = {}
    
    if filter_expression and expression_values:
        params['FilterExpression'] = filter_expression
        params['ExpressionAttributeValues'] = expression_values
    
    response = table.scan(**params)
    return response.get('Items', [])

# S3 Operation Helpers
def s3_upload_file(bucket_name, file_obj, object_name, content_type=None):
    """Upload a file to S3 bucket"""
    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type
    
    s3.Bucket(bucket_name).upload_fileobj(file_obj, object_name, ExtraArgs=extra_args)
    return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"

def s3_get_object(bucket_name, object_name):
    """Get an object from S3 bucket"""
    response = s3.Object(bucket_name, object_name).get()
    return response['Body'].read()

def s3_delete_object(bucket_name, object_name):
    """Delete an object from S3 bucket"""
    s3.Object(bucket_name, object_name).delete()
    return True
