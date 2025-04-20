import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const Navigation = () => {
  const { currentUser, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    if (await logout()) {
      navigate('/login');
    }
  };

  // Don't show navigation if not logged in
  if (!currentUser) return null;

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/">Autonomous Shipping Truck Management</Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link className="nav-link" to="/">Dashboard</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/trucks">Trucks</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/monitoring">Monitoring</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/alerts">Alerts</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/routes">Routes</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/vision">Vision</Link>
            </li>
          </ul>
          <div className="d-flex">
            <span className="navbar-text me-3">
              Welcome, {currentUser.username || currentUser.name || 'User'}
            </span>
            <button className="btn btn-outline-light" onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
