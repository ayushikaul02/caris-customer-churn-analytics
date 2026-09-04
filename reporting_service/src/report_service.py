import pandas as pd
from datetime import datetime, timedelta
import os
import logging
from typing import Optional, Dict, Any, List

# PDF libraries
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab not installed. PDF reports will be disabled.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportService:
    """Enterprise-grade report generation service"""
    
    def __init__(self):
        self.report_path = "./reporting_service/reports"
        os.makedirs(self.report_path, exist_ok=True)
        logger.info("ReportService initialized")
    
    def generate_monthly_report(self, df: pd.DataFrame, month: Optional[str] = None) -> Dict[str, Any]:
        """Generate monthly business report"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        logger.info(f"Generating monthly report for {month}...")

        try:
            total_customers = len(df)
            active_customers = len(df[df["status"] == "active"]) if "status" in df.columns else 0
            churned_customers = len(df[df["status"] == "churned"]) if "status" in df.columns else 0
            new_customers = 0

            if "join_date" in df.columns:
                df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
                thirty_days_ago = datetime.now() - timedelta(days=30)
                new_customers = len(df[df["join_date"] > thirty_days_ago])

            total_revenue = float(df["total_spent"].sum()) if "total_spent" in df.columns else 0
            avg_revenue = float(df["total_spent"].mean()) if "total_spent" in df.columns else 0
            churn_rate = churned_customers / total_customers if total_customers > 0 else 0
            retention_rate = active_customers / total_customers if total_customers > 0 else 0

            report = {
                "report_type": "Monthly Business Report",
                "period": month,
                "generated_date": datetime.now().isoformat(),
                "summary": {
                    "total_customers": int(total_customers),
                    "active_customers": int(active_customers),
                    "churned_customers": int(churned_customers),
                    "new_customers": int(new_customers),
                    "total_revenue": round(total_revenue, 2),
                    "avg_customer_value": round(avg_revenue, 2),
                    "churn_rate": round(churn_rate, 4),
                    "retention_rate": round(retention_rate, 4)
                },
                "recommendations": [
                    {
                        "priority": "High",
                        "action": "Focus retention efforts on high-risk customers with personalized offers",
                        "expected_impact": "Reduce churn by 15-20%",
                        "timeline": "Immediate"
                    },
                    {
                        "priority": "High",
                        "action": "Improve customer engagement through targeted communication campaigns",
                        "expected_impact": "Increase engagement by 25%",
                        "timeline": "Next 30 days"
                    },
                    {
                        "priority": "Medium",
                        "action": "Enhance customer support experience to reduce churn",
                        "expected_impact": "Improve satisfaction score by 10%",
                        "timeline": "Next 60 days"
                    },
                    {
                        "priority": "Medium",
                        "action": "Develop loyalty programs for long-term customers",
                        "expected_impact": "Increase retention by 5-10%",
                        "timeline": "Next 90 days"
                    }
                ]
            }

            if "customer_segment" in df.columns and "total_spent" in df.columns:
                segment_data = {}
                for segment in df["customer_segment"].unique():
                    segment_df = df[df["customer_segment"] == segment]
                    segment_data[segment] = {
                        "customer_count": int(len(segment_df)),
                        "total_revenue": round(float(segment_df["total_spent"].sum()), 2),
                        "avg_revenue": round(float(segment_df["total_spent"].mean()), 2),
                        "churn_rate": round(len(segment_df[segment_df["status"] == "churned"]) / len(segment_df) if len(segment_df) > 0 else 0, 4)
                    }
                report["segment_analysis"] = segment_data

            logger.info("✅ Monthly report generated successfully")
            return report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "report_type": "Monthly Business Report",
                "period": month,
                "generated_date": datetime.now().isoformat(),
                "summary": {
                    "total_customers": len(df),
                    "active_customers": 0,
                    "churned_customers": 0,
                    "new_customers": 0,
                    "total_revenue": 0,
                    "avg_customer_value": 0,
                    "churn_rate": 0,
                    "retention_rate": 0
                },
                "recommendations": [
                    {
                        "priority": "Low",
                        "action": "System error - please check logs",
                        "expected_impact": "N/A",
                        "timeline": "Immediate"
                    }
                ],
                "error": str(e)
            }

    def generate_quarterly_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate quarterly business report"""
        current_month = datetime.now().month
        quarter = f"Q{(current_month-1)//3 + 1} {datetime.now().year}"
        
        logger.info(f"Generating quarterly report for {quarter}...")
        
        total_customers = len(df)
        active_customers = len(df[df["status"] == "active"]) if "status" in df.columns else 0
        churned_customers = len(df[df["status"] == "churned"]) if "status" in df.columns else 0
        
        return {
            "report_type": "Quarterly Business Report",
            "quarter": quarter,
            "generated_date": datetime.now().isoformat(),
            "summary": {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "churned_customers": churned_customers,
                "total_revenue": float(df["total_spent"].sum()) if "total_spent" in df.columns else 0,
                "avg_customer_value": float(df["total_spent"].mean()) if "total_spent" in df.columns else 0,
                "churn_rate": churned_customers / total_customers if total_customers > 0 else 0,
            },
            "quarterly_trend": "Upward" if total_customers > 0 else "Stable"
        }

    def generate_pdf_report(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Generate PDF report"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        filepath = os.path.join(self.report_path, filename)
        logger.info(f"Generating PDF report: {filepath}")

        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available. Generating text fallback.")
            return self._generate_text_report(df, filename.replace('.pdf', '.txt'))

        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30
            )
            elements.append(Paragraph("📊 CARIS Monthly Business Report", title_style))
            elements.append(Spacer(1, 0.25*inch))

            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#666666')
            )
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", date_style))
            elements.append(Spacer(1, 0.5*inch))

            # Summary table
            data = [
                ['Metric', 'Value'],
                ['Total Customers', str(len(df))],
                ['Active Customers', str(len(df[df['status'] == 'active'])) if 'status' in df.columns else '0'],
                ['Churned Customers', str(len(df[df['status'] == 'churned'])) if 'status' in df.columns else '0'],
                ['Total Revenue', f"${df['total_spent'].sum():,.2f}" if 'total_spent' in df.columns else '$0'],
                ['Churn Rate', f"{len(df[df['status'] == 'churned']) / len(df) * 100:.1f}%" if 'status' in df.columns else '0%']
            ]

            table = Table(data, colWidths=[2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 14),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#b8c6d4')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)

            doc.build(elements)
            logger.info(f"✅ PDF report saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return self._generate_text_report(df, filename.replace('.pdf', '.txt'))

    def _generate_text_report(self, df: pd.DataFrame, filename: str) -> str:
        """Generate plain text report as fallback"""
        filepath = os.path.join(self.report_path, filename)
        try:
            with open(filepath, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("CARIS Monthly Business Report\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%B %d, %Y')}\n")
                f.write("-" * 60 + "\n\n")
                f.write(f"Total Customers: {len(df)}\n")
                f.write(f"Total Revenue: ${df['total_spent'].sum():,.2f}\n" if 'total_spent' in df.columns else '')
                f.write("=" * 60 + "\n")
            return filepath
        except Exception as e:
            logger.error(f"Error generating text report: {e}")
            return filepath

    def generate_excel_report(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Generate Excel report with multiple sheets"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        filepath = os.path.join(self.report_path, filename)
        logger.info(f"Generating Excel report: {filepath}")

        try:
            df_clean = df.copy()
            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                # Summary
                summary_data = {
                    "Metric": ["Total Customers", "Active Customers", "Churned Customers", "Total Revenue", "Churn Rate"],
                    "Value": [
                        len(df_clean),
                        len(df_clean[df_clean["status"] == "active"]) if "status" in df_clean.columns else 0,
                        len(df_clean[df_clean["status"] == "churned"]) if "status" in df_clean.columns else 0,
                        round(float(df_clean["total_spent"].sum() if "total_spent" in df_clean.columns else 0), 2),
                        f"{round(len(df_clean[df_clean['status'] == 'churned']) / len(df_clean) * 100 if 'status' in df_clean.columns else 0, 2)}%"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

                # Customer Data
                if len(df_clean) > 1000:
                    df_clean.head(1000).to_excel(writer, sheet_name="Customer Data", index=False)
                else:
                    df_clean.to_excel(writer, sheet_name="Customer Data", index=False)

                # Segment Analysis
                if "customer_segment" in df_clean.columns:
                    segment_df = df_clean.groupby("customer_segment").agg({
                        "customer_id": "count",
                        "total_spent": ["sum", "mean"]
                    }).reset_index()
                    segment_df.columns = ["Segment", "Customer Count", "Total Revenue", "Average Revenue"]
                    segment_df["Total Revenue"] = segment_df["Total Revenue"].round(2)
                    segment_df["Average Revenue"] = segment_df["Average Revenue"].round(2)
                    segment_df.to_excel(writer, sheet_name="Segment Analysis", index=False)

                # Risk Analysis
                if "risk_level" in df_clean.columns:
                    risk_df = df_clean.groupby("risk_level").agg({
                        "customer_id": "count"
                    }).reset_index()
                    risk_df.columns = ["Risk Level", "Customer Count"]
                    risk_df.to_excel(writer, sheet_name="Risk Analysis", index=False)

            logger.info(f"✅ Excel report saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            csv_path = filepath.replace(".xlsx", ".csv")
            df.to_csv(csv_path, index=False)
            return csv_path

    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Get list of available reports"""
        files = os.listdir(self.report_path)
        reports = []
        for f in files:
            stat = os.stat(os.path.join(self.report_path, f))
            reports.append({
                "filename": f,
                "type": f.split(".")[-1] if "." in f else "unknown",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        return sorted(reports, key=lambda x: x["created"], reverse=True)