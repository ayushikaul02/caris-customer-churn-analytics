import React from 'react';
import { Typography, Box } from '@mui/material';
import Layout from '../components/Layout/Layout';

const Customers: React.FC = () => {
  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          👥 Customers
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Customer management page coming soon...
        </Typography>
      </Box>
    </Layout>
  );
};

export default Customers;