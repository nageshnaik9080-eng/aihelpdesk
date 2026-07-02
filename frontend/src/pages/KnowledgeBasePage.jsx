import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Grid,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ArticleList from '../components/ArticleList';
import ArticleView from '../components/ArticleView';
import { apiErrorMessage } from '../api/client';
import { useArticles, useCreateArticle, useSearchKB } from '../hooks/useKnowledge';
import { KB_WRITER_ROLES, useUser } from '../context/UserContext';

const CATEGORIES = ['General', 'Password/Access', 'Network', 'Email', 'Hardware', 'Software', 'HR/Payroll', 'Finance/Reimbursement', 'Facilities'];

export default function KnowledgeBasePage() {
  const { role } = useUser();
  const canWrite = role != null && KB_WRITER_ROLES.includes(role);

  const articlesQuery = useArticles();
  const createArticle = useCreateArticle();

  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState('');
  const searchQuery = useSearchKB(query);

  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newCategory, setNewCategory] = useState('General');

  const handleCreate = () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    createArticle.mutate(
      { title: newTitle.trim(), content: newContent.trim(), category: newCategory },
      {
        onSuccess: (a) => {
          setSelected(a);
          setNewTitle('');
          setNewContent('');
          setNewCategory('General');
        },
      },
    );
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Knowledge base
      </Typography>

      <TextField
        placeholder="Semantic search the knowledge base…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        inputProps={{ 'aria-label': 'search knowledge base' }}
      />

      {query.trim() && (
        <Paper sx={{ p: 2, mb: 2 }} elevation={1}>
          <Typography variant="subtitle2" gutterBottom>
            Search results
          </Typography>
          {searchQuery.isError && (
            <Alert severity="error">{apiErrorMessage(searchQuery.error)}</Alert>
          )}
          {searchQuery.isLoading && <Typography color="text.secondary">Searching…</Typography>}
          <List dense>
            {(searchQuery.data ?? []).map((r, i) => (
              <ListItem key={i} disableGutters>
                <ListItemText
                  primary={`${r.title} — ${Math.round(r.score * 100)}%`}
                  secondary={r.snippet}
                />
              </ListItem>
            ))}
            {searchQuery.data && searchQuery.data.length === 0 && !searchQuery.isLoading && (
              <Typography color="text.secondary">No matches.</Typography>
            )}
          </List>
        </Paper>
      )}

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          {articlesQuery.isError ? (
            <Alert severity="error">{apiErrorMessage(articlesQuery.error)}</Alert>
          ) : (
            <ArticleList
              articles={articlesQuery.data ?? []}
              onSelect={setSelected}
              selectedId={selected?.id}
            />
          )}
        </Grid>
        <Grid item xs={12} md={8}>
          <ArticleView article={selected} />

          {canWrite && (
            <Paper sx={{ p: 3, mt: 2 }} elevation={1}>
              <Typography variant="h6" gutterBottom>
                New article
              </Typography>
              <Stack spacing={2}>
                <TextField
                  label="Title"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  fullWidth
                  size="small"
                />
                <TextField
                  select
                  label="Category"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  sx={{ maxWidth: 260 }}
                  size="small"
                >
                  {CATEGORIES.map((c) => (
                    <MenuItem key={c} value={c}>
                      {c}
                    </MenuItem>
                  ))}
                </TextField>
                <TextField
                  label="Content"
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  multiline
                  minRows={4}
                  fullWidth
                  size="small"
                />
                {createArticle.isError && (
                  <Alert severity="error">{apiErrorMessage(createArticle.error)}</Alert>
                )}
                <Box>
                  <Button
                    variant="contained"
                    onClick={handleCreate}
                    disabled={!newTitle.trim() || !newContent.trim() || createArticle.isPending}
                  >
                    Publish article
                  </Button>
                </Box>
              </Stack>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
