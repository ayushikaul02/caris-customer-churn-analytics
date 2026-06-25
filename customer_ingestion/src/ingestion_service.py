import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import requests
from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """Enterprise-grade data ingestion service"""

    def __init__(self):
        self.raw_data_path = "./data/raw"
        self.processed_data_path = "./data/processed"
        os.makedirs(self.raw_data_path, exist_ok=True)
        os.makedirs(self.processed_data_path, exist_ok=True)
        logger.info("DataIngestionService initialized")

    def ingest_from_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Ingest data from CSV file"""
        try:
            logger.info(f"Ingesting CSV file: {file_path}")
            df = pd.read_csv(file_path, **kwargs)
            self._validate_data(df)
            self._save_raw_data(df, "csv")
            logger.info(f"✅ Successfully ingested {len(df)} records from CSV")
            return df
        except Exception as e:
            logger.error(f"Error ingesting CSV: {e}")
            raise

    def ingest_from_excel(self, file_path: str, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """Ingest data from Excel file"""
        try:
            logger.info(f"Ingesting Excel file: {file_path}")
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            self._validate_data(df)
            self._save_raw_data(df, "excel")
            logger.info(f"✅ Successfully ingested {len(df)} records from Excel")
            return df
        except Exception as e:
            logger.error(f"Error ingesting Excel: {e}")
            raise

    def ingest_from_api(
        self, api_url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Ingest data from REST API"""
        try:
            logger.info(f"Ingesting data from API: {api_url}")
            response = requests.get(api_url, headers=headers or {}, params=params or {}, **kwargs)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            elif isinstance(data, dict) and "items" in data:
                df = pd.DataFrame(data["items"])
            else:
                raise ValueError(f"Unexpected API response format: {type(data)}")

            self._validate_data(df)
            self._save_raw_data(df, "api")
            logger.info(f"✅ Successfully ingested {len(df)} records from API")
            return df
        except Exception as e:
            logger.error(f"Error ingesting API data: {e}")
            raise

    def ingest_from_database(self, query: str, connection_string: Optional[str] = None) -> pd.DataFrame:
        """Ingest data from SQL database"""
        try:
            logger.info("Ingesting data from database")
            import sqlalchemy
            from sqlalchemy import create_engine

            if connection_string:
                engine = create_engine(connection_string)
            else:
                from common.src.config.config import DATABASE_URL

                engine = create_engine(DATABASE_URL)

            df = pd.read_sql(query, engine)
            self._validate_data(df)
            self._save_raw_data(df, "database")
            logger.info(f"✅ Successfully ingested {len(df)} records from database")
            return df
        except Exception as e:
            logger.error(f"Error ingesting from database: {e}")
            raise

    def _validate_data(self, df: pd.DataFrame):
        """Validate ingested data"""
        if df.empty:
            raise ValueError("Empty data frame - no data to process")

        # Check for required columns
        required_columns = ["customer_id", "name", "email"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"⚠️ Missing required columns: {missing_columns}")

        # Check for duplicate customer_ids
        if "customer_id" in df.columns:
            duplicates = df["customer_id"].duplicated().sum()
            if duplicates > 0:
                logger.warning(f"⚠️ Found {duplicates} duplicate customer IDs")

        # Check for null values in key columns
        if "email" in df.columns:
            null_emails = df["email"].isnull().sum()
            if null_emails > 0:
                logger.warning(f"⚠️ Found {null_emails} missing emails")

    def _save_raw_data(self, df: pd.DataFrame, source_type: str):
        """Save raw data with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"raw_data_{source_type}_{timestamp}.csv"
        filepath = os.path.join(self.raw_data_path, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"📁 Raw data saved to {filepath}")

    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data"""
        filepath = os.path.join(self.processed_data_path, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"📁 Processed data saved to {filepath}")

    def get_available_files(self) -> List[str]:
        """Get list of available raw data files"""
        files = os.listdir(self.raw_data_path)
        return [f for f in files if f.endswith(".csv")]

    def load_latest_data(self, prefix: Optional[str] = None) -> pd.DataFrame:
        """Load the most recent data file"""
        files = self.get_available_files()
        if prefix:
            files = [f for f in files if f.startswith(prefix)]

        if not files:
            raise FileNotFoundError("No data files found")

        # Sort by modification time
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.raw_data_path, f)))
        filepath = os.path.join(self.raw_data_path, latest_file)
        logger.info(f"Loading latest data: {latest_file}")
        return pd.read_csv(filepath)


# Example usage
if __name__ == "__main__":
    ingestion = DataIngestionService()
    # Test with sample data
    try:
        df = ingestion.ingest_from_csv("./data/raw/customers.csv")
        print(f"✅ Loaded {len(df)} customers")
    except FileNotFoundError:
        print("⚠️ Sample data not found. Run generate_sample_data.py first.")
