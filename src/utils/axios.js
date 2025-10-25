// src/utils/axios.js

import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',
  // ❌ REMOVE THIS LINE - it's forcing JSON and blocking file uploads:
  // headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

// Add request interceptor for debugging
instance.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', config.method.toUpperCase(), config.url);
    console.log('📦 Content-Type:', config.headers['Content-Type']);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
instance.interceptors.response.use(
  (response) => {
    console.log('📥 API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default instance;