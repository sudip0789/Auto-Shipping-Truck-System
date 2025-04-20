#!/usr/bin/env python3
"""
Script to set up DynamoDB tables for the Autonomous Shipping Truck Management Platform.
This script will create the necessary tables and populate them with sample data.
"""
import boto3
import uuid
import time
import hashlib
import os
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_REGION = 'us-east-2'
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', 'your-access-key')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', 'your-secret-key')

# Table names
DYNAMODB_USERS_TABLE = 'ast-users'
DYNAMODB_TRUCKS_TABLE = 'ast-trucks'
DYNAMODB_ALERTS_TABLE = 'ast-alerts'
DYNAMODB_ROUTES_TABLE = 'ast-routes'

def create_dynamodb_client():
    """Create and return a DynamoDB client"""
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    return session.resource('dynamodb')

def create_table(dynamodb, table_name, key_schema, attribute_definitions):
    """Create a DynamoDB table if it doesn't exist"""
    existing_tables = [table.name for table in dynamodb.tables.all()]
    
    if table_name in existing_tables:
        print(f"Table {table_name} already exists.")
        return dynamodb.Table(table_name)
    
    print(f"Creating table {table_name}...")
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    # Wait for table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Table {table_name} created successfully.")
    return table

def hash_password(password):
    """Create a simple hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_users_table(dynamodb):
    """Create the users table"""
    table = create_table(
        dynamodb,
        DYNAMODB_USERS_TABLE,
        key_schema=[{'AttributeName': 'username', 'KeyType': 'HASH'}],
        attribute_definitions=[{'AttributeName': 'username', 'AttributeType': 'S'}]
    )
    
    # Add sample users
    sample_users = [
        {
            'username': 'sudip',
            'password': hash_password('1234'),
            'email': 'admin@example.com'
        },
        {
            'username': 'user',
            'password': hash_password('password'),
            'email': 'user@example.com'
        }
    ]
    
    for user in sample_users:
        try:
            table.put_item(Item=user)
            print(f"Added user: {user['username']}")
        except Exception as e:
            print(f"Error adding user {user['username']}: {str(e)}")
    
    return table

def create_trucks_table(dynamodb):
    """Create the trucks table"""
    table = create_table(
        dynamodb,
        DYNAMODB_TRUCKS_TABLE,
        key_schema=[{'AttributeName': 'truck_id', 'KeyType': 'HASH'}],
        attribute_definitions=[{'AttributeName': 'truck_id', 'AttributeType': 'S'}]
    )
    
    # Add sample trucks
    sample_trucks = [
        {
            'truck_id': f"truck-{uuid.uuid4()}",
            'truck_name': 'Alpha Hauler',
            'truck_model': 'Tesla Semi',
            'manufacture_year': 2023,
            'status': 'active'
        },
        {
            'truck_id': f"truck-{uuid.uuid4()}",
            'truck_name': 'Beta Transporter',
            'truck_model': 'Volvo VNR Electric',
            'manufacture_year': 2022,
            'status': 'maintenance'
        },
        {
            'truck_id': f"truck-{uuid.uuid4()}",
            'truck_name': 'Gamma Freighter',
            'truck_model': 'Freightliner eCascadia',
            'manufacture_year': 2023,
            'status': 'idle'
        }
    ]
    
    for truck in sample_trucks:
        try:
            table.put_item(Item=truck)
            print(f"Added truck: {truck['truck_name']}")
        except Exception as e:
            print(f"Error adding truck {truck['truck_name']}: {str(e)}")
    
    return table

def create_alerts_table(dynamodb):
    """Create the alerts table"""
    table = create_table(
        dynamodb,
        DYNAMODB_ALERTS_TABLE,
        key_schema=[{'AttributeName': 'alert_id', 'KeyType': 'HASH'}],
        attribute_definitions=[{'AttributeName': 'alert_id', 'AttributeType': 'S'}]
    )
    
    # Add sample alerts
    sample_alerts = [
        {
            'alert_id': f"alert-{uuid.uuid4()}",
            'truck_id': 'truck-1',
            'alert_type': 'maintenance',
            'severity': 'warning',
            'message': 'Scheduled maintenance due in 3 days',
            'status': 'active'
        },
        {
            'alert_id': f"alert-{uuid.uuid4()}",
            'truck_id': 'truck-2',
            'alert_type': 'system',
            'severity': 'critical',
            'message': 'Battery level below 20%',
            'status': 'active'
        },
        {
            'alert_id': f"alert-{uuid.uuid4()}",
            'truck_id': 'truck-3',
            'alert_type': 'weather',
            'severity': 'info',
            'message': 'Heavy rain expected on route',
            'status': 'resolved'
        }
    ]
    
    for alert in sample_alerts:
        try:
            table.put_item(Item=alert)
            print(f"Added alert: {alert['alert_type']} - {alert['message']}")
        except Exception as e:
            print(f"Error adding alert: {str(e)}")
    
    return table

def create_routes_table(dynamodb):
    """Create the routes table"""
    table = create_table(
        dynamodb,
        DYNAMODB_ROUTES_TABLE,
        key_schema=[{'AttributeName': 'route_id', 'KeyType': 'HASH'}],
        attribute_definitions=[{'AttributeName': 'route_id', 'AttributeType': 'S'}]
    )
    
    # Add sample routes
    sample_routes = [
        {
            'route_id': f"route-{uuid.uuid4()}",
            'truck_id': 'truck-1',
            'start_location': 'San Francisco, CA',
            'end_location': 'Los Angeles, CA',
            'estimated_duration': 6,
            'status': 'in_progress'
        },
        {
            'route_id': f"route-{uuid.uuid4()}",
            'truck_id': 'truck-3',
            'start_location': 'Seattle, WA',
            'end_location': 'Portland, OR',
            'estimated_duration': 3,
            'status': 'scheduled'
        },
        {
            'route_id': f"route-{uuid.uuid4()}",
            'truck_id': 'truck-2',
            'start_location': 'San Jose State University',
            'end_location': 'UC Berkeley',
            'estimated_duration': 1,
            'status': 'completed'
        }
    ]
    
    for route in sample_routes:
        try:
            table.put_item(Item=route)
            print(f"Added route: {route['start_location']} to {route['end_location']}")
        except Exception as e:
            print(f"Error adding route: {str(e)}")
    
    return table

def main():
    """Main function to set up all tables"""
    print("Setting up DynamoDB tables for Autonomous Shipping Truck Management Platform...")
    
    try:
        dynamodb = create_dynamodb_client()
        
        # Create tables
        create_users_table(dynamodb)
        create_trucks_table(dynamodb)
        create_alerts_table(dynamodb)
        create_routes_table(dynamodb)
        
        print("All tables created and populated successfully!")
        
    except Exception as e:
        print(f"Error setting up tables: {str(e)}")


    # Sanity check: scan each table and print item count
    for table_name in [DYNAMODB_USERS_TABLE, DYNAMODB_TRUCKS_TABLE, DYNAMODB_ALERTS_TABLE, DYNAMODB_ROUTES_TABLE]:
        table = dynamodb.Table(table_name)
        response = table.scan()
        print(f"\n[{table_name}] - Total items: {len(response['Items'])}")
        for item in response['Items']:
            print(item)


if __name__ == "__main__":
    main()
