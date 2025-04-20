"""
Route Controller for managing route-related operations
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

def get_all_routes():
    """
    Get all routes from the database
    
    Returns:
        list: List of route objects
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    return dynamodb_scan(routes_table)

def get_route(route_id):
    """
    Get a specific route by ID
    
    Args:
        route_id (str): ID of the route to retrieve
    
    Returns:
        dict: Route object if found, None otherwise
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    return dynamodb_get_item(routes_table, {'route_id': route_id})

def add_route(route_data):
    """
    Add a new route to the database
    
    Args:
        route_data (dict): Route data containing start/end points and truck assignment
        
    Returns:
        dict: Added route object with ID
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    
    # Generate a unique route ID if not provided
    if 'route_id' not in route_data:
        route_data['route_id'] = f"route-{uuid.uuid4()}"
    
    # Add timestamps
    timestamp = int(time.time())
    route_data['created_at'] = timestamp
    route_data['updated_at'] = timestamp
    
    # Set default status if not provided
    if 'status' not in route_data:
        route_data['status'] = 'scheduled'
    
    # Validate required fields
    required_fields = ['start_location', 'end_location', 'truck_id']
    for field in required_fields:
        if field not in route_data:
            return {'error': f'Missing required field: {field}'}
    
    # Store route in DynamoDB
    dynamodb_put_item(routes_table, route_data)
    
    return route_data

def update_route(route_id, route_data):
    """
    Update an existing route
    
    Args:
        route_id (str): ID of the route to update
        route_data (dict): New route data
        
    Returns:
        dict: Updated route object
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    
    # Check if route exists
    route = get_route(route_id)
    if not route:
        return {'error': f'Route {route_id} not found'}
    
    # Update timestamp
    route_data['updated_at'] = int(time.time())
    
    # Create update expression and attribute values
    update_expression = "SET "
    expression_values = {}
    
    for key, value in route_data.items():
        if key != 'route_id':  # Don't update the primary key
            update_expression += f"{key} = :{key}, "
            expression_values[f':{key}'] = value
    
    # Remove trailing comma and space
    update_expression = update_expression[:-2]
    
    # Update route in DynamoDB
    dynamodb_update_item(
        routes_table,
        {'route_id': route_id},
        update_expression,
        expression_values
    )
    
    # Get the updated route
    return get_route(route_id)

def delete_route(route_id):
    """
    Delete a route
    
    Args:
        route_id (str): ID of the route to delete
        
    Returns:
        dict: Result of deletion
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    
    # Check if route exists
    route = get_route(route_id)
    if not route:
        return {'error': f'Route {route_id} not found'}
    
    # Delete route from DynamoDB
    dynamodb_delete_item(routes_table, {'route_id': route_id})
    
    return {'message': f'Route {route_id} deleted successfully'}

def get_routes_by_truck(truck_id):
    """
    Get all routes for a specific truck
    
    Args:
        truck_id (str): ID of the truck
        
    Returns:
        list: List of route objects assigned to the truck
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    return dynamodb_scan(
        routes_table,
        filter_expression='truck_id = :truck_id',
        expression_values={':truck_id': truck_id}
    )

def get_routes_by_status(status):
    """
    Get all routes with a specific status
    
    Args:
        status (str): Route status (e.g., 'scheduled', 'in_progress', 'completed')
        
    Returns:
        list: List of route objects with the specified status
    """
    routes_table = current_app.config.get('DYNAMODB_ROUTES_TABLE')
    return dynamodb_scan(
        routes_table,
        filter_expression='#status = :status',
        expression_values={':status': status}
    )

def start_route(route_id):
    """
    Mark a route as in progress
    
    Args:
        route_id (str): ID of the route to start
        
    Returns:
        dict: Updated route object
    """
    return update_route(route_id, {
        'status': 'in_progress',
        'started_at': int(time.time())
    })

def complete_route(route_id):
    """
    Mark a route as completed
    
    Args:
        route_id (str): ID of the route to complete
        
    Returns:
        dict: Updated route object
    """
    return update_route(route_id, {
        'status': 'completed',
        'completed_at': int(time.time())
    })
