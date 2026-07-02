// Persists the "acting user" locally. Endpoints are public, so identity is just
// the user's email sent as an X-User-Email header (see client.js interceptor).
import { SESSION_STORAGE_KEY } from '../config';

export function getSessionUser() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setSessionUser(user) {
  try {
    if (user) {
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(SESSION_STORAGE_KEY);
    }
  } catch {
    /* ignore storage failures */
  }
}

export function getSessionEmail() {
  return getSessionUser()?.email ?? null;
}
