import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
} from '@mui/material';
import Layout from '../components/Layout/Layout';
import { customersAPI } from '../api/client';

const Customers: React.FC = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const response = await customersAPI.getAll();
        setCustomers(response.data);
      } catch (error) {
        console.error('Error fetching customers:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: '#10b981',
      churned: '#ef4444',
      inactive: '#f59e0b',
      suspended: '#8b5cf6',
    };
    return colors[status] || '#6b7280';
  };

  const filteredCustomers = customers.filter((c: any) => {
    const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
                        c.email.toLowerCase().includes(search.toLowerCase());
    const matchSegment = segmentFilter === 'All' || c.customer_segment === segmentFilter;
    const matchStatus = statusFilter === 'All' || c.status === statusFilter;
    return matchSearch && matchSegment && matchStatus;
  });

  const uniqueSegments = ['All', ...new Set(customers.map((c: any) => c.customer_segment))];
  const uniqueStatuses = ['All', ...new Set(customers.map((c: any) => c.status))];

  if (loading) return <Layout><Typography>Loading...</Typography></Layout>;

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          👥 Customer Management
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <TextField
            label="Search Customers"
            variant="outlined"
            size="small"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ minWidth: 200 }}
          />
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Segment</InputLabel>
            <Select value={segmentFilter} onChange={(e) => setSegmentFilter(e.target.value)}>
              {uniqueSegments.map((seg) => (
                <MenuItem key={seg} value={seg}>{seg}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              {uniqueStatuses.map((status) => (
                <MenuItem key={status} value={status}>{status}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="body2" sx={{ alignSelf: 'center', ml: 'auto' }}>
            Showing {filteredCustomers.length} customers
          </Typography>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Segment</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Total Spent</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCustomers.slice(0, 100).map((c: any) => (
                <TableRow key={c.customer_id}>
                  <TableCell>{c.customer_id}</TableCell>
                  <TableCell>{c.name}</TableCell>
                  <TableCell>{c.email}</TableCell>
                  <TableCell>
                    <Chip label={c.customer_segment} size="small" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={c.status}
                      size="small"
                      sx={{ bgcolor: getStatusColor(c.status), color: 'white' }}
                    />
                  </TableCell>
                  <TableCell align="right">${c.total_spent?.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Layout>
  );
};

export default Customers;