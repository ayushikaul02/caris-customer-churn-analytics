import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import os

fake = Faker()


def generate_customer_data(n=1000):
    """Generate sample customer data"""
    customers = []
    for i in range(n):
        join_date = fake.date_between(start_date="-3y", end_date="today")
        customers.append(
            {
                "customer_id": i + 1,
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "gender": random.choice(["M", "F"]),
                "age": random.randint(18, 75),
                "city": fake.city(),
                "state": fake.state(),
                "country": "USA",
                "join_date": join_date,
                "customer_segment": random.choice(["premium", "gold", "silver", "bronze", "basic"]),
                "status": random.choices(["active", "inactive", "churned", "suspended"], weights=[0.7, 0.1, 0.15, 0.05])[0],
                "monthly_charge": round(random.uniform(20, 200), 2),
            }
        )
    return pd.DataFrame(customers)


def generate_subscription_data(customers_df):
    """Generate sample subscription data"""
    subscriptions = []
    for _, customer in customers_df.iterrows():
        if customer["status"] != "churned":
            start_date = customer["join_date"]
            end_date = start_date + timedelta(days=random.randint(30, 365))
            subscriptions.append(
                {
                    "subscription_id": len(subscriptions) + 1,
                    "customer_id": customer["customer_id"],
                    "plan_name": random.choice(["Basic", "Standard", "Premium", "Enterprise"]),
                    "monthly_fee": round(random.uniform(10, 150), 2),
                    "status": random.choice(["active", "cancelled"]),
                    "start_date": start_date,
                    "end_date": end_date,
                    "auto_renew": random.choice([True, False]),
                }
            )
    return pd.DataFrame(subscriptions)


def generate_transaction_data(customers_df):
    """Generate sample transaction data"""
    transactions = []
    for _, customer in customers_df.iterrows():
        if customer["status"] != "churned":
            num_transactions = random.randint(5, 20)
            for _ in range(num_transactions):
                date = customer["join_date"] + timedelta(days=random.randint(0, 365))
                transactions.append(
                    {
                        "transaction_id": len(transactions) + 1,
                        "customer_id": customer["customer_id"],
                        "amount": round(random.uniform(10, 500), 2),
                        "transaction_date": date,
                        "payment_method": random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"]),
                        "transaction_type": random.choice(["purchase", "refund", "subscription"]),
                        "description": fake.sentence(),
                    }
                )
    return pd.DataFrame(transactions)


def generate_support_tickets(customers_df):
    """Generate sample support ticket data"""
    tickets = []
    for _, customer in customers_df.iterrows():
        if random.random() < 0.3:
            num_tickets = random.randint(1, 3)
            for _ in range(num_tickets):
                created_date = customer["join_date"] + timedelta(days=random.randint(0, 365))
                resolved_date = created_date + timedelta(days=random.randint(1, 10))
                tickets.append(
                    {
                        "ticket_id": len(tickets) + 1,
                        "customer_id": customer["customer_id"],
                        "issue_type": random.choice(["billing", "technical", "account", "other"]),
                        "priority": random.choice(["low", "medium", "high"]),
                        "status": random.choice(["open", "in_progress", "resolved", "closed"]),
                        "created_date": created_date,
                        "resolved_date": resolved_date if random.random() < 0.7 else None,
                        "satisfaction_score": random.randint(1, 5) if random.random() < 0.5 else None,
                        "description": fake.text(max_nb_chars=100),
                    }
                )
    return pd.DataFrame(tickets)


def generate_referral_data(customers_df):
    """Generate sample referral data"""
    referrals = []
    customer_ids = customers_df["customer_id"].tolist()
    for i in range(100):
        referrer = random.choice(customer_ids)
        # Get a different customer for referred
        available = [cid for cid in customer_ids if cid != referrer]
        if available:
            referred = random.choice(available)
            referrals.append(
                {
                    "referral_id": len(referrals) + 1,
                    "referrer_id": referrer,
                    "referred_id": referred,
                    "referral_date": fake.date_between(start_date="-2y", end_date="today"),
                    "status": random.choice(["pending", "accepted", "completed"]),
                    "reward_amount": round(random.uniform(10, 50), 2),
                }
            )
    return pd.DataFrame(referrals)


def save_sample_data():
    """Generate and save all sample data"""
    print("Generating customer data...")
    customers_df = generate_customer_data(1000)

    print("Generating transaction data...")
    transactions_df = generate_transaction_data(customers_df)

    # Calculate total spent per customer
    total_spent = transactions_df.groupby("customer_id")["amount"].sum().reset_index()
    total_spent.columns = ["customer_id", "total_spent"]

    # Merge total spent back to customers
    customers_df = customers_df.merge(total_spent, on="customer_id", how="left")
    customers_df["total_spent"] = customers_df["total_spent"].fillna(0)

    print("Generating subscription data...")
    subscriptions_df = generate_subscription_data(customers_df)

    print("Generating support tickets...")
    support_tickets_df = generate_support_tickets(customers_df)

    print("Generating referral data...")
    referrals_df = generate_referral_data(customers_df)

    # Create raw data directory
    os.makedirs("./data/raw", exist_ok=True)

    # Save to CSV
    print("Saving data...")
    customers_df.to_csv("./data/raw/customers.csv", index=False)
    subscriptions_df.to_csv("./data/raw/subscriptions.csv", index=False)
    transactions_df.to_csv("./data/raw/transactions.csv", index=False)
    support_tickets_df.to_csv("./data/raw/support_tickets.csv", index=False)
    referrals_df.to_csv("./data/raw/referrals.csv", index=False)

    print("=" * 50)
    print("✅ Sample data generated and saved successfully!")
    print("=" * 50)
    print(f"📊 Customers: {len(customers_df)}")
    print(f"📊 Subscriptions: {len(subscriptions_df)}")
    print(f"📊 Transactions: {len(transactions_df)}")
    print(f"📊 Support Tickets: {len(support_tickets_df)}")
    print(f"📊 Referrals: {len(referrals_df)}")
    print("=" * 50)
    print(f"📁 Files saved in: ./data/raw/")

    return {
        "customers": customers_df,
        "subscriptions": subscriptions_df,
        "transactions": transactions_df,
        "support_tickets": support_tickets_df,
        "referrals": referrals_df,
    }


if __name__ == "__main__":
    save_sample_data()
