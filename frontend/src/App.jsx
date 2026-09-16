import React from 'react';
import { Container, Typography, Button, Stack } from '@mui/material';

function App() {
  return (
    <Container maxWidth="sm" style={{ marginTop: '2rem' }}>
      <Stack spacing={2} alignItems="center">
        <Typography variant="h3" component="h1" color="primary" gutterBottom>
          MUI + Vite + React
        </Typography>
        <Typography variant="body1" textAlign="center">
          Your project environment is fully configured and ready!
        </Typography>
        <Button variant="contained" color="secondary">
          MUI Button
        </Button>
      </Stack>
    </Container>
  );
}

export default App;
