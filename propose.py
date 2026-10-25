import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text
import time

import os

# Delete old DB file if it exists so you start fresh every run
if os.path.exists("stock_exchange.db"):
    os.remove("stock_exchange.db")


# 1. Establish database connection (Creates stock_exchange.db automatically)
engine = create_engine("sqlite:///stock_exchange.db")

# 2. Infrastructure Setup: Define Schemas & Relations
with engine.connect() as conn:
    # Dimension Table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS companies (
            ticker TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            sector TEXT
        );
    """))
    # Fact Table with Relational Constraints
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            price_date DATE NOT NULL,
            close_price REAL NOT NULL,
            volume INTEGER,
            FOREIGN KEY (ticker) REFERENCES companies(ticker),
            UNIQUE(ticker, price_date)
        );
    """))
    conn.commit()

# 3. Data Collection (Yahoo Finance API)
tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
print("Fetching live market data from Yahoo Finance...")
raw_data = yf.download(tickers, start="2025-01-01", end="2026-01-01")

# 4. The Ingestion Pipeline (Pandas-to-SQLite)
prices_df = raw_data.stack(level=1).reset_index()
prices_df.columns = ['price_date', 'ticker', 'close_price', 'high_price', 'low_price', 'open_price', 'volume']
clean_prices = prices_df[['price_date', 'ticker', 'close_price', 'volume']].copy()
clean_prices['price_date'] = pd.to_datetime(clean_prices['price_date']).dt.date

# 5. Populate Metadata Dimension Table
companies_data = pd.DataFrame([
    {"ticker": "AAPL", "company_name": "Apple Inc.", "sector": "Tech"},
    {"ticker": "MSFT", "company_name": "Microsoft Corp.", "sector": "Tech"},
    {"ticker": "NVDA", "company_name": "NVIDIA Corp.", "sector": "Tech"},
    {"ticker": "AMZN", "company_name": "Amazon.com Inc.", "sector": "Retail"},
    {"ticker": "GOOGL", "company_name": "Alphabet Inc.", "sector": "Tech"}
])

# Write data into the tables
companies_data.to_sql("companies", con=engine, if_exists="append", index=False)
clean_prices.to_sql("stock_prices", con=engine, if_exists="append", index=False)

# 6. Showcase Something Interesting (Baseline Query Performance Measurement)
start_time = time.time()
with engine.connect() as conn:
    result = conn.execute(text("SELECT price_date, ticker, close_price FROM stock_prices WHERE ticker = 'AAPL' ORDER BY price_date DESC LIMIT 5;"))
    rows = result.fetchall()
end_time = time.time()

print("\n--- INFRASTRUCTURE TEST SUCCESSFUL ---")
print(f"Database populated with {len(clean_prices)} historical records.")
print(f"Baseline Query execution time for 'AAPL': {(end_time - start_time) * 1000:.3f} ms")
print("\nMost recent data fetched from your new database:")
for row in rows:
    print(f"Date: {row[0]} | Ticker: {row[1]} | Close: ${row[2]:.2f}")
