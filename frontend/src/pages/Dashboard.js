import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [truckStats, setTruckStats] = useState(null);
  const [alertStats, setAlertStats] = useState(null);
  const [routeStats, setRouteStats] = useState(null);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch truck statistics
        const truckResponse = await api.get('/trucks/stats');
        setTruckStats(truckResponse.data);
        
        // Fetch alert statistics
        const alertResponse = await api.get('/alerts/stats');
        setAlertStats(alertResponse.data);
        
        // Fetch route statistics
        const routeResponse = await api.get('/routes/stats');
        setRouteStats(routeResponse.data);
        
        // Fetch recent alerts
        const recentAlertsResponse = await api.get('/alerts/recent');
        setRecentAlerts(recentAlertsResponse.data);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try refreshing the page.');
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  if (loading) {
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
      <h1 className="mb-4">Dashboard</h1>
      
      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <h5 className="card-title">Trucks</h5>
              <p className="display-4">{truckStats?.total || 0}</p>
              <p className="card-text">
                Active: {truckStats?.active || 0} | 
                Maintenance: {truckStats?.maintenance || 0}
              </p>
              <Link to="/trucks" className="btn btn-light">Manage Trucks</Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card bg-warning text-dark">
            <div className="card-body">
              <h5 className="card-title">Alerts</h5>
              <p className="display-4">{alertStats?.total || 0}</p>
              <p className="card-text">
                Active: {alertStats?.active || 0} | 
                Resolved: {alertStats?.resolved || 0}
              </p>
              <Link to="/alerts" className="btn btn-dark">View Alerts</Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h5 className="card-title">Routes</h5>
              <p className="display-4">{routeStats?.total || 0}</p>
              <p className="card-text">
                Active: {routeStats?.active || 0} | 
                Completed: {routeStats?.completed || 0}
              </p>
              <Link to="/routes" className="btn btn-light">Schedule Routes</Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Alerts Section */}
      <div className="row">
        <div className="col-md-12">
          <div className="card">
            <div className="card-header bg-light">
              <h5 className="card-title mb-0">Recent Alerts</h5>
            </div>
            <div className="card-body">
              {recentAlerts.length === 0 ? (
                <div className="text-center py-3">
                  <p className="text-muted">No recent alerts</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Alert ID</th>
                        <th>Type</th>
                        <th>Truck</th>
                        <th>Message</th>
                        <th>Time</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentAlerts.map(alert => (
                        <tr key={alert.alert_id}>
                          <td>{alert.alert_id}</td>
                          <td>{alert.alert_type}</td>
                          <td>{alert.truck_id}</td>
                          <td>{alert.message}</td>
                          <td>{new Date(alert.timestamp * 1000).toLocaleString()}</td>
                          <td>
                            <span className={`badge bg-${alert.status === 'active' ? 'danger' : 'success'}`}>
                              {alert.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="text-end mt-3">
                <Link to="/alerts" className="btn btn-outline-primary">View All Alerts</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
