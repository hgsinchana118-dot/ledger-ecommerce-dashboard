"""
Generates a synthetic e-commerce orders dataset so the dashboard
has something to analyze out of the box.

Run:  python generate_sample_data.py
Output: data/ecommerce_data.csv
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N = 2000

categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Beauty", "Sports", "Toys"]
category_price_range = {
    "Electronics": (50, 900),
    "Clothing": (10, 150),
    "Home & Kitchen": (15, 400),
    "Books": (5, 60),
    "Beauty": (5, 120),
    "Sports": (10, 300),
    "Toys": (5, 100),
}
regions = ["North", "South", "East", "West", "Central"]
payment_methods = ["Credit Card", "Debit Card", "UPI", "PayPal", "Cash on Delivery"]
order_statuses = ["Delivered", "Delivered", "Delivered", "Delivered", "Shipped", "Cancelled", "Returned"]

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
for i in range(1, N + 1):
    category = np.random.choice(categories, p=[0.22, 0.20, 0.15, 0.10, 0.13, 0.12, 0.08])
    low, high = category_price_range[category]
    price = round(np.random.uniform(low, high), 2)
    quantity = np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.15, 0.07, 0.05, 0.03])
    discount_pct = np.random.choice([0, 0, 5, 10, 15, 20, 25], p=[0.35, 0.15, 0.15, 0.15, 0.1, 0.06, 0.04])
    revenue = round(price * quantity * (1 - discount_pct / 100), 2)

    order_date = start_date + timedelta(days=int(np.random.rand() * date_range_days))
    # seasonal bump around Nov-Dec
    if order_date.month in (11, 12) and np.random.rand() < 0.4:
        order_date = order_date.replace(month=np.random.choice([11, 12]))

    rows.append({
        "order_id": f"ORD{10000 + i}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "customer_id": f"CUST{np.random.randint(1, 600):04d}",
        "customer_age": int(np.clip(np.random.normal(34, 11), 18, 70)),
        "category": category,
        "product_price": price,
        "quantity": quantity,
        "discount_pct": discount_pct,
        "revenue": revenue,
        "region": np.random.choice(regions),
        "payment_method": np.random.choice(payment_methods),
        "order_status": np.random.choice(order_statuses),
        "rating": np.random.choice([1, 2, 3, 4, 5], p=[0.03, 0.05, 0.15, 0.37, 0.40]),
    })

df = pd.DataFrame(rows)
df.to_csv("data/ecommerce_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/ecommerce_data.csv")
print(df.head())
