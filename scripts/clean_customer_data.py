import pandas as pd
import os


def clean_customer_data():
    """Clean and deduplicate customer data"""
    df = pd.read_csv("./data/raw/customers.csv")

    print(f"Original data: {len(df)} rows")
    print(f"Duplicate customer_ids: {df['customer_id'].duplicated().sum()}")

    # Remove duplicates keeping first occurrence
    df = df.drop_duplicates(subset=["customer_id"], keep="first")

    # Clean city names (remove "City: " prefix)
    if "city" in df.columns:
        df["city"] = df["city"].astype(str).str.replace("City: ", "", regex=False)

    # Clean state names
    if "state" in df.columns:
        df["state"] = df["state"].astype(str).str.strip()

    # Clean names (fix missing names)
    if "name" in df.columns:
        # If name contains @, it's an email, use email before @ as name
        mask = df["name"].astype(str).str.contains("@", na=False)
        df.loc[mask, "name"] = df.loc[mask, "email"].str.split("@").str[0]

    # Ensure customer_id is integer
    if "customer_id" in df.columns:
        df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").fillna(0).astype(int)

    # Ensure total_spent is numeric
    if "total_spent" in df.columns:
        df["total_spent"] = pd.to_numeric(df["total_spent"], errors="coerce").fillna(0)

    # Save cleaned data
    df.to_csv("./data/raw/customers_cleaned.csv", index=False)

    print(f"Cleaned data: {len(df)} rows")
    print(f"Unique customer_ids: {df['customer_id'].nunique()}")
    print("✅ Data cleaned and saved to customers_cleaned.csv")

    return df


if __name__ == "__main__":
    clean_customer_data()
