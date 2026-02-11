"""
E-Commerce Transaction Data Generator
Generates realistic customer transaction data for RFM analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 5000
NUM_TRANSACTIONS = 50000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)

print("Generating E-Commerce Transaction Data...")

# Generate customer base
customer_ids = [f"CUST{str(i).zfill(5)}" for i in range(1, NUM_CUSTOMERS + 1)]

# Customer segments (will influence their behavior)
customer_segments = np.random.choice(
    ['High Value', 'Medium Value', 'Low Value', 'At Risk', 'New'],
    size=NUM_CUSTOMERS,
    p=[0.15, 0.25, 0.30, 0.20, 0.10]
)

# Generate transactions
transactions = []

for i in range(NUM_TRANSACTIONS):
    # Select customer
    customer_id = random.choice(customer_ids)
    customer_index = customer_ids.index(customer_id)
    segment = customer_segments[customer_index]
    
    # Transaction date
    days_range = (END_DATE - START_DATE).days
    transaction_date = START_DATE + timedelta(days=random.randint(0, days_range))
    
    # Purchase amount based on segment
    if segment == 'High Value':
        amount = np.random.gamma(5, 50)  # Higher spending
    elif segment == 'Medium Value':
        amount = np.random.gamma(3, 30)
    elif segment == 'Low Value':
        amount = np.random.gamma(2, 15)
    elif segment == 'At Risk':
        amount = np.random.gamma(2, 20)
    else:  # New
        amount = np.random.gamma(2, 25)
    
    # Product categories
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 
                  'Beauty', 'Toys', 'Food & Beverage']
    category = random.choice(categories)
    
    # Quantity
    quantity = random.randint(1, 5)
    
    # Payment method
    payment_method = random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Cash on Delivery'])
    
    # Country
    country = random.choice(['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France'])
    
    transactions.append({
        'transaction_id': f"TXN{str(i+1).zfill(6)}",
        'customer_id': customer_id,
        'transaction_date': transaction_date,
        'amount': round(amount, 2),
        'quantity': quantity,
        'category': category,
        'payment_method': payment_method,
        'country': country
    })

# Create DataFrame
df_transactions = pd.DataFrame(transactions)

# Sort by date
df_transactions = df_transactions.sort_values('transaction_date').reset_index(drop=True)

# Save to CSV
output_path = 'data/ecommerce_transactions.csv'
df_transactions.to_csv(output_path, index=False)

print(f"\n✅ Generated {len(df_transactions)} transactions for {NUM_CUSTOMERS} customers")
print(f"✅ Data saved to: {output_path}")
print(f"\nData Overview:")
print(df_transactions.head(10))
print(f"\nData Statistics:")
print(df_transactions.describe())
print(f"\nDate Range: {df_transactions['transaction_date'].min()} to {df_transactions['transaction_date'].max()}")
print(f"Total Revenue: ${df_transactions['amount'].sum():,.2f}")
