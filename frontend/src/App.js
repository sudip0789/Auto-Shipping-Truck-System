import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Navigation from './components/Navigation';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Trucks from './pages/Trucks';
import Monitoring from './pages/Monitoring';
import Alerts from './pages/Alerts';
import RouteManagement from './pages/Routes';
import Vision from './pages/Vision';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Navigation />
          <div className="container mt-4">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } />
              <Route path="/trucks" element={
                <PrivateRoute>
                  <Trucks />
                </PrivateRoute>
              } />
              <Route path="/monitoring" element={
                <PrivateRoute>
                  <Monitoring />
                </PrivateRoute>
              } />
              <Route path="/alerts" element={
                <PrivateRoute>
                  <Alerts />
                </PrivateRoute>
              } />
              <Route path="/routes" element={
                <PrivateRoute>
                  <RouteManagement />
                </PrivateRoute>
              } />
              <Route path="/vision" element={
                <PrivateRoute>
                  <Vision />
                </PrivateRoute>
              } />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
