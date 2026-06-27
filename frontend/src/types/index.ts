export interface User {
  username: string;
  role: 'admin' | 'analyst' | 'manager';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: string;
}

export interface CustomerKPI {
  total_customers: number;
  active_customers: number;
  churned_customers: number;
  retention_rate: number;
}

export interface RevenueKPI {
  total_revenue: number;
  avg_revenue_per_customer: number;
  monthly_revenue: number;
}

export interface ChurnKPI {
  churn_rate: number;
  lost_revenue: number;
  high_risk_customers: number;
}

export interface DashboardMetrics {
  customer_kpis: CustomerKPI;
  revenue_kpis: RevenueKPI;
  churn_kpis: ChurnKPI;
  segment_kpis: {
    segment_distribution: Record<string, number>;
    status_distribution: Record<string, number>;
  };
}

export interface Customer {
  customer_id: number;
  name: string;
  email: string;
  customer_segment: string;
  status: string;
  total_spent: number;
}

export interface Recommendation {
  customer_id: number;
  customer_name: string;
  risk_level: string;
  recommendations: string[];
  priority: string;
}