import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Monitoring = () => {
  // State for trucks and their telemetry data
  const [trucks, setTrucks] = useState([]);
  const [truckTelemetry, setTruckTelemetry] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Refresh interval in milliseconds
  const refreshInterval = 30000; // 30 seconds

  useEffect(() => {
    // Initial data fetch
    fetchTrucksAndTelemetry();
    
    // Set up periodic refresh
    const interval = setInterval(fetchTrucksAndTelemetry, refreshInterval);
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []);
  
  // Fetch both trucks and their telemetry data
  const fetchTrucksAndTelemetry = async () => {
    try {
      setLoading(true);
      
      // First, fetch all trucks
      const trucksResponse = await api.get('/trucks');
      const trucksList = trucksResponse.data;
      setTrucks(trucksList);
      
      // Then, fetch telemetry data for each truck
      const telemetryData = {};
      for (const truck of trucksList) {
        try {
          const telemetryResponse = await api.get(`/trucks/${truck.truck_id}/telemetry`);
          telemetryData[truck.truck_id] = telemetryResponse.data;
        } catch (telemetryErr) {
          console.warn(`Failed to fetch telemetry for truck ${truck.truck_id}:`, telemetryErr);
          telemetryData[truck.truck_id] = null;
        }
      }
      
      setTruckTelemetry(telemetryData);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching monitoring data:', err);
      setError('Failed to load monitoring data. Please try refreshing the page.');
      setLoading(false);
    }
  };
  
  // Generate a status badge with appropriate color
  const StatusBadge = ({ status }) => {
    let badgeClass = '';
    
    switch (status?.toLowerCase()) {
      case 'active':
        badgeClass = 'bg-success';
        break;
      case 'maintenance':
        badgeClass = 'bg-warning text-dark';
        break;
      case 'idle':
        badgeClass = 'bg-secondary';
        break;
      case 'offline':
        badgeClass = 'bg-danger';
        break;
      case 'charging':
        badgeClass = 'bg-info';
        break;
      default:
        badgeClass = 'bg-light text-dark';
    }
    
    return <span className={`badge ${badgeClass}`}>{status || 'Unknown'}</span>;
  };
  
  if (loading && trucks.length === 0) {
    return (
      <div className="d-flex justify-content-center mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="alert alert-danger">{error}</div>
    );
  }

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Truck Monitoring</h1>
        <div>
          <button
            className="btn btn-primary"
            onClick={fetchTrucksAndTelemetry}
          >
            <i className="fas fa-sync-alt me-2"></i> Refresh Data
          </button>
        </div>
      </div>
      
      {/* Monitoring Cards */}
      <div className="row">
        {trucks.length === 0 ? (
          <div className="col-12">
            <div className="alert alert-info">
              No trucks found. Add trucks to start monitoring.
            </div>
          </div>
        ) : (
          trucks.map(truck => (
            <div className="col-md-6 col-lg-4 mb-4" key={truck.truck_id}>
              <div className="card h-100">
                <div className="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">{truck.truck_name}</h5>
                  <StatusBadge status={truck.status} />
                </div>
                <div className="card-body">
                  <div className="mb-3">
                    <strong>Truck ID:</strong> {truck.truck_id}<br />
                    <strong>Model:</strong> {truck.truck_model}<br />
                    <strong>Year:</strong> {truck.manufacture_year}<br />
                  </div>
                  
                  <h6 className="border-bottom pb-2 mb-3">Telemetry Data</h6>
                  
                  {!truckTelemetry[truck.truck_id] ? (
                    <div className="text-center text-muted py-3">
                      {loading ? (
                        <div className="spinner-border spinner-border-sm text-secondary" role="status">
                          <span className="visually-hidden">Loading...</span>
                        </div>
                      ) : (
                        <p className="mb-0">No telemetry data available</p>
                      )}
                    </div>
                  ) : (
                    <div>
                      <div className="mb-2">
                        <strong>Location:</strong> {' '}
                        {truckTelemetry[truck.truck_id].location ?
                          `(${truckTelemetry[truck.truck_id].location.lat.toFixed(6)}, 
                            ${truckTelemetry[truck.truck_id].location.lng.toFixed(6)})` :
                          'Unknown'
                        }
                      </div>
                      <div className="mb-2">
                        <strong>Speed:</strong> {' '}
                        {truckTelemetry[truck.truck_id].speed ?
                          `${truckTelemetry[truck.truck_id].speed} km/h` :
                          'N/A'
                        }
                      </div>
                      <div className="mb-2">
                        <strong>Battery:</strong> {' '}
                        {truckTelemetry[truck.truck_id].battery ?
                          `${truckTelemetry[truck.truck_id].battery}%` :
                          'N/A'
                        }
                      </div>
                      <div className="mb-2">
                        <strong>Fuel Level:</strong> {' '}
                        {truckTelemetry[truck.truck_id].fuel ?
                          `${truckTelemetry[truck.truck_id].fuel}%` :
                          'N/A'
                        }
                      </div>
                      <div className="mb-2">
                        <strong>Temperature:</strong> {' '}
                        {truckTelemetry[truck.truck_id].temperature ?
                          `${truckTelemetry[truck.truck_id].temperature}°C` :
                          'N/A'
                        }
                      </div>
                      <div>
                        <strong>Last Update:</strong> {' '}
                        {truckTelemetry[truck.truck_id].timestamp ?
                          new Date(truckTelemetry[truck.truck_id].timestamp * 1000).toLocaleString() :
                          'N/A'
                        }
                      </div>
                    </div>
                  )}
                </div>
                <div className="card-footer bg-light">
                  <button className="btn btn-sm btn-outline-primary me-2">
                    <i className="fas fa-map-marker-alt me-1"></i> Track
                  </button>
                  <button className="btn btn-sm btn-outline-info me-2">
                    <i className="fas fa-chart-line me-1"></i> Details
                  </button>
                  <button className="btn btn-sm btn-outline-warning">
                    <i className="fas fa-bell me-1"></i> Alerts
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Monitoring;
