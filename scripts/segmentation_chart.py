import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
from customer_analytics.src.analytics_service import CustomerAnalyticsService

# Load data
df = pd.read_csv("data/raw/customers_cleaned.csv")

# Run segmentation
analytics = CustomerAnalyticsService()
segmented_df = analytics.segment_customers(df)

# Count segments
segment_counts = segmented_df["segment_label"].value_counts()

# Create pie chart
plt.figure(figsize=(8, 6))
colors = ["#2c3e50", "#3498db", "#1abc9c", "#e74c3c"]
plt.pie(segment_counts.values, labels=segment_counts.index, autopct="%1.1f%%", colors=colors, startangle=90)
plt.title("Customer Segmentation Results - 4 Segments Identified", fontsize=14, fontweight="bold")
plt.axis("equal")

# Save the chart
plt.savefig("segmentation_chart.png", dpi=300, bbox_inches="tight")
print("✅ Segmentation chart saved as 'segmentation_chart.png'")
plt.show()
