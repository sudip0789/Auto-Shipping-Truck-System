"""
Routes for the Autonomous Shipping Truck Management Platform
"""
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session, flash
from app.controllers import truck_controller, alert_controller, route_controller, simulation_controller, user_controller, vision_controller
import time
import hashlib

# Blueprint for main web routes
main_blueprint = Blueprint('main', __name__)

# Blueprint for API routes
api_blueprint = Blueprint('api', __name__)

# Vision API routes


@api_blueprint.route('/vision/process', methods=['POST'])
def process_vision_image():
    """Process an image for vision detection"""
    data = request.json
    if not data or 'image_data' not in data:
        return jsonify({'status': 'error', 'message': 'No image data provided'}), 400

    truck_id = data.get('truck_id')
    result = vision_controller.process_image(data['image_data'], truck_id)

    return jsonify(result)


@api_blueprint.route('/vision/detections', methods=['GET'])
def get_vision_detections():
    """Get recent vision detections"""
    limit = request.args.get('limit', 10, type=int)
    detections = vision_controller.get_recent_detections(limit)
    return jsonify(detections)


@api_blueprint.route('/vision/stats', methods=['GET'])
def get_vision_stats():
    """Get vision detection statistics"""
    # This would normally query the database for actual stats
    # For now, we'll return simulated data
    stats = {
        'total_detections': 127,
        'emergency_detections': 18,
        'detection_counts': {
            'vehicle': 45,
            'pedestrian': 23,
            'traffic_light': 12,
            'traffic_sign': 8,
            'ambulance': 3,
            'police_car': 5,
            'fire_truck': 2,
            'maintenance_vehicle': 7,
            'accident': 4,
            'fire': 1,
            'smoke': 3,
            'construction': 9,
            'road_closure': 5
        }
    }
    return jsonify(stats)

# Authentication routes


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate against DynamoDB users table
        user = user_controller.authenticate_user(username, password)
        if user:
            session['logged_in'] = True
            session['username'] = username
            session['user_role'] = user.get('role', 'user')
            return redirect(url_for('main.index'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error, title='Login')


@main_blueprint.route('/logout')
def logout():
    """Handle user logout"""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out successfully.')
    return redirect(url_for('main.login'))

# Main web routes for the dashboard


@main_blueprint.route('/')
@main_blueprint.route('/index')
def index():
    """Render the main dashboard page"""
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    return render_template('index.html', title='Autonomous Truck Dashboard')


@main_blueprint.route('/trucks')
def trucks():
    """Render the truck management page"""
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    return render_template('trucks.html', title='Truck Management')


@main_blueprint.route('/monitoring')
def monitoring():
    """Render the truck monitoring page"""
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    return render_template('monitoring.html', title='Truck Monitoring')


@main_blueprint.route('/alerts')
def alerts():
    """Render the alerts management page"""
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    return render_template('alerts.html', title='Alert Management')


@main_blueprint.route('/routes')
def routes():
    """Render the route scheduling page"""
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    return render_template('routes.html', title='Route Scheduling')


@main_blueprint.route('/simulation')
def simulation():
    """Render the simulation page"""
    return render_template('simulation.html', title='CARLA Simulation')


@main_blueprint.route('/vision')
def vision():
    """Render the computer vision page"""
    return render_template('vision.html', title='Computer Vision')

# API routes for the backend
# API Auth routes


@api_blueprint.route('/auth/login', methods=['POST'])
def api_auth_login():
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
    user = user_controller.authenticate_user(username, password)
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    token = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()
    return jsonify({'token': token, 'user': user}), 200


@api_blueprint.route('/auth/logout', methods=['POST'])
def api_auth_logout():
    return jsonify({'message': 'Logged out'}), 200

# Truck Management API


@api_blueprint.route('/trucks', methods=['GET'])
def get_trucks():
    """Get all trucks"""
    return jsonify(truck_controller.get_all_trucks())


@api_blueprint.route('/trucks/<truck_id>', methods=['GET'])
def get_truck(truck_id):
    """Get a specific truck by ID"""
    return jsonify(truck_controller.get_truck(truck_id))


@api_blueprint.route('/trucks', methods=['POST'])
def add_truck():
    """Add a new truck"""
    return jsonify(truck_controller.add_truck(request.json))


@api_blueprint.route('/trucks/<truck_id>', methods=['PUT'])
def update_truck(truck_id):
    """Update an existing truck"""
    return jsonify(truck_controller.update_truck(truck_id, request.json))


@api_blueprint.route('/trucks/<truck_id>', methods=['DELETE'])
def delete_truck(truck_id):
    """Delete a truck"""
    return jsonify(truck_controller.delete_truck(truck_id))

# Alert Management API


@api_blueprint.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    return jsonify(alert_controller.get_all_alerts())


@api_blueprint.route('/alerts/<alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get a specific alert by ID"""
    return jsonify(alert_controller.get_alert(alert_id))


@api_blueprint.route('/alerts', methods=['POST'])
def add_alert():
    """Add a new alert"""
    return jsonify(alert_controller.add_alert(request.json))


@api_blueprint.route('/alerts/<alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """Update an existing alert"""
    return jsonify(alert_controller.update_alert(alert_id, request.json))


@api_blueprint.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    return jsonify(alert_controller.resolve_alert(alert_id, request.json))


@api_blueprint.route('/alerts/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    return jsonify(alert_controller.delete_alert(alert_id))

# Route Scheduling API


@api_blueprint.route('/routes', methods=['GET'])
def get_routes():
    """Get all routes"""
    return jsonify(route_controller.get_all_routes())


@api_blueprint.route('/routes/<route_id>', methods=['GET'])
def get_route(route_id):
    """Get a specific route by ID"""
    return jsonify(route_controller.get_route(route_id))


@api_blueprint.route('/routes', methods=['POST'])
def add_route():
    """Add a new route"""
    return jsonify(route_controller.add_route(request.json))


@api_blueprint.route('/routes/<route_id>', methods=['PUT'])
def update_route(route_id):
    """Update an existing route"""
    return jsonify(route_controller.update_route(route_id, request.json))


@api_blueprint.route('/routes/<route_id>', methods=['DELETE'])
def delete_route(route_id):
    """Delete a route"""
    return jsonify(route_controller.delete_route(route_id))

# Simulation API


@api_blueprint.route('/simulation/start', methods=['POST'])
def start_simulation():
    """Start a CARLA simulation"""
    return jsonify(simulation_controller.start_simulation(request.json))


@api_blueprint.route('/simulation/status', methods=['GET'])
def simulation_status():
    """Get simulation status"""
    return jsonify(simulation_controller.get_simulation_status())


@api_blueprint.route('/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop a CARLA simulation"""
    return jsonify(simulation_controller.stop_simulation())

# Truck Tracking/Monitoring API
# @api_blueprint.route('/trucks/<truck_id>/location', methods=['GET'])
# def get_truck_location(truck_id):
#     """Get real-time location of a truck"""
#     return jsonify(truck_controller.get_truck_location(truck_id))

# @api_blueprint.route('/trucks/<truck_id>/status', methods=['GET'])
# def get_truck_status(truck_id):
#     """Get real-time status of a truck"""
#     return jsonify(truck_controller.get_truck_status(truck_id))


@api_blueprint.route('/trucks/<truck_id>/telemetry', methods=['GET'])
def get_truck_telemetry(truck_id):
    """Get telemetry data for a specific truck"""
    # Get both location and status data
    location_data = truck_controller.get_truck_location(truck_id)
    status_data = truck_controller.get_truck_status(truck_id)

    # Check if either function returned an error
    if 'error' in location_data:
        return jsonify(location_data), 404

    # Format the data to match what the frontend expects
    # Convert all values to native Python types for proper JSON serialization
    telemetry = {
        'location': {
            'lat': float(location_data.get('latitude', 0)),
            'lng': float(location_data.get('longitude', 0))
        },
        'speed': float(location_data.get('speed', 0)),
        'battery': float(status_data.get('battery_level', 0)),
        'fuel': float(status_data.get('fuel_level', 0)),
        'temperature': float(status_data.get('engine_temperature', 0)),
        'timestamp': location_data.get('timestamp', int(time.time()))
    }

    return jsonify(telemetry)

# Dashboard Stats APIs


@api_blueprint.route('/trucks/stats', methods=['GET'])
def get_truck_stats():
    """Get truck statistics for dashboard"""
    trucks = truck_controller.get_all_trucks()
    active_count = sum(
        1 for truck in trucks if truck.get('status') == 'active')
    inactive_count = len(trucks) - active_count

    return jsonify({
        'total': len(trucks),
        'active': active_count,
        'inactive': inactive_count
    })


@api_blueprint.route('/alerts/stats', methods=['GET'])
def get_alert_stats():
    """Get alert statistics for dashboard"""
    alerts = alert_controller.get_all_alerts()
    critical_count = sum(
        1 for alert in alerts if alert.get('severity') == 'critical')
    warning_count = sum(
        1 for alert in alerts if alert.get('severity') == 'warning')
    info_count = sum(1 for alert in alerts if alert.get('severity') == 'info')
    active_count = sum(
        1 for alert in alerts if alert.get('status') == 'active')
    resolved_count = sum(
        1 for alert in alerts if alert.get('status') == 'resolved')

    return jsonify({
        'total': len(alerts),
        'critical': critical_count,
        'warning': warning_count,
        'info': info_count,
        'active': active_count,
        'resolved': resolved_count
    })


@api_blueprint.route('/routes/stats', methods=['GET'])
def get_route_stats():
    """Get route statistics for dashboard"""
    routes = route_controller.get_all_routes()
    scheduled_count = sum(
        1 for route in routes if route.get('status') == 'scheduled')
    inprogress_count = sum(
        1 for route in routes if route.get('status') == 'in_progress')
    completed_count = sum(
        1 for route in routes if route.get('status') == 'completed')

    return jsonify({
        'total': len(routes),
        'scheduled': scheduled_count,
        'inprogress': inprogress_count,
        'completed': completed_count
    })


@api_blueprint.route('/alerts/recent', methods=['GET'])
def get_recent_alerts():
    """Get recent alerts for dashboard"""
    alerts = alert_controller.get_all_alerts()
    # Sort by timestamp descending and take the first 5
    recent_alerts = sorted(alerts, key=lambda x: x.get(
        'created_at', 0), reverse=True)[:5]
    return jsonify(recent_alerts)
