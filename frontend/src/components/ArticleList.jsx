import {
  Chip,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  Typography,
} from '@mui/material';

export default function ArticleList({ articles, onSelect, selectedId }) {
  if (!articles.length) {
    return (
      <Paper sx={{ p: 3 }} elevation={1}>
        <Typography color="text.secondary">No articles in the knowledge base yet.</Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={1}>
      <List disablePadding>
        {articles.map((a) => (
          <ListItemButton
            key={a.id}
            selected={selectedId === a.id}
            onClick={() => onSelect(a)}
          >
            <ListItemText
              primary={a.title}
              secondary={
                <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                  <Chip size="small" label={a.category} variant="outlined" />
                  <Chip size="small" label={`${a.retrieval_count} retrievals`} variant="outlined" />
                </Stack>
              }
              secondaryTypographyProps={{ component: 'div' }}
            />
          </ListItemButton>
        ))}
      </List>
    </Paper>
  );
}
