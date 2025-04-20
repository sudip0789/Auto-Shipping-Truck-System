import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { Modal, Button } from 'react-bootstrap';

const Vision = () => {
  // State for vision data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [systemActive, setSystemActive] = useState(true);
  const [cameraFeed, setCameraFeed] = useState(null);
  const [detectionStats, setDetectionStats] = useState({
    vehicles: 0,
    pedestrians: 0,
    traffic_signals: 0
  });
  const [incidents, setIncidents] = useState([]);
  
  // Refs
  const videoRef = useRef(null);
  
  // Fetch vision data on component mount
  useEffect(() => {
    fetchVisionData();
    
    // Set up periodic refresh
    const interval = setInterval(fetchVisionData, 10000); // Refresh every 10 seconds
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []);
  
  // Function to fetch vision data
  const fetchVisionData = async () => {
    try {
      setLoading(true);
      
      // Fetch vision statistics
      const statsResponse = await api.get('/vision/stats');
      
      // Update detection stats
      setDetectionStats({
        vehicles: statsResponse.data.detection_counts.vehicle || 0,
        pedestrians: statsResponse.data.detection_counts.pedestrian || 0,
        traffic_signals: (statsResponse.data.detection_counts.traffic_light || 0) + 
                        (statsResponse.data.detection_counts.traffic_sign || 0)
      });
      
      // Fetch recent detections for incidents
      const detectionsResponse = await api.get('/vision/detections');
      
      // Filter for emergency incidents
      const emergencyClasses = ['ambulance', 'police_car', 'fire_truck', 'maintenance_vehicle', 'accident', 'fire', 'smoke'];
      const emergencyDetections = detectionsResponse.data.filter(detection => 
        emergencyClasses.includes(detection.detection_type)
      );
      
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching vision data:', err);
      setError('Failed to load vision data. Please try refreshing the page.');
      setLoading(false);
    }
  };
}; 
export default Vision;
