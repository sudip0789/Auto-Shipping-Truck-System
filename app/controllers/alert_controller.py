"""
Alert Controller for managing alert-related operations
"""
import uuid
import time
from flask import current_app
from app.utils.aws_utils import (
    dynamodb_get_item, 
    dynamodb_put_item, 
    dynamodb_update_item, 
    dynamodb_delete_item,
    dynamodb_scan
)

def get_all_alerts():
    """
    Get all alerts from the database
    
    Returns:
        list: List of alert objects
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    return dynamodb_scan(alerts_table)

def get_alert(alert_id):
    """
    Get a specific alert by ID
    
    Args:
        alert_id (str): ID of the alert to retrieve
    
    Returns:
        dict: Alert object if found, None otherwise
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    return dynamodb_get_item(alerts_table, {'alert_id': alert_id})

def add_alert(alert_data):
    """
    Add a new alert to the database
    
    Args:
        alert_data (dict): Alert data containing details
        
    Returns:
        dict: Added alert object with ID
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    
    # Generate a unique alert ID if not provided
    if 'alert_id' not in alert_data:
        alert_data['alert_id'] = f"alert-{uuid.uuid4()}"
    
    # Add timestamps
    timestamp = int(time.time())
    alert_data['created_at'] = timestamp
    alert_data['updated_at'] = timestamp
    
    # Set default status if not provided
    if 'status' not in alert_data:
        alert_data['status'] = 'active'
    
    # Store alert in DynamoDB
    dynamodb_put_item(alerts_table, alert_data)
    
    return alert_data

def resolve_alert(alert_id, resolution_data):
    """
    Resolve an alert
    
    Args:
        alert_id (str): ID of the alert to resolve
        resolution_data (dict): Resolution details
        
    Returns:
        dict: Updated alert object
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    
    # Check if alert exists
    alert = get_alert(alert_id)
    if not alert:
        return {'error': f'Alert {alert_id} not found'}
    
    # Update alert with resolution data
    update_data = {
        'status': 'resolved',
        'resolved_at': int(time.time()),
        'updated_at': int(time.time())
    }
    
    # Add resolution notes if provided
    if 'resolution_notes' in resolution_data:
        update_data['resolution_notes'] = resolution_data['resolution_notes']
    
    # Add resolution action if provided
    if 'resolution_action' in resolution_data:
        update_data['resolution_action'] = resolution_data['resolution_action']
    
    # Create update expression and attribute values
    update_expression = "SET "
    expression_values = {}
    
    for key, value in update_data.items():
        update_expression += f"{key} = :{key}, "
        expression_values[f':{key}'] = value
    
    # Remove trailing comma and space
    update_expression = update_expression[:-2]
    
    # Update alert in DynamoDB
    dynamodb_update_item(
        alerts_table,
        {'alert_id': alert_id},
        update_expression,
        expression_values
    )
    
    # Get the updated alert
    return get_alert(alert_id)

def get_active_alerts():
    """
    Get all active (unresolved) alerts
    
    Returns:
        list: List of active alert objects
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    return dynamodb_scan(
        alerts_table,
        filter_expression='#status = :status',
        expression_values={':status': 'active'}
    )

def get_alerts_by_truck(truck_id):
    """
    Get all alerts for a specific truck
    
    Args:
        truck_id (str): ID of the truck
        
    Returns:
        list: List of alert objects for the truck
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    return dynamodb_scan(
        alerts_table,
        filter_expression='truck_id = :truck_id',
        expression_values={':truck_id': truck_id}
    )

def get_alerts_by_severity(severity):
    """
    Get all alerts with a specific severity level
    
    Args:
        severity (str): Severity level (e.g., 'critical', 'high', 'medium', 'low')
        
    Returns:
        list: List of alert objects with the specified severity
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    return dynamodb_scan(
        alerts_table,
        filter_expression='severity = :severity',
        expression_values={':severity': severity}
    )

def update_alert(alert_id, alert_data):
    """
    Update an existing alert
    
    Args:
        alert_id (str): ID of the alert to update
        alert_data (dict): Updated alert data
        
    Returns:
        dict: Updated alert object
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    
    # Check if alert exists
    alert = get_alert(alert_id)
    if not alert:
        return {'error': f'Alert {alert_id} not found'}
    
    # Add updated timestamp
    alert_data['updated_at'] = int(time.time())
    
    # Create update expression and attribute values
    update_expression = "SET "
    expression_values = {}
    
    for key, value in alert_data.items():
        # Skip the alert_id as it's the primary key
        if key != 'alert_id':
            update_expression += f"{key} = :{key}, "
            expression_values[f':{key}'] = value
    
    # Remove trailing comma and space
    update_expression = update_expression[:-2]
    
    # Update alert in DynamoDB
    dynamodb_update_item(
        alerts_table,
        {'alert_id': alert_id},
        update_expression,
        expression_values
    )
    
    # Get the updated alert
    return get_alert(alert_id)

def delete_alert(alert_id):
    """
    Delete an alert
    
    Args:
        alert_id (str): ID of the alert to delete
        
    Returns:
        dict: Result of the delete operation
    """
    alerts_table = current_app.config.get('DYNAMODB_ALERTS_TABLE')
    
    # Check if alert exists
    alert = get_alert(alert_id)
    if not alert:
        return {'error': f'Alert {alert_id} not found'}
    
    # Delete alert from DynamoDB
    dynamodb_delete_item(alerts_table, {'alert_id': alert_id})
    
    return {'message': f'Alert {alert_id} deleted successfully'}
