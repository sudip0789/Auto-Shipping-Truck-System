import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="container">
      <div className="row justify-content-center mt-5">
        <div className="col-md-8 text-center">
          <h1 className="display-1">404</h1>
          <h2 className="mb-4">Page Not Found</h2>
          <p className="lead mb-4">
            The page you are looking for doesn't exist or has been moved.
          </p>
          <Link to="/" className="btn btn-primary">
            <i className="fas fa-home me-2"></i> Go to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
