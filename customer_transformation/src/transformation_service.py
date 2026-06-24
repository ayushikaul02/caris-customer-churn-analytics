import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformationService:
    """Enterprise-grade data transformation service"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.label_encoders = {}
        self.imputers = {}
        logger.info("DataTransformationService initialized")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main cleaning pipeline"""
        logger.info("Starting data cleaning...")
        df = df.copy()
        df = self._handle_missing_values(df)
        df = self._remove_duplicates(df)
        df = self._detect_outliers(df)
        df = self._standardize_formats(df)
        df = self._clean_strings(df)
        logger.info("✅ Data cleaning completed")
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                if df[col].dtype in ['float64', 'int64']:
                    # For numerical: use median
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    self.imputers[col] = {'method': 'median', 'value': median_val}
                elif df[col].dtype == 'object':
                    # For categorical: use mode or 'Unknown'
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                    df[col] = df[col].fillna(mode_val)
                    self.imputers[col] = {'method': 'mode', 'value': mode_val}
                elif df[col].dtype == 'datetime64[ns]':
                    # For datetime: use current date
                    df[col] = df[col].fillna(pd.Timestamp.now())
                    self.imputers[col] = {'method': 'current_date'}
                
                logger.info(f"  Filled {null_count} missing values in '{col}'")
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records intelligently"""
        initial_count = len(df)
        
        # Check for duplicates on key columns
        if 'customer_id' in df.columns:
            df = df.drop_duplicates(subset=['customer_id'], keep='first')
        else:
            df = df.drop_duplicates()
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"  Removed {removed_count} duplicate records")
        return df
    
    def _detect_outliers(self, df: pd.DataFrame, method='iqr') -> pd.DataFrame:
        """Detect and handle outliers"""
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                if outlier_count > 0:
                    # Cap outliers instead of removing
                    df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                    logger.info(f"  Capped {outlier_count} outliers in '{col}'")
        return df
    
    def _standardize_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data formats"""
        # Convert date columns
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Convert numeric columns
        numeric_columns = ['total_spent', 'monthly_charge', 'age']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _clean_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean string columns"""
        str_columns = df.select_dtypes(include=['object']).columns
        for col in str_columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace('nan', 'Unknown')
            df[col] = df[col].str.replace('None', 'Unknown')
        
        # Standardize common values
        if 'gender' in df.columns:
            gender_map = {
                'M': 'Male', 'm': 'Male', 'male': 'Male', 'MALE': 'Male',
                'F': 'Female', 'f': 'Female', 'female': 'Female', 'FEMALE': 'Female'
            }
            df['gender'] = df['gender'].map(gender_map).fillna('Unknown')
        
        if 'status' in df.columns:
            df['status'] = df['status'].str.lower().str.strip()
        
        if 'customer_segment' in df.columns:
            df['customer_segment'] = df['customer_segment'].str.lower().str.strip()
        
        return df
    
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new features from existing data"""
        logger.info("Starting feature engineering...")
        df = df.copy()
        
        # Customer tenure
        if 'join_date' in df.columns:
            df['join_date'] = pd.to_datetime(df['join_date'])
            today = datetime.now()
            df['tenure_days'] = (today - df['join_date']).dt.days
            df['tenure_months'] = df['tenure_days'] / 30.44
            df['tenure_years'] = df['tenure_days'] / 365.25
            
            # Tenure categories
            df['tenure_category'] = pd.cut(
                df['tenure_days'],
                bins=[-1, 30, 90, 180, 365, 730, float('inf')],
                labels=['New', 'Recent', 'Medium', 'Established', 'Loyal', 'Long-standing']
            )
        
        # Revenue metrics
        if 'monthly_charge' in df.columns and 'tenure_months' in df.columns:
            df['lifetime_value_estimate'] = df['monthly_charge'] * df['tenure_months']
        
        if 'total_spent' in df.columns and 'tenure_months' in df.columns:
            df['avg_monthly_spend'] = df['total_spent'] / df['tenure_months'].clip(lower=1)
        
        # Customer segment encoding
        if 'customer_segment' in df.columns:
            segment_map = {
                'basic': 0, 'bronze': 1, 'silver': 2, 'gold': 3, 'premium': 4
            }
            df['segment_encoded'] = df['customer_segment'].map(segment_map).fillna(0)
        
        # Risk scoring
        if 'status' in df.columns:
            risk_map = {
                'active': 1,
                'inactive': 2,
                'suspended': 3,
                'churned': 4
            }
            df['risk_score'] = df['status'].map(risk_map).fillna(2)
        
        # Engagement score (if we have transaction data)
        if 'total_spent' in df.columns:
            df['engagement_score'] = pd.cut(
                df['total_spent'],
                bins=[-1, 100, 500, 1000, 5000, float('inf')],
                labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
            )
        
        # Age group
        if 'age' in df.columns:
            df['age_group'] = pd.cut(
                df['age'],
                bins=[-1, 18, 25, 35, 45, 55, 65, float('inf')],
                labels=['Under 18', '18-25', '26-35', '36-45', '46-55', '56-65', '65+']
            )
        
        logger.info(f"✅ Feature engineering completed. Created {len(df.columns)} features")
        return df
    
    def normalize_data(self, df: pd.DataFrame, method='minmax') -> pd.DataFrame:
        """Normalize numerical features"""
        df = df.copy()
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        if method == 'minmax':
            scaled_data = self.minmax_scaler.fit_transform(df[numerical_cols])
            df[numerical_cols] = scaled_data
            logger.info("✅ Min-Max normalization completed")
        elif method == 'standard':
            scaled_data = self.scaler.fit_transform(df[numerical_cols])
            df[numerical_cols] = scaled_data
            logger.info("✅ Standard normalization completed")
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        df = df.copy()
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if df[col].nunique() < 20:  # Only encode low cardinality columns
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                logger.info(f"  Encoded '{col}' with {df[col].nunique()} unique values")
        
        return df
    
    def prepare_for_analytics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Full data preparation pipeline for analytics"""
        logger.info("Starting full data preparation pipeline...")
        df = self.clean_data(df)
        df = self.feature_engineering(df)
        df = self.encode_categorical(df)
        logger.info("✅ Data preparation completed")
        return df
    
    def get_data_quality_report(self, df: pd.DataFrame) -> dict:
        """Generate data quality report"""
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'column_types': df.dtypes.astype(str).to_dict(),
            'unique_values': {col: df[col].nunique() for col in df.columns},
            'numeric_stats': {}
        }
        
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            report['numeric_stats'][col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std())
            }
        
        return report

# Example usage
if __name__ == "__main__":
    transformer = DataTransformationService()
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        prepared_df = transformer.prepare_for_analytics(df)
        print(f"✅ Data prepared: {len(prepared_df)} rows, {len(prepared_df.columns)} columns")
        print("Features:", list(prepared_df.columns))
    except FileNotFoundError:
        print("⚠️ Sample data not found. Run generate_sample_data.py first.")