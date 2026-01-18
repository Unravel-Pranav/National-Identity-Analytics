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
  
  // Meta
  getAvailableDates: () => api.get('/api/available-dates'),
  
  // Summary & Overview
  getSummary: (params) => api.get('/api/summary', { params }),
  
  // States
  getAllStates: (params) => api.get('/api/states', { params }),
  getStateDetail: (stateName, params) => api.get(`/api/states/${encodeURIComponent(stateName)}`, { params }),
  compareStates: (state1, state2, params) => 
    api.get(`/api/states/compare/${encodeURIComponent(state1)}/${encodeURIComponent(state2)}`, { params }),
  
  // Clustering
  getClustering: (params) => api.get('/api/clustering', { params }),
  
  // Anomalies
  getAnomalies: (limit = 50, params) => api.get(`/api/anomalies`, { params: { limit, ...params } }),
  
  // Forecasting
  getForecast: (metric, days = 30, params) => api.get(`/api/forecast/${metric}`, { params: { days, ...params } }),
  
  // Trends
  getMonthlyTrends: (params) => api.get('/api/trends/monthly', { params }),
  getDailyTrends: (limit = 90, params) => api.get(`/api/trends/daily`, { params: { limit, ...params } }),
  
  // Pincodes
  getHighRiskPincodes: (limit = 100, params) => api.get(`/api/pincodes/high-risk`, { params: { limit, ...params } }),
  searchPincode: (pincode, params) => api.get(`/api/search/pincode/${pincode}`, { params }),
  
  // Cache
  clearCache: () => api.post('/api/cache/clear'),
};

export default apiService;

