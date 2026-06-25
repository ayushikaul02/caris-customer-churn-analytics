import pandas as pd
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self):
        self.report_path = "./reporting_service/reports"
        os.makedirs(self.report_path, exist_ok=True)
        logger.info("ReportService initialized")

    def generate_monthly_report(self, df: pd.DataFrame, month: str = None) -> dict:
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        logger.info(f"Generating monthly report for {month}...")

        total_customers = len(df)
        active_customers = len(df[df["status"] == "active"]) if "status" in df.columns else 0
        churned_customers = len(df[df["status"] == "churned"]) if "status" in df.columns else 0

        return {
            "report_type": "Monthly Business Report",
            "period": month,
            "generated_date": datetime.now().isoformat(),
            "summary": {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "churned_customers": churned_customers,
                "total_revenue": float(df["total_spent"].sum()) if "total_spent" in df.columns else 0,
                "avg_customer_value": float(df["total_spent"].mean()) if "total_spent" in df.columns else 0,
                "churn_rate": churned_customers / total_customers if total_customers > 0 else 0,
            },
        }

    def generate_excel_report(self, df: pd.DataFrame, filename: str = None) -> str:
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        filepath = os.path.join(self.report_path, filename)
        logger.info(f"Generating Excel report: {filepath}")

        try:
            df_clean = df.copy()

            # Create Excel file
            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                # Sheet 1: Summary
                summary_data = {
                    "Metric": [
                        "Total Customers",
                        "Active Customers",
                        "Churned Customers",
                        "Total Revenue",
                        "Average Revenue",
                        "Churn Rate",
                    ],
                    "Value": [
                        len(df_clean),
                        len(df_clean[df_clean["status"] == "active"]) if "status" in df_clean.columns else 0,
                        len(df_clean[df_clean["status"] == "churned"]) if "status" in df_clean.columns else 0,
                        round(float(df_clean["total_spent"].sum() if "total_spent" in df_clean.columns else 0), 2),
                        round(float(df_clean["total_spent"].mean() if "total_spent" in df_clean.columns else 0), 2),
                        f"{round(len(df_clean[df_clean['status'] == 'churned']) / len(df_clean) * 100 if 'status' in df_clean.columns else 0, 2)}%",
                    ],
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

                # Sheet 2: Customer Data
                df_clean.head(100).to_excel(writer, sheet_name="Customer Data", index=False)

                # Sheet 3: Segment Analysis
                if "customer_segment" in df_clean.columns:
                    segment_df = (
                        df_clean.groupby("customer_segment")
                        .agg({"customer_id": "count", "total_spent": ["sum", "mean"]})
                        .reset_index()
                    )
                    segment_df.columns = ["Segment", "Customer Count", "Total Revenue", "Average Revenue"]
                    segment_df["Total Revenue"] = segment_df["Total Revenue"].round(2)
                    segment_df["Average Revenue"] = segment_df["Average Revenue"].round(2)
                    segment_df.to_excel(writer, sheet_name="Segment Analysis", index=False)

            logger.info(f"✅ Excel report saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error: {e}")
            csv_path = filepath.replace(".xlsx", ".csv")
            df.to_csv(csv_path, index=False)
            logger.info(f"✅ CSV saved to {csv_path}")
            return csv_path

    def get_available_reports(self) -> list:
        files = os.listdir(self.report_path)
        reports = []
        for f in files:
            stat = os.stat(os.path.join(self.report_path, f))
            reports.append(
                {
                    "filename": f,
                    "type": f.split(".")[-1] if "." in f else "unknown",
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
            )
        return sorted(reports, key=lambda x: x["created"], reverse=True)
