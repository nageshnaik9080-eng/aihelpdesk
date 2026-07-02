import axios from 'axios';
import { API_BASE_URL } from '../config';
import { getSessionEmail } from './session';

// Single Axios instance for all backend calls.
//
// The backend is reached over plain HTTP, so there is no TLS handshake and
// nothing for the browser to verify. If you ever point this at an HTTPS backend
// with a self-signed certificate, note that browsers ALWAYS verify certificates
// and there is no in-page way to disable that — you would need to trust the cert
// in the OS/browser, or keep using plain HTTP as configured here.
export const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { Accept: 'application/json' },
});

// The API is public (no token). We only attach the acting user's email so the
// backend can scope persona-specific data (see backend/app/api/deps.py).
client.interceptors.request.use((config) => {
  const email = getSessionEmail();
  if (email) {
    config.headers.set('X-User-Email', email);
  }
  return config;
});

// Surface a readable message from FastAPI's {detail: ...} error bodies.
export function apiErrorMessage(err) {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
    return err.message;
  }
  return err instanceof Error ? err.message : 'Unexpected error';
}

export default client;
