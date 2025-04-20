import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal, Button } from 'react-bootstrap';

const Trucks = () => {
  // State management
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Truck form data
  const [truckFormData, setTruckFormData] = useState({
    truck_name: '',
    truck_model: '',
    manufacture_year: new Date().getFullYear(),
    status: 'idle',
    notes: '',
    sensors: []
  });
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedTruck, setSelectedTruck] = useState(null);

  // Load trucks on component mount
  useEffect(() => {
    fetchTrucks();
  }, []);
  
  // Fetch trucks from API
  const fetchTrucks = async () => {
    try {
      setLoading(true);
      const response = await api.get('/trucks');
      setTrucks(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching trucks:', err);
      setError('Failed to load trucks. Please try refreshing the page.');
      setLoading(false);
    }
  };
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTruckFormData({
      ...truckFormData,
      [name]: name === 'manufacture_year' ? parseInt(value, 10) : value
    });
  };
  
  // Handle sensor checkbox changes
  const handleSensorChange = (sensorName) => {
    const sensors = [...truckFormData.sensors];
    if (sensors.includes(sensorName)) {
      setTruckFormData({
        ...truckFormData,
        sensors: sensors.filter(s => s !== sensorName)
      });
    } else {
      setTruckFormData({
        ...truckFormData,
        sensors: [...sensors, sensorName]
      });
    }
  };
  
  // Reset form data
  const resetFormData = () => {
    setTruckFormData({
      truck_name: '',
      truck_model: '',
      manufacture_year: new Date().getFullYear(),
      status: 'idle',
      notes: '',
      sensors: []
    });
  };
  
  // Open add truck modal
  const openAddModal = () => {
    resetFormData();
    setShowAddModal(true);
  };
  
  // Open edit truck modal
  const openEditModal = (truck) => {
    setSelectedTruck(truck);
    setTruckFormData({
      truck_name: truck.truck_name || '',
      truck_model: truck.truck_model || '',
      manufacture_year: truck.manufacture_year || new Date().getFullYear(),
      status: truck.status || 'idle',
      notes: truck.notes || '',
      sensors: truck.sensors || []
    });
    setShowEditModal(true);
  };
  
  // Open delete truck modal
  const openDeleteModal = (truck) => {
    setSelectedTruck(truck);
    setShowDeleteModal(true);
  };
  
  // Add a new truck
  const addTruck = async () => {
    try {
      const response = await api.post('/trucks', truckFormData);
      // Add the new truck to the state
      setTrucks([...trucks, response.data]);
      setShowAddModal(false);
      resetFormData();
    } catch (err) {
      console.error('Error adding truck:', err);
      alert(`Failed to add truck: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Update an existing truck
  const updateTruck = async () => {
    if (!selectedTruck) return;
    
    try {
      await api.put(`/trucks/${selectedTruck.truck_id}`, truckFormData);
      // Update the trucks array with the edited truck
      setTrucks(trucks.map(truck => 
        truck.truck_id === selectedTruck.truck_id ? 
          { ...truck, ...truckFormData } : truck
      ));
      setShowEditModal(false);
      setSelectedTruck(null);
    } catch (err) {
      console.error('Error updating truck:', err);
      alert(`Failed to update truck: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Delete a truck
  const deleteTruck = async () => {
    if (!selectedTruck) return;
    
    try {
      await api.delete(`/trucks/${selectedTruck.truck_id}`);
      // Remove the deleted truck from the state
      setTrucks(trucks.filter(truck => truck.truck_id !== selectedTruck.truck_id));
      setShowDeleteModal(false);
      setSelectedTruck(null);
    } catch (err) {
      console.error('Error deleting truck:', err);
      alert(`Failed to delete truck: ${err.response?.data?.error || err.message}`);
    }
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
        <h1>Truck Management</h1>
        <button className="btn btn-primary" onClick={openAddModal}>
          <i className="fas fa-plus me-2"></i> Add New Truck
        </button>
      </div>
      
      {/* Trucks Table */}
      {trucks.length === 0 ? (
        <div className="alert alert-info">
          No trucks found. Click "Add New Truck" to add one.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Model</th>
                <th>Year</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {trucks.map(truck => (
                <tr key={truck.truck_id}>
                  <td>{truck.truck_id}</td>
                  <td>{truck.truck_name}</td>
                  <td>{truck.truck_model}</td>
                  <td>{truck.manufacture_year}</td>
                  <td>
                    <span className={`badge bg-${
                      truck.status === 'active' ? 'success' : 
                      truck.status === 'maintenance' ? 'warning' : 
                      truck.status === 'idle' ? 'secondary' : 
                      'info'
                    }`}>
                      {truck.status}
                    </span>
                  </td>
                  <td>{truck.last_updated ? new Date(truck.last_updated * 1000).toLocaleString() : 'N/A'}</td>
                  <td>
                    <button 
                      className="btn btn-sm btn-info me-1" 
                      onClick={() => alert(`Truck Details: ${JSON.stringify(truck, null, 2)}`)}
                      title="View Details"
                    >
                      <i className="fas fa-eye"></i>
                    </button>
                    <button 
                      className="btn btn-sm btn-warning me-1" 
                      onClick={() => openEditModal(truck)}
                      title="Edit Truck"
                    >
                      <i className="fas fa-edit"></i>
                    </button>
                    <button 
                      className="btn btn-sm btn-danger" 
                      onClick={() => openDeleteModal(truck)}
                      title="Delete Truck"
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
      
      {/* Add Truck Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)} size="lg">
        <Modal.Header closeButton className="bg-primary text-white">
          <Modal.Title>Add New Truck</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form id="addTruckForm">
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="truck_name" className="form-label">Truck Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="truck_name"
                  name="truck_name"
                  value={truckFormData.truck_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="truck_model" className="form-label">Model</label>
                <input
                  type="text"
                  className="form-control"
                  id="truck_model"
                  name="truck_model"
                  value={truckFormData.truck_model}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="manufacture_year" className="form-label">Manufacture Year</label>
                <input
                  type="number"
                  className="form-control"
                  id="manufacture_year"
                  name="manufacture_year"
                  min="2000"
                  max="2030"
                  value={truckFormData.manufacture_year}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="status" className="form-label">Status</label>
                <select
                  className="form-select"
                  id="status"
                  name="status"
                  value={truckFormData.status}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select status</option>
                  <option value="active">Active</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="idle">Idle</option>
                  <option value="charging">Charging</option>
                  <option value="offline">Offline</option>
                </select>
              </div>
            </div>
            <div className="mb-3">
              <label htmlFor="notes" className="form-label">Notes (Optional)</label>
              <textarea
                className="form-control"
                id="notes"
                name="notes"
                rows="3"
                value={truckFormData.notes}
                onChange={handleInputChange}
              ></textarea>
            </div>
          </form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={addTruck}>
            Add Truck
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Edit Truck Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} size="lg">
        <Modal.Header closeButton className="bg-warning text-dark">
          <Modal.Title>Edit Truck</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form id="editTruckForm">
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="edit_truck_name" className="form-label">Truck Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="edit_truck_name"
                  name="truck_name"
                  value={truckFormData.truck_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="edit_truck_model" className="form-label">Model</label>
                <input
                  type="text"
                  className="form-control"
                  id="edit_truck_model"
                  name="truck_model"
                  value={truckFormData.truck_model}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>
            <div className="row mb-3">
              <div className="col-md-6">
                <label htmlFor="edit_manufacture_year" className="form-label">Manufacture Year</label>
                <input
                  type="number"
                  className="form-control"
                  id="edit_manufacture_year"
                  name="manufacture_year"
                  min="2000"
                  max="2030"
                  value={truckFormData.manufacture_year}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="edit_status" className="form-label">Status</label>
                <select
                  className="form-select"
                  id="edit_status"
                  name="status"
                  value={truckFormData.status}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select status</option>
                  <option value="active">Active</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="idle">Idle</option>
                  <option value="charging">Charging</option>
                  <option value="offline">Offline</option>
                </select>
              </div>
            </div>
            <div className="mb-3">
              <label htmlFor="edit_notes" className="form-label">Notes (Optional)</label>
              <textarea
                className="form-control"
                id="edit_notes"
                name="notes"
                rows="3"
                value={truckFormData.notes}
                onChange={handleInputChange}
              ></textarea>
            </div>
          </form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={updateTruck}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Delete Truck Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton className="bg-danger text-white">
          <Modal.Title>Delete Truck</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete {selectedTruck?.truck_name}?</p>
          <p className="text-danger fw-bold">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={deleteTruck}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default Trucks;
