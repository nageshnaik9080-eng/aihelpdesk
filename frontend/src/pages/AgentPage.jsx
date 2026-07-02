import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogContent,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import TicketList from '../components/TicketList';
import TicketDetail from '../components/TicketDetail';
import { apiErrorMessage } from '../api/client';
import { useEscalateTicket, useResolveTicket, useTickets } from '../hooks/useTickets';

const ESCALATION_TARGETS = ['L2', 'L3', 'vendor'];

export default function AgentPage() {
  const ticketsQuery = useTickets();
  const resolve = useResolveTicket();
  const escalate = useEscalateTicket();

  const [selected, setSelected] = useState(null);
  const [resolution, setResolution] = useState('');
  const [target, setTarget] = useState('L2');
  const [note, setNote] = useState('');

  const openTicket = (t) => {
    setSelected(t);
    setResolution('');
    setTarget('L2');
    setNote('');
  };

  const closeDialog = () => setSelected(null);
  const isClosed = selected && ['resolved', 'closed'].includes(selected.status);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Agent queue
      </Typography>

      {ticketsQuery.isError ? (
        <Alert severity="error">{apiErrorMessage(ticketsQuery.error)}</Alert>
      ) : (
        <TicketList
          tickets={ticketsQuery.data ?? []}
          onSelect={openTicket}
          selectedId={selected?.id}
          emptyText={ticketsQuery.isLoading ? 'Loading…' : 'No tickets in your queue.'}
        />
      )}

      <Dialog open={!!selected} onClose={closeDialog} maxWidth="sm" fullWidth>
        <DialogContent>
          {selected && (
            <TicketDetail ticket={selected}>
              {isClosed ? (
                <Typography variant="body2" color="text.secondary">
                  This ticket is already {selected.status}.
                </Typography>
              ) : (
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Resolve
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <TextField
                        size="small"
                        fullWidth
                        multiline
                        placeholder="Resolution details for the employee…"
                        value={resolution}
                        onChange={(e) => setResolution(e.target.value)}
                        inputProps={{ 'aria-label': 'resolution' }}
                      />
                      <Button
                        variant="contained"
                        disabled={!resolution.trim() || resolve.isPending}
                        onClick={() =>
                          resolve.mutate(
                            { id: selected.id, resolution: resolution.trim() },
                            { onSuccess: closeDialog },
                          )
                        }
                      >
                        Resolve
                      </Button>
                    </Stack>
                  </Box>

                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Escalate
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <TextField
                        select
                        size="small"
                        label="Target"
                        value={target}
                        onChange={(e) => setTarget(e.target.value)}
                        sx={{ minWidth: 110 }}
                      >
                        {ESCALATION_TARGETS.map((t) => (
                          <MenuItem key={t} value={t}>
                            {t}
                          </MenuItem>
                        ))}
                      </TextField>
                      <TextField
                        size="small"
                        fullWidth
                        placeholder="Escalation note"
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        inputProps={{ 'aria-label': 'escalation note' }}
                      />
                      <Button
                        color="error"
                        variant="outlined"
                        disabled={escalate.isPending}
                        onClick={() =>
                          escalate.mutate(
                            { id: selected.id, target, note: note.trim() },
                            { onSuccess: closeDialog },
                          )
                        }
                      >
                        Escalate
                      </Button>
                    </Stack>
                  </Box>

                  {(resolve.isError || escalate.isError) && (
                    <Alert severity="error">
                      {apiErrorMessage(resolve.error ?? escalate.error)}
                    </Alert>
                  )}
                </Stack>
              )}
            </TicketDetail>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}
