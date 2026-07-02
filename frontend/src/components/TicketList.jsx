import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import StatusChip from './StatusChip';

function formatDate(value) {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

export default function TicketList({
  tickets,
  onSelect,
  selectedId,
  emptyText = 'No tickets yet.',
}) {
  if (!tickets.length) {
    return (
      <Paper sx={{ p: 3 }} elevation={1}>
        <Typography color="text.secondary">{emptyText}</Typography>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper} elevation={1}>
      <Table size="small" aria-label="tickets">
        <TableHead>
          <TableRow>
            <TableCell>#</TableCell>
            <TableCell>Title</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Priority</TableCell>
            <TableCell>Dept</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tickets.map((t) => (
            <TableRow
              key={t.id}
              hover
              selected={selectedId === t.id}
              onClick={() => onSelect?.(t)}
              sx={{ cursor: onSelect ? 'pointer' : 'default' }}
            >
              <TableCell>{t.id}</TableCell>
              <TableCell sx={{ maxWidth: 320 }}>{t.title || t.description.slice(0, 60)}</TableCell>
              <TableCell>{t.category ?? '—'}</TableCell>
              <TableCell sx={{ textTransform: 'capitalize' }}>{t.priority ?? '—'}</TableCell>
              <TableCell>{t.department ?? '—'}</TableCell>
              <TableCell>
                <StatusChip status={t.status} />
              </TableCell>
              <TableCell>{formatDate(t.created_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
