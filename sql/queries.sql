-- ============================================================================
-- E-COMMERCE CUSTOMER SEGMENTATION - SQL SCRIPTS
-- ============================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS ecommerce_analytics;
USE ecommerce_analytics;

-- ============================================================================
-- TABLE CREATION
-- ============================================================================

-- Transactions Table
CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    transaction_date DATETIME NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    category VARCHAR(50),
    payment_method VARCHAR(50),
    country VARCHAR(50),
    INDEX idx_customer (customer_id),
    INDEX idx_date (transaction_date)
);

-- RFM Analysis Table
CREATE TABLE rfm_analysis (
    customer_id VARCHAR(20) PRIMARY KEY,
    recency INT,
    frequency INT,
    monetary DECIMAL(10, 2),
    r_score INT,
    f_score INT,
    m_score INT,
    rfm_score INT,
    segment VARCHAR(50)
);

-- ============================================================================
-- BUSINESS INTELLIGENCE QUERIES
-- ============================================================================

-- Query 1: Total Revenue and Transaction Count
SELECT 
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_transaction_value,
    MAX(transaction_date) AS latest_transaction,
    MIN(transaction_date) AS earliest_transaction
FROM transactions;

-- Query 2: Monthly Revenue Trend
SELECT 
    DATE_FORMAT(transaction_date, '%Y-%m') AS month,
    COUNT(*) AS transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(amount) AS revenue,
    AVG(amount) AS avg_order_value
FROM transactions
GROUP BY month
ORDER BY month;

-- Query 3: Top 10 Customers by Revenue
SELECT 
    customer_id,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_spent,
    AVG(amount) AS avg_order_value,
    MAX(transaction_date) AS last_purchase_date,
    DATEDIFF(CURDATE(), MAX(transaction_date)) AS days_since_last_purchase
FROM transactions
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- Query 4: Revenue by Category
SELECT 
    category,
    COUNT(*) AS transactions,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_transaction_value,
    ROUND((SUM(amount) / (SELECT SUM(amount) FROM transactions)) * 100, 2) AS revenue_percentage
FROM transactions
GROUP BY category
ORDER BY total_revenue DESC;

-- Query 5: Customer Segment Distribution
SELECT 
    segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(recency), 2) AS avg_recency,
    ROUND(AVG(frequency), 2) AS avg_frequency,
    ROUND(AVG(monetary), 2) AS avg_monetary,
    SUM(monetary) AS total_revenue,
    ROUND((COUNT(*) / (SELECT COUNT(*) FROM rfm_analysis)) * 100, 2) AS percentage
FROM rfm_analysis
GROUP BY segment
ORDER BY total_revenue DESC;

-- Query 6: High-Value Customers (Champions + Loyal)
SELECT 
    r.customer_id,
    r.segment,
    r.recency,
    r.frequency,
    r.monetary,
    r.rfm_score
FROM rfm_analysis r
WHERE r.segment IN ('Champions', 'Loyal Customers')
ORDER BY r.monetary DESC;

-- Query 7: At-Risk Customers Needing Intervention
SELECT 
    customer_id,
    segment,
    recency AS days_since_last_purchase,
    frequency AS total_orders,
    monetary AS total_spent
FROM rfm_analysis
WHERE segment IN ('At Risk', 'About to Sleep', 'Need Attention')
ORDER BY monetary DESC;

-- Query 8: Customer Cohort Analysis (First Purchase Month)
SELECT 
    DATE_FORMAT(first_purchase_date, '%Y-%m') AS cohort_month,
    COUNT(DISTINCT customer_id) AS customers_acquired,
    SUM(total_revenue) AS cohort_revenue,
    AVG(total_revenue) AS avg_customer_value
FROM (
    SELECT 
        customer_id,
        MIN(transaction_date) AS first_purchase_date,
        SUM(amount) AS total_revenue
    FROM transactions
    GROUP BY customer_id
) cohort_data
GROUP BY cohort_month
ORDER BY cohort_month;

-- Query 9: Payment Method Performance
SELECT 
    payment_method,
    COUNT(*) AS transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_transaction_value
FROM transactions
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- Query 10: Country-wise Revenue Analysis
SELECT 
    country,
    COUNT(*) AS transactions,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(amount) AS revenue,
    AVG(amount) AS avg_order_value,
    ROUND((SUM(amount) / (SELECT SUM(amount) FROM transactions)) * 100, 2) AS revenue_share
FROM transactions
GROUP BY country
ORDER BY revenue DESC;

-- Query 11: Customer Lifetime Value (CLV) Calculation
SELECT 
    customer_id,
    COUNT(*) AS total_orders,
    SUM(amount) AS lifetime_value,
    AVG(amount) AS avg_order_value,
    MIN(transaction_date) AS first_purchase,
    MAX(transaction_date) AS last_purchase,
    DATEDIFF(MAX(transaction_date), MIN(transaction_date)) AS customer_lifespan_days
FROM transactions
GROUP BY customer_id
HAVING total_orders > 1
ORDER BY lifetime_value DESC
LIMIT 50;

-- Query 12: Automated Weekly Segment Refresh
WITH customer_metrics AS (
    SELECT 
        customer_id,
        DATEDIFF(CURDATE(), MAX(transaction_date)) AS recency,
        COUNT(*) AS frequency,
        SUM(amount) AS monetary
    FROM transactions
    GROUP BY customer_id
)
SELECT 
    customer_id,
    recency,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency) AS f_score,
    NTILE(5) OVER (ORDER BY monetary) AS m_score
FROM customer_metrics;

-- ============================================================================
-- VIEWS FOR DASHBOARD
-- ============================================================================

-- View 1: Daily Revenue Summary
CREATE OR REPLACE VIEW vw_daily_revenue AS
SELECT 
    DATE(transaction_date) AS date,
    COUNT(*) AS transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(amount) AS revenue,
    AVG(amount) AS avg_order_value
FROM transactions
GROUP BY date
ORDER BY date DESC;

-- View 2: Segment Summary View
CREATE OR REPLACE VIEW vw_segment_summary AS
SELECT 
    r.segment,
    COUNT(*) AS customer_count,
    AVG(r.recency) AS avg_recency,
    AVG(r.frequency) AS avg_frequency,
    AVG(r.monetary) AS avg_monetary,
    SUM(r.monetary) AS total_revenue
FROM rfm_analysis r
GROUP BY r.segment;

-- =================================
