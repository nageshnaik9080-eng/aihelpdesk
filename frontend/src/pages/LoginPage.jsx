import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Container,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { apiErrorMessage } from '../api/client';
import { homePathForRole, useUser } from '../context/UserContext';
import { useUsers } from '../hooks/useAnalytics';

const DEMO_PASSWORD = 'Password123';

export default function LoginPage() {
  const { setUser } = useUser();
  const navigate = useNavigate();
  const usersQuery = useUsers();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState(DEMO_PASSWORD);

  const loginMutation = useMutation({
    mutationFn: () => login(email.trim(), password),
    onSuccess: (res) => {
      const known = usersQuery.data?.find((u) => u.email === res.email);
      const user =
        known ?? {
          id: 0,
          email: res.email,
          full_name: res.full_name,
          role_name: res.role,
        };
      setUser(user);
      navigate(homePathForRole(user.role_name), { replace: true });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email.trim() || !password) return;
    loginMutation.mutate();
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 10 }}>
      <Paper sx={{ p: 4 }} elevation={3}>
        <Stack alignItems="center" spacing={1} sx={{ mb: 3 }}>
          <SupportAgentIcon color="primary" sx={{ fontSize: 44 }} />
          <Typography variant="h5">AI Helpdesk Router</Typography>
          <Typography variant="body2" color="text.secondary">
            Sign in to choose your persona view
          </Typography>
        </Stack>

        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              select
              label="Demo user"
              value={usersQuery.data?.some((u) => u.email === email) ? email : ''}
              onChange={(e) => {
                setEmail(e.target.value);
                setPassword(DEMO_PASSWORD);
              }}
              helperText={
                usersQuery.isError
                  ? 'Could not load users — is the backend running & seeded?'
                  : 'Pick a seeded demo user, or type an email below.'
              }
              disabled={usersQuery.isLoading}
              fullWidth
            >
              {(usersQuery.data ?? []).map((u) => (
                <MenuItem key={u.id} value={u.email}>
                  {u.full_name || u.email} — {String(u.role_name).replace(/_/g, ' ')}
                  {u.department ? ` (${u.department})` : ''}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              fullWidth
              inputProps={{ 'aria-label': 'email' }}
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              fullWidth
              helperText={`Seeded demo password: ${DEMO_PASSWORD}`}
              inputProps={{ 'aria-label': 'password' }}
            />

            {loginMutation.isError && (
              <Alert severity="error">{apiErrorMessage(loginMutation.error)}</Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
