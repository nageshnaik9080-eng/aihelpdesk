import { Box, Chip, Divider, Grid, Link, Paper, Stack, Typography } from '@mui/material';
import StatusChip from './StatusChip';

function Field({ label, value }) {
  return (
    <Grid item xs={6} sm={4}>
      <Typography variant="caption" color="text.secondary" display="block">
        {label}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
        {value ?? '—'}
      </Typography>
    </Grid>
  );
}

export default function TicketDetail({ ticket, children }) {
  return (
    <Paper sx={{ p: 3 }} elevation={0}>
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 1 }}>
        <Typography variant="h6">
          #{ticket.id} — {ticket.title || 'Untitled'}
        </Typography>
        <StatusChip status={ticket.status} />
      </Stack>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Field label="Category" value={ticket.category} />
        <Field label="Priority" value={ticket.priority} />
        <Field label="Department" value={ticket.department} />
        <Field label="Intent" value={ticket.intent} />
        <Field label="Confidence" value={`${Math.round((ticket.confidence ?? 0) * 100)}%`} />
        <Field
          label="Assigned agent"
          value={ticket.assigned_agent_id ? `#${ticket.assigned_agent_id}` : 'Unassigned'}
        />
      </Grid>

      <Typography variant="caption" color="text.secondary" display="block">
        Description
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
        {ticket.description}
      </Typography>

      {ticket.resolution && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>
            Resolution{' '}
            <Chip
              size="small"
              label={ticket.resolution_source === 'auto' ? 'AI auto-resolved' : 'Agent'}
              color={ticket.resolution_source === 'auto' ? 'success' : 'default'}
            />
          </Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {ticket.resolution}
          </Typography>
          {ticket.kb_sources && ticket.kb_sources.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Sources:
              </Typography>{' '}
              {ticket.kb_sources.map((s, i) => (
                <Link key={i} component="span" sx={{ mr: 1 }} underline="hover">
                  {String(s.title ?? `Source ${i + 1}`)}
                </Link>
              ))}
            </Box>
          )}
        </>
      )}

      {ticket.escalation_target && (
        <Box sx={{ mt: 2 }}>
          <Chip color="error" size="small" label={`Escalated to ${ticket.escalation_target}`} />
        </Box>
      )}

      {children && (
        <>
          <Divider sx={{ my: 2 }} />
          {children}
        </>
      )}
    </Paper>
  );
}
