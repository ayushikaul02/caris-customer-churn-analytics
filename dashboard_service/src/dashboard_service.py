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
    """Enterprise-grade dashboard service for CARIS"""
    
    def __init__(self):
        self.templates_path = "./dashboard-service/templates"
        self.static_path = "./dashboard-service/static"
        os.makedirs(self.templates_path, exist_ok=True)
        os.makedirs(self.static_path, exist_ok=True)
        logger.info("DashboardService initialized successfully")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe for analytics"""
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
        """Get comprehensive dashboard metrics"""
        try:
            logger.info("Generating dashboard metrics...")
            df = self._clean_dataframe(df)
            
            total_customers = len(df)
            active_customers = len(df[df['status'].str.contains('active', case=False, na=False)])
            churned_customers = len(df[df['status'].str.contains('churned', case=False, na=False)])
            
            # New Customers (last 30 days)
            new_customers = 0
            if 'join_date' in df.columns:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                new_customers = len(df[df['join_date'] > thirty_days_ago])
            
            total_revenue = df['total_spent'].sum() if 'total_spent' in df.columns else 0
            avg_revenue = df['total_spent'].mean() if 'total_spent' in df.columns else 0
            monthly_revenue = df['monthly_charge'].sum() if 'monthly_charge' in df.columns else 0
            
            # Revenue Growth
            revenue_growth = 0
            if 'monthly_charge' in df.columns and 'join_date' in df.columns:
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
        """Create regional performance dashboard"""
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

    def create_revenue_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create revenue dashboard data"""
        try:
            logger.info("Creating revenue dashboard...")
            df = self._clean_dataframe(df)
            
            dashboard = {}
            
            if 'customer_segment' in df.columns and 'total_spent' in df.columns:
                segment_revenue = df.groupby('customer_segment')['total_spent'].sum().sort_values(ascending=False)
                dashboard['segment_revenue'] = {str(k): round(float(v), 2) for k, v in segment_revenue.to_dict().items()}
                dashboard['segment_percentage'] = {str(k): round(float(v) / segment_revenue.sum() * 100, 2) for k, v in segment_revenue.to_dict().items()}
            
            if 'total_spent' in df.columns:
                top_customers = df.nlargest(10, 'total_spent')
                dashboard['top_customers'] = [
                    {
                        'customer_id': int(row['customer_id']),
                        'name': row['name'] if 'name' in row else 'Unknown',
                        'total_spent': round(float(row['total_spent']), 2),
                        'segment': row['customer_segment'] if 'customer_segment' in row else 'unknown'
                    }
                    for _, row in top_customers.iterrows()
                ]
            
            if 'total_spent' in df.columns:
                revenue_bins = [0, 100, 500, 1000, 5000, 10000, float('inf')]
                revenue_labels = ['0-100', '101-500', '501-1000', '1001-5000', '5001-10000', '10000+']
                df['revenue_bucket'] = pd.cut(df['total_spent'], bins=revenue_bins, labels=revenue_labels)
                dashboard['revenue_distribution'] = df['revenue_bucket'].value_counts().sort_index().to_dict()
            
            dashboard['summary'] = {
                'total_revenue': round(float(df['total_spent'].sum() if 'total_spent' in df.columns else 0), 2),
                'average_revenue': round(float(df['total_spent'].mean() if 'total_spent' in df.columns else 0), 2),
                'max_revenue': round(float(df['total_spent'].max() if 'total_spent' in df.columns else 0), 2),
                'min_revenue': round(float(df['total_spent'].min() if 'total_spent' in df.columns else 0), 2),
                'median_revenue': round(float(df['total_spent'].median() if 'total_spent' in df.columns else 0), 2),
                'total_monthly_revenue': round(float(df['monthly_charge'].sum() if 'monthly_charge' in df.columns else 0), 2)
            }
            
            dashboard['timestamp'] = datetime.now().isoformat()
            logger.info("Revenue dashboard created successfully")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating revenue dashboard: {str(e)}")
            raise

    def create_customer_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create customer dashboard data"""
        try:
            logger.info("Creating customer dashboard...")
            df = self._clean_dataframe(df)
            
            dashboard = {}
            
            if 'customer_segment' in df.columns:
                dashboard['segment_distribution'] = df['customer_segment'].value_counts().to_dict()
            
            if 'status' in df.columns:
                dashboard['status_distribution'] = df['status'].value_counts().to_dict()
            
            if 'gender' in df.columns:
                dashboard['gender_distribution'] = df['gender'].value_counts().to_dict()
            
            if 'age' in df.columns and df['age'].notna().any():
                age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
                age_labels = ['0-18', '19-25', '26-35', '36-45', '46-55', '56-65', '65+']
                df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
                dashboard['age_distribution'] = df['age_group'].value_counts().sort_index().to_dict()
            
            if 'state' in df.columns:
                dashboard['state_distribution'] = df['state'].value_counts().head(10).to_dict()
            
            if 'city' in df.columns:
                dashboard['city_distribution'] = df['city'].value_counts().head(10).to_dict()
            
            dashboard['summary'] = {
                'total_customers': int(len(df)),
                'active_customers': int(len(df[df['status'].str.contains('active', case=False, na=False)])) if 'status' in df.columns else 0,
                'churned_customers': int(len(df[df['status'].str.contains('churned', case=False, na=False)])) if 'status' in df.columns else 0,
                'retention_rate': round(len(df[df['status'].str.contains('active', case=False, na=False)]) / len(df) if len(df) > 0 else 0, 4),
                'average_tenure_days': round(float(df['join_date'].apply(lambda x: (datetime.now() - x).days).mean() if 'join_date' in df.columns else 0), 0)
            }
            
            dashboard['timestamp'] = datetime.now().isoformat()
            logger.info("Customer dashboard created successfully")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating customer dashboard: {str(e)}")
            raise

    def create_churn_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create churn dashboard data"""
        try:
            logger.info("Creating churn dashboard...")
            df = self._clean_dataframe(df)
            
            dashboard = {}
            
            if 'customer_segment' in df.columns and 'status' in df.columns:
                churn_by_segment = df.groupby('customer_segment')['status'].apply(
                    lambda x: round((x.str.contains('churned', case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard['churn_by_segment'] = churn_by_segment.to_dict()
            
            if 'risk_level' in df.columns:
                dashboard['risk_distribution'] = df['risk_level'].value_counts().to_dict()
            
            if 'join_date' in df.columns and 'status' in df.columns:
                df['tenure_days'] = (datetime.now() - df['join_date']).dt.days
                tenure_bins = [0, 30, 90, 180, 365, 730, float('inf')]
                tenure_labels = ['0-30', '31-90', '91-180', '181-365', '366-730', '730+']
                df['tenure_group'] = pd.cut(df['tenure_days'], bins=tenure_bins, labels=tenure_labels)
                
                churn_by_tenure = df.groupby('tenure_group')['status'].apply(
                    lambda x: round((x.str.contains('churned', case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard['churn_by_tenure'] = churn_by_tenure.to_dict()
            
            if 'monthly_charge' in df.columns and 'status' in df.columns:
                charge_bins = [0, 50, 100, 150, 200, float('inf')]
                charge_labels = ['0-50', '51-100', '101-150', '151-200', '200+']
                df['charge_group'] = pd.cut(df['monthly_charge'], bins=charge_bins, labels=charge_labels)
                
                churn_by_charge = df.groupby('charge_group')['status'].apply(
                    lambda x: round((x.str.contains('churned', case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard['churn_by_monthly_charge'] = churn_by_charge.to_dict()
            
            churned = len(df[df['status'].str.contains('churned', case=False, na=False)]) if 'status' in df.columns else 0
            total = len(df)
            
            dashboard['summary'] = {
                'overall_churn_rate': round(churned / total if total > 0 else 0, 4),
                'churned_customers': int(churned),
                'total_customers': int(total),
                'lost_revenue': round(float(df[df['status'].str.contains('churned', case=False, na=False)]['total_spent'].sum() if 'total_spent' in df.columns else 0), 2),
                'high_risk_customers': int(len(df[df['risk_level'].isin(['high', 'critical'])]) if 'risk_level' in df.columns else 0),
            }
            
            dashboard['timestamp'] = datetime.now().isoformat()
            logger.info("Churn dashboard created successfully")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating churn dashboard: {str(e)}")
            raise

    def get_support_kpis(self, df: pd.DataFrame, tickets_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate support KPIs"""
        try:
            logger.info("Calculating support KPIs...")
            
            if tickets_df.empty:
                return {
                    "ticket_resolution_time": 0,
                    "customer_satisfaction": 0,
                    "open_tickets": 0,
                    "total_tickets": 0
                }
            
            # Clean tickets data
            tickets_df = tickets_df.copy()
            tickets_df['created_date'] = pd.to_datetime(tickets_df['created_date'], errors='coerce')
            tickets_df['resolved_date'] = pd.to_datetime(tickets_df['resolved_date'], errors='coerce')
            
            # Average resolution time (hours)
            tickets_df['resolution_time'] = (tickets_df['resolved_date'] - tickets_df['created_date']).dt.total_seconds() / 3600
            avg_resolution = tickets_df['resolution_time'].mean()
            
            # Average satisfaction score
            avg_satisfaction = tickets_df['satisfaction_score'].mean() if 'satisfaction_score' in tickets_df.columns else 0
            
            # Open tickets
            open_tickets = len(tickets_df[tickets_df['status'] == 'open'])
            
            kpis = {
                "ticket_resolution_time": round(avg_resolution, 2) if not pd.isna(avg_resolution) else 0,
                "customer_satisfaction": round(avg_satisfaction, 2) if not pd.isna(avg_satisfaction) else 0,
                "open_tickets": open_tickets,
                "total_tickets": len(tickets_df)
            }
            
            logger.info("Support KPIs calculated successfully")
            return kpis
            
        except Exception as e:
            logger.error(f"Error calculating support KPIs: {str(e)}")
            return {
                "ticket_resolution_time": 0,
                "customer_satisfaction": 0,
                "open_tickets": 0,
                "total_tickets": 0,
                "error": str(e)
            }


# Example usage
if __name__ == "__main__":
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        tickets_df = pd.read_csv('./data/raw/support_tickets.csv')
        
        dashboard = DashboardService()
        
        metrics = dashboard.get_dashboard_metrics(df)
        regional = dashboard.create_regional_dashboard(df)
        revenue = dashboard.create_revenue_dashboard(df)
        customer = dashboard.create_customer_dashboard(df)
        churn = dashboard.create_churn_dashboard(df)
        support = dashboard.get_support_kpis(df, tickets_df)
        
        print("=" * 60)
        print("✅ All dashboards generated successfully!")
        print("=" * 60)
        print(f"📊 Total Customers: {metrics['customer_kpis']['total_customers']}")
        print(f"💰 Total Revenue: ${metrics['revenue_kpis']['total_revenue']:,.2f}")
        print(f"📈 Churn Rate: {metrics['churn_kpis']['churn_rate']:.2%}")
        print(f"🛠️ Support KPIs: {support}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")