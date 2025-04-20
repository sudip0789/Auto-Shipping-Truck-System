import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal, Button } from 'react-bootstrap';

const Routes = () => {
  // State for routes data
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for trucks (needed for dropdown selection)
  const [trucks, setTrucks] = useState([]);
  
  // State for route form
  const [routeForm, setRouteForm] = useState({
    route_name: '',
    truck_id: '',
    start_location: '',
    end_location: '',
    status: 'scheduled',
    estimated_start_time: '',
    estimated_end_time: '',
    waypoints: []
  });
  
  // State for waypoint input
  const [waypoint, setWaypoint] = useState('');
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState(null);
  
  // Route statuses for dropdown
  const routeStatuses = ['scheduled', 'in_progress', 'completed', 'cancelled'];
  
  // Fetch routes and trucks on component mount
  useEffect(() => {
    fetchRoutes();
    fetchTrucks();
  }, []);
  
  // Function to fetch all routes
  const fetchRoutes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/routes');
      setRoutes(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching routes:', err);
      setError('Failed to load routes. Please try refreshing the page.');
      setLoading(false);
    }
  };
  
  // Function to fetch all trucks (for dropdown selection)
  const fetchTrucks = async () => {
    try {
      const response = await api.get('/trucks');
      setTrucks(response.data);
    } catch (err) {
      console.error('Error fetching trucks for dropdown:', err);
    }
  };
  
  // Handle input changes for route form
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRouteForm({
      ...routeForm,
      [name]: value
    });
  };
  
  // Handle waypoint input
  const handleWaypointChange = (e) => {
    setWaypoint(e.target.value);
  };
  
  // Add waypoint to route form
  const addWaypoint = () => {
    if (waypoint.trim() !== '') {
      setRouteForm({
        ...routeForm,
        waypoints: [...routeForm.waypoints, waypoint.trim()]
      });
      setWaypoint('');
    }
  };
  
  // Remove waypoint from route form
  const removeWaypoint = (index) => {
    const newWaypoints = [...routeForm.waypoints];
    newWaypoints.splice(index, 1);
    setRouteForm({
      ...routeForm,
      waypoints: newWaypoints
    });
  };
  
  // Reset form data
  const resetFormData = () => {
    setRouteForm({
      route_name: '',
      truck_id: '',
      start_location: '',
      end_location: '',
      status: 'scheduled',
      estimated_start_time: '',
      estimated_end_time: '',
      waypoints: []
    });
    setWaypoint('');
  };
  
  // Open add route modal
  const openAddModal = () => {
    resetFormData();
    setShowAddModal(true);
  };
  
  // Open edit route modal
  const openEditModal = (route) => {
    setSelectedRoute(route);
    setRouteForm({
      route_name: route.route_name || '',
      truck_id: route.truck_id || '',
      start_location: route.start_location || '',
      end_location: route.end_location || '',
      status: route.status || 'scheduled',
      estimated_start_time: route.estimated_start_time ? formatDateTimeForInput(route.estimated_start_time) : '',
      estimated_end_time: route.estimated_end_time ? formatDateTimeForInput(route.estimated_end_time) : '',
      waypoints: route.waypoints || []
    });
    setShowEditModal(true);
  };
  
  // Format timestamp for input fields
  const formatDateTimeForInput = (timestamp) => {
    if (!timestamp) return '';
    // Convert to local time
    const date = new Date(timestamp * 1000);
    return new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
      .toISOString()
      .slice(0, 16);
  };
  
  // Open delete route modal
  const openDeleteModal = (route) => {
    setSelectedRoute(route);
    setShowDeleteModal(true);
  };
  
  // Add a new route
  const addRoute = async () => {
    try {
      // Convert datetime fields to timestamps
      const formattedData = {
        ...routeForm,
        estimated_start_time: routeForm.estimated_start_time ? Math.floor(new Date(routeForm.estimated_start_time).getTime() / 1000) : null,
        estimated_end_time: routeForm.estimated_end_time ? Math.floor(new Date(routeForm.estimated_end_time).getTime() / 1000) : null
      };
      
      const response = await api.post('/routes', formattedData);
      // Add the new route to the state
      setRoutes([...routes, response.data]);
      setShowAddModal(false);
      resetFormData();
    } catch (err) {
      console.error('Error adding route:', err);
      alert(`Failed to add route: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Update an existing route
  const updateRoute = async () => {
    if (!selectedRoute) return;
    
    try {
      // Convert datetime fields to timestamps
      const formattedData = {
        ...routeForm,
        estimated_start_time: routeForm.estimated_start_time ? Math.floor(new Date(routeForm.estimated_start_time).getTime() / 1000) : null,
        estimated_end_time: routeForm.estimated_end_time ? Math.floor(new Date(routeForm.estimated_end_time).getTime() / 1000) : null
      };
      
      await api.put(`/routes/${selectedRoute.route_id}`, formattedData);
      // Update the routes array with the edited route
      setRoutes(routes.map(route => 
        route.route_id === selectedRoute.route_id ? 
          { ...route, ...formattedData } : route
      ));
      setShowEditModal(false);
      setSelectedRoute(null);
    } catch (err) {
      console.error('Error updating route:', err);
      alert(`Failed to update route: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Delete a route
  const deleteRoute = async () => {
    if (!selectedRoute) return;
    
    try {
      await api.delete(`/routes/${selectedRoute.route_id}`);
      // Remove the deleted route from the state
      setRoutes(routes.filter(route => route.route_id !== selectedRoute.route_id));
      setShowDeleteModal(false);
      setSelectedRoute(null);
    } catch (err) {
      console.error('Error deleting route:', err);
      alert(`Failed to delete route: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Get status badge class based on status
  const getStatusBadgeClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'scheduled':
        return 'bg-info';
      case 'in_progress':
        return 'bg-primary';
      case 'completed':
        return 'bg-success';
      case 'cancelled':
        return 'bg-danger';
      default:
        return 'bg-secondary';
    }
  };
  
  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };
  
  // Loading state
  if (loading) {
    return (
      <div className="d-flex justify-content-center mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="alert alert-danger">{error}</div>
    );
  }
  
  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Route Management</h1>
        <button className="btn btn-primary" onClick={openAddModal}>
          <i className="fas fa-plus me-2"></i> Add New Route
        </button>
      </div>
      
      {/* Routes Table */}
      {routes.length === 0 ? (
        <div className="alert alert-info">
          No routes found. Click "Add New Route" to create one.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Truck</th>
                <th>From</th>
                <th>To</th>
                <th>Status</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {routes.map(route => (
                <tr key={route.route_id}>
                  <td>{route.route_id}</td>
                  <td>{route.route_name}</td>
                  <td>{route.truck_id}</td>
                  <td>{route.start_location}</td>
                  <td>{route.end_location}</td>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(route.status)}`}>
                      {route.status}
                    </span>
                  </td>
                  <td>{formatTimestamp(route.estimated_start_time)}</td>
                  <td>{formatTimestamp(route.estimated_end_time)}</td>
                  <td>
                    <button 
                      className="btn btn-sm btn-info me-1" 
                      onClick={() => alert(`Route Details: ${JSON.stringify(route, null, 2)}`)}
                      title="View Details"
                    >
                      <i className="fas fa-eye"></i>
                    </button>
                    <button 
                      className="btn btn-sm btn-warning me-1" 
                      onClick={() => openEditModal(route)}
                      title="Edit Route"
                    >
                      <i className="fas fa-edit"></i>
                    </button>
                    <button 
                      className="btn btn-sm btn-danger" 
                      onClick={() => openDeleteModal(route)}
                      title="Delete Route"
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Add Route Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)} size="lg">
        <Modal.Header closeButton className="bg-primary text-white">
          <Modal.Title>Add New Route</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form id="addRouteForm">
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="route_name" className="form-label">Route Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="route_name"
                  name="route_name"
                  value={routeForm.route_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="truck_id" className="form-label">Truck</label>
                <select
                  className="form-select"
                  id="truck_id"
                  name="truck_id"
                  value={routeForm.truck_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select Truck</option>
                  {trucks.map(truck => (
                    <option key={truck.truck_id} value={truck.truck_id}>
                      {truck.truck_name} ({truck.truck_id})
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="start_location" className="form-label">Start Location</label>
                <input
                  type="text"
                  className="form-control"
                  id="start_location"
                  name="start_location"
                  value={routeForm.start_location}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="end_location" className="form-label">End Location</label>
                <input
                  type="text"
                  className="form-control"
                  id="end_location"
                  name="end_location"
                  value={routeForm.end_location}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="estimated_start_time" className="form-label">Estimated Start Time</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  id="estimated_start_time"
                  name="estimated_start_time"
                  value={routeForm.estimated_start_time}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="estimated_end_time" className="form-label">Estimated End Time</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  id="estimated_end_time"
                  name="estimated_end_time"
                  value={routeForm.estimated_end_time}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            
            <div className="mb-3">
              <label htmlFor="status" className="form-label">Status</label>
              <select
                className="form-select"
                id="status"
                name="status"
                value={routeForm.status}
                onChange={handleInputChange}
                required
              >
                {routeStatuses.map(status => (
                  <option key={status} value={status}>{status.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            
            {/* Waypoints */}
            <div className="mb-3">
              <label className="form-label">Waypoints</label>
              <div className="input-group mb-3">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Add a waypoint location"
                  value={waypoint}
                  onChange={handleWaypointChange}
                />
                <button
                  type="button"
                  className="btn btn-outline-primary"
                  onClick={addWaypoint}
                >
                  Add
                </button>
              </div>
              
              {routeForm.waypoints.length > 0 && (
                <ul className="list-group mt-2">
                  {routeForm.waypoints.map((wp, index) => (
                    <li
                      key={index}
                      className="list-group-item d-flex justify-content-between align-items-center"
                    >
                      {wp}
                      <button
                        type="button"
                        className="btn btn-sm btn-danger"
                        onClick={() => removeWaypoint(index)}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={addRoute}>
            Add Route
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Edit Route Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} size="lg">
        <Modal.Header closeButton className="bg-warning text-dark">
          <Modal.Title>Edit Route</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form id="editRouteForm">
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="edit_route_name" className="form-label">Route Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="edit_route_name"
                  name="route_name"
                  value={routeForm.route_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="edit_truck_id" className="form-label">Truck</label>
                <select
                  className="form-select"
                  id="edit_truck_id"
                  name="truck_id"
                  value={routeForm.truck_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select Truck</option>
                  {trucks.map(truck => (
                    <option key={truck.truck_id} value={truck.truck_id}>
                      {truck.truck_name} ({truck.truck_id})
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="edit_start_location" className="form-label">Start Location</label>
                <input
                  type="text"
                  className="form-control"
                  id="edit_start_location"
                  name="start_location"
                  value={routeForm.start_location}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="edit_end_location" className="form-label">End Location</label>
                <input
                  type="text"
                  className="form-control"
                  id="edit_end_location"
                  name="end_location"
                  value={routeForm.end_location}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="edit_estimated_start_time" className="form-label">Estimated Start Time</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  id="edit_estimated_start_time"
                  name="estimated_start_time"
                  value={routeForm.estimated_start_time}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="edit_estimated_end_time" className="form-label">Estimated End Time</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  id="edit_estimated_end_time"
                  name="estimated_end_time"
                  value={routeForm.estimated_end_time}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            
            <div className="mb-3">
              <label htmlFor="edit_status" className="form-label">Status</label>
              <select
                className="form-select"
                id="edit_status"
                name="status"
                value={routeForm.status}
                onChange={handleInputChange}
                required
              >
                {routeStatuses.map(status => (
                  <option key={status} value={status}>{status.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            
            {/* Waypoints */}
            <div className="mb-3">
              <label className="form-label">Waypoints</label>
              <div className="input-group mb-3">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Add a waypoint location"
                  value={waypoint}
                  onChange={handleWaypointChange}
                />
                <button
                  type="button"
                  className="btn btn-outline-primary"
                  onClick={addWaypoint}
                >
                  Add
                </button>
              </div>
              
              {routeForm.waypoints.length > 0 && (
                <ul className="list-group mt-2">
                  {routeForm.waypoints.map((wp, index) => (
                    <li
                      key={index}
                      className="list-group-item d-flex justify-content-between align-items-center"
                    >
                      {wp}
                      <button
                        type="button"
                        className="btn btn-sm btn-danger"
                        onClick={() => removeWaypoint(index)}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={updateRoute}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Delete Route Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton className="bg-danger text-white">
          <Modal.Title>Delete Route</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete the route <strong>{selectedRoute?.route_name}</strong>?</p>
          <p className="text-danger fw-bold">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={deleteRoute}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default Routes;
