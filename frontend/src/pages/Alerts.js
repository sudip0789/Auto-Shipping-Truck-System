import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal, Button } from 'react-bootstrap';

const Alerts = () => {
  // State for alerts data
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for alert form
  const [alertForm, setAlertForm] = useState({
    alert_type: '',
    truck_id: '',
    message: '',
    severity: 'medium',
    status: 'active'
  });
  
  // State for trucks (needed for dropdown selection)
  const [trucks, setTrucks] = useState([]);
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  
  // Alert types and severities for dropdowns
  const alertTypes = ['System', 'Maintenance', 'Security', 'Battery', 'Fuel', 'Collision', 'Route', 'Other'];
  const alertSeverities = ['low', 'medium', 'high', 'critical'];
  
  // Fetch alerts and trucks on component mount
  useEffect(() => {
    fetchAlerts();
    fetchTrucks();
  }, []);
  
  // Function to fetch all alerts
  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/alerts');
      setAlerts(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to load alerts. Please try refreshing the page.');
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
  
  // Handle input changes for alert form
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAlertForm({
      ...alertForm,
      [name]: value
    });
  };
  
  // Open add alert modal
  const openAddModal = () => {
    setAlertForm({
      alert_type: '',
      truck_id: '',
      message: '',
      severity: 'medium',
      status: 'active'
    });
    setShowAddModal(true);
  };
  
  // Open resolve alert modal
  const openResolveModal = (alert) => {
    setSelectedAlert(alert);
    setShowResolveModal(true);
  };
  
  // Create a new alert
  const addAlert = async () => {
    try {
      const response = await api.post('/alerts', alertForm);
      // Add the new alert to the state
      setAlerts([...alerts, response.data]);
      setShowAddModal(false);
      // Reset form
      setAlertForm({
        alert_type: '',
        truck_id: '',
        message: '',
        severity: 'medium',
        status: 'active'
      });
    } catch (err) {
      console.error('Error adding alert:', err);
      alert(`Failed to add alert: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Resolve an existing alert
  const resolveAlert = async () => {
    if (!selectedAlert) return;
    
    try {
      await api.post(`/alerts/${selectedAlert.alert_id}/resolve`, {
        resolution_notes: document.getElementById('resolution_notes').value
      });
      
      // Update the alerts array with the resolved alert
      setAlerts(alerts.map(alert => 
        alert.alert_id === selectedAlert.alert_id ? 
          { ...alert, status: 'resolved' } : alert
      ));
      
      setShowResolveModal(false);
      setSelectedAlert(null);
    } catch (err) {
      console.error('Error resolving alert:', err);
      alert(`Failed to resolve alert: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Delete an alert
  const deleteAlert = async (alertId) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return;
    
    try {
      await api.delete(`/alerts/${alertId}`);
      // Remove the deleted alert from the state
      setAlerts(alerts.filter(alert => alert.alert_id !== alertId));
    } catch (err) {
      console.error('Error deleting alert:', err);
      alert(`Failed to delete alert: ${err.response?.data?.error || err.message}`);
    }
  };
  
  // Get severity badge class based on severity level
  const getSeverityBadgeClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'low':
        return 'bg-info';
      case 'medium':
        return 'bg-warning text-dark';
      case 'high':
        return 'bg-danger';
      case 'critical':
        return 'bg-danger text-white fw-bold';
      default:
        return 'bg-secondary';
    }
  };
  
  // Get status badge class based on status
  const getStatusBadgeClass = (status) => {
    return status?.toLowerCase() === 'active' ? 'bg-danger' : 'bg-success';
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
        <h1>Alert Management</h1>
        <button className="btn btn-primary" onClick={openAddModal}>
          <i className="fas fa-plus me-2"></i> Add New Alert
        </button>
      </div>
      
      {/* Filter Options */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row">
            <div className="col-md-4 mb-2">
              <select className="form-select">
                <option value="">All Alert Types</option>
                {alertTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div className="col-md-4 mb-2">
              <select className="form-select">
                <option value="">All Severities</option>
                {alertSeverities.map(severity => (
                  <option key={severity} value={severity}>{severity.charAt(0).toUpperCase() + severity.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="col-md-4 mb-2">
              <select className="form-select">
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      {/* Alerts Table */}
      {alerts.length === 0 ? (
        <div className="alert alert-info">
          No alerts found. All systems operating normally.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Truck</th>
                <th>Message</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Timestamp</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(alert => (
                <tr key={alert.alert_id}>
                  <td>{alert.alert_id}</td>
                  <td>{alert.alert_type}</td>
                  <td>{alert.truck_id}</td>
                  <td>{alert.message}</td>
                  <td>
                    <span className={`badge ${getSeverityBadgeClass(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(alert.status)}`}>
                      {alert.status}
                    </span>
                  </td>
                  <td>{new Date(alert.timestamp * 1000).toLocaleString()}</td>
                  <td>
                    {alert.status === 'active' && (
                      <button 
                        className="btn btn-sm btn-success me-1" 
                        onClick={() => openResolveModal(alert)}
                        title="Resolve Alert"
                      >
                        <i className="fas fa-check"></i>
                      </button>
                    )}
                    <button 
                      className="btn btn-sm btn-danger" 
                      onClick={() => deleteAlert(alert.alert_id)}
                      title="Delete Alert"
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
      
      {/* Add Alert Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)}>
        <Modal.Header closeButton className="bg-primary text-white">
          <Modal.Title>Add New Alert</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form id="addAlertForm">
            <div className="mb-3">
              <label htmlFor="alert_type" className="form-label">Alert Type</label>
              <select
                className="form-select"
                id="alert_type"
                name="alert_type"
                value={alertForm.alert_type}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Alert Type</option>
                {alertTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="mb-3">
              <label htmlFor="truck_id" className="form-label">Truck</label>
              <select
                className="form-select"
                id="truck_id"
                name="truck_id"
                value={alertForm.truck_id}
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
            
            <div className="mb-3">
              <label htmlFor="message" className="form-label">Alert Message</label>
              <textarea
                className="form-control"
                id="message"
                name="message"
                rows="3"
                value={alertForm.message}
                onChange={handleInputChange}
                required
              ></textarea>
            </div>
            
            <div className="mb-3">
              <label htmlFor="severity" className="form-label">Severity</label>
              <select
                className="form-select"
                id="severity"
                name="severity"
                value={alertForm.severity}
                onChange={handleInputChange}
                required
              >
                {alertSeverities.map(severity => (
                  <option key={severity} value={severity}>
                    {severity.charAt(0).toUpperCase() + severity.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={addAlert}>
            Add Alert
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Resolve Alert Modal */}
      <Modal show={showResolveModal} onHide={() => setShowResolveModal(false)}>
        <Modal.Header closeButton className="bg-success text-white">
          <Modal.Title>Resolve Alert</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            <strong>Alert ID:</strong> {selectedAlert?.alert_id}<br />
            <strong>Type:</strong> {selectedAlert?.alert_type}<br />
            <strong>Message:</strong> {selectedAlert?.message}
          </p>
          
          <div className="mb-3">
            <label htmlFor="resolution_notes" className="form-label">Resolution Notes</label>
            <textarea
              className="form-control"
              id="resolution_notes"
              rows="3"
              placeholder="Enter resolution details..."
              required
            ></textarea>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowResolveModal(false)}>
            Cancel
          </Button>
          <Button variant="success" onClick={resolveAlert}>
            Resolve Alert
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default Alerts;
