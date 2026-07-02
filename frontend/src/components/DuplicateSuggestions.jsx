import { Alert, Box, Chip, List, ListItem, ListItemText, Typography } from '@mui/material';

export default function DuplicateSuggestions({ suggestions }) {
  if (!suggestions.length) return null;

  return (
    <Alert severity="warning" sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Similar existing tickets found — you may not need a new one:
      </Typography>
      <List dense disablePadding>
        {suggestions.map((s) => (
          <ListItem key={s.ticket_id} disableGutters secondaryAction={
            <Chip size="small" label={`${Math.round(s.similarity * 100)}% match`} />
          }>
            <ListItemText
              primary={<Box component="span">#{s.ticket_id} — {s.title}</Box>}
            />
          </ListItem>
        ))}
      </List>
    </Alert>
  );
}
