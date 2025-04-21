"""
Truck Controller for managing truck-related operations
"""
import uuid
import time
import logging
from flask import current_app
from app.utils.aws_utils import (
    dynamodb_get_item,
    dynamodb_put_item,
    dynamodb_update_item,
    dynamodb_delete_item,
    dynamodb_scan
)


def get_all_trucks():
    """
    Get all trucks from the database

    Returns:
        list: List of truck objects
    """
    trucks_table = current_app.config.get('DYNAMODB_TRUCKS_TABLE')
    logging.info(f"Using table: {trucks_table}")
    try:
        trucks = dynamodb_scan(trucks_table)
        logging.info(f"Retrieved trucks: {trucks}")
        return trucks
    except Exception as e:
        logging.error(f"Error fetching all trucks: {e}")
        return []


def get_truck(truck_id):
    """
    Get a specific truck by ID

    Args:
        truck_id (str): ID of the truck to retrieve

    Returns:
        dict: Truck object if found, None otherwise
    """
    trucks_table = current_app.config.get('DYNAMODB_TRUCKS_TABLE')
    logging.info(f"Querying table {trucks_table} for truck_id={truck_id}")
    try:
        response = dynamodb_get_item(trucks_table, {'truck_id': truck_id})
        logging.info(f"Received response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error fetching truck with ID {truck_id}: {e}")
        return None


def add_truck(truck_data):
    """
    Add a new truck to the database

    Args:
        truck_data (dict): Truck data containing details

    Returns:
        dict: Added truck object with ID
    """
    trucks_table = current_app.config.get('DYNAMODB_TRUCKS_TABLE')
    logging.info(
        f"[add_truck] Called with data: {truck_data}. Target table: {trucks_table}")
    try:
        # Debug: Log the incoming truck_data
        logging.debug(f"[add_truck] Incoming payload: {truck_data}")

        # Required fields for a truck
        required_fields = ['truck_name', 'truck_model', 'manufacture_year']
        missing_fields = [f for f in required_fields if f not in truck_data]
        if missing_fields:
            logging.warning(
                f"[add_truck] Missing required fields: {missing_fields}")
            return {'error': f'Missing required fields: {missing_fields}'}, 400

        # Validate types
        if not isinstance(truck_data['truck_name'], str):
            logging.warning(
                f"[add_truck] Invalid truck_name type: {type(truck_data['truck_name'])}")
            return {'error': 'Truck name must be a string'}, 400
        if not isinstance(truck_data['truck_model'], str):
            logging.warning(
                f"[add_truck] Invalid truck_model type: {type(truck_data['truck_model'])}")
            return {'error': 'Truck model must be a string'}, 400
        if not isinstance(truck_data['manufacture_year'], int):
            logging.warning(
                f"[add_truck] Invalid manufacture_year type: {type(truck_data['manufacture_year'])}")
            return {'error': 'Manufacture year must be an integer'}, 400

        # Generate a unique truck ID if not provided
        if 'truck_id' not in truck_data:
            truck_data['truck_id'] = f"truck-{uuid.uuid4()}"
            logging.info(
                f"[add_truck] Generated new truck ID: {truck_data['truck_id']}")

        # Add timestamps
        timestamp = int(time.time())
        truck_data['created_at'] = timestamp
        truck_data['last_updated'] = timestamp

        # Set default status if not provided
        if 'status' not in truck_data:
            truck_data['status'] = 'idle'

        # Clean up any potentially problematic data types for DynamoDB
        # Convert any float values to integers to avoid DynamoDB issues
        for key, value in truck_data.items():
            if isinstance(value, float):
                truck_data[key] = int(value)
                logging.info(
                    f"[add_truck] Converted float to int for {key}: {value} -> {truck_data[key]}")

        # Store truck in DynamoDB
        logging.info(
            f"[add_truck] Attempting to store truck in DynamoDB: {truck_data}")
        response = dynamodb_put_item(trucks_table, truck_data)
        logging.info(
            f"[add_truck] Successfully added truck. DynamoDB response: {response}")
        return truck_data
    except Exception as e:
        logging.error(f"[add_truck] Error adding truck: {e}")
        return {'error': str(e)}, 500


def update_truck(truck_id, truck_data):
    """
    Update an existing truck

    Args:
        truck_id (str): ID of the truck to update
        truck_data (dict): New truck data

    Returns:
        dict: Updated truck object
    """
    trucks_table = current_app.config.get('DYNAMODB_TRUCKS_TABLE')
    logging.info(
        f"[update_truck] Updating truck_id={truck_id} in table {trucks_table}")
    logging.info(f"[update_truck] Update data received: {truck_data}")

    # Debug: Log the incoming update payload
    logging.debug(
        f"[update_truck] truck_id={truck_id}, incoming payload: {truck_data}")

    # Check if truck exists
    truck = get_truck(truck_id)
    if not truck:
        logging.warning(f"Truck {truck_id} not found")
        return {'error': f'Truck {truck_id} not found'}, 404

    # Required fields for update (if present)
    if 'truck_name' in truck_data and not isinstance(truck_data['truck_name'], str):
        logging.warning(
            f"[update_truck] Invalid truck_name type: {type(truck_data['truck_name'])}")
        return {'error': 'Truck name must be a string'}, 400
    if 'truck_model' in truck_data and not isinstance(truck_data['truck_model'], str):
        logging.warning(
            f"[update_truck] Invalid truck_model type: {type(truck_data['truck_model'])}")
        return {'error': 'Truck model must be a string'}, 400
    if 'manufacture_year' in truck_data and not isinstance(truck_data['manufacture_year'], int):
        logging.warning(
            f"[update_truck] Invalid manufacture_year type: {type(truck_data['manufacture_year'])}")
        return {'error': 'Manufacture year must be an integer'}, 400

    # Update timestamp
    truck_data['last_updated'] = int(time.time())

    # Clean up any potentially problematic data types for DynamoDB
    # Convert any float values to integers to avoid DynamoDB issues
    for key, value in truck_data.items():
        if isinstance(value, float):
            truck_data[key] = int(value)
            logging.info(
                f"[update_truck] Converted float to int for {key}: {value} -> {truck_data[key]}")

    # Create update expression and attribute values
    update_expression = "SET "
    expression_values = {}

    for key, value in truck_data.items():
        if key != 'truck_id':  # Don't update the primary key
            update_expression += f"{key} = :{key}, "
            expression_values[f':{key}'] = value

    # Remove trailing comma and space
    update_expression = update_expression[:-2]

    try:
        # Update truck in DynamoDB
        logging.info(f"[update_truck] Update expression: {update_expression}")
        logging.info(f"[update_truck] Expression values: {expression_values}")

        response = dynamodb_update_item(
            trucks_table,
            {'truck_id': truck_id},
            update_expression,
            expression_values
        )
        logging.info(
            f"[update_truck] Successfully updated truck. Response: {response}")
        return get_truck(truck_id)
    except Exception as e:
        logging.error(f"[update_truck] Error updating truck: {e}")
        return {'error': str(e)}, 500


def delete_truck(truck_id):
    """
    Delete a truck

    Args:
        truck_id (str): ID of the truck to delete

    Returns:
        dict: Result of deletion
    """
    trucks_table = current_app.config.get('DYNAMODB_TRUCKS_TABLE')
    logging.info(
        f"[delete_truck] Deleting truck_id={truck_id} from table {trucks_table}")

    # Check if truck exists
    truck = get_truck(truck_id)
    if not truck:
        logging.warning(f"Truck {truck_id} not found")
        return {'error': f'Truck {truck_id} not found'}

    try:
        # Delete truck from DynamoDB
        response = dynamodb_delete_item(trucks_table, {'truck_id': truck_id})
        logging.info(
            f"[delete_truck] Successfully deleted truck. Response: {response}")
        return {'message': f'Truck {truck_id} deleted successfully'}
    except Exception as e:
        logging.error(f"[delete_truck] Error deleting truck: {e}")
        return {'error': str(e)}


def get_truck_location(truck_id):
    """
    Get the current location of a truck

    Args:
        truck_id (str): ID of the truck

    Returns:
        dict: Location information including coordinates
    """
    truck = get_truck(truck_id)
    if not truck:
        return {'error': f'Truck {truck_id} not found'}

    # In a real system, this would fetch real-time location data
    # For now, we'll return the stored location or a simulated one
    location = {
        'truck_id': truck_id,
        'latitude': truck.get('latitude', 0),
        'longitude': truck.get('longitude', 0),
        'speed': truck.get('speed', 0),
        'heading': truck.get('heading', 0),
        'timestamp': int(time.time())
    }

    return location


def get_truck_status(truck_id):
    """
    Get the current status of a truck

    Args:
        truck_id (str): ID of the truck

    Returns:
        dict: Status information
    """
    truck = get_truck(truck_id)
    if not truck:
        return {'error': f'Truck {truck_id} not found'}

    # In a real system, this would fetch real-time status data
    status = {
        'truck_id': truck_id,
        'status': truck.get('status', 'unknown'),
        'fuel_level': truck.get('fuel_level', 0),
        'battery_level': truck.get('battery_level', 0),
        'engine_temperature': truck.get('engine_temperature', 0),
        'timestamp': int(time.time())
    }

    return status
