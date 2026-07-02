import Chip from '@mui/material/Chip';

// Maps backend TicketStatus values (backend/app/models/ticket.py) to MUI colors.
const STATUS_COLORS = {
  open: 'info',
  in_progress: 'warning',
  routed: 'secondary',
  escalated: 'error',
  resolved: 'success',
  closed: 'default',
  duplicate: 'primary',
};

export default function StatusChip({ status }) {
  const key = (status ?? '').toLowerCase();
  const label = key ? key.replace(/_/g, ' ') : 'unknown';
  return (
    <Chip
      size="small"
      color={STATUS_COLORS[key] ?? 'default'}
      label={label}
      sx={{ textTransform: 'capitalize', fontWeight: 600 }}
    />
  );
}
