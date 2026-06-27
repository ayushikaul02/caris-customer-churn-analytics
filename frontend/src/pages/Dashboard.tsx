import React, { useState, useEffect } from 'react';
import { Grid, Typography, Box, Skeleton } from '@mui/material';
import Layout from '../components/Layout/Layout';
import KPICards from '../components/Dashboard/KPICards';
import { dashboardAPI } from '../api/client';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardAPI.getMetrics();
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <Box sx={{ p: 3 }}>
          <Skeleton variant="text" height={60} />
          <Grid container spacing={3}>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Skeleton variant="rectangular" height={120} />
              </Grid>
            ))}
          </Grid>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          📊 Executive Dashboard
        </Typography>
        <KPICards metrics={metrics} />
      </Box>
    </Layout>
  );
};

export default Dashboard;