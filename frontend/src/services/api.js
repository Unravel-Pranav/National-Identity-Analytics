/**
 * API Service - Handles all backend communication
 * Optimized with caching and error handling
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[API Error]', error.response?.data || error.message);
    return Promise.reject(error.response?.data || { detail: error.message });
  }
);

// ============================================================================
// API Methods
// ============================================================================

export const apiService = {
  // Health & Status
  health: () => api.get('/health'),
  
  // Summary & Overview
  getSummary: () => api.get('/api/summary'),
  
  // States
  getAllStates: () => api.get('/api/states'),
  getStateDetail: (stateName) => api.get(`/api/states/${encodeURIComponent(stateName)}`),
  compareStates: (state1, state2) => 
    api.get(`/api/states/compare/${encodeURIComponent(state1)}/${encodeURIComponent(state2)}`),
  
  // Clustering
  getClustering: () => api.get('/api/clustering'),
  
  // Anomalies
  getAnomalies: (limit = 50) => api.get(`/api/anomalies?limit=${limit}`),
  
  // Forecasting
  getForecast: (metric, days = 30) => api.get(`/api/forecast/${metric}?days=${days}`),
  
  // Trends
  getMonthlyTrends: () => api.get('/api/trends/monthly'),
  getDailyTrends: (limit = 90) => api.get(`/api/trends/daily?limit=${limit}`),
  
  // Pincodes
  getHighRiskPincodes: (limit = 100) => api.get(`/api/pincodes/high-risk?limit=${limit}`),
  searchPincode: (pincode) => api.get(`/api/search/pincode/${pincode}`),
  
  // Cache
  clearCache: () => api.post('/api/cache/clear'),
};

export default apiService;

