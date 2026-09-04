import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { dashboardAPI } from '../api/client';

const Regional: React.FC = () => {
  const [regionalData, setRegionalData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardAPI.getRegional();
        setRegionalData(response.data);
      } catch (error) {
        console.error('Error fetching regional data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '400px',
          }}
        >
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  const topStates = regionalData?.top_states || [];
  const revenueByState = regionalData?.revenue_by_state || {};
  const customersByState = regionalData?.customers_by_state || {};
  const churnByState = regionalData?.churn_rate_by_state || {};

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          🌍 Regional Performance
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Performance metrics by state and city
        </Typography>

        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 3,
            mb: 4,
          }}
        >
          {/* Top Performing States */}
          <Box sx={{ flex: '1 1 300px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🏆 Top Performing States
                </Typography>

                {topStates.map((state: string, index: number) => (
                  <Box
                    key={state}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">
                      {index + 1}. {state}
                    </Typography>

                    <Typography
                      variant="body2"
                      sx={{ fontWeight: 'bold' }}
                    >
                      ${revenueByState[state]?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Box>

          {/* State-wise Summary */}
          <Box sx={{ flex: '1 1 300px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📊 State-wise Summary
                </Typography>

                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>
                          <strong>State</strong>
                        </TableCell>

                        <TableCell align="right">
                          <strong>Customers</strong>
                        </TableCell>

                        <TableCell align="right">
                          <strong>Churn Rate</strong>
                        </TableCell>
                      </TableRow>
                    </TableHead>

                    <TableBody>
                      {Object.keys(customersByState)
                        .slice(0, 10)
                        .map((state) => (
                          <TableRow key={state}>
                            <TableCell>{state}</TableCell>

                            <TableCell align="right">
                              {customersByState[state]}
                            </TableCell>

                            <TableCell align="right">
                              {churnByState[state] !== undefined
                                ? `${(churnByState[state] * 100).toFixed(1)}%`
                                : 'N/A'}
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>
    </Layout>
  );
};

export default Regional;