import React, { useState, useEffect } from 'react';
import { Typography, Box, Grid, Paper, Card, CardContent } from '@mui/material';
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
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Layout><Typography>Loading...</Typography></Layout>;

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          📈 Churn & Revenue Analytics
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Churn by Segment
              </Typography>
              {churnData?.churn_by_segment && (
                <Box>
                  {Object.entries(churnData.churn_by_segment).map(([segment, rate]: [string, any]) => (
                    <Box key={segment} sx={{ mb: 1 }}>
                      <Typography variant="body2">{segment}: {(rate * 100).toFixed(1)}%</Typography>
                      <Box sx={{ width: '100%', bgcolor: '#e0e0e0', borderRadius: 1, height: 8 }}>
                        <Box
                          sx={{
                            width: `${rate * 100}%`,
                            bgcolor: rate > 0.2 ? '#ef4444' : rate > 0.1 ? '#f59e0b' : '#10b981',
                            borderRadius: 1,
                            height: 8,
                          }}
                        />
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Status Distribution
              </Typography>
              {churnData?.status_distribution && (
                <Box>
                  {Object.entries(churnData.status_distribution).map(([status, count]: [string, any]) => (
                    <Box key={status} sx={{ mb: 1 }}>
                      <Typography variant="body2">{status}: {count}</Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};

export default Analytics;