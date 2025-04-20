"""
Simulation Controller for managing CARLA simulation operations
"""
import uuid
import time
import json
import subprocess
import threading
from flask import current_app
import logging

# Store simulation state
simulations = {}

def start_simulation(simulation_data):
    """
    Start a CARLA simulation
    
    Args:
        simulation_data (dict): Simulation configuration
        
    Returns:
        dict: Simulation status and ID
    """
    # Generate a unique simulation ID
    simulation_id = f"sim-{uuid.uuid4()}"
    
    # Get CARLA server settings from config
    carla_server = current_app.config.get('CARLA_SERVER')
    carla_port = current_app.config.get('CARLA_PORT')
    
    # Initialize simulation state
    simulations[simulation_id] = {
        'id': simulation_id,
        'status': 'starting',
        'start_time': int(time.time()),
        'config': simulation_data,
        'logs': [],
        'results': None
    }
    
    # In a real implementation, this would connect to the CARLA server
    # and start a simulation based on the provided configuration
    # For now, we'll simulate this process
    
    # Start simulation in a separate thread
    thread = threading.Thread(
        target=_run_simulation,
        args=(simulation_id, carla_server, carla_port, simulation_data)
    )
    thread.daemon = True
    thread.start()
    
    return {
        'simulation_id': simulation_id,
        'status': 'starting',
        'message': 'Simulation is being initialized'
    }

def get_simulation_status(simulation_id=None):
    """
    Get status of a simulation
    
    Args:
        simulation_id (str, optional): ID of simulation to check
        
    Returns:
        dict or list: Simulation status or list of all simulations
    """
    if simulation_id:
        if simulation_id in simulations:
            return simulations[simulation_id]
        else:
            return {'error': f'Simulation {simulation_id} not found'}
    else:
        # Return summary of all simulations
        return [
            {
                'id': sim_id,
                'status': sim_data['status'],
                'start_time': sim_data['start_time'],
                'duration': int(time.time()) - sim_data['start_time'] if sim_data['status'] != 'completed' else None
            }
            for sim_id, sim_data in simulations.items()
        ]

def stop_simulation(simulation_id=None):
    """
    Stop a CARLA simulation
    
    Args:
        simulation_id (str, optional): ID of simulation to stop
        
    Returns:
        dict: Result of stopping the simulation
    """
    if not simulation_id:
        # Get the most recent simulation if ID not provided
        if not simulations:
            return {'error': 'No active simulations found'}
        simulation_id = sorted(
            simulations.keys(),
            key=lambda x: simulations[x]['start_time'],
            reverse=True
        )[0]
    
    if simulation_id not in simulations:
        return {'error': f'Simulation {simulation_id} not found'}
    
    if simulations[simulation_id]['status'] == 'completed':
        return {'error': f'Simulation {simulation_id} is already completed'}
    
    # Update simulation status
    simulations[simulation_id]['status'] = 'stopping'
    
    # In a real implementation, this would send a stop command to the CARLA server
    # For now, we'll simulate this process
    
    # Finalize the simulation
    simulations[simulation_id]['status'] = 'completed'
    simulations[simulation_id]['end_time'] = int(time.time())
    
    return {
        'simulation_id': simulation_id,
        'status': 'completed',
        'message': 'Simulation stopped successfully'
    }

def get_simulation_results(simulation_id):
    """
    Get results of a completed simulation
    
    Args:
        simulation_id (str): ID of simulation
        
    Returns:
        dict: Simulation results
    """
    if simulation_id not in simulations:
        return {'error': f'Simulation {simulation_id} not found'}
    
    if simulations[simulation_id]['status'] != 'completed':
        return {'error': f'Simulation {simulation_id} is not completed yet'}
    
    return {
        'simulation_id': simulation_id,
        'results': simulations[simulation_id].get('results', {}),
        'logs': simulations[simulation_id].get('logs', [])
    }

def _run_simulation(simulation_id, carla_server, carla_port, config):
    """
    Internal function to run a simulation
    
    Args:
        simulation_id (str): ID of the simulation
        carla_server (str): CARLA server address
        carla_port (int): CARLA server port
        config (dict): Simulation configuration
    """
    try:
        # Update simulation status
        simulations[simulation_id]['status'] = 'running'
        simulations[simulation_id]['logs'].append(f"Connecting to CARLA server at {carla_server}:{carla_port}")
        
        # Simulate a running simulation
        simulations[simulation_id]['logs'].append("Initializing simulation environment")
        time.sleep(2)  # Simulate initialization time
        
        # Log simulation parameters
        simulations[simulation_id]['logs'].append(f"Simulation parameters: {json.dumps(config)}")
        
        # Simulate different simulation stages
        stages = [
            "Loading map and assets",
            "Spawning autonomous truck",
            "Setting up sensors",
            "Configuring traffic",
            "Executing route plan",
            "Processing sensor data",
            "Running autonomous driving logic",
            "Collecting performance metrics"
        ]
        
        for stage in stages:
            if simulations[simulation_id]['status'] == 'stopping':
                simulations[simulation_id]['logs'].append("Simulation stopped by user")
                break
                
            simulations[simulation_id]['logs'].append(stage)
            time.sleep(1)  # Simulate stage duration
        
        # Only generate results if simulation wasn't stopped
        if simulations[simulation_id]['status'] == 'running':
            # Generate simulation results
            simulations[simulation_id]['results'] = {
                'distance_traveled': 8.7,  # km
                'average_speed': 42.3,  # km/h
                'fuel_consumption': 3.2,  # L/100km
                'incidents': 0,
                'emergency_braking': 1,
                'lane_departures': 2,
                'completion_time': 832,  # seconds
                'simulation_time_factor': 1.0
            }
            
            simulations[simulation_id]['logs'].append("Simulation completed successfully")
            simulations[simulation_id]['status'] = 'completed'
            simulations[simulation_id]['end_time'] = int(time.time())
        
    except Exception as e:
        logging.error(f"Error in simulation {simulation_id}: {str(e)}")
        simulations[simulation_id]['status'] = 'error'
        simulations[simulation_id]['error'] = str(e)
        simulations[simulation_id]['logs'].append(f"ERROR: {str(e)}")
