import React, { useState } from 'react';
import { Typography, Box, Button, Grid, Paper, Alert } from '@mui/material';
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

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          📊 Reports
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
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
          </Grid>

          {report && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Report Summary
                </Typography>
                <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                  {JSON.stringify(report, null, 2)}
                </pre>
              </Paper>
            </Grid>
          )}
        </Grid>
      </Box>
    </Layout>
  );
};

export default Reports;