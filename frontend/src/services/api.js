import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? '/api'  // Production - API on same domain
    : 'http://localhost:5000/api', // Development - API on different port
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // Handle 401 Unauthorized responses by redirecting to login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }

    // Handle DynamoDB specific errors
    if (error.response && error.response.data && error.response.data.message) {
      // Log the detailed error for debugging
      console.error('API Error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

export default api;
