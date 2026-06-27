import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  People as PeopleIcon,
  CheckCircle as CheckCircleIcon,
  TrendingDown as TrendingDownIcon,
  AttachMoney as AttachMoneyIcon,
} from '@mui/icons-material';

interface KPICardsProps {
  metrics: any;
}

const KPICards: React.FC<KPICardsProps> = ({ metrics }) => {
  const cards = [
    {
      title: 'Total Customers',
      value: metrics?.customer_kpis?.total_customers || 0,
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: '#667eea',
    },
    {
      title: 'Active Customers',
      value: metrics?.customer_kpis?.active_customers || 0,
      icon: <CheckCircleIcon sx={{ fontSize: 40 }} />,
      color: '#10b981',
    },
    {
      title: 'Churn Rate',
      value: `${((metrics?.churn_kpis?.churn_rate || 0) * 100).toFixed(1)}%`,
      icon: <TrendingDownIcon sx={{ fontSize: 40 }} />,
      color: '#ef4444',
    },
    {
      title: 'Total Revenue',
      value: `$${(metrics?.revenue_kpis?.total_revenue || 0).toLocaleString()}`,
      icon: <AttachMoneyIcon sx={{ fontSize: 40 }} />,
      color: '#f59e0b',
    },
  ];

  return (
    <Grid container spacing={3}>
      {cards.map((card, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Paper
            sx={{
              p: 3,
              textAlign: 'center',
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              color: 'white',
              borderRadius: 2,
              transition: 'transform 0.3s',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: 6,
              },
            }}
          >
            <Box sx={{ color: card.color, mb: 1 }}>{card.icon}</Box>
            <Typography variant="h4" fontWeight="bold">
              {card.value}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.7 }}>
              {card.title}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};

export default KPICards;