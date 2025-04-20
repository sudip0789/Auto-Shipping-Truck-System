"""
User Controller for managing user-related operations
"""
import logging
import hashlib
import time
import uuid
from flask import current_app
from app.utils.aws_utils import (
    dynamodb_get_item, 
    dynamodb_put_item, 
    dynamodb_update_item, 
    dynamodb_delete_item,
    dynamodb_scan
)

def hash_password(password):
    """
    Create a simple hash of the password
    
    Args:
        password (str): The password to hash
        
    Returns:
        str: The hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """
    Authenticate a user with username and password
    
    Args:
        username (str): The username
        password (str): The password
        
    Returns:
        dict: User object if authenticated, None otherwise
    """
    users_table = current_app.config.get('DYNAMODB_USERS_TABLE')
    logging.info(f"Authenticating user {username} against table {users_table}")
    
    try:
        # Get user from DynamoDB
        user = dynamodb_get_item(users_table, {'username': username})
        
        if not user:
            logging.warning(f"User {username} not found")
            return None
        
        # Check password
        hashed_password = hash_password(password)
        if user.get('password') != hashed_password:
            logging.warning(f"Invalid password for user {username}")
            return None
        
        # Remove password from user object before returning
        user_data = {k: v for k, v in user.items() if k != 'password'}
        return user_data
        
    except Exception as e:
        logging.error(f"Error authenticating user {username}: {e}")
        return None

def get_all_users():
    """
    Get all users from the database
    
    Returns:
        list: List of user objects with passwords removed
    """
    users_table = current_app.config.get('DYNAMODB_USERS_TABLE')
    try:
        users = dynamodb_scan(users_table)
        # Remove passwords from user objects
        for user in users:
            if 'password' in user:
                del user['password']
        return users
    except Exception as e:
        logging.error(f"Error fetching all users: {e}")
        return []

def get_user(username):
    """
    Get a specific user by username
    
    Args:
        username (str): Username of the user to retrieve
    
    Returns:
        dict: User object if found, None otherwise
    """
    users_table = current_app.config.get('DYNAMODB_USERS_TABLE')
    try:
        user = dynamodb_get_item(users_table, {'username': username})
        if user and 'password' in user:
            del user['password']
        return user
    except Exception as e:
        logging.error(f"Error fetching user {username}: {e}")
        return None

def add_user(user_data):
    """
    Add a new user to the database
    
    Args:
        user_data (dict): User data containing details
        
    Returns:
        dict: Added user object with password removed
    """
    users_table = current_app.config.get('DYNAMODB_USERS_TABLE')
    logging.info(f"[add_user] Called with data: {user_data}. Target table: {users_table}")
    
    try:
        # Validate input
        if 'username' not in user_data or not isinstance(user_data['username'], str):
            return {'error': 'Username must be a string'}
        
        if 'password' not in user_data or not isinstance(user_data['password'], str):
            return {'error': 'Password must be a string'}
        
        # Check if user already exists
        existing_user = get_user(user_data['username'])
        if existing_user:
            return {'error': f"User {user_data['username']} already exists"}
        
        # Hash the password
        user_data['password'] = hash_password(user_data['password'])
        
        # Add timestamps
        timestamp = int(time.time())
        user_data['created_at'] = timestamp
        
        # Set default role if not provided
        if 'role' not in user_data:
            user_data['role'] = 'user'
        
        # Store user in DynamoDB
        response = dynamodb_put_item(users_table, user_data)
        logging.info(f"[add_user] Successfully added user. DynamoDB response: {response}")
        
        # Remove password before returning
        result = {k: v for k, v in user_data.items() if k != 'password'}
        return result
        
    except Exception as e:
        logging.error(f"[add_user] Error adding user: {e}")
        return {'error': str(e)}

def update_user(username, user_data):
    """
    Update an existing user
    
    Args:
        username (str): Username of the user to update
        user_data (dict): New user data
        
    Returns:
        dict: Updated user object with password removed
    """
    users_table = current_app.config.get('DYNAMODB_USERS_TABLE')
    logging.info(f"[update_user] Updating username={username} in table {users_table}")
    
    # Check if user exists
    user = get_user(username)
    if not user:
        logging.warning(f"User {username} not found")
        return {'error': f'User {username} not found'}
    
    # If password is being updated, hash it
    if 'password' in user_data:
        user_data['password'] = hash_password(user_data['password'])
    
    # Create update expression and attribute values
    update_expression = "SET "
    expression_values = {}
    
    for key, value in user_data.items():
        if key != 'username':  # Don't update the primary key
            update_expression += f"{key} = :{key}, "
            expression_values[f':{key}'] = value
    
    # Remove trailing comma and space
    update_expression = update_expression[:-2]
    
    try:
        # Update user in DynamoDB
        response = dynamodb_update_item(
            users_table,
            {'username': username},
            update_expression,
            expression_values
        )
        logging.info(f"[update_user] Successfully updated user. Response: {response}")
        
        # Get updated user
        updated_user = get_user(username)
        return updated_user
        
    except Exception as e:
        logging.error(f"[update_user] Error updating user: {e}")
        return {'error': str(e)}

def delete_user(username):
    """
    Delete a user
    
    Args:
        username (str): Username of the user to delete
        
    Returns:
        dict: Result of deletion
    """
    users_table = current_app.config.get('DYNAMODB_USERS_TABLE')
    logging.info(f"[delete_user] Deleting username={username} from table {users_table}")
    
    # Check if user exists
    user = get_user(username)
    if not user:
        logging.warning(f"User {username} not found")
        return {'error': f'User {username} not found'}
    
    try:
        # Delete user from DynamoDB
        response = dynamodb_delete_item(users_table, {'username': username})
        logging.info(f"[delete_user] Successfully deleted user. Response: {response}")
        return {'message': f'User {username} deleted successfully'}
        
    except Exception as e:
        logging.error(f"[delete_user] Error deleting user: {e}")
        return {'error': str(e)}
