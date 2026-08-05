import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Grid,
  Paper,
  CircularProgress,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { analyticsAPI } from '../api/client';

const Analytics: React.FC = () => {
  const [churnData, setChurnData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await analyticsAPI.getChurn();
        setChurnData(response.data);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          📈 Churn & Revenue Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Analyze churn patterns and revenue metrics across customer segments
        </Typography>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Churn by Segment
              </Typography>
              {churnData?.churn_by_segment ? (
                <Box>
                  {Object.entries(churnData.churn_by_segment).map(([segment, rate]: [string, any]) => (
                    <Box key={segment} sx={{ mb: 2 }}>
                      <Typography variant="body2">{segment}: {(rate * 100).toFixed(1)}%</Typography>
                      <Box sx={{ width: '100%', bgcolor: '#e0e0e0', borderRadius: 1, height: 8 }}>
                        <Box
                          sx={{
                            width: `${Math.min(rate * 100, 100)}%`,
                            bgcolor: rate > 0.2 ? '#ef4444' : rate > 0.1 ? '#f59e0b' : '#10b981',
                            borderRadius: 1,
                            height: 8,
                          }}
                        />
                      </Box>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No churn data available</Typography>
              )}
            </Paper>
          </Grid>

          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Status Distribution
              </Typography>
              {churnData?.status_distribution ? (
                <Box>
                  {Object.entries(churnData.status_distribution).map(([status, count]: [string, any]) => (
                    <Box key={status} sx={{ mb: 1 }}>
                      <Typography variant="body2">{status}: {count}</Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No status data available</Typography>
              )}
            </Paper>
          </Grid>

          <Grid size={{ xs: 12 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Overall Churn Rate
              </Typography>
              {churnData?.overall_churn_rate !== undefined ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: churnData.overall_churn_rate > 0.15 ? '#ef4444' : '#10b981' }}>
                    {(churnData.overall_churn_rate * 100).toFixed(1)}%
                  </Typography>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total customers: {churnData.total_customers || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Churned: {churnData.churned_count || 0}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No overall churn data available</Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};

export default Analytics;