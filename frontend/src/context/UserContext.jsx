import { createContext, useContext, useMemo, useState } from 'react';
import { getSessionUser, setSessionUser } from '../api/session';

const UserContext = createContext(undefined);

export function UserProvider({ children }) {
  const [user, setUserState] = useState(() => getSessionUser());

  const value = useMemo(
    () => ({
      user,
      role: user?.role_name ?? null,
      setUser: (u) => {
        setSessionUser(u);
        setUserState(u);
      },
      logout: () => {
        setSessionUser(null);
        setUserState(null);
      },
    }),
    [user],
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used within a UserProvider');
  return ctx;
}

// Role helpers used for view routing / conditional UI.
export const AGENT_ROLES = ['it_agent', 'admin_agent'];
export const MANAGER_ROLES = ['helpdesk_manager', 'system_admin'];
export const KB_WRITER_ROLES = ['kb_admin', 'system_admin'];

export function homePathForRole(role) {
  if (!role) return '/login';
  if (MANAGER_ROLES.includes(role)) return '/manager';
  if (AGENT_ROLES.includes(role)) return '/agent';
  return '/employee';
}
