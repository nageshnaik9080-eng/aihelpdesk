import { AppBar, Avatar, Box, Button, Chip, Toolbar, Typography } from '@mui/material';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import NotificationBell from './NotificationBell';

export default function Navbar() {
  const { user, logout } = useUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
      <Toolbar>
        <SupportAgentIcon sx={{ mr: 1.5 }} />
        <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
          HelpRoute
        </Typography>
        {user && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <NotificationBell />
            <Chip
              size="small"
              color="default"
              label={(user.role_name || '').replace(/_/g, ' ')}
              sx={{ bgcolor: 'rgba(255,255,255,0.18)', color: 'inherit', textTransform: 'capitalize' }}
            />
            <Avatar sx={{ width: 30, height: 30, bgcolor: 'secondary.main' }}>
              {(user.full_name || user.email).charAt(0).toUpperCase()}
            </Avatar>
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              {user.full_name || user.email}
            </Typography>
            <Button
              color="inherit"
              size="small"
              startIcon={<LogoutOutlinedIcon />}
              onClick={handleLogout}
            >
              Switch user
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
