import os
# Prevent OpenBLAS memory allocation error on some Windows systems
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_ecommerce_data(num_transactions=1500, num_customers=300):
    np.random.seed(42)
    random.seed(42)

    categories = {
        'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Mouse', 'Keyboard', 'Webcam'],
        'Clothing': ['T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Sweater', 'Socks'],
        'Groceries': ['Milk', 'Bread', 'Eggs', 'Apples', 'Banana', 'Coffee', 'Butter'],
        'Home & Garden': ['Plant', 'Lamp', 'Chair', 'Table', 'Cushion', 'Mug']
    }
    
    items = []
    for cat, prod_list in categories.items():
        for prod in prod_list:
            items.append({'Item': prod, 'Category': cat, 'Price': round(random.uniform(5, 500), 2)})

    transactions = []
    start_date = datetime(2023, 1, 1)
    
    # Natural purchasing patterns to ensure MBA finds strong rules
    patterns = [
        ['Milk', 'Bread', 'Eggs', 'Butter'],
        ['Laptop', 'Mouse', 'Keyboard', 'Webcam'],
        ['Smartphone', 'Headphones'],
        ['Jeans', 'T-Shirt', 'Sneakers'],
        ['Coffee', 'Mug'],
        ['Monitor', 'Laptop']
    ]

    for i in range(num_transactions):
        t_id = f"TXN_{str(i+1000).zfill(5)}"
        c_id = f"CUST_{random.randint(1, num_customers):03d}"
        date = start_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
        
        # Decide if this transaction follows a pattern
        if random.random() < 0.45:
            pattern = random.choice(patterns)
            # Pick a subset of the pattern (at least 2 items if possible)
            subset_size = random.randint(max(2, len(pattern)//2), len(pattern))
            bought_items = random.sample(pattern, subset_size)
        else:
            num_items = random.randint(1, 5)
            bought_items = [random.choice(items)['Item'] for _ in range(num_items)]
            
        bought_items = list(set(bought_items)) # unique items per transaction
            
        for b_item in bought_items:
            item_data = next(img for img in items if img['Item'] == b_item)
            qty = random.randint(1, 4) if item_data['Category'] == 'Groceries' else 1
            
            transactions.append({
                'Transaction_ID': t_id,
                'Customer_ID': c_id,
                'Date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'Item': b_item,
                'Category': item_data['Category'],
                'Quantity': qty,
                'Price': item_data['Price'],
                'Total_Spend': round(qty * item_data['Price'], 2)
            })
            
    df = pd.DataFrame(transactions)
    # Add some null values and duplicates to test the data handler
    df.loc[5:15, 'Customer_ID'] = np.nan
    df = pd.concat([df, df.iloc[10:20]])
    
    df.to_csv("ecommerce_dataset.csv", index=False)
    print("Dataset generated as ecommerce_dataset.csv with", len(df), "records.")

if __name__ == "__main__":
    generate_ecommerce_data()
