import { useState } from 'react';
import { Box, Button, Stack, TextField, ToggleButton, ToggleButtonGroup, Typography } from '@mui/material';
import ThumbUpAltIcon from '@mui/icons-material/ThumbUpAlt';
import ThumbDownAltIcon from '@mui/icons-material/ThumbDownAlt';

export default function FeedbackForm({ onSubmit, submitting = false }) {
  const [rating, setRating] = useState(null);
  const [comment, setComment] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (rating == null) return;
    onSubmit(rating, comment.trim());
    setComment('');
    setRating(null);
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="subtitle2" gutterBottom>
        Was this resolution helpful?
      </Typography>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="flex-start">
        <ToggleButtonGroup
          exclusive
          value={rating}
          onChange={(_, val) => setRating(val)}
          aria-label="rating"
          size="small"
        >
          <ToggleButton value={1} aria-label="helpful" color="success">
            <ThumbUpAltIcon fontSize="small" sx={{ mr: 0.5 }} /> Yes
          </ToggleButton>
          <ToggleButton value={0} aria-label="not helpful" color="error">
            <ThumbDownAltIcon fontSize="small" sx={{ mr: 0.5 }} /> No
          </ToggleButton>
        </ToggleButtonGroup>
        <TextField
          size="small"
          label="Comment (optional)"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          fullWidth
          inputProps={{ 'aria-label': 'comment' }}
        />
        <Button type="submit" variant="contained" disabled={rating == null || submitting}>
          {submitting ? 'Sending…' : 'Send feedback'}
        </Button>
      </Stack>
    </Box>
  );
}
