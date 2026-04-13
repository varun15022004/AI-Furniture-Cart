import React from 'react';
import ReactDOM from 'react-dom/client';
import axios from 'axios';
import './index.css';
import App from './App';

// Setup global Axios defaults for Vercel deployment where the backend is hosted under /_/backend
if (process.env.NODE_ENV === 'production') {
  axios.interceptors.request.use(config => {
    // Only prefix API routes that start with /api
    if (config.url && config.url.startsWith('/api')) {
      config.url = `/_/backend${config.url}`;
    }
    return config;
  });
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);