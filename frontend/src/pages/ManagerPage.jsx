import { Alert, Box, Button, Stack, Typography } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import Dashboard from '../components/Dashboard';
import { apiErrorMessage } from '../api/client';
import { useAnalytics } from '../hooks/useAnalytics';

export default function ManagerPage() {
  const analytics = useAnalytics();

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5">Helpdesk analytics</Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={() => analytics.refetch()}
          disabled={analytics.isFetching}
        >
          Refresh
        </Button>
      </Stack>

      {analytics.isError ? (
        <Alert severity="error">{apiErrorMessage(analytics.error)}</Alert>
      ) : (
        <Dashboard data={analytics.data} loading={analytics.isLoading} />
      )}
    </Box>
  );
}
