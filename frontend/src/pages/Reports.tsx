import React, { useState } from 'react';
import {
  Typography,
  Box,
  Button,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { reportsAPI } from '../api/client';

const Reports: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleExport = async (type: 'excel' | 'pdf') => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      let response;
      if (type === 'excel') {
        response = await reportsAPI.getExcel();
        alert('Excel report generated! Check the server logs for the file location.');
      } else {
        response = await reportsAPI.getPDF();
        // Create download link for PDF
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `CARIS_Report_${new Date().toISOString().slice(0, 10)}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
      setSuccess(true);
    } catch (err) {
      setError('Failed to generate report. Please try again.');
      console.error(err);
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
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Generate and download business reports in multiple formats.
        </Typography>

        <Paper sx={{ p: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            onClick={() => handleExport('excel')}
            disabled={loading}
            sx={{ minWidth: 150 }}
          >
            {loading ? <CircularProgress size={24} /> : '📥 Export Excel'}
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => handleExport('pdf')}
            disabled={loading}
            sx={{ minWidth: 150 }}
          >
            {loading ? <CircularProgress size={24} /> : '📄 Export PDF'}
          </Button>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Report generated successfully!
          </Alert>
        )}
      </Box>
    </Layout>
  );
};

export default Reports;