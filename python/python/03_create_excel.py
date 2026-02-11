"""
Create Excel Dashboard and Analysis Workbook
"""

import pandas as pd
import xlsxwriter

print("Creating Excel Analysis Workbook...")

# Load data
rfm = pd.read_csv('data/rfm_analysis.csv')
segment_summary = pd.read_csv('data/segment_summary.csv')
transactions = pd.read_csv('data/ecommerce_transactions.csv')

# Create Excel writer
output_path = 'excel/Customer_Segmentation_Analysis.xlsx'
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
workbook = writer.book

# Define formats
header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'fg_color': '#4472C4',
    'font_color': 'white',
    'border': 1
})

currency_format = workbook.add_format({'num_format': '$#,##0.00'})
percent_format = workbook.add_format({'num_format': '0.00%'})
number_format = workbook.add_format({'num_format': '#,##0'})

# Sheet 1: Executive Summary
exec_summary = pd.DataFrame({
    'Metric': [
        'Total Customers',
        'Total Transactions',
        'Total Revenue',
        'Average Customer Value',
        'High-Value Customers (Champions + Loyal)',
        'At-Risk Customers',
        'Churn Rate (>90 days)',
        'Average Recency (days)',
        'Average Frequency (orders)',
        'Average Monetary ($)'
    ],
    'Value': [
        len(rfm),
        len(transactions),
        rfm['monetary'].sum(),
        rfm['monetary'].mean(),
        len(rfm[rfm['segment'].isin(['Champions', 'Loyal Customers'])]),
        len(rfm[rfm['segment'].isin(['At Risk', 'Lost', 'About to Sleep'])]),
        len(rfm[rfm['recency'] > 90]) / len(rfm),
        rfm['recency'].mean(),
        rfm['frequency'].mean(),
        rfm['monetary'].mean()
    ]
})
exec_summary.to_excel(writer, sheet_name='Executive Summary', index=False)

# Sheet 2: Segment Analysis
segment_summary.to_excel(writer, sheet_name='Segment Analysis', index=False)

# Sheet 3: RFM Data
rfm.to_excel(writer, sheet_name='RFM Data', index=False)

# Sheet 4: Top 100 Customers
top_customers = rfm.nlargest(100, 'monetary')[['customer_id', 'segment', 'recency', 'frequency', 'monetary', 'rfm_score']]
top_customers.to_excel(writer, sheet_name='Top 100 Customers', index=False)

# Sheet 5: At-Risk Customers
at_risk = rfm[rfm['segment'].isin(['At Risk', 'About to Sleep', 'Need Attention'])].sort_values('monetary', ascending=False)
at_risk.to_excel(writer, sheet_name='At-Risk Customers', index=False)

# Sheet 6: Monthly Trends
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
monthly_trends = transactions.groupby(transactions['transaction_date'].dt.to_period('M')).agg({
    'transaction_id': 'count',
    'customer_id': 'nunique',
    'amount': 'sum'
}).reset_index()
monthly_trends.columns = ['Month', 'Transactions', 'Unique Customers', 'Revenue']
monthly_trends['Month'] = monthly_trends['Month'].astype(str)
monthly_trends.to_excel(writer, sheet_name='Monthly Trends', index=False)

# Sheet 7: Category Analysis
category_analysis = transactions.groupby('category').agg({
    'transaction_id': 'count',
    'customer_id': 'nunique',
    'amount': 'sum'
}).reset_index()
category_analysis.columns = ['Category', 'Transactions', 'Unique Customers', 'Revenue']
category_analysis = category_analysis.sort_values('Revenue', ascending=False)
category_analysis.to_excel(writer, sheet_name='Category Analysis', index=False)

# Apply formatting to all sheets
for sheet_name in writer.sheets:
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:Z', 18)

writer.close()

print(f"✅ Excel workbook created: {output_path}")
print(f"✅ Sheets created:")
print(f"   1. Executive Summary")
print(f"   2. Segment Analysis")
print(f"   3. RFM Data")
print(f"   4. Top 100 Customers")
print(f"   5. At-Risk Customers")
print(f"   6. Monthly Trends")
print(f"   7. Category Analysis")
