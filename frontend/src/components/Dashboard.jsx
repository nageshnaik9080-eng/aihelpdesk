import { Box, Card, CardContent, Grid, LinearProgress, Paper, Stack, Typography } from '@mui/material';

function pct(value) {
  return `${Math.round((value ?? 0) * 100)}%`;
}

function KpiCard({ label, value, hint }) {
  return (
    <Card elevation={2} sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="overline" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          {value}
        </Typography>
        {hint && (
          <Typography variant="caption" color="text.secondary">
            {hint}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

function Breakdown({ title, data }) {
  const entries = Object.entries(data ?? {});
  const max = Math.max(1, ...entries.map(([, v]) => v));
  return (
    <Paper sx={{ p: 2, height: '100%' }} elevation={1}>
      <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 700 }}>
        {title}
      </Typography>
      {entries.length === 0 && <Typography color="text.secondary">No data.</Typography>}
      <Stack spacing={1.5}>
        {entries.map(([key, value]) => (
          <Box key={key}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {value}
              </Typography>
            </Box>
            <LinearProgress variant="determinate" value={(value / max) * 100} />
          </Box>
        ))}
      </Stack>
    </Paper>
  );
}

export default function Dashboard({ data, loading }) {
  if (loading) return <LinearProgress />;
  if (!data) return <Typography color="text.secondary">No analytics available.</Typography>;

  const avgRes = data.avg_resolution_minutes;
  const avgFirst = data.avg_first_response_minutes;

  return (
    <Box>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard label="Total tickets" value={String(data.total_tickets)} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Auto-resolution rate"
            value={pct(data.auto_resolution_rate)}
            hint={`${data.auto_resolved} auto / ${data.agent_resolved} by agents`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard label="Routing accuracy" value={pct(data.routing_accuracy)} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard label="Escalation rate" value={pct(data.escalation_rate)} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Avg resolution"
            value={avgRes != null ? `${Math.round(avgRes)} min` : '—'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Avg first response"
            value={avgFirst != null ? `${Math.round(avgFirst)} min` : '—'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="CSAT"
            value={data.csat != null ? pct(data.csat) : '—'}
            hint="Employee satisfaction"
          />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mt: 0.5 }}>
        <Grid item xs={12} md={6}>
          <Breakdown title="Tickets by department" data={data.by_department} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Breakdown title="Tickets by status" data={data.by_status} />
        </Grid>
      </Grid>
    </Box>
  );
}
