import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetentionEngine:
    """Enterprise-grade retention recommendation engine"""

    def __init__(self):
        self.recommendation_templates = {
            "critical": [
                "🚨 URGENT: Schedule immediate retention call with customer",
                "🎯 Offer personalized premium discount of 30%",
                "📞 Assign dedicated account manager",
                "💎 Provide VIP status and exclusive benefits",
                "🎁 Offer 3 months free upgrade to highest tier",
            ],
            "high": [
                "📧 Send personalized retention email with special offer",
                "🎯 Offer 20% discount on next 3 bills",
                "📞 Schedule customer success consultation",
                "⭐ Provide loyalty points bonus worth $50",
                "🎁 Free premium feature trial for 6 months",
            ],
            "medium": [
                "📧 Send engagement email with product tips",
                "🎯 Offer 10% discount on next bill",
                "📞 Invite to customer feedback session",
                "🤝 Introduce referral program benefits",
                "📊 Provide personalized usage analytics",
            ],
            "low": [
                "📧 Send monthly newsletter with updates",
                "👥 Invite to customer community forum",
                "⚡ Early access to new features",
                "📝 Request product feedback and reviews",
                "🎓 Offer free training webinars",
            ],
            "vip": [
                "👔 Assign dedicated account manager",
                "💎 Provide exclusive VIP perks",
                "🎉 Invite to exclusive events",
                "🆘 Priority support line",
                "🎓 Free advanced training sessions",
            ],
        }

        logger.info("RetentionEngine initialized")

    def generate_recommendations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate retention recommendations for customers"""
        logger.info("Generating retention recommendations...")
        df = df.copy()

        # Ensure risk_level exists
        if "risk_level" not in df.columns:
            logger.warning("Risk level not found. Setting default.")
            df["risk_level"] = "Low"

        recommendations = []
        for _, row in df.iterrows():
            rec = self._get_recommendations_for_customer(row)
            recommendations.append(rec)

        df["recommendations"] = recommendations
        df["recommendation_priority"] = df["recommendations"].apply(lambda x: x["priority"] if isinstance(x, dict) else "low")

        logger.info(f"✅ Recommendations generated for {len(df)} customers")
        return df

    def _get_recommendations_for_customer(self, customer: pd.Series) -> dict:
        """Get personalized recommendations for a single customer"""
        recommendations = []
        priority = "low"

        # Get risk level
        risk_level = customer.get("risk_level", "low")
        if isinstance(risk_level, str):
            risk_level = risk_level.lower()

        # Get customer segment
        segment = customer.get("customer_segment", "basic")
        if isinstance(segment, str):
            segment = segment.lower()

        # Check if VIP
        is_vip = segment in ["premium", "gold"]

        # Select recommendation templates based on risk
        if risk_level in ["critical"]:
            templates = self.recommendation_templates["critical"]
            priority = "critical"
            num_recommendations = 3
        elif risk_level in ["high"]:
            templates = self.recommendation_templates["high"]
            priority = "high"
            num_recommendations = 3
        elif risk_level in ["medium"]:
            templates = self.recommendation_templates["medium"]
            priority = "medium"
            num_recommendations = 2
        elif is_vip:
            templates = self.recommendation_templates["vip"]
            priority = "high"
            num_recommendations = 2
        else:
            templates = self.recommendation_templates["low"]
            priority = "low"
            num_recommendations = 2

        # Select recommendations
        selected = random.sample(templates, min(num_recommendations, len(templates)))

        # Personalized intro
        name = customer.get("name", "Customer")
        personalized = [f"👋 Personalized recommendations for {name}"]
        personalized.extend(selected)

        urgency = "immediate" if risk_level in ["critical", "high"] else "soon"

        return {
            "customer_id": int(customer.get("customer_id", 0)),
            "customer_name": name,
            "recommendations": personalized,
            "priority": priority,
            "urgency": urgency,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat(),
        }

    def create_promotional_campaigns(self, df: pd.DataFrame) -> dict:
        """Create promotional campaigns based on customer segments"""
        logger.info("Creating promotional campaigns...")
        campaigns = {}

        total_customers = len(df)

        # 1. High-risk customers retention campaign
        if "risk_level" in df.columns:
            high_risk_df = df[df["risk_level"].isin(["High", "Critical"])]
            if not high_risk_df.empty:
                campaigns["high_risk_retention"] = {
                    "name": "🚨 High-Risk Customer Retention Campaign",
                    "target_segment": "High Risk Customers",
                    "target_count": int(len(high_risk_df)),
                    "percentage": round(len(high_risk_df) / total_customers * 100, 2),
                    "offer_type": "Personalized Discount",
                    "discount_range": "20-30%",
                    "estimated_budget": 5000,
                    "expected_retention_rate": 0.65,
                    "channel": "Email + SMS + Phone Call",
                    "timeline": "Immediate",
                    "message": "We value you as a customer. Here's a personalized offer to show our appreciation.",
                }

        # 2. VIP customer campaign
        if "customer_segment" in df.columns:
            vip_df = df[df["customer_segment"].str.lower().isin(["premium", "gold"])]
            if not vip_df.empty:
                campaigns["vip_exclusive"] = {
                    "name": "💎 VIP Exclusive Benefits Campaign",
                    "target_segment": "VIP Customers",
                    "target_count": int(len(vip_df)),
                    "percentage": round(len(vip_df) / total_customers * 100, 2),
                    "offer_type": "Exclusive Benefits",
                    "estimated_budget": 3000,
                    "expected_retention_rate": 0.90,
                    "channel": "Email + Phone Call",
                    "timeline": "Next Week",
                    "message": "Thank you for being a valued VIP customer. Enjoy these exclusive benefits.",
                }

        # 3. Loyalty rewards campaign
        if "tenure_days" in df.columns and "total_spent" in df.columns:
            loyal_df = df[
                (df["tenure_days"] > 365) & (df["status"] == "active") & (df["total_spent"] > df["total_spent"].quantile(0.5))
            ]
            if not loyal_df.empty:
                campaigns["loyalty_rewards"] = {
                    "name": "⭐ Loyalty Rewards Program",
                    "target_segment": "Loyal Customers",
                    "target_count": int(len(loyal_df)),
                    "percentage": round(len(loyal_df) / total_customers * 100, 2),
                    "offer_type": "Loyalty Points",
                    "discount_range": "15-25%",
                    "estimated_budget": 4000,
                    "expected_retention_rate": 0.85,
                    "channel": "Email + App Notification",
                    "timeline": "End of Month",
                    "message": "Thank you for your loyalty! We're excited to reward you with exclusive benefits.",
                }

        # 4. Referral program
        campaigns["referral_program"] = {
            "name": "🤝 Referral Program Launch",
            "target_segment": "All Active Customers",
            "target_count": int(len(df[df["status"] == "active"])) if "status" in df.columns else 0,
            "percentage": round(len(df[df["status"] == "active"]) / total_customers * 100 if "status" in df.columns else 0, 2),
            "offer_type": "Referral Rewards",
            "discount_range": "$25-$100 per referral",
            "estimated_budget": 1500,
            "expected_retention_rate": 0.50,
            "channel": "Email + Social Media",
            "timeline": "Next Month",
            "message": "Refer a friend and earn rewards! Both you and your friend will receive special benefits.",
        }

        logger.info(f"✅ Created {len(campaigns)} campaigns")
        return campaigns
