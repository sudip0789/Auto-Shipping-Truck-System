import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { Spinner, Alert } from 'react-bootstrap';
console.log("Vision rendered");
const Vision = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detectionStats, setDetectionStats] = useState({
    vehicles: 0,
    pedestrians: 0,
    traffic_signals: 0,
  });
  const [detections, setDetections] = useState([]);
  const scrollRef = useRef(null);

  const intervalRef = useRef(null);

  useEffect(() => {
    console.log("Vision mounted");
    // fetchVisionData();

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    fetchVisionData();

    // intervalRef.current = setInterval(() => {
    //   console.log("Interval firing");
    //   fetchVisionData();
    // }, 10000);

    return () => {
      console.log("Cleaning up Vision");
      clearInterval(intervalRef.current);
    };
  }, []);


  const fetchVisionData = async () => {
    try {
      setLoading(true);

      // Fetch all detections
      const detectionsResponse = await api.get('/detections');
      const detectionItems = detectionsResponse.data || [];

      // Compute totals dynamically from all records
      let vehicles = 0;
      let pedestrians = 0;
      let traffic_signals = 0;

      detectionItems.forEach(det => {
        vehicles += Number(det.num_car) || 0;
        pedestrians += Number(det.num_person) || 0;
        // Add your own logic if you separate traffic_light vs. traffic_sign
        traffic_signals += Number(det.num_traffic_lights) || 0;
      });

      // Set state
      setDetectionStats({ vehicles, pedestrians, traffic_signals });
      setDetections(detectionItems);
      setError(null);
    } catch (err) {
      console.error('Error fetching vision data:', err);
      setError('Failed to load vision data. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  const scrollLeft = () => {
    scrollRef.current?.scrollBy({ left: -300, behavior: 'smooth' });
  };

  const scrollRight = () => {
    scrollRef.current?.scrollBy({ left: 300, behavior: 'smooth' });
  };

  const emergencyClasses = ['ambulance', 'police_car', 'fire_truck', 'maintenance_vehicle', 'accident', 'fire', 'smoke'];
  const emergencyDetections = detections.filter(d => emergencyClasses.includes(d.detection_type));

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Vision Monitoring</h1>

      {error && <Alert variant="danger">{error}</Alert>}
      {loading ? (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" variant="primary" />
        </div>
      ) : (
        <>
          {/* Detection Summary */}
          <div className="row mb-4">
            <div className="col-md-4">
              <div className="card text-center">
                <div className="card-body bg-light">
                  <h5 className="card-title">🚗 Vehicles</h5>
                  <p className="display-6">{detectionStats.vehicles}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card text-center">
                <div className="card-body bg-light">
                  <h5 className="card-title">🚶 Pedestrians</h5>
                  <p className="display-6">{detectionStats.pedestrians}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card text-center">
                <div className="card-body bg-light">
                  <h5 className="card-title">🚦 Traffic Signals</h5>
                  <p className="display-6">{detectionStats.traffic_signals}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Scrollable Camera Feed */}
          <div className="card mb-4">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Recent Detections</h5>
              <div>
                <button className="btn btn-outline-secondary btn-sm me-2" onClick={scrollLeft}>◀</button>
                <button className="btn btn-outline-secondary btn-sm" onClick={scrollRight}>▶</button>
              </div>
            </div>
            <div ref={scrollRef} className="d-flex overflow-auto p-3 gap-3">
              {detections.map((det, i) => (
                <div key={i} className="card" style={{ minWidth: '250px' }}>
                  <img
                    src={`http://localhost:5000/static/output/${det.image_name}`}
                    className="card-img-top"
                    alt={det.image_name}
                    style={{ height: '160px', objectFit: 'cover' }}
                  />
                  <div className="card-body">
                    <h6 className="card-title">{det.detection_type}</h6>
                    <p className="card-text small mb-1">Image: {det.image_name}</p>
                    <p className="text-muted small mb-0">{det.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Emergency Incidents */}
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0 text-danger">Critical Incidents</h5>
            </div>
            <div className="card-body">
              {emergencyDetections.length === 0 ? (
                <p className="text-muted">No critical incidents detected.</p>
              ) : (
                <div className="row">
                  {emergencyDetections.map((incident, i) => (
                    <div key={i} className="col-md-6 mb-3">
                      <div className="alert alert-danger">
                        <strong>{incident.detection_type.toUpperCase()}</strong> detected in <em>{incident.image_name}</em><br />
                        <small className="text-muted">{incident.timestamp}</small>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Vision;
