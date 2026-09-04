"""
ETL Pipeline for CARIS - Customer Churn Analytics & Retention Intelligence System

This module handles the complete ETL process:
- Extract: Read data from CSV files
- Transform: Clean, validate, and engineer features
- Load: Save processed data to CSV or database
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging
from typing import Dict, Any, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Complete ETL Pipeline for CARIS"""
    
    def __init__(self, raw_path: str = "./data/raw", processed_path: str = "./data/processed"):
        self.raw_path = raw_path
        self.processed_path = processed_path
        os.makedirs(raw_path, exist_ok=True)
        os.makedirs(processed_path, exist_ok=True)
        logger.info("ETL Pipeline initialized")
    
    # ==================== EXTRACT ====================
    
    def extract_customers(self) -> pd.DataFrame:
        """Extract customer data from CSV"""
        try:
            filepath = os.path.join(self.raw_path, "customers.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"✅ Extracted {len(df)} customers from {filepath}")
                return df
            else:
                logger.warning(f"⚠️ File not found: {filepath}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error extracting customers: {e}")
            return pd.DataFrame()
    
    def extract_transactions(self) -> pd.DataFrame:
        """Extract transaction data from CSV"""
        try:
            filepath = os.path.join(self.raw_path, "transactions.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"✅ Extracted {len(df)} transactions from {filepath}")
                return df
            else:
                logger.warning(f"⚠️ File not found: {filepath}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error extracting transactions: {e}")
            return pd.DataFrame()
    
    def extract_subscriptions(self) -> pd.DataFrame:
        """Extract subscription data from CSV"""
        try:
            filepath = os.path.join(self.raw_path, "subscriptions.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"✅ Extracted {len(df)} subscriptions from {filepath}")
                return df
            else:
                logger.warning(f"⚠️ File not found: {filepath}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error extracting subscriptions: {e}")
            return pd.DataFrame()
    
    def extract_support_tickets(self) -> pd.DataFrame:
        """Extract support ticket data from CSV"""
        try:
            filepath = os.path.join(self.raw_path, "support_tickets.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"✅ Extracted {len(df)} support tickets from {filepath}")
                return df
            else:
                logger.warning(f"⚠️ File not found: {filepath}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error extracting support tickets: {e}")
            return pd.DataFrame()
    
    def extract_referrals(self) -> pd.DataFrame:
        """Extract referral data from CSV"""
        try:
            filepath = os.path.join(self.raw_path, "referrals.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"✅ Extracted {len(df)} referrals from {filepath}")
                return df
            else:
                logger.warning(f"⚠️ File not found: {filepath}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error extracting referrals: {e}")
            return pd.DataFrame()
    
    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """Extract all data"""
        logger.info("📊 Starting extraction of all data...")
        
        data = {
            'customers': self.extract_customers(),
            'transactions': self.extract_transactions(),
            'subscriptions': self.extract_subscriptions(),
            'support_tickets': self.extract_support_tickets(),
            'referrals': self.extract_referrals()
        }
        
        total_records = sum(len(df) for df in data.values())
        logger.info(f"✅ Extracted {total_records} total records")
        
        return data
    
    # ==================== TRANSFORM ====================
    
    def transform_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform customer data"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # Clean column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Convert date columns
        if 'join_date' in df.columns:
            df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce')
        
        # Clean status
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.lower().str.strip()
            df['status'] = df['status'].replace(['nan', 'none'], 'active')
        
        # Clean segment
        if 'customer_segment' in df.columns:
            df['customer_segment'] = df['customer_segment'].astype(str).str.lower().str.strip()
            df['customer_segment'] = df['customer_segment'].replace(['nan', 'none'], 'basic')
        
        # Clean numeric columns
        numeric_cols = ['age', 'monthly_charge', 'total_spent']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Feature Engineering
        if 'join_date' in df.columns:
            today = datetime.now()
            df['tenure_days'] = (today - df['join_date']).dt.days
            df['tenure_months'] = df['tenure_days'] / 30.44
            df['tenure_years'] = df['tenure_days'] / 365.25
        
        # Calculate revenue per month
        if 'total_spent' in df.columns and 'tenure_months' in df.columns:
            df['avg_monthly_spend'] = df['total_spent'] / df['tenure_months'].clip(lower=1)
        
        # Segment encoding
        if 'customer_segment' in df.columns:
            segment_map = {
                'basic': 0, 'bronze': 1, 'silver': 2, 
                'gold': 3, 'premium': 4
            }
            df['segment_encoded'] = df['customer_segment'].map(segment_map).fillna(0)
        
        logger.info(f"✅ Transformed {len(df)} customers")
        return df
    
    def transform_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform transaction data"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # Clean column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Convert date columns
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Clean numeric columns
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        
        # Extract month and year
        if 'transaction_date' in df.columns:
            df['transaction_month'] = df['transaction_date'].dt.month
            df['transaction_year'] = df['transaction_date'].dt.year
            df['transaction_quarter'] = df['transaction_date'].dt.quarter
        
        logger.info(f"✅ Transformed {len(df)} transactions")
        return df
    
    def transform_subscriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform subscription data"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # Clean column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Convert date columns
        for col in ['start_date', 'end_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean numeric columns
        if 'monthly_fee' in df.columns:
            df['monthly_fee'] = pd.to_numeric(df['monthly_fee'], errors='coerce').fillna(0)
        
        # Calculate subscription duration
        if 'start_date' in df.columns and 'end_date' in df.columns:
            df['duration_days'] = (df['end_date'] - df['start_date']).dt.days
            df['duration_months'] = df['duration_days'] / 30.44
        
        logger.info(f"✅ Transformed {len(df)} subscriptions")
        return df
    
    def transform_support_tickets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform support ticket data"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # Clean column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Convert date columns
        for col in ['created_date', 'resolved_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate resolution time
        if 'created_date' in df.columns and 'resolved_date' in df.columns:
            df['resolution_hours'] = (df['resolved_date'] - df['created_date']).dt.total_seconds() / 3600
        
        # Clean satisfaction score
        if 'satisfaction_score' in df.columns:
            df['satisfaction_score'] = pd.to_numeric(df['satisfaction_score'], errors='coerce')
        
        logger.info(f"✅ Transformed {len(df)} support tickets")
        return df
    
    def transform_all(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform all data"""
        logger.info("🔄 Starting transformation of all data...")
        
        transformed = {
            'customers': self.transform_customers(data.get('customers', pd.DataFrame())),
            'transactions': self.transform_transactions(data.get('transactions', pd.DataFrame())),
            'subscriptions': self.transform_subscriptions(data.get('subscriptions', pd.DataFrame())),
            'support_tickets': self.transform_support_tickets(data.get('support_tickets', pd.DataFrame())),
            'referrals': data.get('referrals', pd.DataFrame())  # Minimal transformation needed
        }
        
        total_records = sum(len(df) for df in transformed.values())
        logger.info(f"✅ Transformed {total_records} total records")
        
        return transformed
    
    # ==================== LOAD ====================
    
    def load_data(self, data: Dict[str, pd.DataFrame], prefix: str = "transformed") -> Dict[str, str]:
        """Load transformed data to CSV"""
        logger.info("💾 Starting loading of data...")
        
        filepaths = {}
        
        for name, df in data.items():
            if not df.empty:
                filename = f"{prefix}_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                filepath = os.path.join(self.processed_path, filename)
                df.to_csv(filepath, index=False)
                filepaths[name] = filepath
                logger.info(f"✅ Loaded {len(df)} {name} to {filepath}")
        
        logger.info(f"✅ Loaded {len(filepaths)} files")
        return filepaths
    
    # ==================== FULL PIPELINE ====================
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete ETL pipeline"""
        logger.info("=" * 60)
        logger.info("🚀 Starting ETL Pipeline...")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Step 1: Extract
        raw_data = self.extract_all()
        
        # Step 2: Transform
        transformed_data = self.transform_all(raw_data)
        
        # Step 3: Load
        filepaths = self.load_data(transformed_data)
        
        # Step 4: Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': round(duration, 2),
            'records_extracted': sum(len(df) for df in raw_data.values()),
            'records_transformed': sum(len(df) for df in transformed_data.values()),
            'files_loaded': len(filepaths),
            'filepaths': filepaths
        }
        
        logger.info("=" * 60)
        logger.info(f"✅ ETL Pipeline completed in {duration:.2f} seconds")
        logger.info(f"📊 Records Processed: {summary['records_transformed']}")
        logger.info(f"📁 Files Loaded: {summary['files_loaded']}")
        logger.info("=" * 60)
        
        return summary
    
    def run_incremental_update(self) -> Dict[str, Any]:
        """Run incremental ETL update (append new data only)"""
        logger.info("🔄 Running incremental update...")
        
        # This would compare existing data and only update new records
        # For now, just run full pipeline
        return self.run_full_pipeline()
    
    def generate_data_quality_report(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate data quality report"""
        report = {}
        
        for name, df in data.items():
            if df.empty:
                report[name] = {'status': 'empty'}
                continue
            
            report[name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'null_counts': df.isnull().sum().to_dict(),
                'duplicates': df.duplicated().sum(),
                'data_types': df.dtypes.astype(str).to_dict(),
                'sample': df.head(3).to_dict('records')
            }
        
        return report


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    # Create ETL pipeline instance
    etl = ETLPipeline()
    
    # Run the full pipeline
    summary = etl.run_full_pipeline()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ETL PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Start Time: {summary['start_time']}")
    print(f"End Time: {summary['end_time']}")
    print(f"Duration: {summary['duration_seconds']} seconds")
    print(f"Records Processed: {summary['records_transformed']}")
    print(f"Files Loaded: {summary['files_loaded']}")
    print("\nGenerated Files:")
    for name, path in summary['filepaths'].items():
        print(f"  - {name}: {path}")
    print("=" * 60)