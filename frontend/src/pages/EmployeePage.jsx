import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  Grid,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material';
import TicketForm from '../components/TicketForm';
import TicketList from '../components/TicketList';
import DuplicateSuggestions from '../components/DuplicateSuggestions';
import FeedbackForm from '../components/FeedbackForm';
import TicketDetail from '../components/TicketDetail';
import { apiErrorMessage } from '../api/client';
import {
  useCloseTicket,
  useSubmitFeedback,
  useSubmitTicket,
  useTickets,
} from '../hooks/useTickets';

export default function EmployeePage() {
  const ticketsQuery = useTickets();
  const submit = useSubmitTicket();
  const feedback = useSubmitFeedback();
  const closeTicket = useCloseTicket();

  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(null);

  const handleSubmit = (input) => {
    submit.mutate(input, { onSuccess: (res) => setResult(res) });
  };

  const canFeedback = selected && ['resolved', 'closed'].includes(selected.status);
  const canClose = selected && selected.status === 'resolved';

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Submit &amp; track your requests
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TicketForm onSubmit={handleSubmit} submitting={submit.isPending} />
          {submit.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {apiErrorMessage(submit.error)}
            </Alert>
          )}
          {result && (
            <Alert
              severity={result.ticket.status === 'resolved' ? 'success' : 'info'}
              sx={{ mt: 2 }}
            >
              Ticket #{result.ticket.id} created — status <strong>{result.ticket.status}</strong>.
              {result.ticket.resolution && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {result.ticket.resolution}
                </Typography>
              )}
            </Alert>
          )}
          {result && <DuplicateSuggestions suggestions={result.duplicate_suggestions} />}
          {result && result.pipeline.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2">AI pipeline trace</Typography>
              <List dense>
                {result.pipeline.map((step, i) => (
                  <ListItem key={i} disableGutters>
                    <ListItemText
                      primary={`${step.agent} — ${step.event}`}
                      secondary={step.detail}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            My tickets
          </Typography>
          {ticketsQuery.isError ? (
            <Alert severity="error">{apiErrorMessage(ticketsQuery.error)}</Alert>
          ) : (
            <TicketList
              tickets={ticketsQuery.data ?? []}
              onSelect={setSelected}
              selectedId={selected?.id}
              emptyText={ticketsQuery.isLoading ? 'Loading…' : 'No tickets yet.'}
            />
          )}
        </Grid>
      </Grid>

      <Dialog open={!!selected} onClose={() => setSelected(null)} maxWidth="sm" fullWidth>
        <DialogContent>
          {selected && (
            <TicketDetail ticket={selected}>
              {canFeedback ? (
                <FeedbackForm
                  submitting={feedback.isPending}
                  onSubmit={(rating, comment) =>
                    feedback.mutate(
                      { id: selected.id, rating, comment },
                      { onSuccess: () => setSelected(null) },
                    )
                  }
                />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Feedback becomes available once the ticket is resolved or closed.
                </Typography>
              )}
            </TicketDetail>
          )}
        </DialogContent>
        <DialogActions>
          {canClose && selected && (
            <Button
              onClick={() =>
                closeTicket.mutate({ id: selected.id }, { onSuccess: () => setSelected(null) })
              }
              disabled={closeTicket.isPending}
            >
              Close ticket
            </Button>
          )}
          <Button onClick={() => setSelected(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
