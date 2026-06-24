import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import json
from retention_engine.src.retention_service import RetentionEngine
from customer_analytics.src.analytics_service import CustomerAnalyticsService

# Load data
df = pd.read_csv('data/raw/customers_cleaned.csv')

# Calculate risk scores first (if not already present)
analytics = CustomerAnalyticsService()
df = analytics.calculate_risk_score(df)

# Generate recommendations
engine = RetentionEngine()
recommended_df = engine.generate_recommendations(df)

# Show recommendations for first 5 customers
print("=" * 60)
print("PERSONALIZED RETENTION RECOMMENDATIONS")
print("=" * 60)

for i in range(min(5, len(recommended_df))):
    row = recommended_df.iloc[i]
    rec = row['recommendations']
    print(f"\n📌 Customer: {rec.get('customer_name', 'Unknown')}")
    print(f"   Risk Level: {rec.get('risk_level', 'Unknown')}")
    print(f"   Priority: {rec.get('priority', 'low')}")
    print(f"   Urgency: {rec.get('urgency', 'soon')}")
    print("   Recommendations:")
    for r in rec.get('recommendations', []):
        print(f"     • {r}")
    print("-" * 40)