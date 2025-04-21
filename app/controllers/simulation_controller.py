"""
Simulation Controller for managing CARLA simulation operations
"""

import random
from app.controllers import truck_controller
import logging
from flask import current_app
import threading
import subprocess
import json
import time
import uuid

import os
import sys

# Add CARLA egg file to system path FIRST, before trying to import it
CARLA_PATH = "C:/Users/triti/Downloads/CARLA_0.9.15/WindowsNoEditor"
egg_path = f"{CARLA_PATH}/PythonAPI/carla/dist/carla-0.9.15-py3.7-win-amd64.egg"

# Check if the egg file exists
if not os.path.exists(egg_path):
    logging.error(f"CARLA egg file not found at: {egg_path}")
    # List available egg files to help troubleshoot
    dist_dir = f"{CARLA_PATH}/PythonAPI/carla/dist/"
    if os.path.exists(dist_dir):
        logging.info(f"Available files in {dist_dir}:")
        for file in os.listdir(dist_dir):
            logging.info(f"  - {file}")

    # Fallback to mock carla implementation
    class MockCarla:
        class Client:
            def __init__(self, host, port):
                self.host = host
                self.port = port

            def set_timeout(self, seconds):
                pass

            def get_world(self):
                return MockCarla.World()

        class World:
            def __init__(self):
                pass

            def get_map(self):
                return MockCarla.Map()

        class Map:
            def __init__(self):
                pass

            def get_spawn_points(self):
                return []

    carla = MockCarla()
    logging.warning("Using mock CARLA implementation")
else:
    sys.path.append(egg_path)
    try:
        import carla
        logging.info("CARLA module imported successfully")
    except ImportError as e:
        logging.error(f"Failed to import CARLA module: {e}")
        raise

# Store simulation state
simulations = {}

# def start_simulation(simulation_data):
#     """
#     Start a CARLA simulation

#     Args:
#         simulation_data (dict): Simulation configuration

#     Returns:
#         dict: Simulation status and ID
#     """
#     # Generate a unique simulation ID
#     simulation_id = f"sim-{uuid.uuid4()}"

#     # Get CARLA server settings from config
#     carla_server = current_app.config.get('CARLA_SERVER')
#     carla_port = current_app.config.get('CARLA_PORT')

#     # Initialize simulation state
#     simulations[simulation_id] = {
#         'id': simulation_id,
#         'status': 'starting',
#         'start_time': int(time.time()),
#         'config': simulation_data,
#         'logs': [],
#         'results': None
#     }

#     # In a real implementation, this would connect to the CARLA server
#     # and start a simulation based on the provided configuration
#     # For now, we'll simulate this process

#     # Start simulation in a separate thread
#     thread = threading.Thread(
#         target=_run_simulation,
#         args=(simulation_id, carla_server, carla_port, simulation_data)
#     )
#     thread.daemon = True
#     thread.start()

#     return {
#         'simulation_id': simulation_id,
#         'status': 'starting',
#         'message': 'Simulation is being initialized'
#     }


def start_simulation(simulation_data):
    """
    Start a CARLA simulation with actual vehicle spawning

    Args:
        simulation_data (dict): Contains truck_ids and simulation settings

    Returns:
        dict: Simulation status and ID
    """
    # Generate simulation ID as before
    simulation_id = f"sim-{uuid.uuid4()}"

    # Get CARLA server settings from config
    carla_server = current_app.config.get('CARLA_SERVER', '127.0.0.1')
    carla_port = current_app.config.get('CARLA_PORT', 2000)

    # Initialize simulation state
    simulations[simulation_id] = {
        'id': simulation_id,
        'status': 'starting',
        'start_time': int(time.time()),
        'config': simulation_data,
        'logs': [],
        'results': None,
        'vehicles': {},  # Will store CARLA vehicle objects
        'carla_client': None,
        'carla_world': None
    }

    # Start simulation in a thread to not block the API response
    thread = threading.Thread(
        target=_run_simulation_with_carla,
        args=(simulation_id, carla_server, carla_port, simulation_data)
    )
    thread.daemon = True
    thread.start()

    return {
        'simulation_id': simulation_id,
        'status': 'starting',
        'message': 'Simulation is being initialized with CARLA'
    }


def _run_simulation_with_carla(simulation_id, carla_server, carla_port, config):
    """
    Connect to CARLA and spawn vehicles

    Args:
        simulation_id (str): ID of the simulation
        carla_server (str): CARLA server address
        carla_port (int): CARLA server port
        config (dict): Simulation configuration
    """
    try:
        simulations[simulation_id]['logs'].append(
            f"Connecting to CARLA at {carla_server}:{carla_port}")

        # Connect to CARLA
        client = carla.Client(carla_server, carla_port)
        client.set_timeout(10.0)
        world = client.get_world()

        # Store client and world for later use
        simulations[simulation_id]['carla_client'] = client
        simulations[simulation_id]['carla_world'] = world

        # Load desired map if specified
        if 'map' in config and config['map']:
            simulations[simulation_id]['logs'].append(
                f"Loading map {config['map']}")
            client.load_world(config['map'])
            world = client.get_world()  # Refresh world after map change

        # Get truck IDs to spawn from config
        truck_ids = config.get('truck_ids', [])
        if not truck_ids:
            simulations[simulation_id]['logs'].append(
                "No trucks specified, using default truck")
            truck_ids = ['truck-default']

        # Get spawn points
        spawn_points = world.get_map().get_spawn_points()

        # Spawn vehicles for each truck ID
        for truck_id in truck_ids:
            # Get truck data from database
            truck_data = truck_controller.get_truck(truck_id)
            if not truck_data:
                simulations[simulation_id]['logs'].append(
                    f"Truck {truck_id} not found, skipping")
                continue

            # Use truck model to determine vehicle type
            # You can map your truck models to CARLA vehicle blueprints here
            truck_model = truck_data.get('truck_model', 'Tesla Semi')
            bp_name = "vehicle.tesla.model3"  # Default

            if "tesla" in truck_model.lower():
                bp_name = "vehicle.tesla.model3"
            elif "volvo" in truck_model.lower():
                bp_name = "vehicle.volvo.polestar"
            elif "freight" in truck_model.lower():
                bp_name = "vehicle.carlamotors.carlacola"

            # Get a random spawn point
            spawn_point = random.choice(
                spawn_points) if spawn_points else carla.Transform()

            # Get the blueprint
            blueprint_library = world.get_blueprint_library()
            vehicle_bp = blueprint_library.find(bp_name)

            # Set vehicle attributes
            vehicle_bp.set_attribute('role_name', f'truck_{truck_id}')

            # Spawn the vehicle
            carla_vehicle = world.spawn_actor(vehicle_bp, spawn_point)

            # Store vehicle in simulation
            simulations[simulation_id]['vehicles'][truck_id] = carla_vehicle
            simulations[simulation_id]['logs'].append(
                f"Spawned vehicle for truck {truck_id}")

            # Set vehicle to autopilot mode
            carla_vehicle.set_autopilot(True)

        simulations[simulation_id]['status'] = 'running'
        simulations[simulation_id]['logs'].append(
            "Simulation running with vehicles")

        # Update truck location in database periodically
        update_interval = 1.0  # seconds
        while simulations[simulation_id]['status'] == 'running':
            update_truck_positions(simulation_id)
            time.sleep(update_interval)

    except Exception as e:
        logging.error(f"Error in CARLA simulation {simulation_id}: {str(e)}")
        simulations[simulation_id]['status'] = 'error'
        simulations[simulation_id]['error'] = str(e)
        simulations[simulation_id]['logs'].append(f"ERROR: {str(e)}")


def update_truck_positions(simulation_id):
    """Update truck positions in database from CARLA vehicles"""
    if simulation_id not in simulations:
        return

    sim_data = simulations[simulation_id]
    if sim_data['status'] != 'running':
        return

    # Update each vehicle
    for truck_id, carla_vehicle in sim_data['vehicles'].items():
        # Get transform and velocity
        transform = carla_vehicle.get_transform()
        velocity = carla_vehicle.get_velocity()

        # Calculate speed in km/h
        speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5

        # Update truck data in database
        truck_controller.update_truck(truck_id, {
            # CARLA uses different coordinate system
            'latitude': float(transform.location.y),
            'longitude': float(transform.location.x),
            'speed': float(speed),
            'heading': float(transform.rotation.yaw),
            'timestamp': int(time.time())
        })


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
        simulations[simulation_id]['logs'].append(
            f"Connecting to CARLA server at {carla_server}:{carla_port}")

        # Simulate a running simulation
        simulations[simulation_id]['logs'].append(
            "Initializing simulation environment")
        time.sleep(2)  # Simulate initialization time

        # Log simulation parameters
        simulations[simulation_id]['logs'].append(
            f"Simulation parameters: {json.dumps(config)}")

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
                simulations[simulation_id]['logs'].append(
                    "Simulation stopped by user")
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

            simulations[simulation_id]['logs'].append(
                "Simulation completed successfully")
            simulations[simulation_id]['status'] = 'completed'
            simulations[simulation_id]['end_time'] = int(time.time())

    except Exception as e:
        logging.error(f"Error in simulation {simulation_id}: {str(e)}")
        simulations[simulation_id]['status'] = 'error'
        simulations[simulation_id]['error'] = str(e)
        simulations[simulation_id]['logs'].append(f"ERROR: {str(e)}")
