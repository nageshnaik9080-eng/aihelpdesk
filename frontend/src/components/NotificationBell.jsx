import { useState } from 'react';
import {
  Badge,
  Box,
  Divider,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Popover,
  Typography,
} from '@mui/material';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import { useMarkNotificationRead, useNotifications } from '../hooks/useNotifications';

function formatDate(value) {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

export default function NotificationBell() {
  const { data } = useNotifications();
  const markRead = useMarkNotificationRead();
  const [anchorEl, setAnchorEl] = useState(null);

  const items = data ?? [];
  const unread = items.filter((n) => !n.is_read).length;

  const open = (e) => setAnchorEl(e.currentTarget);
  const close = () => setAnchorEl(null);

  return (
    <>
      <IconButton color="inherit" onClick={open} aria-label="notifications">
        <Badge badgeContent={unread} color="error">
          <NotificationsNoneIcon />
        </Badge>
      </IconButton>

      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={close}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Box sx={{ width: 360, maxHeight: 440, overflow: 'auto' }}>
          <Typography variant="subtitle1" sx={{ p: 2, pb: 1, fontWeight: 700 }}>
            Notifications {unread > 0 && `(${unread} new)`}
          </Typography>
          <Divider />
          {items.length === 0 ? (
            <Typography color="text.secondary" sx={{ p: 2 }}>
              No notifications yet.
            </Typography>
          ) : (
            <List disablePadding>
              {items.map((n) => (
                <ListItemButton
                  key={n.id}
                  onClick={() => !n.is_read && markRead.mutate(n.id)}
                  sx={{ bgcolor: n.is_read ? 'transparent' : 'action.hover', alignItems: 'flex-start' }}
                >
                  <ListItemText
                    primary={n.message}
                    secondary={`${n.type} · ${formatDate(n.created_at)}`}
                    primaryTypographyProps={{
                      variant: 'body2',
                      fontWeight: n.is_read ? 400 : 600,
                    }}
                  />
                </ListItemButton>
              ))}
            </List>
          )}
        </Box>
      </Popover>
    </>
  );
}
