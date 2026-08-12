# Ledger — E-commerce Data Analysis (Flask + seaborn)

A small Flask app that turns an orders CSV into a dashboard of seaborn charts:
revenue trend, revenue by category/region, order status breakdown, customer age
distribution, a correlation heatmap, and price-vs-quantity.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

You can either:
- Click **"Use sample data"** to explore the dashboard immediately with a
  generated dataset (`data/ecommerce_data.csv`, regenerate any time with
  `python generate_sample_data.py`), or
- Upload your own CSV.

## Your own CSV

Required columns (any casing/spacing is normalized automatically):
- `order_date` — a parseable date
- `category` — product category
- `revenue` — numeric order revenue

Optional columns that unlock extra charts:
- `region` — bar chart of revenue by region
- `customer_age` — age distribution histogram
- `order_status` — pie chart of status breakdown
- `product_price`, `quantity` — scatter plot of price vs quantity
- any other numeric columns — included in the correlation heatmap

## Project structure

```
app.py                   Flask routes (upload, sample, dashboard)
analysis.py               pandas + seaborn logic, returns base64 chart images
generate_sample_data.py   creates data/ecommerce_data.csv
templates/                Jinja2 templates (base, index, dashboard)
static/uploads/           uploaded CSVs land here
data/ecommerce_data.csv   sample dataset
```

## Notes

- Charts are rendered server-side with matplotlib's non-interactive `Agg`
  backend and embedded directly as base64 PNGs — no static image files to
  clean up.
- `app.secret_key` in `app.py` is a placeholder — set a real secret
  (e.g. from an environment variable) before deploying anywhere public.
- The dev server (`app.run(debug=True)`) is for local use only; use a
  WSGI server like gunicorn for production.

## Extending it

Some natural next steps if you want to go further:
- Swap the in-memory upload for a small SQLite table so history persists
  across restarts.
- Add a date-range or category filter on the dashboard.
- Add cohort/retention analysis if your data has repeat customers.
- Export the dashboard as a PDF report (see the `pdf` skill if you're
  working with Claude on this again).
