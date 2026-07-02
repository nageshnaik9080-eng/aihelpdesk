import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import EmployeePage from './pages/EmployeePage';
import AgentPage from './pages/AgentPage';
import ManagerPage from './pages/ManagerPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import DatabasePage from './pages/DatabasePage';
import { homePathForRole, useUser } from './context/UserContext';

function RequireUser({ children }) {
  const { user } = useUser();
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const { user, role } = useUser();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to={homePathForRole(role)} replace /> : <LoginPage />}
      />
      <Route
        element={
          <RequireUser>
            <Layout />
          </RequireUser>
        }
      >
        <Route index element={<Navigate to={homePathForRole(role)} replace />} />
        <Route path="/employee" element={<EmployeePage />} />
        <Route path="/agent" element={<AgentPage />} />
        <Route path="/manager" element={<ManagerPage />} />
        <Route path="/database" element={<DatabasePage />} />
        <Route path="/kb" element={<KnowledgeBasePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
