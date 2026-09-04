"""
Data Cleaning Framework for CARIS
Handles: Missing values, duplicates, outliers, standardization
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Complete data cleaning framework"""
    
    def __init__(self):
        self.cleaning_report = {}
        logger.info("DataCleaner initialized")
    
    def clean_dataframe(self, df: pd.DataFrame, 
                        remove_duplicates: bool = True,
                        handle_missing: bool = True,
                        detect_outliers: bool = True,
                        standardize: bool = True) -> pd.DataFrame:
        """Main cleaning pipeline"""
        
        df = df.copy()
        report = {
            'original_rows': len(df),
            'original_columns': len(df.columns),
            'steps': []
        }
        
        # Step 1: Remove duplicates
        if remove_duplicates:
            before = len(df)
            df = df.drop_duplicates()
            after = len(df)
            if before != after:
                report['steps'].append({
                    'step': 'remove_duplicates',
                    'removed': before - after
                })
                logger.info(f"✅ Removed {before - after} duplicates")
        
        # Step 2: Handle missing values
        if handle_missing:
            missing_before = df.isnull().sum().sum()
            df = self._handle_missing_values(df)
            missing_after = df.isnull().sum().sum()
            if missing_before != missing_after:
                report['steps'].append({
                    'step': 'handle_missing',
                    'filled': missing_before - missing_after
                })
                logger.info(f"✅ Filled {missing_before - missing_after} missing values")
        
        # Step 3: Detect outliers
        if detect_outliers:
            outlier_count = self._detect_outliers(df)
            if outlier_count > 0:
                report['steps'].append({
                    'step': 'detect_outliers',
                    'found': outlier_count
                })
                logger.info(f"✅ Detected {outlier_count} outliers")
        
        # Step 4: Standardize
        if standardize:
            df = self._standardize_data(df)
            report['steps'].append({
                'step': 'standardize',
                'status': 'completed'
            })
            logger.info(f"✅ Standardized data")
        
        report['final_rows'] = len(df)
        report['final_columns'] = len(df.columns)
        self.cleaning_report = report
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Intelligent missing value handling"""
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                if df[col].dtype in ['float64', 'int64']:
                    # Numeric: fill with median
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    logger.debug(f"  Filled {null_count} missing in '{col}' with median")
                elif df[col].dtype == 'object':
                    # Categorical: fill with mode or 'Unknown'
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                    df[col] = df[col].fillna(mode_val)
                    logger.debug(f"  Filled {null_count} missing in '{col}' with mode")
                elif df[col].dtype == 'datetime64[ns]':
                    # Datetime: fill with current date
                    df[col] = df[col].fillna(pd.Timestamp.now())
        
        return df
    
    def _detect_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> int:
        """Detect outliers using IQR method"""
        outlier_count = 0
        
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                if outliers > 0:
                    outlier_count += outliers
                    # Cap outliers instead of removing
                    df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                    logger.debug(f"  Capped {outliers} outliers in '{col}'")
        
        return outlier_count
    
    def _standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data formats"""
        
        # Standardize string columns
        str_cols = df.select_dtypes(include=['object']).columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.lower()
            df[col] = df[col].replace(['nan', 'none', 'null'], 'unknown')
        
        # Standardize dates
        date_cols = df.select_dtypes(include=['datetime64']).columns
        for col in date_cols:
            df[col] = pd.to_datetime(df[col])
        
        # Standardize numeric columns
        num_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Gender standardization
        if 'gender' in df.columns:
            gender_map = {
                'm': 'male', 'male': 'male', 'M': 'male',
                'f': 'female', 'female': 'female', 'F': 'female'
            }
            df['gender'] = df['gender'].map(gender_map).fillna('unknown')
        
        # Status standardization
        if 'status' in df.columns:
            status_map = {
                'active': 'active', 'a': 'active',
                'churned': 'churned', 'c': 'churned',
                'inactive': 'inactive', 'i': 'inactive',
                'suspended': 'suspended', 's': 'suspended'
            }
            df['status'] = df['status'].map(status_map).fillna('unknown')
        
        return df
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get the cleaning report"""
        return self.cleaning_report
    
    def save_cleaned_data(self, df: pd.DataFrame, filepath: str):
        """Save cleaned data to CSV"""
        df.to_csv(filepath, index=False)
        logger.info(f"✅ Cleaned data saved to {filepath}")