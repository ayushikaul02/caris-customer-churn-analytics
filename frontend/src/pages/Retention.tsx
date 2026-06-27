import React, { useState, useEffect } from 'react';
import { Typography, Box, Paper, Chip } from '@mui/material';
import Layout from '../components/Layout/Layout';
import { retentionAPI } from '../api/client';

const Retention: React.FC = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await retentionAPI.getRecommendations();
        setRecommendations(response.data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getRiskColor = (risk: string) => {
    const colors: Record<string, string> = {
      critical: '#ef4444',
      high: '#ef4444',
      medium: '#f59e0b',
      low: '#10b981',
    };
    return colors[risk.toLowerCase()] || '#6b7280';
  };

  if (loading) return <Layout><Typography>Loading...</Typography></Layout>;

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          🎯 Retention Recommendations
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {recommendations.slice(0, 10).map((rec: any, index) => (
            <Paper
              key={index}
              sx={{
                p: 2,
                borderLeft: `4px solid ${getRiskColor(rec.risk_level)}`,
                bgcolor: rec.risk_level === 'Critical' || rec.risk_level === 'High' ? '#fef2f2' : '#f8fafc',
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {rec.customer_name}
                </Typography>
                <Chip
                  label={rec.risk_level}
                  size="small"
                  sx={{ bgcolor: getRiskColor(rec.risk_level), color: 'white' }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {rec.recommendations?.join(' • ')}
              </Typography>
            </Paper>
          ))}
        </Box>
      </Box>
    </Layout>
  );
};

export default Retention;