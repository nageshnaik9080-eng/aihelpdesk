// Central runtime config. Reads the Vite env var when running under Vite;
// falls back to localhost so tests (Jest, no import.meta.env) work too.
const env = (typeof import.meta !== 'undefined' && import.meta.env) || {};

// Backend is served over plain HTTP (no TLS), so there is no SSL certificate
// for the browser to verify. Point this at wherever the FastAPI backend runs.
export const API_BASE_URL = env.VITE_API_URL || 'http://localhost:8000';

export const SESSION_STORAGE_KEY = 'helpdesk_user';
