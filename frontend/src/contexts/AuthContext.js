import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Check if user is logged in on page load
    const username = localStorage.getItem('username');
    if (username) {
      fetchCurrentUser(username);
    } else {
      setLoading(false);
    }
  }, []);
  
  const fetchCurrentUser = async (username) => {
    try {
      const response = await axios.post('/api/user', { username });
      setCurrentUser(response.data);
    } catch (error) {
      console.error('Error fetching current user:', error);
      localStorage.removeItem('username');
    } finally {
      setLoading(false);
    }
  };
  
  const login = async (username, password) => {
    try {
      // FormData format for legacy Flask login endpoint
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      console.log(' login response:', response);
      
      if (response.data && response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        setCurrentUser(response.data.user);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };
  
  const logout = async () => {
    try {
      await api.post('/auth/logout');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setCurrentUser(null);
      return true;
    } catch (error) {
      console.error('Logout error:', error);
      // Still remove items on error
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setCurrentUser(null);
      return false;
    }
  };
  
  const value = {
    currentUser,
    login,
    logout,
    loading
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
