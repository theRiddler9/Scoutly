import axios from 'axios';

// Empty string = relative requests (e.g. "/api/discovery/run"), which get
// routed through the Vite dev-server proxy in vite.config.js straight to your
// local backend on :8000. Previously this defaulted to a deployed Render URL,
// so every request silently skipped your local backend and hit production
// instead — which is why things could "work" in code but look dead in the UI.
// Set VITE_API_URL in a .env file to point at a real deployed backend.
const API_BASE = import.meta.env.VITE_API_URL || '';


const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Profile ──────────────────────────────────────────────────────────────────

export const profileApi = {
  create: (data) => api.post('/api/profile', data),
  get: (id = 1) => api.get(`/api/profile/${id}`),
  list: () => api.get('/api/profile'),
  update: (id, data) => api.put(`/api/profile/${id}`, data),
  delete: (id) => api.delete(`/api/profile/${id}`),
};

// ── Opportunities ────────────────────────────────────────────────────────────

export const opportunitiesApi = {
  list: (params = {}) => api.get('/api/opportunities', { params }),
  get: (id, profileId = 1) => api.get(`/api/opportunities/${id}`, { params: { profile_id: profileId } }),
  triggerMatch: (data) => api.post('/api/opportunities/match', data),
  clearAll: () => api.delete('/api/opportunities/clear'),
};

// ── Applications ─────────────────────────────────────────────────────────────

export const applicationsApi = {
  list: () => api.get('/api/applications'),
  get: (id) => api.get(`/api/applications/${id}`),
  fill: (data) => api.post('/api/applications/fill', data),
  getScreenshot: (id) => `${API_BASE}/api/applications/${id}/screenshot`,
  approve: (id, approved = true) => api.post(`/api/applications/${id}/approve`, { approved }),
  getFieldLogs: (id) => api.get(`/api/applications/${id}/field-logs`),
};

// ── Discovery ────────────────────────────────────────────────────────────────

export const discoveryApi = {
  run: (data = {}) => api.post('/api/discovery/run', data),
  getSources: () => api.get('/api/discovery/sources'),
};

// ── Dashboard ────────────────────────────────────────────────────────────────

export const dashboardApi = {
  getStats: () => api.get('/api/dashboard/stats'),
};

export default api;
