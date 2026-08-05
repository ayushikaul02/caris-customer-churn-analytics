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
  Alert,
  CircularProgress,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { reportsAPI } from '../api/client';

const Reports: React.FC = () => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await reportsAPI.getMonthly();
      setReport(response.data);
    } catch (error) {
      console.error('Error generating report:', error);
      setError('Failed to generate report. Please try again.');
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
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Generate and view monthly business reports
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
            {loading ? <CircularProgress size={24} /> : 'Generate Report'}
          </Button>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

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
                        <TableCell align="right">{report.summary?.total_customers || 0}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Active Customers</TableCell>
                        <TableCell align="right">{report.summary?.active_customers || 0}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Churned Customers</TableCell>
                        <TableCell align="right">{report.summary?.churned_customers || 0}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Churn Rate</TableCell>
                        <TableCell align="right">
                          {report.summary?.churn_rate !== undefined ? `${(report.summary.churn_rate * 100).toFixed(1)}%` : '0%'}
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
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </Layout>
  );
};

export default Reports;