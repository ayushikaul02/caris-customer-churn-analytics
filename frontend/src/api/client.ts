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

// Auth API
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

// Dashboard API
export const dashboardAPI = {
  getMetrics: () => api.get('/api/dashboard/metrics'),
};