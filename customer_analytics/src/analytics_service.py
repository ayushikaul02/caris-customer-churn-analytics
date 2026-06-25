import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerAnalyticsService:
    """Enterprise-grade customer analytics service"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.cluster_labels = {}
        logger.info("CustomerAnalyticsService initialized")

    def segment_customers(self, df: pd.DataFrame, n_segments: int = 4) -> pd.DataFrame:
        """Perform customer segmentation using K-Means"""
        logger.info(f"Starting customer segmentation with {n_segments} segments...")
        df = df.copy()

        # Select features for segmentation (only use columns that exist)
        features = ["total_spent", "monthly_charge"]

        # Add age if it exists
        if "age" in df.columns:
            features.append("age")

        # Add tenure_days if it exists
        if "tenure_days" in df.columns:
            features.append("tenure_days")

        # Filter to available features
        available_features = [f for f in features if f in df.columns]

        if not available_features:
            logger.warning("Required features not available for segmentation")
            df["segment_label"] = "Standard"
            return df

        # Prepare data
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)

        # Perform K-Means clustering
        kmeans = KMeans(n_clusters=n_segments, random_state=42, n_init=10)
        df["customer_segment_cluster"] = kmeans.fit_predict(X_scaled)
        self.models["kmeans"] = kmeans

        # Assign segment labels based on total_spent
        if "total_spent" in df.columns:
            segment_avg_spend = df.groupby("customer_segment_cluster")["total_spent"].mean()
            median_spend = segment_avg_spend.median()

            segment_labels = []
            for cluster in df["customer_segment_cluster"].unique():
                avg_spend = segment_avg_spend[cluster]
                if avg_spend > segment_avg_spend.quantile(0.75):
                    label = "Premium"
                elif avg_spend > median_spend:
                    label = "High Value"
                else:
                    label = "Standard"
                segment_labels.append(label)

            label_map = dict(zip(df["customer_segment_cluster"].unique(), segment_labels))
            df["segment_label"] = df["customer_segment_cluster"].map(label_map)
        else:
            df["segment_label"] = "Standard"

        logger.info(f"✅ Segmentation completed. Segments: {df['segment_label'].unique().tolist()}")
        return df

    def analyze_churn(self, df: pd.DataFrame) -> dict:
        """Analyze customer churn patterns"""
        logger.info("Analyzing churn patterns...")

        # Clean data
        if "status" in df.columns:
            df["status"] = df["status"].astype(str).str.strip().str.lower()

        churn_analysis = {}

        # Overall churn rate
        churned = len(df[df["status"] == "churned"])
        total = len(df)
        churn_analysis["overall_churn_rate"] = round(churned / total if total > 0 else 0, 4)
        churn_analysis["churned_count"] = int(churned)
        churn_analysis["total_customers"] = int(total)

        # Churn by segment
        if "customer_segment" in df.columns:
            df["customer_segment"] = df["customer_segment"].astype(str).str.strip().str.lower()
            segment_churn = (
                df.groupby("customer_segment")["status"]
                .apply(lambda x: round((x == "churned").sum() / len(x) if len(x) > 0 else 0, 4))
                .to_dict()
            )
            churn_analysis["churn_by_segment"] = segment_churn

        # Churn by segment label
        if "segment_label" in df.columns:
            segment_label_churn = (
                df.groupby("segment_label")["status"]
                .apply(lambda x: round((x == "churned").sum() / len(x) if len(x) > 0 else 0, 4))
                .to_dict()
            )
            churn_analysis["churn_by_segment_label"] = segment_label_churn

        # Status distribution
        churn_analysis["status_distribution"] = df["status"].value_counts().to_dict()

        logger.info("✅ Churn analysis completed")
        return churn_analysis

    def analyze_revenue(self, df: pd.DataFrame) -> dict:
        """Analyze revenue metrics"""
        logger.info("Analyzing revenue metrics...")

        revenue_analysis = {}

        # Clean data
        if "total_spent" in df.columns:
            df["total_spent"] = pd.to_numeric(df["total_spent"], errors="coerce").fillna(0)

        # Basic revenue metrics
        revenue_analysis["total_revenue"] = round(float(df["total_spent"].sum()), 2)
        revenue_analysis["average_revenue"] = round(float(df["total_spent"].mean()), 2)
        revenue_analysis["median_revenue"] = round(float(df["total_spent"].median()), 2)
        revenue_analysis["max_revenue"] = round(float(df["total_spent"].max()), 2)
        revenue_analysis["min_revenue"] = round(float(df["total_spent"].min()), 2)

        # Revenue by segment
        if "customer_segment" in df.columns:
            segment_revenue = df.groupby("customer_segment")["total_spent"].sum().to_dict()
            revenue_analysis["revenue_by_segment"] = {k: round(float(v), 2) for k, v in segment_revenue.items()}

        # Top customers
        top_customers = df.nlargest(10, "total_spent")
        revenue_analysis["top_customers"] = [
            {
                "customer_id": int(row["customer_id"]),
                "name": row["name"] if "name" in row else "Unknown",
                "total_spent": round(float(row["total_spent"]), 2),
                "segment": row["customer_segment"] if "customer_segment" in row else "unknown",
            }
            for _, row in top_customers.iterrows()
        ]

        logger.info("✅ Revenue analysis completed")
        return revenue_analysis

    def calculate_risk_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate churn risk score for each customer"""
        logger.info("Calculating churn risk scores...")
        df = df.copy()

        # Risk factors with weights
        risk_factors = []

        # 1. Status based risk
        if "status" in df.columns:
            status_risk = {"active": 0.1, "inactive": 0.4, "suspended": 0.7, "churned": 1.0}
            df["status_risk"] = df["status"].map(status_risk).fillna(0.5)
            risk_factors.append(("status_risk", 0.3))

        # 2. Tenure risk
        if "tenure_days" in df.columns:
            df["tenure_risk"] = 1 / (df["tenure_days"] / 365 + 1)
            risk_factors.append(("tenure_risk", 0.25))

        # 3. Engagement risk
        if "total_spent" in df.columns and "tenure_days" in df.columns:
            df["avg_monthly_spend"] = df["total_spent"] / (df["tenure_days"] / 30 + 1)
            df["engagement_risk"] = 1 / (df["avg_monthly_spend"] / 100 + 1)
            risk_factors.append(("engagement_risk", 0.2))

        # 4. Monthly charge risk
        if "monthly_charge" in df.columns:
            df["charge_risk"] = df["monthly_charge"] / 200
            risk_factors.append(("charge_risk", 0.15))

        # 5. Age risk
        if "age" in df.columns:
            df["age_risk"] = df["age"] / 100
            risk_factors.append(("age_risk", 0.1))

        # Calculate weighted risk score
        if risk_factors:
            df["churn_risk_score"] = sum(df[factor] * weight for factor, weight in risk_factors)
            df["churn_risk_score"] = df["churn_risk_score"].clip(0, 1)

        # Categorize risk levels
        df["risk_level"] = pd.cut(
            df["churn_risk_score"],
            bins=[-0.01, 0.2, 0.4, 0.6, 0.8, 1.01],
            labels=["Very Low", "Low", "Medium", "High", "Critical"],
        )

        logger.info(f"✅ Risk scores calculated for {len(df)} customers")
        return df
