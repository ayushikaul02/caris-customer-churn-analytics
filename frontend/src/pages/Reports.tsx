import React, { useState } from 'react';
import {
  Typography,
  Box,
  Button,
  Paper,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { reportsAPI } from '../api/client';

const Reports: React.FC = () => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generateReport = async () => {
    setLoading(true);
    try {
      const response = await reportsAPI.getMonthly();
      setReport(response.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          📊 Reports
        </Typography>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Monthly Business Report
          </Typography>
          <Button
            variant="contained"
            onClick={generateReport}
            disabled={loading}
            sx={{ mt: 1 }}
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </Button>
        </Paper>

        {report && (
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {report.report_type || 'Monthly Business Report'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Period: {report.period} | Generated: {new Date(report.generated_date).toLocaleString()}
              </Typography>

              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Executive Summary
                </Typography>

                {/* KPI Cards using Box with flexbox */}
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
                  <Box sx={{ flex: 1, minWidth: '150px' }}>
                    <Card sx={{ bgcolor: '#f0f4ff' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          Total Customers
                        </Typography>
                        <Typography variant="h4">
                          {report.summary?.total_customers || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                  <Box sx={{ flex: 1, minWidth: '150px' }}>
                    <Card sx={{ bgcolor: '#e8f5e9' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          Active Customers
                        </Typography>
                        <Typography variant="h4">
                          {report.summary?.active_customers || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                  <Box sx={{ flex: 1, minWidth: '150px' }}>
                    <Card sx={{ bgcolor: '#fce4ec' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          Churned Customers
                        </Typography>
                        <Typography variant="h4">
                          {report.summary?.churned_customers || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                  <Box sx={{ flex: 1, minWidth: '150px' }}>
                    <Card sx={{ bgcolor: '#fff3e0' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          Total Revenue
                        </Typography>
                        <Typography variant="h4">
                          {formatCurrency(report.summary?.total_revenue || 0)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                </Box>

                {/* Details Table */}
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Detailed Metrics
                </Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Metric</strong></TableCell>
                        <TableCell align="right"><strong>Value</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Total Customers</TableCell>
                        <TableCell align="right">{report.summary?.total_customers}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Active Customers</TableCell>
                        <TableCell align="right">{report.summary?.active_customers}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Churned Customers</TableCell>
                        <TableCell align="right">{report.summary?.churned_customers}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Churn Rate</TableCell>
                        <TableCell align="right">
                          {report.summary?.churn_rate ? `${(report.summary.churn_rate * 100).toFixed(1)}%` : '0%'}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Total Revenue</TableCell>
                        <TableCell align="right">{formatCurrency(report.summary?.total_revenue || 0)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Average Customer Value</TableCell>
                        <TableCell align="right">{formatCurrency(report.summary?.avg_customer_value || 0)}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Recommendations */}
                {report.recommendations && report.recommendations.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Recommendations
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {report.recommendations.map((rec: any, index: number) => (
                        <Paper key={index} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                          <Typography variant="body2">
                            <strong>Priority:</strong> {rec.priority}
                          </Typography>
                          <Typography variant="body2">
                            <strong>Action:</strong> {rec.action}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Impact: {rec.expected_impact}
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </Layout>
  );
};

export default Reports;