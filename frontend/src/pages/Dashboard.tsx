import React, { useState, useEffect } from 'react';
import { Typography, Box, Skeleton, Paper } from '@mui/material';
import Layout from '../components/Layout/Layout';
import KPICards from '../components/Dashboard/KPICards';
import { dashboardAPI } from '../api/client';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
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
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Box key={i} sx={{ flex: '1 1 200px', minWidth: '180px' }}>
                <Skeleton variant="rectangular" height={120} />
              </Box>
            ))}
          </Box>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          📊 Executive Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Real-time customer churn analytics and retention insights
        </Typography>

        {/* KPI Cards */}
        <KPICards metrics={metrics} />

        {/* Business Impact Section */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
            💰 Business Impact
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            {/* Revenue at Risk */}
            <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
              <Paper sx={{ p: 2, bgcolor: '#fef2f2', borderLeft: '4px solid #ef4444' }}>
                <Typography variant="body2" color="text.secondary">Revenue at Risk</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#ef4444' }}>
                  ${((metrics?.churn_kpis?.high_risk_customers || 0) * (metrics?.revenue_kpis?.avg_revenue_per_customer || 0)).toLocaleString()}
                </Typography>
              </Paper>
            </Box>

            {/* Potential Savings */}
            <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
              <Paper sx={{ p: 2, bgcolor: '#fefce8', borderLeft: '4px solid #f59e0b' }}>
                <Typography variant="body2" color="text.secondary">Potential Savings</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#f59e0b' }}>
                  ${(((metrics?.churn_kpis?.high_risk_customers || 0) * (metrics?.revenue_kpis?.avg_revenue_per_customer || 0)) * 0.5).toLocaleString()}
                </Typography>
              </Paper>
            </Box>

            {/* New Customers */}
            <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
              <Paper sx={{ p: 2, bgcolor: '#ecfdf5', borderLeft: '4px solid #10b981' }}>
                <Typography variant="body2" color="text.secondary">New Customers (30 days)</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#10b981' }}>
                  {metrics?.customer_kpis?.new_customers || 0}
                </Typography>
              </Paper>
            </Box>

            {/* Revenue Growth */}
            <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
              <Paper sx={{ p: 2, bgcolor: '#eff6ff', borderLeft: '4px solid #3b82f6' }}>
                <Typography variant="body2" color="text.secondary">Revenue Growth</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#3b82f6' }}>
                  {metrics?.revenue_kpis?.revenue_growth !== undefined ? `${(metrics.revenue_kpis.revenue_growth * 100).toFixed(1)}%` : '0%'}
                </Typography>
              </Paper>
            </Box>
          </Box>
        </Box>
      </Box>
    </Layout>
  );
};

export default Dashboard;