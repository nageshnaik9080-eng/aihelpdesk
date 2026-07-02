import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import StorageIcon from '@mui/icons-material/Storage';
import { apiErrorMessage } from '../api/client';
import { useDbOverview } from '../hooks/useAdmin';
import StatusChip from '../components/StatusChip';

function formatDate(value) {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

export default function DatabasePage() {
  const { data, isLoading, isError, error, refetch, isFetching } = useDbOverview();

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <StorageIcon color="primary" />
          <Typography variant="h5">Database</Typography>
        </Stack>
        <Button startIcon={<RefreshIcon />} onClick={() => refetch()} disabled={isFetching}>
          Refresh
        </Button>
      </Stack>

      {isError && <Alert severity="error">{apiErrorMessage(error)}</Alert>}
      {isLoading && <Typography color="text.secondary">Loading…</Typography>}

      {data && (
        <>
          <Alert severity={data.exists ? 'success' : 'warning'} sx={{ mb: 2 }}>
            SQLite file <code>{data.db_file}</code> — {data.exists ? 'present' : 'missing'} (
            {(data.size_bytes / 1024).toFixed(1)} KB). Auto-refreshes every 10s.
          </Alert>

          <Typography variant="h6" gutterBottom>
            Row counts
          </Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {Object.entries(data.counts).map(([table, count]) => (
              <Grid item xs={6} sm={4} md={2} key={table}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {count}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {table.replace(/_/g, ' ')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={7}>
              <Typography variant="h6" gutterBottom>
                Recent tickets
              </Typography>
              <TableContainer component={Paper} elevation={1}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>#</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Dept</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Created</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.recent_tickets.map((t) => (
                      <TableRow key={t.id}>
                        <TableCell>{t.id}</TableCell>
                        <TableCell sx={{ maxWidth: 220 }}>{t.title}</TableCell>
                        <TableCell>{t.category ?? '—'}</TableCell>
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
            </Grid>

            <Grid item xs={12} lg={5}>
              <Typography variant="h6" gutterBottom>
                Recent users
              </Typography>
              <TableContainer component={Paper} elevation={1}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>#</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Role</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.recent_users.map((u) => (
                      <TableRow key={u.id}>
                        <TableCell>{u.id}</TableCell>
                        <TableCell sx={{ maxWidth: 220 }}>{u.email}</TableCell>
                        <TableCell sx={{ textTransform: 'capitalize' }}>
                          {u.role_name.replace(/_/g, ' ')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Recent feedback
              </Typography>
              {data.recent_feedback.length === 0 ? (
                <Paper sx={{ p: 2 }} elevation={1}>
                  <Typography color="text.secondary">No feedback yet.</Typography>
                </Paper>
              ) : (
                <TableContainer component={Paper} elevation={1}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>#</TableCell>
                        <TableCell>Ticket</TableCell>
                        <TableCell>Rating</TableCell>
                        <TableCell>Comment</TableCell>
                        <TableCell>Created</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {data.recent_feedback.map((f) => (
                        <TableRow key={f.id}>
                          <TableCell>{f.id}</TableCell>
                          <TableCell>#{f.ticket_id}</TableCell>
                          <TableCell>
                            <Chip
                              size="small"
                              color={f.rating === 1 ? 'success' : 'error'}
                              label={f.rating === 1 ? '👍 helpful' : '👎 not helpful'}
                            />
                          </TableCell>
                          <TableCell>{f.comment || '—'}</TableCell>
                          <TableCell>{formatDate(f.created_at)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
