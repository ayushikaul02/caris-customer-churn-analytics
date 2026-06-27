import React from 'react';
import { Typography, Box } from '@mui/material';
import Layout from '../components/Layout/Layout';

const Retention: React.FC = () => {
  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          🎯 Retention
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Retention page coming soon...
        </Typography>
      </Box>
    </Layout>
  );
};

export default Retention;