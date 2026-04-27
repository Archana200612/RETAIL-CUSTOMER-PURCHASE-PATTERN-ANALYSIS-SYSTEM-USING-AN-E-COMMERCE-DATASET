import csv
import random
from datetime import datetime, timedelta

def generate_minimal_data(num_rows=500):
    categories = ['Electronics', 'Clothing', 'Groceries', 'Home & Garden']
    items = ['Laptop', 'T-Shirt', 'Milk', 'Plant', 'Mouse', 'Sneakers', 'Bread', 'Lamp']
    
    filename = "ecommerce_dataset.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Transaction_ID', 'Customer_ID', 'Date', 'Item', 'Category', 'Quantity', 'Price', 'Total_Spend'])
        
        start_date = datetime(2023, 1, 1)
        for i in range(num_rows):
            t_id = f"TXN_{1000 + (i // 2)}" # Some rows share transaction ID
            c_id = f"CUST_{random.randint(1, 100):03d}"
            date = start_date + timedelta(days=random.randint(0, 30))
            item = random.choice(items)
            cat = categories[items.index(item) // 2]
            qty = random.randint(1, 5)
            price = round(random.uniform(10, 100), 2)
            total = round(qty * price, 2)
            
            writer.writerow([t_id, c_id, date.strftime('%Y-%m-%d %H:%M:%S'), item, cat, qty, price, total])
            
    print(f"Minimal dataset created: {filename}")

if __name__ == "__main__":
    generate_minimal_data()
