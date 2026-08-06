import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardService:
    
    def __init__(self):
        self.templates_path = "./dashboard-service/templates"
        self.static_path = "./dashboard-service/static"
        os.makedirs(self.templates_path, exist_ok=True)
        os.makedirs(self.static_path, exist_ok=True)
        logger.info("DashboardService initialized successfully")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        string_columns = ['status', 'customer_segment', 'gender', 'city', 'state']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
                df[col] = df[col].replace('nan', 'unknown')
        
        numeric_columns = ['total_spent', 'monthly_charge', 'age']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if 'customer_id' in df.columns:
            df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce').fillna(0).astype(int)
        
        if 'join_date' in df.columns:
            df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce')
        
        if 'customer_id' in df.columns:
            df = df.drop_duplicates(subset=['customer_id'], keep='first')
        
        return df
    
    def get_dashboard_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        try:
            logger.info("Generating dashboard metrics...")
            df = self._clean_dataframe(df)
            
            total_customers = len(df)
            active_customers = len(df[df['status'].str.contains('active', case=False, na=False)])
            churned_customers = len(df[df['status'].str.contains('churned', case=False, na=False)])
            
            # NEW: New Customers (last 30 days)
            new_customers = 0
            if 'join_date' in df.columns:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                new_customers = len(df[df['join_date'] > thirty_days_ago])
            
            total_revenue = df['total_spent'].sum() if 'total_spent' in df.columns else 0
            avg_revenue = df['total_spent'].mean() if 'total_spent' in df.columns else 0
            monthly_revenue = df['monthly_charge'].sum() if 'monthly_charge' in df.columns else 0
            
            # NEW: Revenue Growth (using monthly revenue)
            revenue_growth = 0
            if 'monthly_charge' in df.columns:
                # Simulate monthly growth based on join dates
                if 'join_date' in df.columns:
                    df['month'] = df['join_date'].dt.to_period('M')
                    monthly_charges = df.groupby('month')['monthly_charge'].sum()
                    if len(monthly_charges) > 1:
                        revenue_growth = (monthly_charges.iloc[-1] - monthly_charges.iloc[-2]) / monthly_charges.iloc[-2]
            
            churn_rate = churned_customers / total_customers if total_customers > 0 else 0
            retention_rate = active_customers / total_customers if total_customers > 0 else 0
            
            high_risk_count = 0
            if 'risk_level' in df.columns:
                high_risk_count = len(df[df['risk_level'].isin(['high', 'critical'])])
            
            lost_revenue = df[df['status'].str.contains('churned', case=False, na=False)]['total_spent'].sum() if 'total_spent' in df.columns else 0
            
            segment_distribution = {}
            if 'customer_segment' in df.columns:
                segment_distribution = df['customer_segment'].value_counts().to_dict()
            
            status_distribution = {}
            if 'status' in df.columns:
                status_distribution = df['status'].value_counts().to_dict()
            
            metrics = {
                'customer_kpis': {
                    'total_customers': int(total_customers),
                    'active_customers': int(active_customers),
                    'churned_customers': int(churned_customers),
                    'new_customers': int(new_customers),
                    'retention_rate': round(retention_rate, 4),
                },
                'revenue_kpis': {
                    'total_revenue': round(float(total_revenue), 2),
                    'avg_revenue_per_customer': round(float(avg_revenue), 2),
                    'monthly_revenue': round(float(monthly_revenue), 2),
                    'revenue_growth': round(float(revenue_growth), 4),
                },
                'churn_kpis': {
                    'churn_rate': round(churn_rate, 4),
                    'lost_revenue': round(float(lost_revenue), 2),
                    'high_risk_customers': int(high_risk_count),
                },
                'segment_kpis': {
                    'segment_distribution': segment_distribution,
                    'status_distribution': status_distribution,
                    'top_segments': dict(sorted(segment_distribution.items(), key=lambda x: x[1], reverse=True)[:5]) if segment_distribution else {}
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Dashboard metrics generated successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Error generating dashboard metrics: {str(e)}")
            raise

    def create_regional_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        try:
            logger.info("Creating regional dashboard...")
            df = self._clean_dataframe(df)
            
            dashboard = {}
            
            if 'state' in df.columns and 'total_spent' in df.columns:
                state_revenue = df.groupby('state')['total_spent'].sum().sort_values(ascending=False)
                dashboard['revenue_by_state'] = {str(k): round(float(v), 2) for k, v in state_revenue.to_dict().items()}
                dashboard['top_states'] = list(state_revenue.head(5).index)
            
            if 'city' in df.columns and 'total_spent' in df.columns:
                city_revenue = df.groupby('city')['total_spent'].sum().sort_values(ascending=False).head(10)
                dashboard['revenue_by_city'] = {str(k): round(float(v), 2) for k, v in city_revenue.to_dict().items()}
            
            if 'state' in df.columns:
                dashboard['customers_by_state'] = df['state'].value_counts().to_dict()
            
            if 'state' in df.columns and 'status' in df.columns:
                churn_by_state = df.groupby('state')['status'].apply(
                    lambda x: round((x.str.contains('churned', case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard['churn_rate_by_state'] = {str(k): round(float(v), 4) for k, v in churn_by_state.to_dict().items()}
            
            dashboard['timestamp'] = datetime.now().isoformat()
            logger.info("Regional dashboard created successfully")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating regional dashboard: {str(e)}")
            raise