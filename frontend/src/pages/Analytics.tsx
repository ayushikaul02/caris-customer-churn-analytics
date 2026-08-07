import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  CircularProgress,
  Card,
  CardContent,
  Slider,
  Button,
  Alert,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { analyticsAPI, retentionAPI } from '../api/client';

const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [clvData, setClvData] = useState<any[]>([]);
  const [impactData, setImpactData] = useState<any>(null);
  const [discount, setDiscount] = useState<number>(10);
  const [whatIfResult, setWhatIfResult] = useState<any>(null);
  const [whatIfLoading, setWhatIfLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clvRes, impactRes] = await Promise.all([
          analyticsAPI.getCLV(),
          analyticsAPI.getRevenueImpact(),
        ]);
        setClvData(clvRes.data || []);
        setImpactData(impactRes.data);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleWhatIf = async () => {
    setWhatIfLoading(true);
    try {
      const res = await retentionAPI.getWhatIf(discount);
      setWhatIfResult(res.data);
    } catch (error) {
      console.error('What-If error:', error);
    } finally {
      setWhatIfLoading(false);
    }
  };

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
          📈 Advanced Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Customer Lifetime Value, Revenue Impact, and Retention Simulation
        </Typography>

        {/* Revenue Impact Cards */}
        <Typography variant="h6" gutterBottom>
          💰 Revenue Impact
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
          <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
            <Card sx={{ bgcolor: '#fef2f2', borderLeft: '4px solid #ef4444' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">Revenue at Risk</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#ef4444' }}>
                  ${impactData?.revenue_at_risk?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
            <Card sx={{ bgcolor: '#fefce8', borderLeft: '4px solid #f59e0b' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">Potential Savings</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#f59e0b' }}>
                  ${impactData?.potential_savings?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
            <Card sx={{ bgcolor: '#ecfdf5', borderLeft: '4px solid #10b981' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">Retention ROI</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#10b981' }}>
                  {impactData?.retention_roi || 0}x
                </Typography>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 200px', minWidth: '180px' }}>
            <Card sx={{ bgcolor: '#eff6ff', borderLeft: '4px solid #3b82f6' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">High-Risk Customers</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#3b82f6' }}>
                  {impactData?.high_risk_count || 0}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* CLV Table */}
        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            💎 Customer Lifetime Value (CLV)
          </Typography>
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Customer ID</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>CLV</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Category</th>
                </tr>
              </thead>
              <tbody>
                {clvData.slice(0, 10).map((c: any) => (
                  <tr key={c.customer_id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px' }}>{c.customer_id}</td>
                    <td style={{ padding: '8px' }}>${c.clv?.toFixed(2)}</td>
                    <td style={{ padding: '8px' }}>
                      <strong>{c.clv_category}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        </Paper>

        {/* What-If Simulator */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            🎯 What-If Retention Simulator
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Simulate the impact of offering a discount to all customers.
          </Typography>

          <Box sx={{ width: '100%', maxWidth: 400 }}>
            <Typography>
              Discount Offer: <strong>{discount}%</strong>
            </Typography>
            <Slider
              value={discount}
              onChange={(_, v) => setDiscount(v as number)}
              min={0}
              max={50}
              step={1}
              valueLabelDisplay="auto"
            />
          </Box>

          <Button
            variant="contained"
            onClick={handleWhatIf}
            disabled={whatIfLoading}
            sx={{ mt: 2 }}
          >
            {whatIfLoading ? <CircularProgress size={24} /> : 'Simulate Impact'}
          </Button>

          {whatIfResult && (
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                📊 Simulation Results
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                <Typography variant="body2">
                  <strong>Current Churn:</strong> {whatIfResult.current_churn_rate}%
                </Typography>
                <Typography variant="body2">
                  <strong>Predicted Churn:</strong> {whatIfResult.predicted_churn_rate}%
                </Typography>
                <Typography variant="body2">
                  <strong>Customers Saved:</strong> {whatIfResult.customers_saved}
                </Typography>
                <Typography variant="body2">
                  <strong>Revenue Saved:</strong> ${whatIfResult.revenue_saved?.toLocaleString()}
                </Typography>
              </Box>
            </Alert>
          )}
        </Paper>
      </Box>
    </Layout>
  );
};

export default Analytics;