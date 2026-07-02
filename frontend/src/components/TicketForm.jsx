import { useRef, useState } from 'react';
import { Box, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SendIcon from '@mui/icons-material/Send';

export default function TicketForm({ onSubmit, submitting = false }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const canSubmit = description.trim().length > 0 && !submitting;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    onSubmit({ title: title.trim(), description: description.trim(), file });
    setTitle('');
    setDescription('');
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <Paper component="form" onSubmit={handleSubmit} sx={{ p: 3 }} elevation={2}>
      <Typography variant="h6" gutterBottom>
        Submit a support request
      </Typography>
      <Stack spacing={2}>
        <TextField
          label="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          fullWidth
          size="small"
          inputProps={{ 'aria-label': 'title' }}
        />
        <TextField
          label="Describe your issue"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          multiline
          minRows={4}
          fullWidth
          placeholder="e.g. I forgot my password and I'm locked out of my email."
          inputProps={{ 'aria-label': 'description' }}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Button
            component="label"
            variant="outlined"
            startIcon={<UploadFileIcon />}
          >
            Attach screenshot
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              aria-label="attachment"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </Button>
          {file && (
            <Typography variant="body2" color="text.secondary">
              {file.name}
            </Typography>
          )}
          <Box sx={{ flexGrow: 1 }} />
          <Button
            type="submit"
            variant="contained"
            startIcon={<SendIcon />}
            disabled={!canSubmit}
          >
            {submitting ? 'Submitting…' : 'Submit ticket'}
          </Button>
        </Box>
      </Stack>
    </Paper>
  );
}
