import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)

# --- 1. Generate Dim_Product ---
products_data = [
    {'Product_ID': 'P001', 'Product_Name': '10GB Monthly Data', 'Category': 'Data', 'Base_Price_KES': 1000, 'Commission_Rate': 0.05},
    {'Product_ID': 'P002', 'Product_Name': '50GB Monthly Data', 'Category': 'Data', 'Base_Price_KES': 3000, 'Commission_Rate': 0.05},
    {'Product_ID': 'P003', 'Product_Name': 'Home Fiber 20Mbps', 'Category': 'Fiber', 'Base_Price_KES': 4000, 'Commission_Rate': 0.10},
    {'Product_ID': 'P004', 'Product_Name': 'Home Fiber 50Mbps', 'Category': 'Fiber', 'Base_Price_KES': 6500, 'Commission_Rate': 0.12},
    {'Product_ID': 'P005', 'Product_Name': 'Unlimited Voice Plan', 'Category': 'Voice', 'Base_Price_KES': 1500, 'Commission_Rate': 0.07}
]
dim_product = pd.DataFrame(products_data)

# --- 2. Generate Dim_Agent ---
num_agents = 800  # Increased for massive scale
kenyan_counties = ['Nairobi', 'Mombasa', 'Kiambu', 'Nakuru', 'Kisumu', 'Machakos', 'Uasin Gishu', 'Kajiado']

agents_data = []
for i in range(1, num_agents + 1):
    agents_data.append({
        'Agent_ID': f'AGT{i:04d}',
        'Agent_Name': fake.unique.name(),
        'County': np.random.choice(kenyan_counties, p=[0.3, 0.15, 0.15, 0.1, 0.1, 0.05, 0.05, 0.1]),
        'Agent_Status': np.random.choice(['Active', 'Inactive'], p=[0.85, 0.15])
    })
dim_agent = pd.DataFrame(agents_data)

# --- 3. Generate Dim_Date ---
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 11, 12)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

dim_date = pd.DataFrame({
    'Date': date_range,
    'Year': date_range.year,
    'Quarter': date_range.quarter,
    'Month_Num': date_range.month,
    'Month_Name': date_range.strftime('%B'),
    'Day_of_Week': date_range.strftime('%A')
})

# --- 4. Generate Fact_Sales ---
num_transactions = 500000  # Supersized transaction volume

# Create a weighted probability for dates to simulate business growth over time
# This ensures your Power BI line charts show a realistic upward trend
date_probabilities = np.linspace(1, 3, len(date_range))
date_probabilities /= date_probabilities.sum()

dates = np.random.choice(date_range, num_transactions, p=date_probabilities)

# Only allow Active agents to make sales
active_agents = dim_agent[dim_agent['Agent_Status'] == 'Active']['Agent_ID'].tolist()
agents = np.random.choice(active_agents, num_transactions)
products = np.random.choice(dim_product['Product_ID'], num_transactions)

fact_sales = pd.DataFrame({
    'Transaction_ID': [f'TXN{i:07d}' for i in range(1, num_transactions + 1)],
    'Date': dates,
    'Agent_ID': agents,
    'Product_ID': products
})

# Merge with product table to calculate prices and commissions
fact_sales = fact_sales.merge(dim_product[['Product_ID', 'Base_Price_KES', 'Commission_Rate']], on='Product_ID', how='left')

# Add variance to sales amounts (simulate discounts or up-sells)
variance_multiplier = np.random.uniform(0.85, 1.15, num_transactions)
fact_sales['Amount_KES'] = (fact_sales['Base_Price_KES'] * variance_multiplier).round(0)

# Calculate Commission
fact_sales['Commission_KES'] = (fact_sales['Amount_KES'] * fact_sales['Commission_Rate']).round(0)

# Clean up Fact table columns
fact_sales = fact_sales[['Transaction_ID', 'Date', 'Agent_ID', 'Product_ID', 'Amount_KES', 'Commission_KES']]
fact_sales = fact_sales.sort_values(by='Date').reset_index(drop=True)

# --- 5. Export to CSV ---
dim_product.to_csv('Dim_Product.csv', index=False)
dim_agent.to_csv('Dim_Agent.csv', index=False)
dim_date.to_csv('Dim_Date.csv', index=False)
fact_sales.to_csv('Fact_Sales.csv', index=False)

print(f"Success! Generated {num_transactions:,} transactions across {num_agents} agents.")