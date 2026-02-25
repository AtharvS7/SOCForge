import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: `${API_BASE}/api`,
    headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('socforge_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('socforge_token');
            localStorage.removeItem('socforge_user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth
export const authAPI = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    me: () => api.get('/auth/me'),
};

// Dashboard
export const dashboardAPI = {
    stats: () => api.get('/dashboard/stats'),
    severityDistribution: () => api.get('/dashboard/severity-distribution'),
    alertTrend: () => api.get('/dashboard/alert-trend'),
    mitreCoverage: () => api.get('/dashboard/mitre-coverage'),
    recentAlerts: (limit = 10) => api.get(`/dashboard/recent-alerts?limit=${limit}`),
    topAttackers: () => api.get('/dashboard/top-attackers'),
};

// Alerts
export const alertsAPI = {
    list: (params) => api.get('/alerts/', { params }),
    get: (id) => api.get(`/alerts/${id}`),
    update: (id, data) => api.patch(`/alerts/${id}`, data),
    stats: () => api.get('/alerts/stats'),
};

// Events
export const eventsAPI = {
    list: (params) => api.get('/events/', { params }),
    get: (id) => api.get(`/events/${id}`),
    ingest: (events) => api.post('/events/ingest', { events }),
};

// Detection Rules
export const detectionAPI = {
    listRules: (params) => api.get('/detection/rules', { params }),
    getRule: (id) => api.get(`/detection/rules/${id}`),
    createRule: (data) => api.post('/detection/rules', data),
    updateRule: (id, data) => api.patch(`/detection/rules/${id}`, data),
    deleteRule: (id) => api.delete(`/detection/rules/${id}`),
};

// Simulation
export const simulationAPI = {
    scenarios: () => api.get('/simulation/scenarios'),
    start: (data) => api.post('/simulation/start', data),
    status: (id) => api.get(`/simulation/status/${id}`),
};

// Incidents
export const incidentsAPI = {
    list: (params) => api.get('/incidents/', { params }),
    get: (id) => api.get(`/incidents/${id}`),
    update: (id, data) => api.patch(`/incidents/${id}`, data),
    timeline: (id) => api.get(`/incidents/${id}/timeline`),
};

// Reports
export const reportsAPI = {
    list: () => api.get('/reports/'),
    get: (id) => api.get(`/reports/${id}`),
    generate: (data) => api.post('/reports/generate', data),
    downloadPdf: (id) => api.get(`/reports/${id}/pdf`, { responseType: 'blob' }),
};

export default api;
