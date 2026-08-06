import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH API ====================
export const authAPI = {
  login: (username: string, password: string) =>
    api.post<{ access_token: string; role: string }>('/api/auth/login', {
      username,
      password,
    }),
  logout: () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  },
};

// ==================== DASHBOARD API ====================
export const dashboardAPI = {
  getMetrics: () => api.get('/api/dashboard/metrics'),
  getRegional: () => api.get('/api/dashboard/regional'),  // NEW: Regional Dashboard
  getRevenue: () => api.get('/api/dashboard/revenue'),
  getCustomer: () => api.get('/api/dashboard/customer'),
  getChurn: () => api.get('/api/dashboard/churn'),
};

// ==================== CUSTOMERS API ====================
export const customersAPI = {
  getAll: () => api.get('/api/customers'),
  getOne: (id: number) => api.get(`/api/customers/${id}`),
};

// ==================== ANALYTICS API ====================
export const analyticsAPI = {
  getChurn: () => api.get('/api/analytics/churn'),
  getRevenue: () => api.get('/api/analytics/revenue'),
  getSegments: () => api.post('/api/analytics/customer-segments'),
  getCLV: () => api.get('/api/analytics/clv'),  // NEW: CLV
  getRevenueImpact: () => api.get('/api/analytics/revenue-impact'),  // NEW: Revenue Impact
};

// ==================== RETENTION API ====================
export const retentionAPI = {
  getRecommendations: () => api.post('/api/retention/recommendations'),
  getCampaigns: () => api.get('/api/retention/campaigns'),
};

// ==================== REPORTS API ====================
export const reportsAPI = {
  getMonthly: () => api.get('/api/reports/monthly'),
  getExcel: () => api.get('/api/reports/excel'),
  getAvailable: () => api.get('/api/reports/available'),
};