import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import json
from dashboard_service.src.dashboard_service import DashboardService

# Load data
df = pd.read_csv('data/raw/customers_cleaned.csv')

# Initialize dashboard service
dashboard = DashboardService()

# Get all metrics
metrics = dashboard.get_dashboard_metrics(df)

# Print formatted output
print("=" * 60)
print("📊 CARIS DASHBOARD METRICS")
print("=" * 60)

print("\n👥 CUSTOMER KPIs:")
print(f"   Total Customers     : {metrics['customer_kpis']['total_customers']}")
print(f"   Active Customers    : {metrics['customer_kpis']['active_customers']}")
print(f"   Churned Customers   : {metrics['customer_kpis']['churned_customers']}")
print(f"   Retention Rate      : {metrics['customer_kpis']['retention_rate']:.2%}")

print("\n💰 REVENUE KPIs:")
print(f"   Total Revenue       : ₹{metrics['revenue_kpis']['total_revenue']:,.2f}")
print(f"   Avg Revenue/Customer: ₹{metrics['revenue_kpis']['avg_revenue_per_customer']:,.2f}")
print(f"   Monthly Revenue     : ₹{metrics['revenue_kpis']['monthly_revenue']:,.2f}")

print("\n📉 CHURN KPIs:")
print(f"   Churn Rate          : {metrics['churn_kpis']['churn_rate']:.2%}")
print(f"   Lost Revenue        : ₹{metrics['churn_kpis']['lost_revenue']:,.2f}")
print(f"   High-Risk Customers : {metrics['churn_kpis']['high_risk_customers']}")

print("\n📊 SEGMENT KPIs:")
for segment, count in metrics['segment_kpis']['segment_distribution'].items():
    print(f"   {segment.capitalize():12} : {count}")

print("\n" + "=" * 60)
print("✅ Dashboard metrics generated successfully!")