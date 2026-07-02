import { Box, Chip, Divider, Paper, Typography } from '@mui/material';

export default function ArticleView({ article }) {
  if (!article) {
    return (
      <Paper sx={{ p: 3, height: '100%' }} elevation={1}>
        <Typography color="text.secondary">Select an article to read it.</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }} elevation={1}>
      <Typography variant="h5" gutterBottom>
        {article.title}
      </Typography>
      <Box sx={{ mb: 2 }}>
        <Chip size="small" label={article.category} color="primary" variant="outlined" />
      </Box>
      <Divider sx={{ mb: 2 }} />
      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
        {article.content}
      </Typography>
    </Paper>
  );
}
