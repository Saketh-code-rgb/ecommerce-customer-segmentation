"""
RFM Analysis & Customer Segmentation
Recency, Frequency, Monetary Analysis for E-Commerce Customers
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print("E-COMMERCE CUSTOMER SEGMENTATION - RFM ANALYSIS")
print("=" * 80)

# Load data
print("\n📂 Loading transaction data...")
df = pd.read_csv('data/ecommerce_transactions.csv')
df['transaction_date'] = pd.to_datetime(df['transaction_date'])

print(f"✅ Loaded {len(df)} transactions")
print(f"✅ Date range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
print(f"✅ Unique customers: {df['customer_id'].nunique()}")

# Set analysis date (last date + 1 day)
analysis_date = df['transaction_date'].max() + pd.Timedelta(days=1)
print(f"✅ Analysis date: {analysis_date}")

# Calculate RFM metrics
print("\n📊 Calculating RFM metrics...")

rfm = df.groupby('customer_id').agg({
    'transaction_date': lambda x: (analysis_date - x.max()).days,  # Recency
    'transaction_id': 'count',  # Frequency
    'amount': 'sum'  # Monetary
}).reset_index()

rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

print("✅ RFM metrics calculated")
print(f"\nRFM Statistics:")
print(rfm.describe())

# Create RFM scores (1-5 scale, 5 being best)
print("\n📈 Creating RFM scores...")

rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
rfm['m_score'] = pd.qcut(rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert to numeric
rfm['r_score'] = rfm['r_score'].astype(int)
rfm['f_score'] = rfm['f_score'].astype(int)
rfm['m_score'] = rfm['m_score'].astype(int)

# Calculate RFM score
rfm['rfm_score'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']

print("✅ RFM scores created")

# Customer Segmentation
print("\n🎯 Segmenting customers...")

def segment_customer(row):
    if row['rfm_score'] >= 13:
        return 'Champions'
    elif row['rfm_score'] >= 11:
        return 'Loyal Customers'
    elif row['rfm_score'] >= 9 and row['r_score'] >= 4:
        return 'Potential Loyalists'
    elif row['rfm_score'] >= 9:
        return 'Recent Customers'
    elif row['rfm_score'] >= 7 and row['r_score'] >= 3:
        return 'Promising'
    elif row['rfm_score'] >= 7:
        return 'Need Attention'
    elif row['rfm_score'] >= 5 and row['r_score'] >= 3:
        return 'About to Sleep'
    elif row['rfm_score'] >= 5:
        return 'At Risk'
    else:
        return 'Lost'

rfm['segment'] = rfm.apply(segment_customer, axis=1)

print("✅ Customers segmented")

# Segment analysis
print("\n📊 CUSTOMER SEGMENT ANALYSIS")
print("=" * 80)

segment_summary = rfm.groupby('segment').agg({
    'customer_id': 'count',
    'recency': 'mean',
    'frequency': 'mean',
    'monetary': 'sum'
}).reset_index()

segment_summary.columns = ['Segment', 'Customer_Count', 'Avg_Recency', 'Avg_Frequency', 'Total_Revenue']
segment_summary['Avg_Revenue_Per_Customer'] = segment_summary['Total_Revenue'] / segment_summary['Customer_Count']
segment_summary['Percentage'] = (segment_summary['Customer_Count'] / len(rfm) * 100).round(2)

# Sort by revenue
segment_summary = segment_summary.sort_values('Total_Revenue', ascending=False)

print(segment_summary.to_string(index=False))

# Calculate key metrics
print("\n📈 KEY BUSINESS METRICS")
print("=" * 80)

total_customers = len(rfm)
total_revenue = rfm['monetary'].sum()
avg_customer_value = total_revenue / total_customers
high_value_customers = len(rfm[rfm['segment'].isin(['Champions', 'Loyal Customers'])])
at_risk_customers = len(rfm[rfm['segment'].isin(['At Risk', 'Lost', 'About to Sleep'])])

print(f"Total Customers: {total_customers:,}")
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Customer Value: ${avg_customer_value:,.2f}")
print(f"High-Value Customers (Champions + Loyal): {high_value_customers:,} ({high_value_customers/total_customers*100:.1f}%)")
print(f"At-Risk Customers: {at_risk_customers:,} ({at_risk_customers/total_customers*100:.1f}%)")

# Calculate churn rate (customers not purchased in last 90 days)
churned_customers = len(rfm[rfm['recency'] > 90])
churn_rate = churned_customers / total_customers * 100
print(f"Churn Rate (>90 days inactive): {churn_rate:.1f}%")

# Save RFM results
print("\n💾 Saving results...")
rfm.to_csv('data/rfm_analysis.csv', index=False)
segment_summary.to_csv('data/segment_summary.csv', index=False)

print("✅ RFM analysis saved to: rfm_analysis.csv")
print("✅ Segment summary saved to: segment_summary.csv")

print("\n" + "=" * 80)
print("✅ RFM ANALYSIS COMPLETE!")
print("=" * 80)
