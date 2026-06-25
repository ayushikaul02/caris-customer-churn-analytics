import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import logging
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardService:
    """
    Enterprise-grade Dashboard Service for CARIS System
    Provides comprehensive KPI metrics and dashboard data
    """

    def __init__(self):
        """Initialize dashboard service with required paths"""
        self.templates_path = "./dashboard-service/templates"
        self.static_path = "./dashboard-service/static"
        os.makedirs(self.templates_path, exist_ok=True)
        os.makedirs(self.static_path, exist_ok=True)
        logger.info("DashboardService initialized successfully")

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare dataframe for analytics

        Args:
            df: Raw pandas DataFrame

        Returns:
            Cleaned pandas DataFrame
        """
        df = df.copy()

        # Clean string columns
        string_columns = ["status", "customer_segment", "gender", "city", "state"]
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
                df[col] = df[col].replace("nan", "unknown")

        # Clean numeric columns
        numeric_columns = ["total_spent", "monthly_charge", "age"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Clean customer_id
        if "customer_id" in df.columns:
            df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").fillna(0).astype(int)

        # Clean names
        if "name" in df.columns:
            df["name"] = df["name"].astype(str).str.strip()
            # Fix emails in name field
            mask = df["name"].str.contains("@", na=False)
            if mask.any():
                df.loc[mask, "name"] = df.loc[mask, "email"].str.split("@").str[0]

        # Handle join_date
        if "join_date" in df.columns:
            df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")

        # Remove duplicates
        if "customer_id" in df.columns:
            df = df.drop_duplicates(subset=["customer_id"], keep="first")

        return df

    def _calculate_retention_rate(self, df: pd.DataFrame) -> float:
        """
        Calculate customer retention rate

        Args:
            df: Customer DataFrame

        Returns:
            Retention rate as float
        """
        if "status" not in df.columns or len(df) == 0:
            return 0.0

        active_count = len(df[df["status"].str.contains("active", case=False, na=False)])
        total_count = len(df)

        return round(active_count / total_count if total_count > 0 else 0, 4)

    def _calculate_churn_rate(self, df: pd.DataFrame) -> float:
        """
        Calculate churn rate

        Args:
            df: Customer DataFrame

        Returns:
            Churn rate as float
        """
        if "status" not in df.columns or len(df) == 0:
            return 0.0

        churned_count = len(df[df["status"].str.contains("churned", case=False, na=False)])
        total_count = len(df)

        return round(churned_count / total_count if total_count > 0 else 0, 4)

    def _calculate_growth_rate(self, df: pd.DataFrame, period: str = "monthly") -> float:
        """
        Calculate growth rate for a given period

        Args:
            df: Customer DataFrame
            period: 'monthly', 'quarterly', 'yearly'

        Returns:
            Growth rate as float
        """
        if "join_date" not in df.columns or len(df) < 2:
            return 0.0

        # Group by period
        if period == "monthly":
            df["period"] = df["join_date"].dt.to_period("M")
        elif period == "quarterly":
            df["period"] = df["join_date"].dt.to_period("Q")
        else:
            df["period"] = df["join_date"].dt.to_period("Y")

        # Count customers per period
        period_counts = df.groupby("period").size().sort_index()

        if len(period_counts) < 2:
            return 0.0

        # Calculate growth rate
        latest = period_counts.iloc[-1]
        previous = period_counts.iloc[-2]

        return round((latest - previous) / previous if previous > 0 else 0, 4)

    def get_dashboard_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics

        Args:
            df: Raw customer DataFrame

        Returns:
            Dictionary with all dashboard metrics
        """
        try:
            logger.info("Generating dashboard metrics...")

            # Clean data
            df = self._clean_dataframe(df)

            # Basic counts
            total_customers = len(df)
            active_customers = len(df[df["status"].str.contains("active", case=False, na=False)])
            churned_customers = len(df[df["status"].str.contains("churned", case=False, na=False)])
            new_customers = len(df[df["join_date"] > datetime.now() - timedelta(days=30)]) if "join_date" in df.columns else 0

            # Revenue metrics
            total_revenue = df["total_spent"].sum() if "total_spent" in df.columns else 0
            avg_revenue = df["total_spent"].mean() if "total_spent" in df.columns else 0
            monthly_revenue = df["monthly_charge"].sum() if "monthly_charge" in df.columns else 0

            # Churn metrics
            churn_rate = self._calculate_churn_rate(df)
            retention_rate = self._calculate_retention_rate(df)
            lost_revenue = (
                df[df["status"].str.contains("churned", case=False, na=False)]["total_spent"].sum()
                if "total_spent" in df.columns
                else 0
            )

            # Risk metrics
            high_risk_count = 0
            if "risk_level" in df.columns:
                high_risk_count = len(df[df["risk_level"].isin(["high", "critical"])])

            # Growth metrics
            growth_rate = self._calculate_growth_rate(df)

            # Segment distribution
            segment_distribution = {}
            if "customer_segment" in df.columns:
                segment_distribution = df["customer_segment"].value_counts().to_dict()

            # Status distribution
            status_distribution = {}
            if "status" in df.columns:
                status_distribution = df["status"].value_counts().to_dict()

            metrics = {
                "customer_kpis": {
                    "total_customers": int(total_customers),
                    "active_customers": int(active_customers),
                    "churned_customers": int(churned_customers),
                    "new_customers": int(new_customers),
                    "retention_rate": retention_rate,
                    "growth_rate": growth_rate,
                },
                "revenue_kpis": {
                    "total_revenue": round(float(total_revenue), 2),
                    "avg_revenue_per_customer": round(float(avg_revenue), 2),
                    "monthly_revenue": round(float(monthly_revenue), 2),
                    "revenue_growth": growth_rate,
                },
                "churn_kpis": {
                    "churn_rate": churn_rate,
                    "lost_revenue": round(float(lost_revenue), 2),
                    "high_risk_customers": int(high_risk_count),
                    "churn_trend": self._calculate_churn_trend(df) if "join_date" in df.columns else [],
                },
                "segment_kpis": {
                    "segment_distribution": segment_distribution,
                    "status_distribution": status_distribution,
                    "top_segments": (
                        dict(sorted(segment_distribution.items(), key=lambda x: x[1], reverse=True)[:5])
                        if segment_distribution
                        else {}
                    ),
                },
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("Dashboard metrics generated successfully")
            return metrics

        except Exception as e:
            logger.error(f"Error generating dashboard metrics: {str(e)}")
            raise

    def _calculate_churn_trend(self, df: pd.DataFrame) -> list:
        """
        Calculate churn trend over time

        Args:
            df: Customer DataFrame

        Returns:
            List of churn rates by period
        """
        if "join_date" not in df.columns or "status" not in df.columns:
            return []

        # Create month column
        df["month"] = df["join_date"].dt.to_period("M")

        # Calculate churn rate per month
        churn_trend = []
        for month in df["month"].unique():
            month_data = df[df["month"] == month]
            total = len(month_data)
            churned = len(month_data[month_data["status"].str.contains("churned", case=False, na=False)])
            rate = churned / total if total > 0 else 0
            churn_trend.append(
                {
                    "period": str(month),
                    "churn_rate": round(rate, 4),
                    "total_customers": int(total),
                    "churned_customers": int(churned),
                }
            )

        return sorted(churn_trend, key=lambda x: x["period"])

    def create_revenue_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create revenue dashboard data

        Args:
            df: Customer DataFrame

        Returns:
            Revenue dashboard data
        """
        try:
            logger.info("Creating revenue dashboard...")
            df = self._clean_dataframe(df)

            dashboard = {}

            # Revenue by segment
            if "customer_segment" in df.columns and "total_spent" in df.columns:
                segment_revenue = df.groupby("customer_segment")["total_spent"].sum().sort_values(ascending=False)
                dashboard["segment_revenue"] = {str(k): round(float(v), 2) for k, v in segment_revenue.to_dict().items()}
                dashboard["segment_percentage"] = {
                    str(k): round(float(v) / segment_revenue.sum() * 100, 2) for k, v in segment_revenue.to_dict().items()
                }

            # Top customers by revenue
            if "total_spent" in df.columns:
                top_customers = df.nlargest(10, "total_spent")
                dashboard["top_customers"] = [
                    {
                        "customer_id": int(row["customer_id"]),
                        "name": row["name"] if "name" in row else "Unknown",
                        "total_spent": round(float(row["total_spent"]), 2),
                        "segment": row["customer_segment"] if "customer_segment" in row else "unknown",
                    }
                    for _, row in top_customers.iterrows()
                ]

            # Revenue distribution
            if "total_spent" in df.columns:
                revenue_bins = [0, 100, 500, 1000, 5000, 10000, float("inf")]
                revenue_labels = ["0-100", "101-500", "501-1000", "1001-5000", "5001-10000", "10000+"]
                df["revenue_bucket"] = pd.cut(df["total_spent"], bins=revenue_bins, labels=revenue_labels)
                dashboard["revenue_distribution"] = df["revenue_bucket"].value_counts().sort_index().to_dict()

            # Key revenue metrics
            dashboard["summary"] = {
                "total_revenue": round(float(df["total_spent"].sum() if "total_spent" in df.columns else 0), 2),
                "average_revenue": round(float(df["total_spent"].mean() if "total_spent" in df.columns else 0), 2),
                "max_revenue": round(float(df["total_spent"].max() if "total_spent" in df.columns else 0), 2),
                "min_revenue": round(float(df["total_spent"].min() if "total_spent" in df.columns else 0), 2),
                "median_revenue": round(float(df["total_spent"].median() if "total_spent" in df.columns else 0), 2),
                "total_monthly_revenue": round(float(df["monthly_charge"].sum() if "monthly_charge" in df.columns else 0), 2),
            }

            dashboard["timestamp"] = datetime.now().isoformat()

            logger.info("Revenue dashboard created successfully")
            return dashboard

        except Exception as e:
            logger.error(f"Error creating revenue dashboard: {str(e)}")
            raise

    def create_customer_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create customer dashboard data

        Args:
            df: Customer DataFrame

        Returns:
            Customer dashboard data
        """
        try:
            logger.info("Creating customer dashboard...")
            df = self._clean_dataframe(df)

            dashboard = {}

            # Customer distribution
            if "customer_segment" in df.columns:
                dashboard["segment_distribution"] = df["customer_segment"].value_counts().to_dict()

            if "status" in df.columns:
                dashboard["status_distribution"] = df["status"].value_counts().to_dict()

            if "gender" in df.columns:
                dashboard["gender_distribution"] = df["gender"].value_counts().to_dict()

            # Age distribution
            if "age" in df.columns and df["age"].notna().any():
                age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
                age_labels = ["0-18", "19-25", "26-35", "36-45", "46-55", "56-65", "65+"]
                df["age_group"] = pd.cut(df["age"], bins=age_bins, labels=age_labels)
                dashboard["age_distribution"] = df["age_group"].value_counts().sort_index().to_dict()

            # Geographic distribution
            if "state" in df.columns:
                dashboard["state_distribution"] = df["state"].value_counts().head(10).to_dict()
            if "city" in df.columns:
                dashboard["city_distribution"] = df["city"].value_counts().head(10).to_dict()

            # Key metrics
            dashboard["summary"] = {
                "total_customers": int(len(df)),
                "active_customers": (
                    int(len(df[df["status"].str.contains("active", case=False, na=False)])) if "status" in df.columns else 0
                ),
                "churned_customers": (
                    int(len(df[df["status"].str.contains("churned", case=False, na=False)])) if "status" in df.columns else 0
                ),
                "retention_rate": self._calculate_retention_rate(df),
                "average_tenure_days": round(
                    float(
                        df["join_date"].apply(lambda x: (datetime.now() - x).days).mean() if "join_date" in df.columns else 0
                    ),
                    0,
                ),
            }

            dashboard["timestamp"] = datetime.now().isoformat()

            logger.info("Customer dashboard created successfully")
            return dashboard

        except Exception as e:
            logger.error(f"Error creating customer dashboard: {str(e)}")
            raise

    def create_churn_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create churn dashboard data

        Args:
            df: Customer DataFrame

        Returns:
            Churn dashboard data
        """
        try:
            logger.info("Creating churn dashboard...")
            df = self._clean_dataframe(df)

            dashboard = {}

            # Churn by segment
            if "customer_segment" in df.columns and "status" in df.columns:
                churn_by_segment = df.groupby("customer_segment")["status"].apply(
                    lambda x: round((x.str.contains("churned", case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard["churn_by_segment"] = churn_by_segment.to_dict()

            # Risk distribution
            if "risk_level" in df.columns:
                dashboard["risk_distribution"] = df["risk_level"].value_counts().to_dict()

            # Churn by tenure
            if "join_date" in df.columns and "status" in df.columns:
                df["tenure_days"] = (datetime.now() - df["join_date"]).dt.days
                tenure_bins = [0, 30, 90, 180, 365, 730, float("inf")]
                tenure_labels = ["0-30", "31-90", "91-180", "181-365", "366-730", "730+"]
                df["tenure_group"] = pd.cut(df["tenure_days"], bins=tenure_bins, labels=tenure_labels)

                churn_by_tenure = df.groupby("tenure_group")["status"].apply(
                    lambda x: round((x.str.contains("churned", case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard["churn_by_tenure"] = churn_by_tenure.to_dict()

            # Churn by monthly charge
            if "monthly_charge" in df.columns and "status" in df.columns:
                charge_bins = [0, 50, 100, 150, 200, float("inf")]
                charge_labels = ["0-50", "51-100", "101-150", "151-200", "200+"]
                df["charge_group"] = pd.cut(df["monthly_charge"], bins=charge_bins, labels=charge_labels)

                churn_by_charge = df.groupby("charge_group")["status"].apply(
                    lambda x: round((x.str.contains("churned", case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard["churn_by_monthly_charge"] = churn_by_charge.to_dict()

            # Key churn metrics
            churned = len(df[df["status"].str.contains("churned", case=False, na=False)]) if "status" in df.columns else 0
            total = len(df)

            dashboard["summary"] = {
                "overall_churn_rate": self._calculate_churn_rate(df),
                "churned_customers": int(churned),
                "total_customers": int(total),
                "lost_revenue": round(
                    float(
                        df[df["status"].str.contains("churned", case=False, na=False)]["total_spent"].sum()
                        if "total_spent" in df.columns
                        else 0
                    ),
                    2,
                ),
                "high_risk_customers": int(
                    len(df[df["risk_level"].isin(["high", "critical"])]) if "risk_level" in df.columns else 0
                ),
                "churn_trend": self._calculate_churn_trend(df) if "join_date" in df.columns else [],
            }

            dashboard["timestamp"] = datetime.now().isoformat()

            logger.info("Churn dashboard created successfully")
            return dashboard

        except Exception as e:
            logger.error(f"Error creating churn dashboard: {str(e)}")
            raise

    def create_regional_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create regional performance dashboard

        Args:
            df: Customer DataFrame

        Returns:
            Regional dashboard data
        """
        try:
            logger.info("Creating regional dashboard...")
            df = self._clean_dataframe(df)

            dashboard = {}

            # Regional revenue
            if "state" in df.columns and "total_spent" in df.columns:
                regional_revenue = df.groupby("state")["total_spent"].sum().sort_values(ascending=False)
                dashboard["revenue_by_state"] = {str(k): round(float(v), 2) for k, v in regional_revenue.to_dict().items()}

            if "city" in df.columns and "total_spent" in df.columns:
                city_revenue = df.groupby("city")["total_spent"].sum().sort_values(ascending=False).head(10)
                dashboard["revenue_by_city"] = {str(k): round(float(v), 2) for k, v in city_revenue.to_dict().items()}

            # Regional customer distribution
            if "state" in df.columns:
                dashboard["customers_by_state"] = df["state"].value_counts().to_dict()
            if "city" in df.columns:
                dashboard["customers_by_city"] = df["city"].value_counts().head(10).to_dict()

            # Regional churn rates
            if "state" in df.columns and "status" in df.columns:
                churn_by_state = df.groupby("state")["status"].apply(
                    lambda x: round((x.str.contains("churned", case=False, na=False)).sum() / len(x) if len(x) > 0 else 0, 4)
                )
                dashboard["churn_rate_by_state"] = churn_by_state.to_dict()

            # Regional average revenue per customer
            if "state" in df.columns and "total_spent" in df.columns:
                avg_revenue_by_state = df.groupby("state")["total_spent"].mean()
                dashboard["avg_revenue_by_state"] = {
                    str(k): round(float(v), 2) for k, v in avg_revenue_by_state.to_dict().items()
                }

            dashboard["timestamp"] = datetime.now().isoformat()

            logger.info("Regional dashboard created successfully")
            return dashboard

        except Exception as e:
            logger.error(f"Error creating regional dashboard: {str(e)}")
            raise


# Example usage for testing
if __name__ == "__main__":
    try:
        # Load sample data
        df = pd.read_csv("./data/raw/customers.csv")

        # Initialize service
        dashboard = DashboardService()

        # Generate all dashboards
        metrics = dashboard.get_dashboard_metrics(df)
        revenue_dashboard = dashboard.create_revenue_dashboard(df)
        customer_dashboard = dashboard.create_customer_dashboard(df)
        churn_dashboard = dashboard.create_churn_dashboard(df)
        regional_dashboard = dashboard.create_regional_dashboard(df)

        print("=" * 60)
        print("✅ All dashboards generated successfully!")
        print("=" * 60)
        print(f"📊 Total Customers: {metrics['customer_kpis']['total_customers']}")
        print(f"💰 Total Revenue: ${metrics['revenue_kpis']['total_revenue']:,.2f}")
        print(f"📈 Churn Rate: {metrics['churn_kpis']['churn_rate']:.2%}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}")
